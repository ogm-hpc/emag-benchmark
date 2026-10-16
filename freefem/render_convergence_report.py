#!/usr/bin/env python3
"""Render report_data.json (produced by generate_convergence_report.py) into a
self-contained HTML report: one comparison table (iterations/time/converged)
and one convergence-history plot (relative residual norm, log scale, vs
iteration) per case, covering every GMRES/COCG x preconditioner-preset
combination that was run.

Usage:
  python3 freefem/render_convergence_report.py \
      --data results/convergence_report/report_data.json \
      --out results/convergence_report/report.html
"""

from __future__ import annotations

import argparse
import base64
import io
import json
from collections import OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE_DESCRIPTIONS = {
    "case2A": "Empty PEC cavity",
    "case2B": "Two-chamber cavity with iris",
    "case2C": "Ultra-narrow slit benchmark",
    "case2D": "Maze-like cavity",
    "case2E": "Iris-loaded rectangular waveguide",
}

# Paul Tol "bright" qualitative palette: colorblind-safe, reads well against
# the report's paper background. Line style distinguishes the Krylov method.
PRESET_COLORS = {
    "jacobi": "#4477AA",
    "gs": "#AA3377",
    "ssor": "#CCBB44",
    "ic0": "#BBBBBB",
    "ic0_shift": "#66CCEE",
    "ilu": "#EE6677",
    "amg_gamg": "#228833",
    "amg_boomer": "#999999",
    "ams": "#999999",
    "ads": "#999999",
    "bddc": "#999999",
    "cslp": "#CC3311",
}
KRYLOV_STYLE = {"gmres": "-", "cocg": "--", "cslp": "-"}

# Plot chrome tuned to the report's paper/ink tokens so embedded PNGs read as
# part of the page rather than bare matplotlib defaults.
INK = "#1a2230"
PAPER = "#f7f8fa"
GRID = "#c7cdd6"


def fmt_num(x, digits=4):
    if x is None:
        return "-"
    return f"{x:.{digits}g}"


def make_plot(case_key: str, runs: list) -> str:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "text.color": INK,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    })
    fig, ax = plt.subplots(figsize=(7.6, 4.8), dpi=140)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    any_line = False
    for r in runs:
        residuals = r.get("residuals") or []
        if len(residuals) < 2:
            continue
        r0 = residuals[0][1]
        if not r0:
            continue
        xs = [it for it, _ in residuals]
        ys = [val / r0 for _, val in residuals]
        color = PRESET_COLORS.get(r["preset"], INK)
        style = KRYLOV_STYLE.get(r["krylov"], "-")
        label = "CSLP (GMRES, hand-rolled)" if r["preset"] == "cslp" else f"{r['krylov'].upper()} + {r['preset']}"
        lw = 2.6 if r["preset"] == "cslp" else 1.7
        zorder = 5 if r["preset"] == "cslp" else 2
        ax.plot(xs, ys, style, color=color, linewidth=lw, label=label, solid_capstyle="round", zorder=zorder)
        any_line = True
    ax.set_yscale("log")
    ax.set_xlabel("Iteration", fontsize=10)
    ax.set_ylabel("Relative residual  ||rₖ|| / ||r₀||", fontsize=10)
    ax.set_title(f"{case_key}", fontsize=12, color=INK, loc="left", fontweight="bold")
    ax.grid(True, which="major", linestyle="-", linewidth=0.6, color=GRID, alpha=0.9)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.4, color=GRID, alpha=0.5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID)
    ax.tick_params(labelsize=8.5)
    if any_line:
        leg = ax.legend(fontsize=7.8, loc="upper right", ncol=1, frameon=False)
        for text in leg.get_texts():
            text.set_color(INK)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=PAPER)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    return b64


