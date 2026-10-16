#!/usr/bin/env python3
"""Released data of the benchmark (paper 2, chapter 7; next_tasks W6).

Builds, for each parameter set, a folder of the linear system in Matrix Market
format, the mesh and the reference solution, checks it, and zips the whole
release folder:

  <out>/<name>/
    README.pdf                     (W5, copied with --readme)
    MD5SUMS.txt                    md5 of every file of the folder
    sets.csv                       one row per set: problem, tier, frequency, k0, n, nnz, ...
    baseline/summary.csv           rows of pcb_summary.csv of these sets (v1.0, M3 Pro)
    baseline/runs/<job>.json       run records with the full residual histories
    <set>/                         ':' of the canonical sets replaced by '_'
      mesh.msh                     the benchmark mesh (Gmsh 2.2 ASCII, md5 of mesh_md5.txt)
      A.mtx                        system matrix, complex general (PEC rows: penalty)
      b.mtx                        right-hand side, array complex
      x_ref.mtx                    MUMPS reference solution, array complex
      N.mtx                        k0^2 M0 + K0, H(curl) norm matrix, real symmetric (lower triangle)
      G.mtx                        discrete gradient, edges x mesh nodes, integer general
      edges.csv                    edge (row of A), tail node, head node (1-based, G = +1 at head)
      info.json                    set parameters, sizes, checks

Checks per set (written to info.json, the build stops if one fails):
  - mesh md5 equals docs/results_v1/mac_m3pro/mesh_md5.txt
  - the P1 nodes of FreeFEM are the mesh nodes in file order (coordinates)
  - ||b - A x_ref|| / ||b|| of the MUMPS solution is small
  - sqrt(x_ref^H N x_ref) equals the reference norm of solution_check.idp in the
    v1.0 run records (k0^2 ref_l2^2 + ref_curl^2)
  - every row of G has one -1 and one +1

  python3 freefem/pcb/release_data.py build --tier core --name emag_benchmark_core_v1.0 \\
      [--readme path/README.pdf] [--out results/release_v1] [--zip]

Matrices are assembled by pcb_release_export.edp in a job directory made as
run_pcb_benchmark.py makes it (matrix_features.export). Only v1.0 records are read.
"""
import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
import scipy.io
import scipy.sparse as sp

PCB_DIR = Path(__file__).resolve().parent
ROOT = PCB_DIR.parents[1]
sys.path.insert(0, str(PCB_DIR))
import matrix_features as mf  # noqa: E402

REC = ROOT / "docs" / "results_v1" / "mac_m3pro"
RUNS = ROOT / "results" / "pcb_v1"
RES_TOL = 1e-8      # ||b - A x_ref|| / ||b|| of the MUMPS solution
NORM_TOL = 1e-5     # relative difference of ||x_ref||_N to the run record (6 digits there)


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_vec(path: Path) -> np.ndarray:
    with open(path, "rb") as f:
        np.fromfile(f, dtype="<i8", count=1)
        return np.fromfile(f, dtype="<f8")


def load_cvec(path: Path) -> np.ndarray:
    v = load_vec(path)
    n = int(v[0])
    return v[1:1 + n] + 1j * v[1 + n:1 + 2 * n]


def load_sol(path: Path) -> np.ndarray:
    with gzip.open(path, "rt") as f:
        n = int(f.readline())
        v = np.loadtxt(f, dtype=float)
    assert v.shape == (n, 2), path
    return v[:, 0] + 1j * v[:, 1]


def msh_nodes(path: Path) -> np.ndarray:
    """Node coordinates of a Gmsh 2.2 ASCII mesh, in file order (tags 1..n)."""
    with open(path) as f:
        for line in f:
            if line.strip() == "$Nodes":
                n = int(f.readline())
                tags = np.empty(n, dtype=np.int64)
                xyz = np.empty((n, 3))
                for k in range(n):
                    t, x, y, z = f.readline().split()
                    tags[k], xyz[k] = int(t), (float(x), float(y), float(z))
                assert np.array_equal(tags, np.arange(1, n + 1)), "node tags are not 1..n"
                return xyz
    raise ValueError(f"no $Nodes in {path}")


def summary_rows() -> list[dict]:
    rows = list(csv.DictReader((REC / "pcb_summary.csv").open(encoding="utf-8")))
    assert all(r["solverVersion"] == "1.0" for r in rows), "only v1.0 records"
    return rows


