#!/usr/bin/env python3
"""Assemble the minimal-preset gallery page: mesh diagrams (rendered from the
actual .msh files) + schematic sketches (hand-drawn SVG, illustrative not
mesh-accurate) for each of the 5 cases in CASE_PRESETS["minimal"]."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "multi_combo" / "minimal_preset_gallery.html"


def b64(name: str) -> str:
    return (ROOT / "results" / "multi_combo" / f"{name}.b64").read_text().strip()


def schematic_case2a() -> str:
    # Simple isometric box: PEC cavity, Lx=4, Ly=2, Lz=2 (lambda0 units).
    return """
<svg viewBox="0 0 420 300" class="schematic">
  <defs>
    <pattern id="hatch2a" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="6" stroke="var(--ink-soft)" stroke-width="1"/>
    </pattern>
  </defs>
  <!-- isometric box: front face, top face, side face -->
  <polygon points="90,220 270,220 270,110 90,110" fill="var(--c-pec)" fill-opacity="0.18" stroke="var(--ink)" stroke-width="1.5"/>
  <polygon points="90,110 270,110 330,70 150,70" fill="var(--c-pec)" fill-opacity="0.32" stroke="var(--ink)" stroke-width="1.5"/>
  <polygon points="270,220 270,110 330,70 330,180" fill="var(--c-pec)" fill-opacity="0.45" stroke="var(--ink)" stroke-width="1.5"/>
  <rect x="90" y="110" width="180" height="110" fill="url(#hatch2a)" opacity="0.5"/>
  <text x="180" y="250" text-anchor="middle" class="lbl">Lx = 4&#955;&#8320;</text>
  <text x="55" y="168" text-anchor="middle" class="lbl" transform="rotate(-90 55 168)">Lz = 2&#955;&#8320;</text>
  <text x="305" y="150" text-anchor="middle" class="lbl">Ly = 2&#955;&#8320;</text>
  <text x="180" y="150" text-anchor="middle" class="lbl-em">PEC walls (all faces)</text>
  <text x="180 " y="278" text-anchor="middle" class="note">standard: k&#8320;=2&#960; (0.8% from mode (5,3,1)) &#8226; off_resonance: k&#8320;=2.0</text>
</svg>
"""


def schematic_case3c() -> str:
    # 4x4 checkerboard top view + tiny 3rd-dimension indicator.
    cells = []
    n = 4
    cs = 40
    x0, y0 = 60, 40
    colors = {0: "var(--c-eps1)", 1: "var(--c-eps100)"}
    for i in range(n):
        for j in range(n):
            parity = (i + j) % 2
            cells.append(
                f'<rect x="{x0+i*cs}" y="{y0+j*cs}" width="{cs}" height="{cs}" '
                f'fill="{colors[parity]}" stroke="var(--surface)" stroke-width="2"/>'
            )
    cells_svg = "\n".join(cells)
    return f"""
<svg viewBox="0 0 420 300" class="schematic">
  {cells_svg}
  <rect x="{x0}" y="{y0}" width="{n*cs}" height="{n*cs}" fill="none" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="{x0+n*cs/2}" y="{y0+n*cs+22}" text-anchor="middle" class="lbl">4&#215;4 shown (actual: 4&#215;4&#215;4 = 64 cells)</text>
  <text x="{x0+n*cs+50}" y="{y0+20}" class="lbl-em" fill="var(--c-eps1-ink)">&#9632; Eps1 (air)</text>
  <text x="{x0+n*cs+50}" y="{y0+42}" class="lbl-em" fill="var(--c-eps100-ink)">&#9632; Eps100 (&#956;r=100)</text>
  <text x="210" y="278" text-anchor="middle" class="note">L=2&#955;&#8320; cube, cell size h=L/Nc=0.5&#955;&#8320; &#8226; coarse_check: Nc=4</text>
