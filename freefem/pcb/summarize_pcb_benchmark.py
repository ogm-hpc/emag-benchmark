#!/usr/bin/env python3
"""Summary of the PCB benchmark results (pcb_problem_benchmark_settings.md 13.2, 15.5).

Reads the result JSONs of run_pcb_benchmark.py run (<out>/runs/*.json) and
writes, into --dest:

  pcb_summary.csv            standard runs (result name without '@'), one row per
                             case x combination (13.2 columns where they apply)
  pcb_summary_variants.csv   runs with '@' in the name (other port, E1, --freq,
                             --tag: sensitivity and diagnostic variants)
  pcb_summary.md             Markdown: status/time matrix and detailed table of
                             the standard runs, then the table of the variants

Times: setup = time to the first residual (mesh read, assembly, preconditioner
set-up), solve = last residual time - setup, total = wall-clock time of the
process. |dS| = max over the S-parameters of |S - S_MUMPS| against the
mumps/direct result of the same case (for a tagged variant: the same case
without the tag, unless the tag has its own MUMPS result; for a set whose
only MUMPS result is --mrhs shared, that full S matrix). MUMPS results are
taken from <out>/runs first, then from the --refs directories (default
results/pcb_ports, where the minimal-set references of task C are).
Solution errors (run --ref-solutions; empty otherwise): relative L2, curl and
H(curl) errors against the saved MUMPS solution (solErrL2, solErrCurl,
solErrHcurl; CSV only). The time of the solution save / error check is not
counted in total.

  python3 freefem/pcb/summarize_pcb_benchmark.py                          # results/pcb_benchmark
  python3 freefem/pcb/summarize_pcb_benchmark.py --out results/pcb_benchmark --dest docs/pcb_results

docs/pcb_results/ holds the records of the reference WSL machine. On a Mac
(pcb_host.py) the summary goes to docs/pcb_results/<host>/ (e.g. mac_m1,
mac_m3pro); writing a Mac's results (or results of another host) into
docs/pcb_results/ itself is refused.

The records of solver v1.0 (docs/paper_plan.md A4) go to docs/results_v1/mac_m3pro/
only: results of another machine, of several machines, or of another
PCB_SOLVER_VERSION than 1.0 are refused there.

  python3 freefem/pcb/summarize_pcb_benchmark.py --dest docs/results_v1/mac_m3pro  # v1.0 records (M3 Pro)

  python3 freefem/pcb/summarize_pcb_benchmark.py --dest docs/pcb_results/mac_m1    # on the M1 Mac
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

PCB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PCB_DIR.parent))

import run_benchmark as rb  # noqa: E402
import pcb_host  # noqa: E402
import convergence_trend as ct  # noqa: E402

ROOT = PCB_DIR.parents[1]
PARAMS_JSON = PCB_DIR / "pcb_case_parameters.json"
EXISTING_JSON = ROOT / "gmsh_templates" / "case_parameters.json"   # case1A-3F (docs/paper_plan.md A2)
DIRECT_COMBO = "mumps/direct"
COMBO_ORDER = list(rb.DEFAULT_COMBOS) + ["npatch_asm/cocg", DIRECT_COMBO]   # run_pcb_benchmark.PCB_DEFAULT_COMBOS
HX_COMBOS = ("hx/gmres", "cslp_hx/gmres")   # run_pcb_benchmark.HX_MASK_COMBOS

COLUMNS = [
    "problem", "caseId", "paramSet", "variant", "suite", "krylov", "preset", "status", "reason", "dof",
    "iterations", "finalRelativeResidual", "minRelativeResidual", "trueRelativeResidual",
    "setupTime", "solveTime", "totalTime", "peakRssGb", "sMaxAbsDiffMumps",
    "solErrL2", "solErrCurl", "solErrHcurl",
    "frequencyGHz", "lengthUnit", "excitation", "excitedPort", "conductorModel", "restart", "accelIcAlpha", "hxMask", "tag",
    "petscExtra",
    "budgetSecond", "kMax", "historyFull",
    # supplementary information of the runs stopped at K_max (or at the time budget before
    # v1.0): convergence_trend.supplement (docs/paper_plan.md 4.2; cslp_hx: N_est pessimistic)
    "trendWindow", "trendSlope", "trendRho", "trendNest", "trendRhoCyc", "trendLastUpdate",
    "trendDropWindow", "timePerIteration", "trendTimeToConverge",
    "solverVersion", "file",
]
TREND_STATUS = ("max_it", "timeout")

STATUS_SHORT = {"converged": "conv", "max_it": "max_it", "timeout": "timeout", "setup_timeout": "setup-timeout",
                "breakdown": "breakdown", "error": "error", "stopped": "stopped"}


def load_runs(runs: Path) -> list:
    out = []
    for fp in sorted(runs.glob("*.json")):
        try:
            r = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  {fp.name}: unreadable ({e}), skipped")
            continue
        if not isinstance(r, dict) or "param_set" not in r or "preset" not in r:
            print(f"  {fp.name}: not a run_pcb_benchmark.py result, skipped")
            continue
        r["_file"] = fp.name
        out.append(r)
    return out


def s_params(r: dict) -> dict:
    """{name: complex} of a result ({} without S-parameters)."""
    s = ((r.get("pcb") or {}).get("ports") or {}).get("S") or {}
    return {k: complex(*v) for k, v in s.items()}


def reference_key(r: dict) -> list:
    """Result names whose mumps/direct run is the reference, in order of preference."""
    key = r["param_set"]
    keys = [key]
    tag = (r.get("pcb") or {}).get("tag")
    if tag and key.endswith(f"@{tag}"):
        keys.append(key[: -len(tag) - 1])
    # multiple right-hand sides (@mrhs-...): the full S matrix of MUMPS with
    # --mrhs shared if there is one, else the single-port MUMPS run of the set
    # (its S column of port 1 is compared)
    parts = [p for p in key.split("@") if p != tag]
    if any(p.startswith("mrhs-") for p in parts):
        keys.append("@".join("mrhs-shared" if p.startswith("mrhs-") else p for p in parts))
    base = "@".join(p for p in parts if not p.startswith("mrhs-"))
    if base not in keys:
        keys.append(base)
    # a set whose only MUMPS run is --mrhs shared (P03 of task L): its full S
    # matrix also serves the single-port runs (not other variants, e.g. @f<GHz>)
    rest = base.split("@")[1:]
    if all(p.startswith("Port") for p in rest):
        full = base.split("@")[0] + "@mrhs-shared"
        if full not in keys:
            keys.append(full)
    return keys


def row_of(r: dict, refs: dict, suites: dict | None = None) -> dict:
    """One summary row. suites: {(problem, set): suite tier}. Sets of the existing
    benchmark (pcb.benchmark "existing") are named <case>:<set>."""
    pcb = r.get("pcb") or {}
    existing = pcb.get("benchmark") == "existing"
    hist = r.get("history") or []
    setup = r.get("setup_time")
    solve = round(hist[-1][2] - setup, 2) if hist and setup is not None else None
    tr = pcb.get("true_residual")
    ds = None
    combo = f"{r['preset']}/{r['krylov']}"
    s = s_params(r)
    if s and combo != DIRECT_COMBO:
        for k in reference_key(r):
            ref = refs.get((r["case"], k))
            if ref:
                common = [n for n in s if n in ref]
                if common:
                    ds = max(abs(s[n] - ref[n]) for n in common)
                break
    key = r["param_set"]
    tr_ind = ct.supplement(r) if r.get("status") in TREND_STATUS else None
    tr_ind = tr_ind or {}
    chk = r.get("solution_check") or {}
    total = r.get("wall")
    if total is not None and chk.get("time") is not None:
        total = round(total - chk["time"], 2)   # without the solution save / error check
    pset = key.split("@")[0]
    return dict(
        problem=r["case"], caseId=f"{r['case']}:{key}" if existing else key,
        paramSet=f"{r['case']}:{pset}" if existing else pset,
        variant=key[len(pset):].lstrip("@"), suite=(suites or {}).get((r["case"], pset)),
        krylov=r["krylov"], preset=r["preset"], status=r.get("status"), reason=r.get("reason"),
        dof=r.get("ndof"), iterations=r.get("iterations"),
        finalRelativeResidual=r.get("final_relres"), minRelativeResidual=r.get("min_relres"),
        trueRelativeResidual=tr[-1][2] if tr else None,
        setupTime=setup, solveTime=solve, totalTime=total, peakRssGb=r.get("peak_rss_gb"),
        sMaxAbsDiffMumps=ds, solErrL2=chk.get("rel_l2"), solErrCurl=chk.get("rel_curl"),
        solErrHcurl=chk.get("rel_hcurl"), frequencyGHz=pcb.get("freq_GHz"),
        lengthUnit=pcb.get("length_unit") or ("lambda0" if existing else "mm"), excitation=pcb.get("excitation"),
        excitedPort=pcb.get("excited_port"), conductorModel=pcb.get("conductor_model") or "pec",
        restart=pcb.get("gmres_restart"),
        accelIcAlpha=pcb.get("accel_ic_alpha"),
        # HX / CSLP+HX: PEC-row mask of the gradient correction (1 = PCB standard since
        # handoff task I-9; 0 = unmasked, also for results written before the field existed)
        hxMask=(int(bool(pcb.get("hx_dirichlet_mask"))) if combo in HX_COMBOS else None),
        tag=pcb.get("tag"), petscExtra=pcb.get("petsc_extra"),
        budgetSecond=r.get("budget"), kMax=(r.get("stop_rule") or {}).get("k_max"),
        historyFull=int(bool(r.get("history_full"))),
        trendWindow=tr_ind.get("window"), trendSlope=tr_ind.get("s"), trendRho=tr_ind.get("rho"),
        trendNest=tr_ind.get("n_est"), trendRhoCyc=tr_ind.get("rho_cyc"),
        trendLastUpdate=tr_ind.get("last_update"), trendDropWindow=tr_ind.get("drop_window"),
        timePerIteration=tr_ind.get("time_per_it"), trendTimeToConverge=tr_ind.get("t_est"),
        solverVersion=pcb.get("solver_version"), file=r["_file"],
    )


def sort_key(row: dict, set_order: dict) -> tuple:
    combo = f"{row['preset']}/{row['krylov']}"
    return (row["problem"], set_order.get((row["problem"], row["paramSet"]), 10 ** 6), row["paramSet"],
            row["variant"], COMBO_ORDER.index(combo) if combo in COMBO_ORDER else len(COMBO_ORDER), combo)


def fmt(v, kind: str = "") -> str:
    if v is None or v == "":
        return "-"
    if kind == "e":
        return f"{v:.1e}"
    if kind == "t":
        return f"{v:.0f}" if v >= 10 else f"{v:.1f}"
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def md_table(header: list, rows: list) -> list:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def md_detail(rows: list, with_variant: bool) -> list:
    header = ["case", "combination"] + (["variant"] if with_variant else []) + [
        "status", "it", "final rel.res", "true rel.res", "setup [s]", "solve [s]", "total [s]",
        "RSS [GB]", "\\|dS\\| vs MUMPS"]
    if with_variant:
        header += ["f [GHz]", "m", "alpha", "HX mask"]
    body = []
    for r in rows:
        line = [r["paramSet"], f"{r['preset']}/{r['krylov']}"] + ([r["variant"]] if with_variant else []) + [
            fmt(r["status"]), fmt(r["iterations"]), fmt(r["finalRelativeResidual"], "e"),
            fmt(r["trueRelativeResidual"], "e"), fmt(r["setupTime"], "t"), fmt(r["solveTime"], "t"),
            fmt(r["totalTime"], "t"), fmt(r["peakRssGb"]), fmt(r["sMaxAbsDiffMumps"], "e")]
        if with_variant:
            line += [fmt(r["frequencyGHz"]), fmt(r["restart"]), fmt(r["accelIcAlpha"]), fmt(r["hxMask"])]
        body.append(line)
    return md_table(header, body)


def stagnant(r: dict) -> bool:
    """Stagnation (paper_plan 4.2): the envelope did not halve over the window,
    or GMRES(m) reduces the residual by less than 10 % per restart cycle."""
    return (r["trendDropWindow"] is not None and r["trendDropWindow"] > 0.5) or \
        (r["trendRhoCyc"] is not None and r["trendRhoCyc"] > 0.9)


def md_trend(rows: list) -> list:
    """Supplementary information of the results stopped at K_max (or the time
    budget): slope of the envelope, extrapolated iteration count and time."""
    out = ["`convergence_trend.py` の指標（docs/paper_plan.md 4.2節）。窓 \\(W\\) は GMRES 系で反復数の20%（リスタート長の整数倍）、"
           "COCG 系で50%。\\(s\\): 窓での \\(\\log_{10}\\hat r\\) の傾き（1反復あたりの桁数）、"
           "\\(N_{\\mathrm{est}}\\): その速さが続いたときの推定収束反復数、\\(\\rho^{\\mathrm{cyc}}\\): GMRES(m) の1周期あたりの縮小率、"
           "最終更新: 包絡線 \\(\\hat r\\) が最後に下がった反復、窓での減少: 窓の終わり／始めの \\(\\hat r\\)。"
           "「停滞」は窓での減少が1/2未満か \\(\\rho^{\\mathrm{cyc}}>0.9\\)。"
           "**cslp_hx/gmres の \\(N_{\\mathrm{est}}\\) は悲観側**（超線形収束。過去の記録の検証で実際の2.7〜4倍、4.3〜4.4節）。"
           "\\(N_{\\mathrm{est}}\\) は推定値で、収束した反復数とは区別する。", ""]
    if any(not r["historyFull"] for r in rows):
        out += ["- 注意: 履歴が間引かれた結果（v1.0 より前、約1,500点）を含む。指標は間引いた履歴から求めた。", ""]
    header = ["case", "combination", "status", "it", "K_max", "r_hat", "s", "N_est", "N_est/K", "rho_cyc",
              "最終更新", "窓での減少", "判定", "total [s]", "s/it", "推定時間 [s]"]
    body = []
    for r in rows:
        k = r["kMax"] or r["iterations"]
        ne = r["trendNest"]
        fin = ne is not None and math.isfinite(ne)
        pess = f"{r['preset']}/{r['krylov']}" in ct.PESSIMISTIC_N_EST
        body.append([
            r["paramSet"], f"{r['preset']}/{r['krylov']}", fmt(r["status"]), fmt(r["iterations"]), fmt(r["kMax"]),
            fmt(r["minRelativeResidual"], "e"), f"{r['trendSlope']:.2e}",
            (f"{ne:.3g}" if fin else "∞") + ("（悲観側）" if pess and fin else ""),
            f"{ne / k:.2g}" if fin and k else "∞", fmt(r["trendRhoCyc"] and round(r["trendRhoCyc"], 4)),
            fmt(r["trendLastUpdate"]), fmt(r["trendDropWindow"] and round(r["trendDropWindow"], 3)),
            "停滞" if stagnant(r) else "遅い収束", fmt(r["totalTime"], "t"),
            fmt(r["timePerIteration"] and round(r["timePerIteration"], 4)),
            fmt(r["trendTimeToConverge"], "t") if fin else "∞"])
    return md_table(header, body)


def md_matrix(rows: list, set_order: dict) -> list:
    """Cases x combinations; a cell is 'total time s (iterations)' when
    converged, else the status and the final relative residual."""
    combos = sorted({f"{r['preset']}/{r['krylov']}" for r in rows},
                    key=lambda c: (COMBO_ORDER.index(c) if c in COMBO_ORDER else len(COMBO_ORDER), c))
    cases = sorted({(r["problem"], r["paramSet"]) for r in rows},
                   key=lambda k: (k[0], set_order.get(k, 10 ** 6), k[1]))
    cell = {(r["problem"], r["paramSet"], f"{r['preset']}/{r['krylov']}"): r for r in rows}
    body = []
    for prob, pset in cases:
        line = [pset]
        for c in combos:
            r = cell.get((prob, pset, c))
            if r is None:
                line.append("")
            elif r["status"] == "converged":
                line.append(f"{fmt(r['totalTime'], 't')} s ({r['iterations']})")
            else:
                line.append(f"{STATUS_SHORT.get(r['status'], r['status'])} "
                            f"{fmt(r['finalRelativeResidual'], 'e')}".rstrip(" -"))
        body.append(line)
    return md_table(["case"] + combos, body)


def write_csv(path: Path, rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: "" if r[k] is None else f"{r[k]:.6g}" if isinstance(r[k], float) else r[k]
                        for k in COLUMNS})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "pcb_benchmark",
                    help="result directory of run_pcb_benchmark.py run (reads <out>/runs)")
    ap.add_argument("--dest", type=Path, default=None, help="output directory (default <out>/summary)")
    ap.add_argument("--refs", type=Path, nargs="*", default=[ROOT / "results" / "pcb_ports"],
                    help="further result directories (reads <dir>/runs) for MUMPS references")
    args = ap.parse_args()
    dest = args.dest or args.out / "summary"

    runs = load_runs(args.out / "runs")
    if not runs:
        print(f"no results in {args.out / 'runs'}")
        return 1
    # Keep the WSL records clean: only the reference machine's results go to docs/pcb_results/.
    host = pcb_host.detect()
    run_hosts = sorted({r.get("host") or "wsl" for r in runs})
    if dest.resolve() == pcb_host.WSL_RESULTS.resolve() and (not host.reference or run_hosts != ["wsl"]):
        print(f"ERROR: {dest} holds the WSL records; this is {host.name} with results of "
              f"{', '.join(run_hosts)}. Use --dest {pcb_host.WSL_RESULTS.relative_to(ROOT).as_posix()}/"
              f"{run_hosts[0] if len(run_hosts) == 1 and run_hosts[0] != 'wsl' else '<host>'}")
        return 2
    if len(run_hosts) > 1:
        print(f"ERROR: results of several machines in {args.out / 'runs'}: {', '.join(run_hosts)}")
        return 2
    # v1.0 records (task A4): only the M3 Pro's results of the frozen solver go to docs/results_v1/mac_m3pro/.
    if dest.resolve().is_relative_to(pcb_host.V1_RESULTS.resolve()):
        v1_dest = pcb_host.V1_RESULTS / pcb_host.V1_RECORD_HOST
        bad_versions = sorted({str((r.get("pcb") or {}).get("solver_version")) for r in runs}
                              - {pcb_host.V1_SOLVER_VERSION})
        if (dest.resolve() != v1_dest.resolve() or host.name != pcb_host.V1_RECORD_HOST
                or run_hosts != [pcb_host.V1_RECORD_HOST] or bad_versions):
            print(f"ERROR: {pcb_host.V1_RESULTS.relative_to(ROOT).as_posix()}/ holds the v1.0 records: only "
                  f"--dest {v1_dest.relative_to(ROOT).as_posix()} on {pcb_host.V1_RECORD_HOST} with results of "
                  f"{pcb_host.V1_RECORD_HOST} and PCB_SOLVER_VERSION {pcb_host.V1_SOLVER_VERSION}. This is "
                  f"{host.name} with results of {', '.join(run_hosts)}"
                  + (f", solver versions {', '.join(bad_versions)}" if bad_versions else ""))
            return 2
    params = json.loads(PARAMS_JSON.read_text(encoding="utf-8"))
    existing = json.loads(EXISTING_JSON.read_text(encoding="utf-8"))
    set_order = {(prob, s): i for prob, pdef in params.items() for i, s in enumerate(pdef["parameter_sets"])}
    set_order.update({(case, f"{case}:{s}"): i for case, cdef in existing.items()
                      for i, s in enumerate(cdef["parameter_sets"])})
    suites = {(prob, s): d.get("suite") for db in (params, existing) for prob, pdef in db.items()
              for s, d in pdef["parameter_sets"].items()}
    refs = {}
    for src in [runs] + [load_runs(d / "runs") for d in args.refs if (d / "runs").is_dir()]:
        for r in src:
            if f"{r['preset']}/{r['krylov']}" == DIRECT_COMBO and s_params(r):
                refs.setdefault((r["case"], r["param_set"]), s_params(r))
    rows = sorted((row_of(r, refs, suites) for r in runs), key=lambda row: sort_key(row, set_order))
    std = [r for r in rows if not r["variant"]]
    var = [r for r in rows if r["variant"]]

    dest.mkdir(parents=True, exist_ok=True)
    write_csv(dest / "pcb_summary.csv", std)
    write_csv(dest / "pcb_summary_variants.csv", var)

    budgets = sorted({r["budgetSecond"] for r in rows if r["budgetSecond"] is not None})
    kmaxes = sorted({(f"{r['preset']}/{r['krylov']}", r["kMax"]) for r in std if r["kMax"]},
                    key=lambda x: (COMBO_ORDER.index(x[0]) if x[0] in COMBO_ORDER else len(COMBO_ORDER), x))
    versions = sorted({r["solverVersion"] for r in rows if r["solverVersion"]})
    md = ["# PCBベンチマーク 結果サマリー"
          + ("" if run_hosts == ["wsl"] else f"（{run_hosts[0]}、WSLの結果とは比べない）"), "",
          f"- 元データ: `{args.out.resolve().relative_to(ROOT).as_posix() if args.out.resolve().is_relative_to(ROOT) else args.out}/runs/`"
          f"（{len(rows)}件。標準 {len(std)}件、変種 {len(var)}件）",
          f"- 予算: {', '.join(f'{b:g}' for b in budgets) or '-'} 秒（setupを含む）。"
          f"PCB_SOLVER_VERSION: {', '.join(versions) or '-'}",
          f"- 反復回数の上限 K_max: {', '.join(f'{c} {k:g}' for c, k in kmaxes) or 'なし（時間の予算で打切り、v1.0 より前の規則）'}",
          "- 生成: `python3 freefem/pcb/summarize_pcb_benchmark.py`。時間の定義・\\|dS\\| はスクリプト冒頭の説明を参照",
          ""]
    # diagnostic parameter sets are not in the evaluation tables (settings 15.4) and are not re-run
    role = {(prob, s): d.get("role") for prob, pdef in params.items() for s, d in pdef["parameter_sets"].items()}
    old_hx = [r for r in std if r["hxMask"] == 0 and role.get((r["problem"], r["paramSet"])) != "diagnostic"]
    if old_hx:
        md += [f"- **注意**: 標準のhx・cslp_hxのうち{len(old_hx)}件はPECの行のマスクなし（作業I-9より前の標準）: "
               + ", ".join(f"{r['paramSet']} {r['preset']}/{r['krylov']}" for r in old_hx), ""]
    if std:
        md += ["## 標準の結果（ケース×組合せ）", "",
               "収束は「総時間 s（反復数）」、それ以外は状態と最終相対残差。", ""]
        md += md_matrix(std, set_order) + [""]
        md += ["## 標準の結果（詳細）", ""] + md_detail(std, False) + [""]
    capped = [r for r in std if r["status"] in TREND_STATUS and r["trendSlope"] is not None]
    if capped:
        md += ["## 上限に達した結果の補足情報", ""] + md_trend(capped) + [""]
    if var:
        md += ["## 変種（名前に `@` を含む結果: 別ポート、E1、`--freq`、`--tag`）", ""]
        md += md_detail(var, True) + [""]
    (dest / "pcb_summary.md").write_text("\n".join(md), encoding="utf-8")
    n_conv = sum(r["status"] == "converged" for r in std)
    print(f"{len(std)} standard ({n_conv} converged), {len(var)} variant results -> {dest}")
    if old_hx:
        print(f"note: {len(old_hx)} standard hx/cslp_hx results without the PEC-row mask (before task I-9)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
