#!/usr/bin/env python3
"""Render results/multi_combo/report_data.json into a single self-contained
HTML report: per-case problem metadata, a performance table (iterations/time/
final relative residual per preset x krylov combo), and an inline-SVG
convergence-history chart (log-scale relative residual vs iteration).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = ROOT / "results" / "multi_combo" / "report_data.json"
DEFAULT_OUT_PATH = ROOT / "results" / "multi_combo" / "report.html"

# Validated categorical palette (dataviz skill's reference palette, slots 1-7:
# blue/orange/aqua/yellow/magenta/green/violet), assigned to CSS custom
# properties so light/dark swap via the stylesheet, not inline hex -- the
# validator's contrast numbers only hold against the exact chart surface
# (#fcfcfb light / #1a1a19 dark) declared in .chart-wrap below.
PRESET_CSS_VAR = {
    "gs": "--series-1", "ssor": "--series-2", "amg_gamg": "--series-3",
    "accel_ic": "--series-4", "cslp": "--series-5", "hx": "--series-6", "cslp_hx": "--series-7",
}
KRYLOV_DASH = {"gmres": "0", "cocg": "4,3"}

CHART_W, CHART_H = 720, 320
CHART_PAD_L, CHART_PAD_B, CHART_PAD_T, CHART_PAD_R = 56, 40, 16, 16


def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def fmt_num(x, digits=3):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "—"
    try:
        if abs(x) >= 1000 or (abs(x) < 1e-3 and x != 0):
            return f"{x:.{digits}e}"
        return f"{x:.{digits}f}"
    except Exception:
        return str(x)


def build_chart_svg(combos, case_id):
    # collect all (iter, relres) series with iter>0 (skip the iter=0 seed point
    # for the log axis, but keep track of its value for y-domain min/max calc)
    series = []
    all_y = []
    max_x = 1
    for c in combos:
        hist = c.get("residual_history") or []
        if len(hist) < 2:
            continue
        init = hist[0][1]
        if not init or init <= 0:
            continue
        pts = [(it, val / init) for it, val in hist if val is not None and val > 0]
        pts = [(it, max(v, 1e-16)) for it, v in pts]
        if len(pts) < 2:
            continue
        series.append({
            "preset": c["preset"], "krylov": c["krylov"], "label": f"{c['preset_label']} / {c['krylov'].upper()}",
            "pts": pts,
        })
        all_y.extend(v for _, v in pts)
        max_x = max(max_x, pts[-1][0])

    if not series:
        return "<p class='muted'>収束履歴データなし</p>"

    y_max = 1.0
    y_min = min(all_y)
    y_min_log = math.floor(math.log10(max(y_min, 1e-16)))
    y_max_log = 0  # relative residual starts at 1.0
    if y_min_log >= y_max_log:
        y_min_log = y_max_log - 1

    def px(it):
        return CHART_PAD_L + (it / max_x) * (CHART_W - CHART_PAD_L - CHART_PAD_R)

    def py(v):
        lv = math.log10(max(v, 10 ** y_min_log))
        frac = (lv - y_min_log) / (y_max_log - y_min_log)
        return CHART_PAD_T + (1 - frac) * (CHART_H - CHART_PAD_T - CHART_PAD_B)

    parts = [f"<svg viewBox='0 0 {CHART_W} {CHART_H}' class='chart' role='img' "
             f"aria-label='収束履歴（相対残差 vs 反復回数、対数軸）'>"]

    # gridlines + y labels (decades)
    for dec in range(y_max_log, y_min_log - 1, -1):
        y = py(10 ** dec)
        parts.append(f"<line x1='{CHART_PAD_L}' y1='{y:.1f}' x2='{CHART_W - CHART_PAD_R}' y2='{y:.1f}' class='gridline'/>")
        label = f"1e{dec}" if dec != 0 else "1"
        parts.append(f"<text x='{CHART_PAD_L - 8}' y='{y + 3:.1f}' class='axislabel' text-anchor='end'>{label}</text>")

    # x labels
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        it = frac * max_x
        x = px(it)
        parts.append(f"<line x1='{x:.1f}' y1='{CHART_PAD_T}' x2='{x:.1f}' y2='{CHART_H - CHART_PAD_B}' class='gridline-v'/>")
        parts.append(f"<text x='{x:.1f}' y='{CHART_H - CHART_PAD_B + 16}' class='axislabel' text-anchor='middle'>{int(it)}</text>")
    parts.append(f"<text x='{CHART_W/2:.1f}' y='{CHART_H - 4}' class='axistitle' text-anchor='middle'>反復回数</text>")
    parts.append(f"<text x='14' y='{CHART_H/2:.1f}' class='axistitle' text-anchor='middle' "
                 f"transform='rotate(-90 14 {CHART_H/2:.1f})'>相対残差（対数）</text>")

    for s in series:
        cvar = PRESET_CSS_VAR.get(s["preset"], "--series-1")
        dash = KRYLOV_DASH.get(s["krylov"], "0")
        pts_str = " ".join(f"{px(it):.1f},{py(v):.1f}" for it, v in s["pts"])
        dash_attr = f" stroke-dasharray='{dash}'" if dash != "0" else ""
        parts.append(f"<polyline points='{pts_str}' class='series' style='stroke:var({cvar})'{dash_attr}/>")

    parts.append("</svg>")

    # legend
    legend = ["<div class='legend'>"]
    for s in series:
        cvar = PRESET_CSS_VAR.get(s["preset"], "--series-1")
        dash = "dashed" if s["krylov"] == "cocg" else "solid"
        legend.append(f"<span class='legend-item'><span class='swatch {dash}' style='--c:var({cvar})'></span>{esc(s['label'])}</span>")
    legend.append("</div>")

    return "".join(parts) + "".join(legend)


def build_case_section(case, idx):
    cid = f"case-{idx}"
    title = f"{case['case_name']} : {case['param_set']}"
    combos = sorted(case["combos"], key=lambda c: (c["preset"], c["krylov"]))

    rows = []
    for c in combos:
        conv = c.get("converged")
        conv_badge = "<span class='badge ok'>✓ 収束</span>" if conv else "<span class='badge no'>✕ 未収束</span>"
        rel = c.get("relative_residual")
        rel_str = fmt_num(rel) if rel is not None else "—"
        rel_cls = "danger" if (rel is not None and rel > 1) else ""
        rows.append(
            f"<tr><td>{esc(c['preset_label'])}</td><td class='mono'>{esc(c['krylov'].upper())}</td>"
            f"<td class='num mono'>{c.get('iterations','—')}</td><td>{conv_badge}</td>"
            f"<td class='num mono'>{fmt_num(c.get('solve_time'),2)}</td>"
            f"<td class='num mono'>{fmt_num(c.get('final_residual'))}</td>"
            f"<td class='num mono {rel_cls}'>{rel_str}</td></tr>"
        )

    params_rows = "".join(
        f"<div class='kv'><span class='k'>{esc(k)}</span><span class='v mono'>{esc(v)}</span></div>"
        for k, v in case["params"].items()
    )

    chart_svg = build_chart_svg(combos, cid)

    return f"""
