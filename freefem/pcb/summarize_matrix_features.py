#!/usr/bin/env python3
"""Table of the matrix features (matrix_features.py) next to the solver
results (docs/matrix_features.md 6).

Reads results/pcb_features/<host>/*.json and joins, per set, the iteration
counts of the WSL records: docs/pcb_results/pcb_summary.csv (PCB sets, rows
without variant / tag, first port) and docs/benchmark_report/summary.csv
(existing benchmark, case:param_set). Writes Markdown and CSV.

  python3 freefem/pcb/summarize_matrix_features.py                 # this host
  python3 freefem/pcb/summarize_matrix_features.py --host mac_m3pro --out docs/pcb_results/mac_m3pro
  python3 freefem/pcb/summarize_matrix_features.py --features results/pcb_features_v1 \
      --iters docs/results_v1/mac_m3pro/pcb_summary.csv --out docs/results_v1/mac_m3pro   # v1.0

--from-csv takes the feature columns from an earlier matrix_features.csv
instead of the JSON files (they stay on the machine that computed them) and
only refills the iteration counts, e.g. on WSL after new runs:

  python3 freefem/pcb/summarize_matrix_features.py --host mac_m3pro \\
      --from-csv docs/pcb_results/mac_m3pro/matrix_features.csv --out docs/pcb_results/mac_m3pro
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

PCB_DIR = Path(__file__).resolve().parent
ROOT = PCB_DIR.parents[1]
sys.path.insert(0, str(PCB_DIR))
import pcb_host  # noqa: E402

COMBOS = ["ssor/gmres", "amg_gamg/gmres", "hx/gmres", "cslp/gmres", "cslp_hx/gmres", "ssor/cocg", "npatch_asm/cocg"]


def status_cell(r: dict) -> str:
    return r["iterations"] if r["status"] == "converged" else "T" if r["status"] == "timeout" else r["status"]


def solver_results(iters: Path | None = None) -> dict:
    """{set: {combo: 'iterations' | 'T' (timeout) | other status}}; iters: one
    pcb_summary.csv with the PCB and the existing sets (<case>:<set>), e.g. the
    v1.0 records docs/results_v1/mac_m3pro/pcb_summary.csv."""
    out: dict = {}
    if iters:
        for r in csv.DictReader(open(iters, encoding="utf-8")):
            if r["variant"] or r["tag"] or r["excitation"] not in ("E2_lumped_port", "gaussian_volume_source"):
                continue
            out.setdefault(r["paramSet"], {})[f"{r['preset']}/{r['krylov']}"] = status_cell(r)
        return out
    for r in csv.DictReader(open(ROOT / "docs" / "pcb_results" / "pcb_summary.csv", encoding="utf-8")):
        if r["variant"] or r["tag"] or r["excitation"] != "E2_lumped_port":
            continue
        combo = f"{r['preset']}/{r['krylov']}"
        out.setdefault(r["paramSet"], {})[combo] = (r["iterations"] if r["status"] == "converged"
                                                    else "T" if r["status"] == "timeout" else r["status"])
    for r in csv.DictReader(open(ROOT / "docs" / "benchmark_report" / "summary.csv", encoding="utf-8")):
        out.setdefault(f"{r['case']}:{r['param_set']}", {})[r["combo"]] = (
            r["iterations"] if r["status"] == "converged" else "T" if r["status"] == "timeout" else r["status"])
    return out


def g(x, fmt):
    return "" if x is None else fmt.format(x)


def row(d: dict, res: dict) -> dict:
    near = d["modes_near_k0"][0] if d.get("modes_near_k0") else {}
    curl = max(d["eig_near0_curl_rayleigh"]) if d.get("eig_near0_curl_rayleigh") else None
    r = {
        "set": d["set"], "n": d["n"],
        "herm_rel": g(d["herm_rel"], "{:.0e}"), "nonnormal_rel": g(d["nonnormal_rel"], "{:.0e}"),
        "n_neg_R": d["inertia_R"]["neg"], "N_grad": d["N_grad"], "beta": d["beta_harmonic"],
        # invalid with SIBC (docs/matrix_features.md 2.2); older results lack has_sibc
        "modes_below_k0": "" if d.get("has_sibc", "sibc" in d["set"]) else d["modes_below_k0_est"],
        "S_neg": d["inertia_S"]["neg"] if "inertia_S" in d else "",
        "S_min_rel": g(None if d["S_lambda_min"] is None else d["S_lambda_min"] / d["sigma_max"], "{:.0e}"),
        "kappa_2": g(d["kappa_2"], "{:.1e}"), "kappa_2_jacobi": g(d["kappa_2_jacobi"], "{:.1e}"),
        "eig0_curl_max": g(curl, "{:.0e}"),
        "open": "Y" if d.get("open_boundary") else "N",
        # resonance only for closed problems (not robust with SM / UPML, docs 5.3)
        "reso_reldist": "" if d.get("open_boundary") else g(d["resonance_reldist"], "{:.3f}"),
        "reso_q": "" if d.get("open_boundary") else
                  "inf" if (near.get("q") or 0) > 1e12 else g(near.get("q"), "{:.0f}"),
        "wall_s": d["wall_s"],
    }
    for c in COMBOS:
        r[c] = res.get(d["set"], {}).get(c, "")
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=pcb_host.detect().name)
    ap.add_argument("--features", type=Path, default=ROOT / "results" / "pcb_features")
    ap.add_argument("--from-csv", type=Path, default=None,
                    help="take the features from this matrix_features.csv and refill only the iteration counts")
    ap.add_argument("--out", type=Path, default=None, help="directory for matrix_features.md / .csv (default: print)")
    ap.add_argument("--iters", type=Path, default=None,
                    help="pcb_summary.csv of the iteration counts (default: the WSL records; "
                         "v1.0: docs/results_v1/mac_m3pro/pcb_summary.csv)")
    a = ap.parse_args()
    res = solver_results(a.iters)
    if a.from_csv:
        rows = list(csv.DictReader(open(a.from_csv, encoding="utf-8")))
        for r in rows:
            for c in COMBOS:
                r[c] = res.get(r["set"], {}).get(c, "")
    else:
        files = sorted((a.features / a.host).glob("*.json"))
        rows = [row(json.loads(f.read_text(encoding="utf-8")), res) for f in files]
    key = lambda r: (not r["set"].startswith("P"), r["set"])
    rows.sort(key=key)
    cols = list(rows[0].keys()) if rows else []
    md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    md += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    text = "\n".join(md) + "\n"
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "matrix_features.md").write_text(
            f"# 行列の特徴量（{a.host}）\n\n`freefem/pcb/summarize_matrix_features.py` で生成。列の意味は "
            "[docs/matrix_features.md](../../matrix_features.md) の4章・6章。反復数は "
            + (f"`{a.iters.as_posix()}`（max_it: 上限 \\(K_{{\\max}}\\)）" if a.iters else "WSL の記録（T: 打切り）")
            + "。\n\n"
            + text, encoding="utf-8")
        with open(a.out / "matrix_features.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