</svg>
"""


def schematic_case3d() -> str:
    # 5x5 rod grid top view.
    dots = []
    n = 5
    cs = 34
    x0, y0 = 90, 40
    for i in range(n):
        for j in range(n):
            cx = x0 + i * cs + cs / 2
            cy = y0 + j * cs + cs / 2
            dots.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="var(--c-eps100)" stroke="var(--ink)" stroke-width="1"/>')
    dots_svg = "\n".join(dots)
    w = n * cs
    return f"""
<svg viewBox="0 0 420 300" class="schematic">
  <rect x="{x0-15}" y="{y0-15}" width="{w+30}" height="{w+30}" fill="var(--c-air)" stroke="var(--ink)" stroke-width="1.5"/>
  {dots_svg}
  <text x="{x0+w/2}" y="{y0+w+35}" text-anchor="middle" class="lbl">5&#215;5 rods, pitch p=0.5&#955;&#8320;, radius R=0.2&#955;&#8320;</text>
  <text x="{x0+w/2}" y="278" text-anchor="middle" class="note">Top view (z-axis into page) &#8226; rod height Hz=1.0&#955;&#8320; &#8226; PEC outer walls</text>
</svg>
"""


def schematic_case2f() -> str:
    # Side-view: waveguide -> iris -> cylindrical cavity with rod.
    return """
<svg viewBox="0 0 420 300" class="schematic">
  <!-- waveguide -->
  <rect x="30" y="120" width="140" height="60" fill="var(--c-air)" stroke="var(--ink)" stroke-width="1.5"/>
  <!-- iris channel -->
  <rect x="170" y="140" width="18" height="20" fill="var(--c-air)" stroke="var(--ink)" stroke-width="1.5"/>
  <!-- cavity -->
  <circle cx="270" cy="150" r="75" fill="var(--c-air)" stroke="var(--ink)" stroke-width="1.5"/>
  <!-- rod -->
  <circle cx="270" cy="150" r="6" fill="var(--c-lossy)" stroke="var(--ink)" stroke-width="1"/>
  <!-- port arrow -->
  <line x1="10" y1="150" x2="30" y2="150" stroke="var(--ink)" stroke-width="2" marker-end="url(#arrow2f)"/>
  <defs>
    <marker id="arrow2f" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 z" fill="var(--ink)"/>
    </marker>
  </defs>
  <text x="20" y="115" text-anchor="middle" class="lbl">PortOut</text>
  <text x="100" y="115" text-anchor="middle" class="lbl">waveguide 86.36&#215;43.18mm</text>
  <text x="179" y="120" text-anchor="middle" class="lbl" font-size="10">iris</text>
  <text x="179" y="200" text-anchor="middle" class="lbl" font-size="10">l=15mm</text>
  <text x="270" y="65" text-anchor="middle" class="lbl">cavity &#8960;90mm</text>
  <text x="270" y="170" text-anchor="middle" class="lbl-em" fill="var(--c-lossy-ink)" font-size="9">rod &#8960;7mm</text>
  <text x="210" y="278" text-anchor="middle" class="note">Plexiglas &#949;r=2.7&#8722;0.01i &#8226; PEC walls &#8226; &#955;&#8320; set to the measured resonance (2490MHz)</text>