<section class="case-card" id="{cid}">
  <div class="case-head">
    <h2>{esc(title)}</h2>
    <p class="case-desc">{esc(case['description'])}</p>
  </div>
  <div class="meta-grid">
    <div class="meta-block">
      <h3>問題設定</h3>
      <div class="kv"><span class="k">パラメータ説明</span><span class="v">{esc(case['param_description'])}</span></div>
      <div class="kv"><span class="k">波数 k0</span><span class="v mono">{fmt_num(case['k0'])}</span></div>
      <div class="kv"><span class="k">λ0</span><span class="v mono">{fmt_num(case['lambda0'])}</span></div>
      <div class="kv"><span class="k">自由度 (Eh.ndof)</span><span class="v mono">{case['ndof']:,}</span></div>
      {params_rows}
    </div>
    <div class="meta-block">
      <h3>解きづらさにつながる特徴</h3>
      <p>{esc(case['difficulty_note'])}</p>
    </div>
  </div>
  <h3>性能比較（反復法 × 前処理）</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>前処理</th><th>反復法</th><th class="num">反復回数</th><th>収束</th>
      <th class="num">求解時間[s]</th><th class="num">最終残差</th><th class="num">相対残差</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <h3>収束履歴</h3>
  <div class="chart-wrap">{chart_svg}</div>