def make_table(runs: list) -> str:
    rows = []
    # GMRES first, then CSLP, then COCG; within each, preset insertion order.
    krylov_rank = {"gmres": 0, "cslp": 1, "cocg": 2}
    ordered = sorted(runs, key=lambda r: (krylov_rank.get(r["krylov"], 3), r["_preset_order"]))
    for r in ordered:
        if r.get("error") and not r.get("residuals"):
            status = f'<span class="badge fail">timeout / fail</span><span class="reason">{r["error"]}</span>'
            it_s = "–"
            time_s = "–"
            final_res = "–"
        else:
            converged = r.get("converged")
            reason = r.get("reason") or "?"
            if converged is True:
                status = f'<span class="badge ok">converged</span><span class="reason">{reason}</span>'
            elif converged is False:
                cls = "warn" if reason == "DIVERGED_ITS" else "fail"
                word = "cap reached" if cls == "warn" else "diverged"
                status = f'<span class="badge {cls}">{word}</span><span class="reason">{reason}</span>'
            elif reason == "TIMEOUT":
                status = '<span class="badge warn">still converging</span><span class="reason">900s wall-clock cutoff, not a stall</span>'
            else:
                status = '<span class="badge fail">unknown</span>'
            it_s = str(r.get("iterations")) if r.get("iterations") is not None else "–"
            time_s = fmt_num(r.get("solve_time"))
            residuals = r.get("residuals") or []
            if residuals and residuals[0][1]:
                final_res = fmt_num(residuals[-1][1] / residuals[0][1], 3)
            else:
                final_res = "–"
        preset_color = PRESET_COLORS.get(r["preset"], INK)
        rows.append(
            "<tr>"
            f"<td><span class='swatch' style='background:{preset_color}'></span>{r['krylov'].upper()}</td>"
            f"<td>{r['preset']}</td>"
            f"<td>{status}</td>"
            f"<td class='num'>{it_s}</td>"
            f"<td class='num'>{time_s}</td>"
            f"<td class='num'>{final_res}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def build_report(data_path: Path, out_path: Path) -> None:
    with data_path.open("r", encoding="utf-8") as f:
        results = json.load(f)

    # Preserve preset first-seen order (for stable table/legend ordering).
    preset_order: "OrderedDict[str, int]" = OrderedDict()
    for r in results:
        preset_order.setdefault(r["preset"], len(preset_order))
    for r in results:
        r["_preset_order"] = preset_order[r["preset"]]

    by_case: "OrderedDict[str, list]" = OrderedDict()
    for r in results:
        key = f"{r['case_name']}_{r['param_set']}"
        by_case.setdefault(key, []).append(r)

    sections = []
    for case_key, runs in by_case.items():
        case_name = runs[0]["case_name"]
        param_set = runs[0]["param_set"]
        desc = CASE_DESCRIPTIONS.get(case_name, "")
        table_html = make_table(runs)
        plot_b64 = make_plot(case_key, runs)
        n_ok = sum(1 for r in runs if r.get("converged"))
        n_total = len(runs)
        sections.append(f"""
<section class="case-section" id="{case_key}">
  <div class="case-head">
    <div class="case-id">{case_name}<span class="param-set">/{param_set}</span></div>
    <div class="case-desc">{desc}</div>
    <div class="case-stat">{n_ok} / {n_total} converged<br><span class="case-stat-sub">rtol 1e-8</span></div>
  </div>
  <div class="grid">
    <div class="table-card">
      <table>
        <thead>
          <tr><th>Krylov</th><th>Preconditioner</th><th>Outcome</th><th class="num">Iter.</th><th class="num">Time (s)</th><th class="num">Final ‖rₖ‖/‖r₀‖</th></tr>
        </thead>
        <tbody>
          {table_html}
        </tbody>
      </table>
    </div>
    <div class="plot-card">
      <img src="data:image/png;base64,{plot_b64}" alt="convergence history for {case_key}"/>
    </div>
  </div>
</section>
""")

    toc = "".join(
        f'<a href="#{key}">{r0["case_name"]}<span>/{r0["param_set"]}</span></a>'
        for key, runs in by_case.items() for r0 in [runs[0]]
    )

    html = f"""<title>GMRES / COCG × Preconditioner — Convergence Report</title>
<style>
  :root {{
    --ink: #1a2230;
    --ink-soft: #4b5768;
    --paper: #eef1f4;
    --paper-raised: #ffffff;
    --line: #d7dde3;
    --accent: #2f7a6f;
    --good: #1f9d55;
    --warn: #b8720f;
    --bad: #b91c1c;
    color-scheme: light dark;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --ink: #e8ecf1;
      --ink-soft: #a9b4c2;
      --paper: #12161c;
      --paper-raised: #1b2129;
      --line: #2a323d;
      --accent: #6fc2b5;
      --good: #3fbd74;
      --warn: #d9922f;
      --bad: #e0554f;
    }}
  }}
  :root[data-theme="dark"] {{
    --ink: #e8ecf1; --ink-soft: #a9b4c2; --paper: #12161c; --paper-raised: #1b2129;
    --line: #2a323d; --accent: #6fc2b5; --good: #3fbd74; --warn: #d9922f; --bad: #e0554f;
  }}
  :root[data-theme="light"] {{
    --ink: #1a2230; --ink-soft: #4b5768; --paper: #eef1f4; --paper-raised: #ffffff;
    --line: #d7dde3; --accent: #2f7a6f; --good: #1f9d55; --warn: #b8720f; --bad: #b91c1c;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    background: var(--paper);
    color: var(--ink);
    max-width: 1180px;
    margin: 0 auto;
    padding: 40px 20px 80px;
    line-height: 1.55;
  }}
  header.report-head {{
    border-bottom: 2px solid var(--ink);
    padding-bottom: 18px;
    margin-bottom: 8px;
  }}
  .eyebrow {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 600;
  }}
  h1 {{
    font-family: Georgia, Cambria, "Times New Roman", serif;
    font-size: 2rem;
    font-weight: 600;
    margin: 6px 0 10px;
    text-wrap: balance;
  }}
  .lead {{
    color: var(--ink-soft);
    max-width: 68ch;
    font-size: 0.96rem;
    margin: 0 0 18px;
  }}
  .legend-strip {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px 18px;
    font-size: 0.82rem;
    color: var(--ink-soft);
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }}
  nav.toc {{
    margin: 22px 0 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }}
  nav.toc a {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.82rem;
    color: var(--ink);
    text-decoration: none;
    border: 1px solid var(--line);
    border-radius: 3px;
    padding: 4px 10px;
    background: var(--paper-raised);
  }}
  nav.toc a span {{ color: var(--ink-soft); }}
  nav.toc a:hover {{ border-color: var(--accent); color: var(--accent); }}
  nav.toc a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}

  .case-section {{
    margin-top: 48px;
    padding-top: 22px;
    border-top: 1px solid var(--line);
    scroll-margin-top: 16px;
  }}
  .case-head {{
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: baseline;
    gap: 4px 16px;
    margin-bottom: 16px;
  }}
  .case-id {{
    font-family: Georgia, Cambria, "Times New Roman", serif;
    font-size: 1.5rem;
    font-weight: 600;
  }}
  .case-id .param-set {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 1rem;
    font-weight: 400;
    color: var(--accent);
  }}
  .case-desc {{
    color: var(--ink-soft);
    font-style: italic;
    align-self: baseline;
  }}
  .case-stat {{
    text-align: right;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.95rem;
    font-weight: 600;
    grid-row: 1 / 3;
  }}
  .case-stat-sub {{
    font-weight: 400;
    font-size: 0.75rem;
    color: var(--ink-soft);
  }}

  .grid {{
    display: grid;
    grid-template-columns: minmax(360px, 1fr) minmax(380px, 1.05fr);
    gap: 22px;
    align-items: start;
  }}
  @media (max-width: 860px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .case-head {{ grid-template-columns: 1fr; }}
    .case-stat {{ text-align: left; grid-row: auto; }}
  }}

  .table-card {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
  th, td {{ padding: 7px 9px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: middle; }}
  th {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--ink-soft);
    font-weight: 600;
  }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .swatch {{
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 2px;
    margin-right: 6px;
  }}
  .badge {{
    display: inline-block;
    padding: 1px 8px;
    border-radius: 3px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: #fff;
  }}
  .badge.ok {{ background: var(--good); }}
  .badge.warn {{ background: var(--warn); }}
  .badge.fail {{ background: var(--bad); }}
  .reason {{
    display: block;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.7rem;
    color: var(--ink-soft);
    margin-top: 2px;
  }}

  .plot-card {{
    background: var(--paper-raised);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 10px;
  }}
  .plot-card img {{ max-width: 100%; height: auto; display: block; border-radius: 2px; }}

  footer.notes {{
    margin-top: 56px;
    padding-top: 16px;
    border-top: 1px solid var(--line);
    font-size: 0.82rem;
    color: var(--ink-soft);
    max-width: 72ch;
  }}
</style>
<header class="report-head">
  <div class="eyebrow">Edge03d Maxwell Solver — Benchmark Series 2</div>
  <h1>GMRES / COCG × Preconditioner Convergence Report</h1>
  <p class="lead">Every combination of Krylov method (GMRES, COCG) and preconditioner preset run to the same rtol=1e-8 stopping criterion, per case. Iteration count and wall-clock solve time compare cost; the convergence-history plot compares shape — how each combination's relative residual actually falls (or fails to).</p>
  <div class="legend-strip">
    <span>— solid = GMRES</span>
    <span>- - dashed = COCG</span>
    <span>y-axis: ‖rₖ‖ / ‖r₀‖ (log scale)</span>
  </div>
  <nav class="toc">{toc}</nav>
</header>
{''.join(sections)}
<footer class="notes">
  <p>COCG (<code>-ksp_type cg -ksp_cg_type symmetric</code>) is retained across every case regardless of relative performance against GMRES: this benchmark's purpose is determining which method/preconditioner combinations can solve this complex-symmetric indefinite system at all, not finding the fastest one. A COCG breakdown (<code>DIVERGED_INDEFINITE_MAT</code>) is itself a reportable result.</p>
</footer>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    build_report(args.data, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
