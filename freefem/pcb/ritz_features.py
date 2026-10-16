#!/usr/bin/env python3
"""Ritz-value features of the preconditioned operators (docs/matrix_features.md 8).

pcb_ritz_probe.idp (run_pcb_benchmark.py ritz) writes the Hessenberg matrix
Hbar ((m+1) x m) of m Arnoldi steps on A M^-1 started from the right-hand
side. From it:

  Ritz values           eig(H_m); residual estimate |h_{m+1,m}| |e_m^T y|
  harmonic Ritz values  eig(H_m + |h_{m+1,m}|^2 H_m^-H e_m e_m^T) (better near 0)
  kappa_ritz            max|Ritz| / min|harmonic Ritz|
  n_small_harm          harmonic Ritz values with |theta| < 1e-2 max|Ritz|
  origin_sep            max_phi min_j Re(e^-i phi theta_j) / max|theta| over the
                        Ritz values: > 0 iff a line separates them from 0
  rho_q, q_out          disk model: the q smallest Ritz values are outliers,
                        the rest lie in a disk |z - c| <= rho |c|; q chosen to
                        minimize pred_iterations = q + log(rtol)/log(rho_q)
  gmres_relres          the GMRES residual curve of the same m steps, exact from
                        Hbar (min ||beta e_1 - Hbar_k y||); extrap_iterations
                        continues its rate over the last 50 steps to rtol

  python3 freefem/pcb/ritz_features.py summarize                     # this host
  python3 freefem/pcb/ritz_features.py summarize --out docs/pcb_results/mac_m3pro
  python3 freefem/pcb/ritz_features.py summarize --src results/pcb_ritz_v1 \
      --iters docs/results_v1/mac_m3pro/pcb_summary.csv --out docs/results_v1/mac_m3pro   # v1.0
  python3 freefem/pcb/ritz_features.py show results/pcb_ritz/mac_m3pro/hessenberg/P05_P05-1__hx.txt
  python3 freefem/pcb/ritz_features.py refeature    # recompute the features of all runs from
                                                    # hessenberg/ (after changing this file)

The iteration counts next to the features come from the same host's records
(docs/pcb_results/<host>/pcb_summary.csv; WSL: docs/pcb_results/pcb_summary.csv),
so Mac probes are compared with Mac solves only (CLAUDE.md).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

PCB_DIR = Path(__file__).resolve().parent
ROOT = PCB_DIR.parents[1]
sys.path.insert(0, str(PCB_DIR))

RTOL = 1e-8
SMALL_REL = 1e-2       # n_small_harm threshold, relative to max|Ritz|
MAX_OUTLIERS = 30      # disk model: largest number of outliers tried
RATE_WINDOW = 50       # extrap_iterations: steps over which the GMRES rate is taken
MAX_PRED = 10**6       # pred_iterations / extrap_iterations above this: None (rho ~ 1)


def load_hessenberg(path: Path) -> tuple:
    """(Hbar (m+1) x m complex, beta = ||start vector||, n) from pcb_ritz_probe.idp's file."""
    lines = Path(path).read_text().splitlines()
    m, n, beta = lines[0].split()
    m = int(m)
    rows = [np.array(l.split(), dtype=float) for l in lines[1:m + 2]]
    H = np.array([r[0::2] + 1j * r[1::2] for r in rows])
    return H.reshape(m + 1, m), float(beta), int(n)


def gmres_curve(Hbar: np.ndarray) -> np.ndarray:
    """Relative GMRES residual after k = 1..m steps: min ||e_1 - Hbar_k y||
    (Givens rotations on a copy, as gmres_precon.idp)."""
    H = Hbar.astype(complex).copy()
    m = H.shape[1]
    g = np.zeros(m + 1, complex)
    g[0] = 1.0
    res = np.empty(m)
    for j in range(m):
        # rotation j zeroes H[j+1, j]; applied at once to rows j, j+1 of all
        # later columns (the earlier rotations have already been applied there)
        a, b = H[j, j], H[j + 1, j]
        r = math.hypot(abs(a), abs(b))
        c, s = (1.0, 0.0) if r == 0 else (abs(a) / r, (a / abs(a) if abs(a) else 1.0) * np.conj(b) / r)
        Hj, Hj1 = H[j, j:].copy(), H[j + 1, j:].copy()
        H[j, j:] = c * Hj + s * Hj1
        H[j + 1, j:] = -np.conj(s) * Hj + c * Hj1
        g[j], g[j + 1] = c * g[j], -np.conj(s) * g[j]
        res[j] = abs(g[j + 1])
    return res


def disk_rho(z: np.ndarray) -> float:
    """min over centres c of max_j |z_j - c| / |c| (>= 1: no disk excludes 0)."""
    if z.size == 0:
        return 0.0

    def f(p):
        c = complex(p[0], p[1])
        return np.max(np.abs(z - c)) / abs(c) if abs(c) > 0 else np.inf
    best = np.inf
    scale = np.max(np.abs(z))
    for c0 in (z.mean(), 0.5 * (z.real.min() + z.real.max()) + 0.5j * (z.imag.min() + z.imag.max()),
               z[np.argmax(np.abs(z))], scale + 0j):
        if abs(c0) == 0:
            continue
        r = minimize(f, [c0.real, c0.imag], method="Nelder-Mead",
                     options=dict(xatol=1e-10 * scale, fatol=1e-12, maxiter=4000))
        best = min(best, r.fun)
    return float(best)