def mesh_md5_table() -> dict:
    out = {}
    for line in (REC / "mesh_md5.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, p = line.split(maxsplit=1)
            out[p.strip()] = h
    return out


def folder_name(pset: str) -> str:
    return pset.replace(":", "_")


def build_set(pset: str, rows: list[dict], dest: Path, scratch: Path, freefem_bin: str) -> dict:
    mine = [r for r in rows if r["paramSet"] == pset]
    mumps = next(r for r in mine if r["preset"] == "mumps")
    job = Path(mumps["file"]).stem            # e.g. P01_P01-1__mumps_direct
    rec = json.loads((RUNS / "runs" / f"{job}.json").read_text(encoding="utf-8"))
    mesh = Path(rec["pcb"]["mesh"]) if rec.get("pcb") else None
    if mesh is None:   # canonical set: mesh named as run_pcb_benchmark.py regress does
        case, ps = pset.split(":")
        mesh = Path("generated_meshes") / "mesh" / f"{case}_{ps}.msh"
    mesh_abs = ROOT / mesh
    ref_md5 = mesh_md5_table()[str(mesh)]
    got_md5 = md5(mesh_abs)
    if got_md5 != ref_md5:
        raise RuntimeError(f"{pset}: mesh md5 {got_md5} != mesh_md5.txt {ref_md5}")

    mf.EXPORT_EDP = "pcb_release_export.edp"
    work = mf.export(pset, scratch, freefem_bin)
    log = (work / "export.log").read_text()
    k0 = float(re.search(r"^K0 (\S+)", log, re.M).group(1))

    A = mf.load_bin(work / "A.bin").tocoo()
    Nm = mf.load_bin(work / "N.bin")
    assert abs(Nm.imag).max() == 0, "N is real"
    Nm = Nm.real.tocoo()
    G = mf.load_bin(work / "G.bin").real.tocsr()
    b = load_cvec(work / "b.bin")
    xyz = load_vec(work / "xyz.bin")
    xyz = xyz[1:1 + 3 * int(xyz[0])].reshape(-1, 3)
    x = load_sol(RUNS / "solutions" / f"{job}.sol.gz")
    n = A.shape[0]
    assert b.size == n and x.size == n and G.shape[0] == n and Nm.shape == (n, n)

    # checks
    node = msh_nodes(mesh_abs)
    if node.shape != xyz.shape or np.abs(node - xyz).max() > 1e-9 * max(1.0, np.abs(node).max()):
        raise RuntimeError(f"{pset}: FreeFEM P1 nodes are not the mesh nodes in file order")
    res = np.linalg.norm(b - A.tocsr() @ x) / np.linalg.norm(b)
    if res > RES_TOL:
        raise RuntimeError(f"{pset}: ||b - A x_ref|| / ||b|| = {res:.2e}")
    nx = float(np.sqrt(np.real(np.vdot(x, Nm.tocsr() @ x))))
    sc = next(json.loads((RUNS / "runs" / f"{Path(r['file']).stem}.json").read_text(encoding="utf-8"))
              ["solution_check"] for r in mine if r["preset"] == "npatch_asm")
    nref = float(np.sqrt(k0 ** 2 * sc["ref_l2"] ** 2 + sc["ref_curl"] ** 2))
    if abs(nx / nref - 1) > NORM_TOL:
        raise RuntimeError(f"{pset}: ||x_ref||_N {nx:.6e} != run record {nref:.6e}")
    tail, head = np.empty(n, dtype=np.int64), np.empty(n, dtype=np.int64)
    for i in range(n):
        cols = G.indices[G.indptr[i]:G.indptr[i + 1]]
        vals = G.data[G.indptr[i]:G.indptr[i + 1]]
        if sorted(vals.tolist()) != [-1.0, 1.0]:
            raise RuntimeError(f"{pset}: row {i} of G is {vals}")
        tail[i], head[i] = cols[vals < 0][0], cols[vals > 0][0]

    # write
    d = dest / folder_name(pset)
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(mesh_abs, d / "mesh.msh")
    head_txt = f"emag_benchmark v1.0, set {pset}"
    scipy.io.mmwrite(d / "A.mtx", A, comment=f"{head_txt}: system matrix A (complex symmetric up to rounding; "
                     "PEC rows and columns kept with the on() penalty)", field="complex", precision=17,
                     symmetry="general")
    scipy.io.mmwrite(d / "b.mtx", b.reshape(-1, 1), comment=f"{head_txt}: right-hand side b",
                     field="complex", precision=17)
    scipy.io.mmwrite(d / "x_ref.mtx", x.reshape(-1, 1), comment=f"{head_txt}: MUMPS reference solution",
                     field="complex", precision=17)
    # N only measures errors: its lower triangle (N is symmetric up to rounding, about 1e-14)
    scipy.io.mmwrite(d / "N.mtx", sp.tril(Nm).tocoo(),
                     comment=f"{head_txt}: H(curl) norm matrix k0^2 M0 + K0 (lower triangle), k0 = {k0!r}",
                     field="real", precision=17, symmetry="symmetric")
    scipy.io.mmwrite(d / "G.mtx", sp.coo_matrix(G).astype(np.int64),
                     comment=f"{head_txt}: discrete gradient, rows = edges (rows of A), "
                     "columns = mesh nodes (Gmsh node tags)", field="integer", symmetry="general")
    with open(d / "edges.csv", "w") as f:
        f.write("edge,tail_node,head_node\n")
        f.writelines(f"{i + 1},{t + 1},{h + 1}\n" for i, (t, h) in enumerate(zip(tail, head)))
    r0 = mumps
    info = {
        "set": pset, "problem": r0["problem"], "tier": r0["suite"], "solver_version": "1.0",
        "frequency_GHz": float(r0["frequencyGHz"]) if r0["frequencyGHz"] else None,
        "length_unit": r0["lengthUnit"] or None, "k0": k0, "excitation": r0["excitation"],
        "excited_port": r0["excitedPort"] or None, "conductor_model": r0["conductorModel"] or None,
        "n": n, "nnz_A": int(A.nnz), "nnz_N_lower": int(sp.tril(Nm).nnz), "mesh_nodes": int(G.shape[1]),
        "mesh_md5": got_md5,
        "checks": {"relres_b_minus_A_xref": res, "norm_N_xref": nx, "norm_ref_run_record": nref,
                   "fem_nodes_equal_mesh_nodes": True, "G_rows_pm1": True},
        "mumps_time_s": float(r0["totalTime"]),
    }
    (d / "info.json").write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
    shutil.rmtree(work)
    print(f"{pset}: n {n}, nnz(A) {A.nnz}, relres {res:.1e}, |x|_N / record - 1 = {nx / nref - 1:.1e}", flush=True)
    return info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    bd = sub.add_parser("build")
    bd.add_argument("--tier", choices=["core", "extended", "challenge", "all"], default="core")
    bd.add_argument("--sets", default="", help="comma-separated sets instead of --tier")
    bd.add_argument("--name", default="emag_benchmark_core_v1.0")
    bd.add_argument("--out", default=str(ROOT / "results" / "release_v1"))
    bd.add_argument("--readme", default="", help="README.pdf to put at the top of the folder")
    bd.add_argument("--zip", action="store_true", help="zip the folder to <out>/<name>.zip")
    bd.add_argument("--zip-by-problem", action="store_true",
                    help="zip per problem to <out>/<name>_files/: <name>_<problem>.zip (the set folders),"
                         " <name>_baseline.zip, and README.pdf, sets.csv, MD5SUMS.txt as they are"
                         " (Zenodo; every zip unpacks into <name>/)")
    bd.add_argument("--freefem-bin", default="FreeFem++-mpi")
    a = ap.parse_args()

    rows = summary_rows()
    sets = sorted({r["paramSet"] for r in rows if a.tier == "all" or r["suite"] == a.tier})
    if a.sets:
        sets = a.sets.split(",")
    dest = Path(a.out) / a.name
    scratch = Path(a.out) / "_work"
    dest.mkdir(parents=True, exist_ok=True)
    infos = []
    for s in sets:
        if (dest / folder_name(s) / "info.json").exists():
            infos.append(json.loads((dest / folder_name(s) / "info.json").read_text(encoding="utf-8")))
            print(f"{s}: kept", flush=True)
            continue
        infos.append(build_set(s, rows, dest, scratch, a.freefem_bin))

    keys = ["set", "problem", "tier", "frequency_GHz", "length_unit", "k0", "excitation", "excited_port",
            "conductor_model", "n", "nnz_A", "mesh_nodes", "mesh_md5"]
    with open(dest / "sets.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["folder"] + keys)
        for i in infos:
            w.writerow([folder_name(i["set"])] + [i[k] for k in keys])
    bl = dest / "baseline" / "runs"
    bl.mkdir(parents=True, exist_ok=True)
    mine = [r for r in rows if r["paramSet"] in sets]
    with open(dest / "baseline" / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(mine)
    for r in mine:
        shutil.copyfile(RUNS / "runs" / r["file"], bl / r["file"])
    if a.readme:
        shutil.copyfile(a.readme, dest / "README.pdf")
    files = sorted(p for p in dest.rglob("*") if p.is_file() and p.name != "MD5SUMS.txt")
    (dest / "MD5SUMS.txt").write_text("".join(f"{md5(p)}  {p.relative_to(dest)}\n" for p in files))
    if a.zip:
        z = Path(a.out) / f"{a.name}.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for p in sorted(dest.rglob("*")):
                if p.is_file():
                    zf.write(p, Path(a.name) / p.relative_to(dest))
        print(f"zip {z}: {z.stat().st_size / 1e6:.0f} MB")
    if a.zip_by_problem:
        zdir = Path(a.out) / f"{a.name}_files"
        zdir.mkdir(parents=True, exist_ok=True)
        groups = {}
        for i in infos:
            prob = i["problem"][:3] if i["problem"].startswith("P08") else i["problem"]   # P08-N2/N4/N8
            groups.setdefault(prob, []).append(dest / folder_name(i["set"]))
        groups["baseline"] = [dest / "baseline"]
        for g, dirs in sorted(groups.items()):
            z = zdir / f"{a.name}_{g}.zip"
            with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                for d in dirs:
                    for p in sorted(d.rglob("*")):
                        if p.is_file():
                            zf.write(p, Path(a.name) / p.relative_to(dest))
            print(f"zip {z.name}: {z.stat().st_size / 1e6:.0f} MB", flush=True)
        for f in ("README.pdf", "sets.csv", "MD5SUMS.txt"):
            if (dest / f).exists():
                shutil.copyfile(dest / f, zdir / f)
    tot = sum(p.stat().st_size for p in dest.rglob("*") if p.is_file())
    print(f"{dest}: {len(sets)} sets, {tot / 1e6:.0f} MB uncompressed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
