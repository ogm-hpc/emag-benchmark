#!/usr/bin/env python3
"""Minimal-preset-only performance report: mesh diagram + schematic sketch
alongside the performance table/chart for each of the 5 CASE_PRESETS["minimal"]
(case,param) entries, grouped by shared mesh (case2A's two param sets share
one mesh/schematic pair). Reuses build_html_report's table/chart builder and
CSS design system, and build_minimal_preset_page's mesh/schematic assets."""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'freefem'))
import build_html_report as bhr  # noqa: E402
import build_minimal_preset_page as bmp  # noqa: E402

report_data = json.loads((ROOT / 'results/multi_combo/report_data.json').read_text(encoding='utf-8'))
cases_by_key = {(c['case_name'], c['param_set']): c for c in report_data['cases']}

GROUPS = [
    (bmp.CASES[0], [('case2A', 'standard'), ('case2A', 'off_resonance')]),
    (bmp.CASES[1], [('case3C', 'coarse_check')]),
    (bmp.CASES[2], [('case3D', 'sparse_array')]),
    (bmp.CASES[3], [('case2F', 'plex7')]),
]

esc = bhr.esc

EXTRA_STYLE = """
.panels { display:grid; grid-template-columns: 1fr 1fr; gap:1.25rem; margin-bottom:1.25rem; }
@media (max-width:760px) { .panels { grid-template-columns:1fr; } }
.panel { margin:0; border:1px solid var(--border); border-radius:10px; padding:.75rem; background:var(--bg); }
.panel-label { font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin-bottom:.5rem; }
.panel img { width:100%; height:auto; display:block; border-radius:6px; }
.panel figcaption { font-size:.78rem; color:var(--muted); margin-top:.4rem; font-family:var(--font-mono); }
svg.schematic { width:100%; height:auto; display:block; }
svg.schematic .lbl { font-size:11px; fill:var(--text); font-family:var(--font-sans); }
svg.schematic .lbl-em { font-size:11px; fill:var(--text); font-weight:600; font-family:var(--font-sans); }
svg.schematic .note { font-size:9.5px; fill:var(--muted); font-family:var(--font-sans); }
.model-group { background:var(--surface); border:1px solid var(--border); border-radius:16px;
  padding:1.75rem 2rem; margin-bottom:2.5rem; }
.group-hd h2 { margin:0 0 .2rem; font-size:1.3rem; font-family:var(--font-mono); }
.group-hd .subtitle { margin:0 0 1.25rem; color:var(--muted); font-size:.92rem; }
.notes { display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; margin-bottom:1.5rem; }
@media (max-width:760px) { .notes { grid-template-columns:1fr; } }
.note-block h3 { font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin:0 0 .4rem; }
.note-block p { font-size:.88rem; margin:0; }
.subnav { display:flex; gap:.4rem; margin-bottom:1rem; flex-wrap:wrap; }
.subnav a { font-family:var(--font-mono); font-size:.76rem; color:var(--accent); text-decoration:none;
  border:1px solid var(--border); padding:.15rem .5rem; border-radius:999px; background:var(--bg); }
.model-group .case-card { border:1px solid var(--border); border-radius:10px; background:var(--bg);
  padding:1.25rem 1.5rem; margin-top:1rem; }
"""


def build_group_html(meta, keys, group_idx):
    gid = f"group-{group_idx}"
    nav_targets = "".join(f'<a href="#case-{esc(k[0])}-{esc(k[1])}">{esc(k[0])}:{esc(k[1])}</a>' for k in keys)

    perf_sections = []
    for i, key in enumerate(keys):
        case = cases_by_key[key]
        section_id = f"case-{key[0]}-{key[1]}"
        html = bhr.build_case_section(case, f"{group_idx}-{i}")
        html = html.replace(f'id="case-{group_idx}-{i}"', f'id="{section_id}"')
        perf_sections.append(html)

    return f"""
<section class="model-group" id="{gid}">
  <header class="group-hd">
    <h2>{esc(meta['title'])}</h2>
    <p class="subtitle">{esc(meta['subtitle'])}</p>
  </header>
  <div class="panels">
    <figure class="panel">
      <div class="panel-label">メッシュ図（実データ）</div>
      <img src="data:image/png;base64,{bmp.b64(meta['img'])}" alt="mesh diagram for {esc(meta['title'])}" />
      <figcaption>DOF = {esc(meta['dof'])} {esc(meta['ndof_note'])}</figcaption>
    </figure>
    <figure class="panel">
      <div class="panel-label">概念図（ポンチ絵）</div>
      {meta['schematic']}
    </figure>
  </div>
  <div class="notes">
    <div class="note-block">
      <h3>解きづらさの性質</h3>
      <p>{esc(meta['difficulty'])}</p>
    </div>
    <div class="note-block">
      <h3>前処理間の違いが出る理由（最小プリセット選定理由）</h3>
      <p>{esc(meta['why'])}</p>
    </div>
  </div>
  <nav class="subnav">{nav_targets}</nav>
  {''.join(perf_sections)}
</section>
"""