</svg>
"""


CASES = [
    {
        "id": "case2a", "title": "case2A : standard / off_resonance",
        "subtitle": "Empty PEC cavity — near-resonance vs. off-resonance (identical mesh)",
        "difficulty": "共振点近傍の閉空洞。standardはモード(5,3,1)からk0が0.8%しか離れておらず全前処理中最難。off_resonanceは全く同じメッシュでk0のみ変え、周波数だけが難易度を左右することを示す対照実験。",
        "why": "CSLPだけが確実に進展し、他の6前処理は数千反復かけても未収束。COCGはGS/SSOR/AMG(GAMG)いずれと組んでも数反復以内に破綻（DIVERGED_INDEFINITE_MAT）。",
        "img": "mesh_case2A.png", "schematic": schematic_case2a(),
        "dof": "92,281", "ndof_note": "(standard/off_resonanceで同一メッシュ)",
    },
    {
        "id": "case3c", "title": "case3C : coarse_check",
        "subtitle": "3D checkerboard dielectric (Nc=4, 64 cells)",
        "difficulty": "材料境界は複雑だが電気的には比較的易しいケース。",
        "why": "全7前処理が実際に収束する唯一のケース（CSLP 18反復〜HX 134反復）——成功/失敗ではなく相対的な効率の順位で前処理を差別化できる、他にない対照ケース。",
        "img": "mesh_case3C.png", "schematic": schematic_case3c(),
        "dof": "17,187", "ndof_note": "",
    },
    {
        "id": "case3d", "title": "case3D : sparse_array",
        "subtitle": "High-permittivity rod array (5×5 rods)",
        "difficulty": "周期構造を持つ多材料ベンチマーク。",
        "why": "HXだけが際立って悪い（1405反復・214秒 vs. 他は数百反復以下）——前処理ごとの幾何依存的な得意/不得意を示す唯一のケース。",
        "img": "mesh_case3D.png", "schematic": schematic_case3d(),
        "dof": "22,942", "ndof_note": "",
    },
    {
        "id": "case2f", "title": "case2F : plex7 (TEAM-19)",
        "subtitle": "Waveguide-fed cylindrical cavity + dielectric rod (Bossavit et al. 1992, EDF)",
        "difficulty": "実測ベンチマーク（COMPUMAG TEAM Workshop Problem 19）。導波管がアイリスを介して円筒空胴に結合し、中心軸上に誘電体棒を挿入。",
        "why": "誘電体負荷でAMG(GAMG)とaccel_ic+COCGが実際に収束するようになる（空条件では未収束）——損失/負荷が不定性を緩和する直接証拠。本プロジェクトで唯一、外部実測値と直接比較できるケース。",
        "img": "mesh_case2F.png", "schematic": schematic_case2f(),
        "dof": "3,635", "ndof_note": "",
    },
]


def esc(s):
    return s


def build_case_html(c):
    return f"""
<section class="case" id="{c['id']}">
  <header class="case-hd">
    <h2>{c['title']}</h2>
    <p class="subtitle">{c['subtitle']}</p>
  </header>
  <div class="panels">
    <figure class="panel">
      <div class="panel-label">メッシュ図（実データ）</div>
      <img src="data:image/png;base64,{b64(c['img'])}" alt="mesh diagram" />
      <figcaption>DOF = {c['dof']} {c['ndof_note']}</figcaption>
    </figure>
    <figure class="panel">
      <div class="panel-label">概念図（ポンチ絵）</div>
      {c['schematic']}
    </figure>
  </div>
  <div class="notes">
    <div class="note-block">
      <h3>解きづらさの性質</h3>
      <p>{c['difficulty']}</p>
    </div>
    <div class="note-block">
      <h3>前処理間の違いが出る理由</h3>
      <p>{c['why']}</p>
    </div>
  </div>
</section>
"""


def main():
    sections = "\n".join(build_case_html(c) for c in CASES)
    nav = "".join(f'<a href="#{c["id"]}">{c["title"].split(":")[0].strip()}</a>' for c in CASES)

    html = f"""<title>最小プリセット — メッシュ図・概念図ギャラリー</title>