def origin_sep(z: np.ndarray, n_phi: int = 7200) -> float:
    phi = np.linspace(0.0, 2 * np.pi, n_phi, endpoint=False)
    proj = (np.exp(-1j * phi)[:, None] * z[None, :]).real
    return float(proj.min(axis=1).max() / np.max(np.abs(z)))


def features(Hbar: np.ndarray, rtol: float = RTOL) -> dict:
    m = Hbar.shape[1]
    Hm = Hbar[:m, :m]
    h = abs(Hbar[m, m - 1])
    theta, Y = np.linalg.eig(Hm)
    ritz_res = h * np.abs(Y[m - 1, :]) / np.linalg.norm(Y, axis=0)
    em = np.zeros(m, complex)
    em[-1] = 1.0
    try:
        f = np.linalg.solve(Hm.conj().T, em)
        Mh = Hm.copy()
        Mh[:, m - 1] += h * h * f
        harm = np.linalg.eigvals(Mh)
    except np.linalg.LinAlgError:
        harm = theta.copy()
    amax = float(np.max(np.abs(theta)))
    hmin = float(np.min(np.abs(harm)))
    order = np.argsort(np.abs(theta))
    rhos = []
    best = (None, None, None)   # (pred, q, rho)
    for q in range(0, min(MAX_OUTLIERS, m - 2) + 1):
        rho = disk_rho(theta[order[q:]])
        rhos.append(rho)
        if rho < 1.0:
            pred = q + (math.ceil(math.log(rtol) / math.log(rho)) if rho > 0 else 1)
            if pred <= MAX_PRED and (best[0] is None or pred < best[0]):
                best = (pred, q, rho)
    res = gmres_curve(Hbar)
    hit = np.nonzero(res <= rtol)[0]
    it_rtol = int(hit[0]) + 1 if hit.size else None
    extrap, rate = it_rtol, None
    if it_rtol is None and m > 2 * 5:
        w = min(RATE_WINDOW, m // 2)
        rate = float((res[-1] / res[-1 - w]) ** (1.0 / w))
        extrap = int(math.ceil(m + math.log(rtol / res[-1]) / math.log(rate))) if rate < 1 else None
        if extrap is not None and extrap > MAX_PRED:
            extrap = None
    rel_res = ritz_res / np.maximum(np.abs(theta), 1e-300)
    return dict(
        m=m, h_last=float(h),
        ritz_abs_max=amax, ritz_abs_min=float(np.min(np.abs(theta))), harm_abs_min=hmin,
        kappa_ritz=amax / hmin if hmin > 0 else None,
        n_small_harm=int(np.sum(np.abs(harm) < SMALL_REL * amax)),
        n_ritz_conv=int(np.sum(rel_res < 1e-6)),
        origin_sep=origin_sep(theta),
        re_min_rel=float(theta.real.min() / amax), n_re_neg=int(np.sum(theta.real < 0)),
        rho_0=rhos[0], q_out=best[1], rho_q=best[2], pred_iterations=best[0],
        gmres_relres_m=float(res[-1]), gmres_it_rtol=it_rtol, gmres_rate_tail=rate,
        extrap_iterations=extrap,
        gmres_relres=[float(x) for x in res],
        ritz=[[float(z.real), float(z.imag)] for z in theta[order]],
        ritz_rel_res=[float(x) for x in rel_res[order]],
        harmonic_ritz=[[float(z.real), float(z.imag)] for z in harm[np.argsort(np.abs(harm))]],
    )


# ---------------------------------------------------------------------------
# Summary table

SUMMARY_PRECS = ("gs", "ssor", "amg_gamg", "accel_ic", "cslp", "hx", "cslp_hx", "npatch_asm")


def solver_iterations(host: str, path: Path | None = None) -> dict:
    """{(set, preset, krylov): iterations | 'T' | status} from host's own records
    (path: a pcb_summary.csv, default docs/pcb_results/<host>/); existing sets
    are keyed <case>:<set> as their probes."""
    path = path or ROOT / "docs" / "pcb_results" / ("" if host == "wsl" else host) / "pcb_summary.csv"
    out = {}
    if not path.exists():
        return out
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r["variant"] or r["tag"] or r["excitation"] not in ("E2_lumped_port", "gaussian_volume_source"):
            continue
        out[(r["paramSet"], r["preset"], r["krylov"])] = (
            r["iterations"] if r["status"] == "converged" else "T" if r["status"] == "timeout" else r["status"])
    return out


def fmt(x, f):
    return "" if x is None else f.format(x)


def summarize(host: str, src: Path, out: Path, start: str, iters: Path | None = None) -> int:
    runs = sorted((src / host / "runs").glob("*.json"))
    recs = [json.loads(p.read_text()) for p in runs]
    recs = [r for r in recs if r.get("start") == start]
    if not recs:
        print(f"no Ritz probe results for host {host} (start {start}) in {src / host / 'runs'}")
        return 1
    its = solver_iterations(host, iters)
    order = {p: i for i, p in enumerate(SUMMARY_PRECS)}
    recs.sort(key=lambda r: (r["set"], order.get(r["prec"], 99)))
    cols = ["set", "prec", "n", "m", "kappa_ritz", "n_small_harm", "origin_sep", "n_re_neg",
            "q_out", "rho_q", "pred_it", "gmres_res_m", "probe_it", "extrap_it", "it_gmres", "it_cocg",
            "inner", "status"]
    rows = []
    for r in recs:
        f = r.get("features") or {}
        rows.append(dict(
            set=r["set"], prec=r["prec"], n=r.get("n", ""), m=f.get("m", ""),
            kappa_ritz=fmt(f.get("kappa_ritz"), "{:.1e}"), n_small_harm=f.get("n_small_harm", ""),
            origin_sep=fmt(f.get("origin_sep"), "{:+.2f}"), n_re_neg=f.get("n_re_neg", ""),
            q_out=fmt(f.get("q_out"), "{}"), rho_q=fmt(f.get("rho_q"), "{:.3f}"),
            pred_it=fmt(f.get("pred_iterations"), "{}"),
            gmres_res_m=fmt(f.get("gmres_relres_m"), "{:.1e}"),
            probe_it=fmt(f.get("gmres_it_rtol"), "{}"),
            extrap_it=fmt(f.get("extrap_iterations"), "{}") if f.get("gmres_it_rtol") is None else "",
            it_gmres=its.get((r["set"], r["prec"], "gmres"), ""),
            it_cocg=its.get((r["set"], r["prec"], "cocg"), ""),
            inner=r.get("inner") or "", status=r["status"]))
    out.mkdir(parents=True, exist_ok=True)
    name = "ritz_features" + ("" if start == "rhs" else f"@{start}")
    with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    md = [f"# Ritz値の特徴量（{host}、開始ベクトル {start}）", "",
          "`freefem/pcb/ritz_features.py summarize` が出力。列の意味は `docs/matrix_features.md` 8章。"
          f"反復数（it_gmres、it_cocg）は同じ計算機の標準の組合せの記録"
          f"（`{(iters or Path('docs/pcb_results') / host / 'pcb_summary.csv').as_posix()}`。"
          "T: 600秒で打ち切り、max_it: 上限 \\(K_{\\max}\\)）。"
          "probe_it はプローブの m ステップ以内に GMRES が \\(10^{-8}\\) に達した反復数、"
          "extrap_it は達しなかったときの末尾50ステップの収束率による外挿。"
          "inner は cslp・hx・cslp_hx の内側の解法（lu: MUMPS で厳密、vcycle: GAMG の V サイクル1回）。"
          "標準の組合せは内側を GMRES（rtol \\(10^{-2}\\)）で解くので、inner のある行は標準とは別の"
          "（標準が近似している）演算子である。", "",
          "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    md += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    (out / f"{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{len(rows)} rows -> {out / name}.md, .csv")
    return 0


def main() -> int:
    import pcb_host
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summarize")
    s.add_argument("--host", default=pcb_host.detect().name)
    s.add_argument("--src", type=Path, default=ROOT / "results" / "pcb_ritz")
    s.add_argument("--out", type=Path, default=None, help="default: results/pcb_ritz/<host>")
    s.add_argument("--start", default="rhs", choices=["rhs", "random"])
    s.add_argument("--iters", type=Path, default=None,
                   help="pcb_summary.csv of the iteration counts (default docs/pcb_results/<host>/; "
                        "v1.0: docs/results_v1/mac_m3pro/pcb_summary.csv)")
    rf = sub.add_parser("refeature")
    rf.add_argument("--host", default=pcb_host.detect().name)
    rf.add_argument("--src", type=Path, default=ROOT / "results" / "pcb_ritz")
    sh = sub.add_parser("show")
    sh.add_argument("file", type=Path)
    a = ap.parse_args()
    if a.cmd == "refeature":
        n = 0
        for p in sorted((a.src / a.host / "runs").glob("*.json")):
            r = json.loads(p.read_text())
            hess = a.src / a.host / "hessenberg" / f"{p.stem}.txt"
            if r.get("status") == "ok" and hess.exists():
                r["features"] = features(load_hessenberg(hess)[0])
                p.write_text(json.dumps(r), encoding="utf-8")
                n += 1
        print(f"{n} runs updated")
        return 0
    if a.cmd == "summarize":
        return summarize(a.host, a.src, a.out or a.src / a.host, a.start, a.iters)
    H, beta, n = load_hessenberg(a.file)
    f = features(H)
    for k, v in f.items():
        if not isinstance(v, list):
            print(f"{k:18s} {v}")
    print("smallest Ritz values:", ", ".join(f"{complex(*z):.3g}" for z in f["ritz"][:8]))
    print("smallest harmonic:   ", ", ".join(f"{complex(*z):.3g}" for z in f["harmonic_ritz"][:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
