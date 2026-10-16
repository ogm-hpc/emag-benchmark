#!/usr/bin/env python3
"""Mesh generation and mesh check for the PCB benchmark (settings 6.1-6.3).

Reads freefem/pcb/pcb_case_parameters.json, substitutes each parameter set into
its .geo template (same "name = value;" substitution as ../inject_params.py),
meshes it with the Gmsh Python API (pip install gmsh), checks that every
physical group listed under "physical_groups" exists with the listed tag and
is not empty, and records the mesh statistics of settings 6.2: node,
tetrahedron and boundary-triangle counts, element counts per physical group,
minimum/maximum edge length, maximum aspect ratio, minimum dihedral angle,
number of tetrahedra with a dihedral angle below 5 and 10 degrees, mesh time
and file size.

  python3 gmsh_templates/pcb/generate_pcb_meshes.py --list
  python3 gmsh_templates/pcb/generate_pcb_meshes.py                  # all sets with a template
  python3 gmsh_templates/pcb/generate_pcb_meshes.py --sets P01-1,P01-2
  python3 gmsh_templates/pcb/generate_pcb_meshes.py --suite core,extended,challenge
  python3 gmsh_templates/pcb/generate_pcb_meshes.py --check-only     # no .msh written

Output: generated_meshes/pcb/{geo,mesh}/<set>.{geo,msh} (MSH 2.2) and
generated_meshes/pcb/mesh_report.json. Exit status 1 if a check fails.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent
ROOT = TEMPLATES_DIR.parent
PARAMS_JSON = ROOT / "freefem" / "pcb" / "pcb_case_parameters.json"
DEFAULT_OUT = ROOT / "generated_meshes" / "pcb"

sys.path.insert(0, str(TEMPLATES_DIR))
from inject_params import substitute_parameters  # noqa: E402

TET4 = 4    # Gmsh element type: 4-node tetrahedron
TRI3 = 2    # 3-node triangle
DIHEDRAL_THRESHOLDS = (5, 10)   # [deg] tetrahedra counted by their minimum dihedral angle


def load_cases() -> dict:
    with open(PARAMS_JSON) as f:
        return json.load(f)


def select(cases: dict, problems: list[str] | None, sets: list[str] | None, suites: list[str] | None = None):
    """Parameter sets to mesh; suites as run_pcb_benchmark.py run --suite
    ("suite" of the set, multi_rhs = sets with multiRhsBudgetPerPort)."""
    for prob, pdef in cases.items():
        if problems and prob not in problems:
            continue
        for name, params in pdef["parameter_sets"].items():
            if sets and name not in sets:
                continue
            if suites and not sets:
                tiers = {params.get("suite")} | ({"multi_rhs"} if "multiRhsBudgetPerPort" in params else set())
                if not tiers & set(suites):
                    continue
            yield prob, pdef, name, params


def dihedral_angles(p):
    """The six dihedral angles [deg] of the tetrahedron with vertices p[0..3]."""
    def sub(a, b):
        return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

    def cross(a, b):
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

    def dot(a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    # Outward face normals; face i is opposite vertex i.
    faces = [(1, 2, 3), (0, 3, 2), (0, 1, 3), (0, 2, 1)]
    normals = []
    for i, (a, b, c) in enumerate(faces):
        n = cross(sub(p[b], p[a]), sub(p[c], p[a]))
        if dot(n, sub(p[i], p[a])) > 0:
            n = (-n[0], -n[1], -n[2])
        s = math.sqrt(dot(n, n))
        normals.append((n[0] / s, n[1] / s, n[2] / s))
    out = []
    for i in range(4):
        for j in range(i + 1, 4):
            c = max(-1.0, min(1.0, -dot(normals[i], normals[j])))
            out.append(math.degrees(math.acos(c)))
    return out


def mesh_statistics(gmsh) -> dict:
    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): (coords[3 * k], coords[3 * k + 1], coords[3 * k + 2]) for k, t in enumerate(node_tags)}

    tet_tags, tet_nodes = gmsh.model.mesh.getElementsByType(TET4)
    tri_tags, _ = gmsh.model.mesh.getElementsByType(TRI3)

    min_edge = gmsh.model.mesh.getElementQualities(tet_tags, "minEdge")
    max_edge = gmsh.model.mesh.getElementQualities(tet_tags, "maxEdge")
    gamma = gmsh.model.mesh.getElementQualities(tet_tags, "gamma")
    sicn = gmsh.model.mesh.getElementQualities(tet_tags, "minSICN")

    gmsh.model.mesh.createEdges()
    _, edge_nodes = gmsh.model.mesh.getAllEdges()
    edge_len = [math.dist(xyz[int(edge_nodes[2 * k])], xyz[int(edge_nodes[2 * k + 1])])
                for k in range(len(edge_nodes) // 2)]

    min_dih, max_dih = 180.0, 0.0
    n_small = {t: 0 for t in DIHEDRAL_THRESHOLDS}   # tetrahedra with a dihedral angle < t
    for k in range(len(tet_tags)):
        p = [xyz[int(tet_nodes[4 * k + i])] for i in range(4)]
        a = dihedral_angles(p)
        amin = min(a)
        min_dih = min(min_dih, amin)
        max_dih = max(max_dih, max(a))
        for t in DIHEDRAL_THRESHOLDS:
            n_small[t] += amin < t

    # Number of tetrahedra sharing each triangular face.
    face_count = {}
    for k in range(len(tet_tags)):
        v = sorted(int(tet_nodes[4 * k + i]) for i in range(4))
        for f in ((v[0], v[1], v[2]), (v[0], v[1], v[3]), (v[0], v[2], v[3]), (v[1], v[2], v[3])):
            face_count[f] = face_count.get(f, 0) + 1

    groups = {}
    for dim, tag in gmsh.model.getPhysicalGroups():
        name = gmsh.model.getPhysicalName(dim, tag)
        n = 0
        adj = {0: 0, 1: 0, 2: 0}   # surface triangles by number of adjacent tetrahedra
        for ent in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
            etypes, etags, enodes = gmsh.model.mesh.getElements(dim, ent)
            n += sum(len(t) for t in etags)
            if dim != 2:
                continue
            for et, en in zip(etypes, enodes):
                if et != TRI3:
                    continue
                for k in range(len(en) // 3):
                    f = tuple(sorted(int(x) for x in en[3 * k:3 * k + 3]))
                    c = face_count.get(f, 0)
                    adj[min(c, 2)] += 1
        groups[name] = {"dim": dim, "tag": tag, "elements": n}
        if dim == 2:
            # outer: faces of one tetrahedron; internal: shared by two;
            # orphan: not a face of any tetrahedron (invalid for the solver).
            groups[name].update({"outer": adj[1], "internal": adj[2], "orphan": adj[0]})

    min_e, max_e = min(min_edge), max(max_edge)
    return {
        "nodes": len(node_tags),
        "tetrahedra": len(tet_tags),
        "boundary_triangles": len(tri_tags),
        "edges": len(edge_len),
        "mean_edge": sum(edge_len) / len(edge_len),
        "min_edge": min_e,
        "max_edge": max_e,
        "max_min_edge_ratio": max_e / min_e,
        # aspect ratio = 1/gamma, gamma = 3 * inradius / circumradius (1 for the regular tetrahedron)
        "max_aspect_ratio": 1.0 / min(gamma),
        "min_gamma": min(gamma),
        "min_sicn": min(sicn),
        "min_dihedral_deg": min_dih,
        "max_dihedral_deg": max_dih,
        "tets_dihedral_below_deg": {str(t): n for t, n in n_small.items()},
        "physical_groups": groups,
    }


def check_groups(pdef: dict, groups: dict) -> list[str]:
    errors = []
    expected = pdef.get("physical_groups", {})
    for kind, dim in (("volumes", 3), ("surfaces", 2)):
        for name, tag in expected.get(kind, {}).items():
            g = groups.get(name)
            if g is None:
                errors.append(f"missing physical group {name}")
            elif g["dim"] != dim or g["tag"] != tag:
                errors.append(f"{name}: dim/tag {g['dim']}/{g['tag']}, expected {dim}/{tag}")
            elif g["elements"] == 0:
                errors.append(f"{name}: no elements")
    for name, g in groups.items():
        if g.get("orphan"):
            errors.append(f"{name}: {g['orphan']} triangles are not faces of any tetrahedron")
    # Groups that exist only for some parameter sets: checked when present.
    for kind, dim in (("volumes_optional", 3), ("surfaces_optional", 2)):
        for name, tag in expected.get(kind, {}).items():
            g = groups.get(name)
            if g is not None and (g["dim"] != dim or g["tag"] != tag or g["elements"] == 0):
                errors.append(f"{name}: dim/tag/elements {g['dim']}/{g['tag']}/{g['elements']}, expected {dim}/{tag}/>0")
    return errors


def rel(path: Path) -> str:
    """Path relative to the repository root when inside it (the report), else absolute."""
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def run_one(gmsh, pdef: dict, name: str, params: dict, out: Path, write_msh: bool) -> dict:
    template = TEMPLATES_DIR / pdef["template"]
    geo = substitute_parameters(template.read_text(), params)
    geo_path = out / "geo" / f"{name}.geo"
    geo_path.parent.mkdir(parents=True, exist_ok=True)
    geo_path.write_text(geo)

    # A fresh Gmsh session per set: gmsh.clear() keeps the options, so a template
    # that sets e.g. Mesh.Algorithm3D (P03: HXT) would change the meshes of the
    # sets generated after it in the same run.
    if gmsh.isInitialized():
        gmsh.finalize()
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("General.Verbosity", 2)
    t0 = time.perf_counter()
    gmsh.open(str(geo_path))
    gmsh.model.mesh.generate(3)
    t_mesh = time.perf_counter() - t0

    rec = {"set": name, "template": pdef["template"], "geo": rel(geo_path),
           "gmsh_version": gmsh.__version__, "mesh_time_s": t_mesh}
    rec.update(mesh_statistics(gmsh))
    if write_msh:
        msh_path = out / "mesh" / f"{name}.msh"
        msh_path.parent.mkdir(parents=True, exist_ok=True)
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.write(str(msh_path))
        rec["msh"] = rel(msh_path)
        rec["msh_bytes"] = msh_path.stat().st_size
    rec["errors"] = check_groups(pdef, rec["physical_groups"])
    return rec


def print_record(rec: dict) -> None:
    status = "OK" if not rec["errors"] else "FAIL"
    print(f"== {rec['set']}  [{status}]  {rec['mesh_time_s']:.1f} s")
    print(f"   nodes {rec['nodes']}, edges {rec['edges']}, tets {rec['tetrahedra']}, "
          f"boundary tris {rec['boundary_triangles']}"
          + (f", {rec['msh_bytes'] / 1e6:.1f} MB" if "msh_bytes" in rec else ""))
    print(f"   edge min {rec['min_edge']:.4g} mean {rec['mean_edge']:.4g} max {rec['max_edge']:.4g} (ratio {rec['max_min_edge_ratio']:.1f}), "
          f"max aspect {rec['max_aspect_ratio']:.2f}, dihedral min {rec['min_dihedral_deg']:.2f} "
          f"max {rec['max_dihedral_deg']:.2f} deg, min SICN {rec['min_sicn']:.3f}")
    print("   tets with a dihedral angle below "
          + ", ".join(f"{t} deg: {n}" for t, n in rec["tets_dihedral_below_deg"].items()))
    for gname, g in rec["physical_groups"].items():
        where = f"  (outer {g['outer']}, internal {g['internal']})" if g["dim"] == 2 else ""
        print(f"   {'vol ' if g['dim'] == 3 else 'surf'} {g['tag']:3d} {gname:14s} {g['elements']}{where}")
    for e in rec["errors"]:
        print(f"   ERROR: {e}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problems", help="comma-separated problems (P01,P03,P05)")
    ap.add_argument("--sets", help="comma-separated parameter sets (P01-1,...)")
    ap.add_argument("--suite", help="comma-separated suite tiers (core, extended, challenge, multi_rhs; "
                                    "settings 15); ignored with --sets")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check-only", action="store_true", help="mesh and check, do not write .msh")
    ap.add_argument("--list", action="store_true", help="list parameter sets and exit")
    args = ap.parse_args()

    cases = load_cases()
    problems = args.problems.split(",") if args.problems else None
    sets = args.sets.split(",") if args.sets else None
    suites = args.suite.split(",") if args.suite else None
    jobs = list(select(cases, problems, sets, suites))

    if args.list:
        for prob, pdef, name, params in jobs:
            have = (TEMPLATES_DIR / pdef["template"]).exists()
            print(f"{name:14s} {params.get('role', ''):17s} {params.get('suite') or '-':10s} {params.get('mesh_level', ''):7s} "
                  f"{pdef['template']}{'' if have else '  (template missing)'}")
        return 0

    import gmsh

    records, failed = [], False
    for prob, pdef, name, params in jobs:
        if not (TEMPLATES_DIR / pdef["template"]).exists():
            print(f"-- {name}: skipped, template {pdef['template']} not found")
            continue
        try:
            rec = run_one(gmsh, pdef, name, params, args.out, not args.check_only)
        except Exception as exc:  # Gmsh raises plain Exception
            rec = {"set": name, "template": pdef["template"], "errors": [f"gmsh: {exc}"]}
            print(f"== {name}  [FAIL]  gmsh: {exc}")
        else:
            print_record(rec)
        failed |= bool(rec["errors"])
        records.append(rec)
    if gmsh.isInitialized():
        gmsh.finalize()

    args.out.mkdir(parents=True, exist_ok=True)
    report = args.out / "mesh_report.json"
    with open(report, "w") as f:
        json.dump(records, f, indent=2)
    print(f"report: {report}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
