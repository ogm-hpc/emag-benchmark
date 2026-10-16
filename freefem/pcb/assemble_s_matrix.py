#!/usr/bin/env python3
"""Full S matrix from per-port excitations (pcb_problem_benchmark_settings.md
5.11, 5.12, 12.2; handoff task J-0).

run_pcb_benchmark.py run --port all writes one result per excited port j
(result names <set>, <set>@Port2, ...), each holding the column S_ij of the
excited port. This script groups the E2 results of one combination
(default mumps/direct) by case (parameter set with the port part of the name
removed: frequency and tag variants stay separate), assembles the n x n
matrix and checks

  * completeness   every port excited (missing columns are reported),
  * reciprocity    max_ij |S_ij - S_ji| (complex-symmetric system: S = S^T),
  * passivity      column power sum_i |S_ij|^2 <= 1 (lossy structures < 1).

With "differential_pairs" in the problem definition (P07: [[P, N], [P, N]],
pair 1 = side 1), the mixed-mode matrix S_mm = M S M^T (M orthogonal,
d = (P - N)/sqrt2, c = (P + N)/sqrt2, order d1, d2, c1, c2) gives
S_dd21, S_cd21, S_dc21, S_cc21. With "lines" (P08: [[near, far], ...],
near = end of the excited port), near- and far-end crosstalk of every
victim line for the first line as aggressor (NEXT = S(v_near, a_near),
FEXT = S(v_far, a_near)) and the through transmission of the aggressor.

Output: a text report on stdout, and with --json a file with the matrices.

  python3 freefem/pcb/assemble_s_matrix.py --sets P07-1
  python3 freefem/pcb/assemble_s_matrix.py --problems P08 --combo cslp_hx/gmres --json s.json
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
import re
import sys
from pathlib import Path

PCB_DIR = Path(__file__).resolve().parent
ROOT = PCB_DIR.parents[1]
PARAMS_JSON = PCB_DIR / "pcb_case_parameters.json"
DEFAULT_RUNS = ROOT / "results" / "pcb_benchmark" / "runs"
S_RE = re.compile(r"^S(?:(\d)(\d)|(\d+)_(\d+))$")   # run_pcb_benchmark.s_name
RECIPROCITY_TOL = 1.0e-3
PASSIVITY_TOL = 1.0e-6


def parse_s_name(name: str) -> tuple | None:
    """'S21' -> (2, 1), 'S12_3' -> (12, 3) (1-based); None if not an S name."""
    m = S_RE.match(name)
    if not m:
        return None
    g = m.groups()
    return (int(g[0]), int(g[1])) if g[0] else (int(g[2]), int(g[3]))


def load_results(runs: Path, combo: str) -> list:
    preset, krylov = combo.split("/")
    out = []
    for fp in sorted(runs.glob("*.json")):
        try:
            r = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(r, dict) or r.get("preset") != preset or r.get("krylov") != krylov:
            continue
        pcb = r.get("pcb") or {}
        if pcb.get("excitation") != "E2_lumped_port" or not (pcb.get("ports") or {}).get("S"):
            continue
        r["_file"] = fp.name
        out.append(r)
    return out


def case_key(r: dict) -> str:
    """Result name without the '@<port>' part of the excited port (a --mrhs
    result, excited_port 'all', holds every column already)."""
    port = r["pcb"]["excited_port"]
    return "@".join(p for p in r["param_set"].split("@") if p != port)


def assemble(results: list, port_names: list) -> dict:
    """{'S': n x n (None = not computed), 'excited': [...], 'status': {...}}
    from the results of one case (one per excited port)."""
    n = len(port_names)
    s = [[None] * n for _ in range(n)]
    excited, status, files = [], {}, {}
    for r in results:
        port = r["pcb"]["excited_port"]
        cols = port_names if port == "all" else [port]     # --mrhs: all columns in one result
        for pc in cols:
            if pc in excited:
                raise RuntimeError(f"{pc} excited twice ({files[pc]}, {r['_file']})")
            excited.append(pc)
            status[pc], files[pc] = r.get("status"), r["_file"]
        for name, v in r["pcb"]["ports"]["S"].items():
            ij = parse_s_name(name)
            if ij is None:
                continue
            i, jj = ij[0] - 1, ij[1] - 1
            if port_names[jj] not in cols:
                raise RuntimeError(f"{r['_file']}: {name} in the result of excited port {port}")
            s[i][jj] = complex(*v)
    return dict(S=s, excited=[p for p in port_names if p in excited], status=status, files=files)


def reciprocity(s: list) -> float | None:
    n = len(s)
    d = [abs(s[i][j] - s[j][i]) for i in range(n) for j in range(i + 1, n)
         if s[i][j] is not None and s[j][i] is not None]
    return max(d) if d else None


def column_power(s: list) -> list:
    """sum_i |S_ij|^2 per column (None for a missing column)."""
    n = len(s)
    return [sum(abs(s[i][j]) ** 2 for i in range(n)) if all(s[i][j] is not None for i in range(n)) else None
            for j in range(n)]


def mixed_mode(s: list, port_names: list, pairs: list) -> dict:
    """Mixed-mode S matrix of two differential pairs [[P, N], [P, N]]: S_mm =
    M S M^T over the four ports, rows/columns (d1, d2, c1, c2)."""
    idx = [[port_names.index(p) for p in pair] for pair in pairs]
    ports = [k for pair in idx for k in pair]
    sub = [[s[i][j] for j in ports] for i in ports]
    r = 1.0 / math.sqrt(2.0)
    # rows: d1, d2, c1, c2; columns: P1, N1, P2, N2
    m = [[r, -r, 0, 0], [0, 0, r, -r], [r, r, 0, 0], [0, 0, r, r]]
    ms = [[sum(m[a][k] * sub[k][b] for k in range(4)) for b in range(4)] for a in range(4)]
    smm = [[sum(ms[a][k] * m[b][k] for k in range(4)) for b in range(4)] for a in range(4)]
    d1, d2, c1, c2 = range(4)
    return dict(S_mm=smm, Sdd11=smm[d1][d1], Sdd21=smm[d2][d1], Scd21=smm[c2][d1],
                Sdc21=smm[d2][c1], Scc21=smm[c2][c1])


def crosstalk(s: list, port_names: list, lines: list) -> dict:
    """Line 1 as aggressor (excited at its near end): through S(far, near) and,
    for every other line, NEXT = S(v_near, a_near), FEXT = S(v_far, a_near)."""
    a_near, a_far = (port_names.index(p) for p in lines[0])
    out = dict(aggressor=lines[0], through=s[a_far][a_near], victims={})
    for k, (vn, vf) in enumerate(lines[1:], start=2):
        out["victims"][f"line{k}"] = dict(ports=[vn, vf], NEXT=s[port_names.index(vn)][a_near],
                                          FEXT=s[port_names.index(vf)][a_near])
    return out


def db(z: complex | None) -> str:
    if z is None:
        return "-"
    return f"{20 * math.log10(max(abs(z), 1e-300)):7.2f} dB <{math.degrees(cmath.phase(z)):7.1f}"


def cjson(z):
    """complex -> [re, im] recursively (None kept)."""
    if isinstance(z, complex):
        return [z.real, z.imag]
    if isinstance(z, list):
        return [cjson(v) for v in z]
    if isinstance(z, dict):
        return {k: cjson(v) for k, v in z.items()}
    return z


def report(problem: str, key: str, pdef: dict, res: dict, freq) -> tuple:
    """(text, record) for one case."""
    names = [p["label"] for p in pdef["ports"]]
    s = res["S"]
    n = len(names)
    rec = dict(problem=problem, case=key, freq_GHz=freq, ports=names, excited=res["excited"],
               status=res["status"], files=res["files"], S=s)
    lines = [f"== {problem} {key}  f={freq} GHz  {len(res['excited'])}/{n} ports excited"]
    missing = [p for p in names if p not in res["excited"]]
    not_conv = [p for p, st in res["status"].items() if st != "converged"]
    if missing:
        lines.append(f"   missing excitations: {', '.join(missing)}")
    if not_conv:
        st = res["status"]
        lines.append("   not converged: " + ", ".join(f"{p} ({st[p]})" for p in not_conv))
    lines.append("   |S_ij| [dB] (rows i, columns j = excited port)")
    w = max(len(p) for p in names)
    lines.append("   " + " " * w + "".join(f"{p:>9s}" for p in names))
    for i, pi in enumerate(names):
        row = "".join(f"{20 * math.log10(max(abs(v), 1e-300)):9.2f}" if v is not None else f"{'-':>9s}"
                      for v in s[i])
        lines.append(f"   {pi:<{w}s}{row}")
    rd = reciprocity(s)
    pw = column_power(s)
    rec["reciprocity_max_abs_diff"] = rd
    rec["column_power"] = pw
    if rd is not None:
        lines.append(f"   reciprocity max|S_ij - S_ji| = {rd:.2e} "
                     f"({'OK' if rd <= RECIPROCITY_TOL else 'CHECK'}, tol {RECIPROCITY_TOL:g})")
    bad = [names[j] for j, v in enumerate(pw) if v is not None and v > 1 + PASSIVITY_TOL]
    have = [v for v in pw if v is not None]
    if have:
        lines.append(f"   column power sum|S_ij|^2: min {min(have):.4f} max {max(have):.4f}"
                     + (f"  NOT PASSIVE: {', '.join(bad)}" if bad else ""))
    rec["passive"] = not bad if have else None
    pairs = pdef.get("differential_pairs")
    if pairs:
        need = [p for pair in pairs for p in pair]
        if all(s[names.index(a)][names.index(b)] is not None for a in need for b in need):
            mm = mixed_mode(s, names, pairs)
            rec["mixed_mode"] = mm
            lines.append(f"   mixed mode (pairs {pairs}):")
            for k in ("Sdd11", "Sdd21", "Scd21", "Sdc21", "Scc21"):
                lines.append(f"     {k} = {db(mm[k])}")
        else:
            lines.append("   mixed mode: needs all columns of the differential ports")
    tl = pdef.get("lines")
    if tl:
        a_near = tl[0][0]
        if a_near in res["excited"]:
            xt = crosstalk(s, names, tl)
            rec["crosstalk"] = xt
            lines.append(f"   crosstalk, aggressor {tl[0][0]}->{tl[0][1]}: through {db(xt['through'])}")
            for v, d in xt["victims"].items():
                lines.append(f"     {v} {d['ports'][0]}/{d['ports'][1]}: NEXT {db(d['NEXT'])}  "
                             f"FEXT {db(d['FEXT'])}")
        else:
            lines.append(f"   crosstalk: needs the excitation of {a_near}")
    return "\n".join(lines), rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=DEFAULT_RUNS, help="result JSON directory")
    ap.add_argument("--combo", default="mumps/direct", help="preset/krylov of the results (default mumps/direct)")
    ap.add_argument("--problems", default="", help="problems, comma separated (default: all with >= 2 ports)")
    ap.add_argument("--sets", default="", help="parameter sets, comma separated")
    ap.add_argument("--json", type=Path, default=None, help="write the matrices to this file")
    args = ap.parse_args()

    cases = json.loads(PARAMS_JSON.read_text(encoding="utf-8"))
    problems = {s.strip() for s in args.problems.split(",") if s.strip()}
    sets = {s.strip() for s in args.sets.split(",") if s.strip()}
    groups = {}
    for r in load_results(args.runs, args.combo):
        prob = r["case"]
        pdef = cases.get(prob)
        if pdef is None or len(pdef.get("ports", [])) < 2:
            continue
        if problems and prob not in problems:
            continue
        key = case_key(r)
        if sets and key.split("@")[0] not in sets:
            continue
        groups.setdefault((prob, key), []).append(r)
    if not groups:
        print(f"no E2 results of {args.combo} with >= 2 ports in {args.runs}")
        return 1
    records, n_bad = [], 0
    for (prob, key), rs in sorted(groups.items()):
        pdef = cases[prob]
        names = [p["label"] for p in pdef["ports"]]
        rvals = {float(p.get("R", 50.0)) for p in pdef["ports"]}
        if len(rvals) > 1:
            print(f"== {prob} {key}: ports with different R {sorted(rvals)}; the columns use their own "
                  "reference, S is not assembled")
            n_bad += 1
            continue
        freqs = {r["pcb"].get("freq_GHz") for r in rs}
        if len(freqs) > 1:
            raise RuntimeError(f"{prob} {key}: results at different frequencies {sorted(freqs)}")
        res = assemble(rs, names)
        text, rec = report(prob, key, pdef, res, freqs.pop())
        print(text)
        records.append(rec)
        rd = rec["reciprocity_max_abs_diff"]
        n_bad += (rd is not None and rd > RECIPROCITY_TOL) or rec["passive"] is False
    if args.json:
        args.json.write_text(json.dumps(cjson(records), indent=1), encoding="utf-8")
        print(f"-> {args.json}")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