</section>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="report_data.json from generate_report_data.py")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT_PATH, help="Output HTML path")
    p.add_argument("--title", type=str, default="反復法×前処理 性能評価レポート", help="Report <title>")
    args = p.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    cases = data["cases"]
    # "case1A" < "case1B" < ... < "case2A" < ... < "case3F" sorts correctly as
    # plain strings for this project's naming scheme -- no manual order table needed.
    cases.sort(key=lambda c: (c["case_name"], c["param_set"]))

    ndofs = [c.get("ndof") for c in cases if c.get("ndof")]
    dof_range = f"DOF {min(ndofs):,}〜{max(ndofs):,}" if ndofs else ""

    nav_items = "".join(
        f"<a href='#case-{i}'>{esc(c['case_name'])}:{esc(c['param_set'])}</a>"
        for i, c in enumerate(cases)
    )
    sections = "".join(build_case_section(c, i) for i, c in enumerate(cases))

    html = f"""<title>{esc(args.title)}</title>
<style>
:root {{
  --bg: #f6f5f2; --surface: #ffffff; --text: #1c1f24; --muted: #6b7280;
  --border: #e2e0da; --accent: #0e7c86; --accent-soft: #e4f3f2;
  --chart-surface: #fcfcfb;
  /* status palette (fixed, never themed -- dataviz skill reference) */
  --good: #0ca30c; --good-bg: #e5f4ea; --critical: #d03b3b; --critical-bg: #fdecec;
  /* categorical series palette (dataviz skill reference, slots 1-7, light step) */
  --series-1: #2a78d6; --series-2: #eb6834; --series-3: #1baf7a; --series-4: #eda100;
  --series-5: #e87ba4; --series-6: #008300; --series-7: #4a3aa7;
  --font-sans: -apple-system, "Segoe UI", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#14171c; --surface:#1b1f26; --text:#e6e8eb; --muted:#9aa1ac; --border:#2b3038;
    --accent:#4fd1c5; --accent-soft:#1c2e2c; --chart-surface:#1a1a19;
    --good:#0ca30c; --good-bg:#123222; --critical:#e66767; --critical-bg:#3a1a1a;
    --series-1:#3987e5; --series-2:#d95926; --series-3:#199e70; --series-4:#c98500;
    --series-5:#d55181; --series-6:#008300; --series-7:#9085e9; }}
}}
:root[data-theme="dark"] {{ --bg:#14171c; --surface:#1b1f26; --text:#e6e8eb; --muted:#9aa1ac; --border:#2b3038;
  --accent:#4fd1c5; --accent-soft:#1c2e2c; --chart-surface:#1a1a19;
  --good:#0ca30c; --good-bg:#123222; --critical:#e66767; --critical-bg:#3a1a1a;
  --series-1:#3987e5; --series-2:#d95926; --series-3:#199e70; --series-4:#c98500;
  --series-5:#d55181; --series-6:#008300; --series-7:#9085e9; }}
:root[data-theme="light"] {{ --bg:#f6f5f2; --surface:#ffffff; --text:#1c1f24; --muted:#6b7280; --border:#e2e0da;
  --accent:#0e7c86; --accent-soft:#e4f3f2; --chart-surface:#fcfcfb;
  --good:#0ca30c; --good-bg:#e5f4ea; --critical:#d03b3b; --critical-bg:#fdecec;
  --series-1:#2a78d6; --series-2:#eb6834; --series-3:#1baf7a; --series-4:#eda100;
  --series-5:#e87ba4; --series-6:#008300; --series-7:#4a3aa7; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font-family:var(--font-sans);
  line-height:1.6; }}
.mono {{ font-family:var(--font-mono); font-variant-numeric: tabular-nums; }}
header.page {{ padding:2.5rem 2rem 1.5rem; max-width:960px; margin:0 auto; }}
header.page h1 {{ font-size:1.6rem; margin:0 0 .5rem; text-wrap:balance; }}
header.page p {{ color:var(--muted); max-width:70ch; }}
.methodology {{ background:var(--surface); border:1px solid var(--border); border-radius:10px;
  padding:1rem 1.25rem; margin-top:1rem; font-size:.92rem; }}
.methodology h2 {{ font-size:1rem; margin:0 0 .5rem; }}
.methodology ul {{ margin:.3rem 0; padding-left:1.2rem; }}
.methodology-note {{ font-size:.85rem; border-left:3px solid var(--accent); padding:.5rem .8rem;
  background:var(--accent-soft); border-radius:0 8px 8px 0; margin-top:.75rem; }}
nav.toc {{ max-width:960px; margin:0 auto 1rem; padding:0 2rem; display:flex; flex-wrap:wrap; gap:.4rem .6rem; }}
nav.toc a {{ font-size:.82rem; color:var(--accent); text-decoration:none; border:1px solid var(--border);
  padding:.2rem .55rem; border-radius:999px; background:var(--surface); }}
nav.toc a:hover {{ background:var(--accent-soft); }}
main {{ max-width:960px; margin:0 auto; padding:0 2rem 4rem; display:flex; flex-direction:column; gap:2rem; }}
.case-card {{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:1.5rem 1.75rem; }}
.case-head h2 {{ margin:0 0 .2rem; font-size:1.25rem; font-family:var(--font-mono); }}
.case-desc {{ color:var(--muted); margin:0 0 1rem; font-size:.9rem; }}
.meta-grid {{ display:grid; grid-template-columns: 1.1fr 1fr; gap:1.25rem; margin-bottom:1.25rem; }}
@media (max-width:760px) {{ .meta-grid {{ grid-template-columns:1fr; }} }}
.meta-block h3 {{ font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted);
  margin:0 0 .5rem; }}
.meta-block p {{ font-size:.88rem; margin:0; }}
.kv {{ display:flex; gap:.6rem; font-size:.85rem; padding:.25rem 0; border-bottom:1px dashed var(--border); }}
.kv .k {{ color:var(--muted); flex:0 0 40%; }}
.kv .v {{ flex:1; word-break:break-word; }}
h3 {{ font-size:.95rem; margin:1.25rem 0 .6rem; }}
.table-wrap {{ overflow-x:auto; border:1px solid var(--border); border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; font-size:.85rem; }}
th, td {{ padding:.5rem .7rem; text-align:left; border-bottom:1px solid var(--border); white-space:nowrap; }}
th {{ background:var(--accent-soft); color:var(--text); font-weight:600; font-size:.78rem;
  text-transform:uppercase; letter-spacing:.03em; }}
td.num, th.num {{ text-align:right; }}
tr:last-child td {{ border-bottom:none; }}
.badge {{ display:inline-flex; align-items:center; gap:.3rem; padding:.1rem .55rem; border-radius:999px;
  font-size:.76rem; font-weight:600; }}
.badge.ok {{ background:var(--good-bg); color:var(--good); }}
.badge.no {{ background:var(--critical-bg); color:var(--critical); }}
td.danger {{ color:var(--critical); font-weight:600; }}
.chart-wrap {{ border:1px solid var(--border); border-radius:10px; padding:1rem; background:var(--chart-surface); }}
svg.chart {{ width:100%; height:auto; display:block; }}
.gridline {{ stroke:var(--border); stroke-width:1; }}
.gridline-v {{ stroke:var(--border); stroke-width:1; stroke-dasharray:2,3; }}
.axislabel {{ font-size:9px; fill:var(--muted); font-family:var(--font-mono); }}
.axistitle {{ font-size:10px; fill:var(--muted); }}
.series {{ fill:none; stroke-width:2; opacity:.95; }}
.legend {{ display:flex; flex-wrap:wrap; gap:.5rem 1rem; margin-top:.6rem; font-size:.78rem; color:var(--muted); }}
.legend-item {{ display:flex; align-items:center; gap:.35rem; }}
.swatch {{ display:inline-block; width:16px; height:0; border-top:3px solid var(--c); }}
.swatch.dashed {{ border-top-style:dashed; }}
.muted {{ color:var(--muted); }}
footer {{ max-width:960px; margin:0 auto; padding:0 2rem 3rem; color:var(--muted); font-size:.8rem; }}
</style>
<header class="page">
  <h1>反復法 × 前処理 性能評価レポート</h1>
  <p>Nédélec辺要素FEM Maxwell方程式ベンチマークにおける、GMRES/COCG × 7前処理（GS, SSOR, AMG(GAMG), 加速係数付きIC(0), CSLP, HX(2項), CSLP+HX(2項)）の性能比較。{esc(dof_range)}、{len(cases)}パラメータセット。</p>
  <p class="methodology-note">2026-07-29〜30の修正を反映：GMRESリスタート既定値を30→300に変更（旧データは実質restart=30相当のため停滞していた可能性）。HX/CSLP+HXは理論的忠実性の修正で発覚したGMRES停滞バグのため、3項版（Π/M_vec補正）を無効化し2項版（スムーザ+勾配補正のみ）を標準実装とした。詳細はproblem_settings.md参照。</p>
  <div class="methodology">
    <h2>手法</h2>
    <ul>
      <li><strong>実行方式</strong>: メッシュ読込・行列アセンブリを1プロセス内で1回だけ行い、11通りの前処理×反復法の組み合わせを連続実行する統合方式（<code>maxwell_edge03d_multi_solve.edp</code>）。個別プロセス方式に比べ約9.6倍高速化（case2Aで実測検証済み）。</li>
      <li><strong>最大反復回数</strong>: 全前処理・反復法共通でmax_it=2000（有効な前処理であれば数百反復で収束するという実測知見に基づく）。</li>
      <li><strong>反復法スコープ</strong>: GMRESとCOCGの2種のみ（本プロジェクトの標準方針）。COCGが不定値行列で破綻・停滞する挙動も除外せず記録している。</li>
    </ul>
  </div>
</header>
<nav class="toc">{nav_items}</nav>
<main>{sections}</main>
<footer>Edge03d Maxwell solver benchmark — generated by build_html_report.py.</footer>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