def main():
    sections = "\n".join(build_group_html(meta, keys, i) for i, (meta, keys) in enumerate(GROUPS))
    nav = "".join(f'<a href="#group-{i}">{esc(meta["title"].split(":")[0].strip())}</a>' for i, (meta, _) in enumerate(GROUPS))

    ndofs = [cases_by_key[k].get('ndof') for group in GROUPS for k in group[1] if cases_by_key[k].get('ndof')]
    dof_range = f"DOF {min(ndofs):,}〜{max(ndofs):,}" if ndofs else ""

    html = f"""<title>最小プリセット — 性能評価レポート</title>
<style>
:root {{
  --bg: #f6f5f2; --surface: #ffffff; --text: #1c1f24; --muted: #6b7280;
  --border: #e2e0da; --accent: #0e7c86; --accent-soft: #e4f3f2;
  --chart-surface: #fcfcfb;
  --good: #0ca30c; --good-bg: #e5f4ea; --critical: #d03b3b; --critical-bg: #fdecec;
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
header.page {{ padding:2.5rem 2rem 1.5rem; max-width:1040px; margin:0 auto; }}
header.page h1 {{ font-size:1.6rem; margin:0 0 .5rem; text-wrap:balance; }}
header.page p {{ color:var(--muted); max-width:80ch; }}
.methodology-note {{ font-size:.85rem; border-left:3px solid var(--accent); padding:.5rem .8rem;
  background:var(--accent-soft); border-radius:0 8px 8px 0; margin-top:.75rem; max-width:80ch; }}
nav.toc {{ max-width:1040px; margin:0 auto 1.5rem; padding:0 2rem; display:flex; flex-wrap:wrap; gap:.4rem .6rem; }}
nav.toc a {{ font-size:.82rem; color:var(--accent); text-decoration:none; border:1px solid var(--border);
  padding:.2rem .55rem; border-radius:999px; background:var(--surface); }}
nav.toc a:hover {{ background:var(--accent-soft); }}
main {{ max-width:1040px; margin:0 auto; padding:0 2rem 4rem; display:flex; flex-direction:column; gap:1rem; }}
.case-card {{ border-radius:14px; }}
.case-head h2 {{ margin:0 0 .2rem; font-size:1.1rem; font-family:var(--font-mono); }}
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
footer {{ max-width:1040px; margin:0 auto; padding:0 2rem 3rem; color:var(--muted); font-size:.8rem; }}
{EXTRA_STYLE}
</style>
<header class="page">
  <h1>最小プリセット — 性能評価レポート</h1>
  <p>Nédélec辺要素FEM Maxwell方程式ベンチマークの最小プリセット（<code>run_multi_combo.py --case-preset minimal</code>）5パラメータセットについて、GMRES/COCG × 7前処理（GS, SSOR, AMG(GAMG), 加速係数付きIC(0), CSLP, HX(2項), CSLP+HX(2項)）の性能比較、実メッシュ図、概念図（ポンチ絵）を1ページにまとめた。{esc(dof_range)}。</p>
  <p class="methodology-note">2026-07-29〜30の修正を反映：GMRESリスタート既定値を30→300に変更。HX/CSLP+HXは理論的忠実性の修正で発覚したGMRES停滞バグのため、3項版を無効化し2項版（スムーザ+勾配補正のみ）を標準実装とした。詳細はproblem_settings.md参照。全18ケースの完全版は別レポート「反復法×前処理 性能評価レポート」を参照。</p>
</header>
<nav class="toc">{nav}</nav>
<main>{sections}</main>
<footer>Edge03d Maxwell solver benchmark — minimal preset (5 param sets) — mesh diagrams rendered directly from generated_meshes/mesh/*.msh (freefem/render_mesh_diagram.py); schematics hand-authored, illustrative not mesh-accurate.</footer>
"""

    out_path = ROOT / 'results/multi_combo/minimal_report.html'
    out_path.write_text(html, encoding='utf-8')
    print(f"Wrote {out_path}")


if __name__ == '__main__':
    main()