<style>
:root {{
  --bg: #f6f5f2; --surface: #ffffff; --ink: #1c1f24; --ink-soft: #6b7280; --border: #e2e0da;
  --accent: #0e7c86; --accent-soft: #e4f3f2;
  --c-pec: #7c8592; --c-air: #cde2fb; --c-eps1: #cde2fb; --c-eps1-ink:#5a7fa8;
  --c-eps100: #eb6834; --c-eps100-ink: #b6491e; --c-lossy: #e87ba4; --c-lossy-ink: #b8477a;
  --font-sans: -apple-system, "Segoe UI", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#14171c; --surface:#1b1f26; --ink:#e6e8eb; --ink-soft:#9aa1ac; --border:#2b3038;
    --accent:#4fd1c5; --accent-soft:#1c2e2c; }}
}}
:root[data-theme="dark"] {{ --bg:#14171c; --surface:#1b1f26; --ink:#e6e8eb; --ink-soft:#9aa1ac; --border:#2b3038;
  --accent:#4fd1c5; --accent-soft:#1c2e2c; }}
:root[data-theme="light"] {{ --bg:#f6f5f2; --surface:#ffffff; --ink:#1c1f24; --ink-soft:#6b7280; --border:#e2e0da;
  --accent:#0e7c86; --accent-soft:#e4f3f2; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:var(--font-sans); line-height:1.6; }}
header.page {{ padding:2.5rem 2rem 1rem; max-width:1000px; margin:0 auto; }}
header.page h1 {{ font-size:1.5rem; margin:0 0 .4rem; text-wrap:balance; }}
header.page p {{ color:var(--ink-soft); max-width:70ch; }}
nav.toc {{ max-width:1000px; margin:0 auto 1.5rem; padding:0 2rem; display:flex; gap:.5rem; flex-wrap:wrap; }}
nav.toc a {{ font-family:var(--font-mono); font-size:.82rem; color:var(--accent); text-decoration:none;
  border:1px solid var(--border); padding:.25rem .6rem; border-radius:999px; background:var(--surface); }}
main {{ max-width:1000px; margin:0 auto; padding:0 2rem 4rem; display:flex; flex-direction:column; gap:2rem; }}
.case {{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:1.5rem 1.75rem; }}
.case-hd h2 {{ margin:0 0 .15rem; font-size:1.15rem; font-family:var(--font-mono); }}
.case-hd .subtitle {{ margin:0 0 1rem; color:var(--ink-soft); font-size:.92rem; }}
.panels {{ display:grid; grid-template-columns: 1fr 1fr; gap:1.25rem; margin-bottom:1.25rem; }}
@media (max-width:760px) {{ .panels {{ grid-template-columns:1fr; }} }}
.panel {{ margin:0; border:1px solid var(--border); border-radius:10px; padding:.75rem; background:var(--bg); }}
.panel-label {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; color:var(--ink-soft); margin-bottom:.5rem; }}
.panel img {{ width:100%; height:auto; display:block; border-radius:6px; }}
.panel figcaption {{ font-size:.78rem; color:var(--ink-soft); margin-top:.4rem; font-family:var(--font-mono); }}
svg.schematic {{ width:100%; height:auto; display:block; }}
svg.schematic .lbl {{ font-size:11px; fill:var(--ink); font-family:var(--font-sans); }}
svg.schematic .lbl-em {{ font-size:11px; fill:var(--ink); font-weight:600; font-family:var(--font-sans); }}
svg.schematic .note {{ font-size:9.5px; fill:var(--ink-soft); font-family:var(--font-sans); }}
.notes {{ display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; }}
@media (max-width:760px) {{ .notes {{ grid-template-columns:1fr; }} }}
.note-block h3 {{ font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; color:var(--ink-soft); margin:0 0 .4rem; }}
.note-block p {{ font-size:.88rem; margin:0; }}
footer {{ max-width:1000px; margin:0 auto; padding:0 2rem 3rem; color:var(--ink-soft); font-size:.8rem; }}
</style>
<header class="page">
  <h1>最小プリセット — メッシュ図・概念図ギャラリー</h1>
  <p>反復法×前処理 性能評価の最小プリセット（<code>run_multi_combo.py --case-preset minimal</code>）を構成する5パラメータセットについて、実際のFEMメッシュ（.mshファイルから直接描画）と概念図を並べた。</p>
</header>
<nav class="toc">{nav}</nav>
<main>{sections}</main>
<footer>Edge03d Maxwell solver benchmark — mesh diagrams rendered directly from generated_meshes/mesh/*.msh (freefem/render_mesh_diagram.py).</footer>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
