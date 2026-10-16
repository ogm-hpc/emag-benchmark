#!/usr/bin/env python3
"""Combine multi-combo production results with case_parameters.json /
problem_settings.md-derived metadata into one JSON blob suitable for
rendering a per-case performance report (tables + convergence-history data).

Usage:
  python3 freefem/generate_report_data.py \
      --results results/multi_combo/small_production.json \
      --out results/multi_combo/report_data.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_freefem_batch as rfb  # noqa: E402

PRESET_LABELS = {
    "gs": "GS", "ssor": "SSOR", "amg_gamg": "AMG(GAMG)", "accel_ic": "加速係数付きIC(0)",
    "cslp": "CSLP", "hx": "HX(2項)", "cslp_hx": "CSLP+HX(2項)",
}

# Eh.ndof (real Edge03d DOF count), measured directly via
# freefem/count_dof_template.edp against the actual generated meshes.
NDOF_LOOKUP = {
    "case1A:standard": 367986, "case1A:high_freq": 623177, "case1A:thick_pml": 867711, "case1A:thin_pml": 225824,
    "case1B:mie_low_eps": 743362,
    "case1C:narrow_aperture": 206953, "case1C:medium_aperture": 206745, "case1C:wide_aperture": 203885,
    "case2A:standard": 92281, "case2A:off_resonance": 92281,
    "case2B:narrow_iris": 308803, "case2B:medium_iris": 280358, "case2B:wide_iris": 277418, "case2B:off_resonance": 280358,
    "case2C:narrow_slit": 181204, "case2C:medium_slit": 181827, "case2C:wide_slit": 175276, "case2C:off_resonance": 181827,
    "case2D:few_walls": 570750, "case2D:many_walls": 669220, "case2D:off_resonance": 570750,
    "case2E:sparse_irises": 138402, "case2E:dense_irises": 171450,
    "case3A:low_contrast": 14028, "case3A:freq_perturb_a": 14028, "case3A:freq_perturb_b": 14028,
    "case3B:few_layers": 163349, "case3B:many_layers": 395461,
    "case3C:coarse_check": 17187, "case3C:medium_check": 64496, "case3C:fine_check": 51012,
    "case3D:sparse_array": 22942, "case3D:dense_array": 73385,
    "case3E:low_loss": 142798, "case3E:medium_loss": 142798, "case3E:high_loss": 142798,
    "case3F:low_contrast_no_loss": 27648, "case3F:high_contrast_with_loss": 27648,
    "case3F:ultra_contrast_high_loss": 27648,
    "case2F:empty": 3270, "case2F:plex7": 3635, "case2F:plex9": 3609,
    "case2F:pvc7": 3662, "case2F:pvc9": 3491,
}

CASE_DIFFICULTY_NOTES = {
    "case1A": "PEC球散乱(6面PML開放系)。閉空洞のような離散共振を持たず、放射減衰により単調な悪条件化が主要因。high_freqは周波数とメッシュ解像度が同時に変わるためstandardとの単純比較は不可。",
    "case1B": "高誘電率球のMie散乱。全パラメータセットでk0R=10固定、εrのみ変化(4/10/15/25)。内部波長が急減し高コントラスト境界を生む。Mie/whispering-gallery型内部共鳴の可能性は理論のみで未確定。",
    "case1C": "開口結合キャビティ散乱。隔壁以外の5面はPMLに接する開放系で、case2B/Cのような閉空洞共鳴とは異なるヘルムホルツ共鳴器的機構が想定される。",
    "case2A": "閉PEC空洞。standardは共振点近傍(モード(5,3,1)よりk0が0.8%乖離)で実測上も最難、off_resonanceは同一メッシュで非共振点(k0=2.0)に設定した比較用。",
    "case2B": "二室キャビティ+アイリス。各室2x2x2の閉空洞。medium_irisは共振点近傍(縮退モード群から約3%)で実測によりAMGで8.8倍の悪条件化を確認済み、off_resonanceはその比較用。",
    "case2C": "超狭スリット問題。閉空洞+g=λ0/100までの極端なスリット形状。medium_slitは共振点近傍でAMGにより13.6倍の悪条件化を実測確認済み。",
    "case2D": "迷路型キャビティ(Lx=8の細長い閉空洞)。モード密度が非常に高く、standardはモード(15,1,1)から0.2%と全ケース中最接近。ただし非共振点との差は実測で1.2倍のみと小さい。",
    "case2E": "周期アイリス列導波管(開放導波路)。Bragg/バンド端条件との理論的乖離は約13%(未実測)。",
    "case3A": "二層誘電体閉空洞。low_contrast/freq_perturb_a/bは同一メッシュ(κ=2)で周波数のみ±5%摂動、共振点近接の有無を実測確認(桁違いの差は見られなかった)。high_contrastはκ=100(本テストでは対象外、DOF>=1M)。",
    "case3B": "多層誘電体閉空洞(Air/PTFE/Alumina交互)。層数N=10/50で材料界面数を比較。",
    "case3C": "3Dチェッカーボード誘電体閉空洞。Nc(市松単位数)を4/8/12と変えて材料境界の複雑さを比較。",
    "case3D": "高誘電率ロッドアレイ。5x5(sparse)/10x10(dense)ロッド配列で周期構造の密度を比較。",
    "case3E": "損失材料インクルージョン閉空洞。tanδ=0.01/0.1/1.0で損失の大小を比較(損失は系を安定化させる可能性があり他の3系列と逆の効きかたをしうる)。",
    "case3F": "5材料混在(モザイク)閉空洞。κ・損失率を段階的に変えて材料コントラストの影響を比較。",
    "case2F": "TEAM Workshop Problem 19(Bossavit et al., EDF 1992)。導波管(86.36x43.18mm)がアイリス(幅15mm)を介して円筒空胴(直径90mm)に結合し、中心軸上に誘電体棒(プレキシガラスまたはPVC、直径7/9mm)を挿入。lambda0は各条件の実測共振周波数(論文Fig.5)に基づく——本プロジェクトで唯一、外部実測値と直接比較できるケース。",
}


def load_msh_ndof_cache():
    # Reuse previously-measured Eh.ndof values (freefem/count_dof_template.edp
    # sweep results) if available; otherwise leave as None (report will show
    # raw mesh element count only).
    return {}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--results", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    results = json.loads(args.results.read_text(encoding="utf-8"))
    case_db = rfb.load_case_params()

    by_case = {}
    for r in results:
        key = f"{r['case_name']}:{r['param_set']}"
        by_case.setdefault(key, []).append(r)

    report = {"cases": []}
    for key, combos in by_case.items():
        case_name, param_set = key.split(":")
        params = case_db[case_name]["parameter_sets"][param_set]
        k0 = rfb.pick_k0(case_name, params)

        combo_out = []
        for r in sorted(combos, key=lambda x: (x["preset"], x["krylov"])):
            residuals = r.get("residuals", [])
            final_res = residuals[-1][1] if residuals else None
            init_res = residuals[0][1] if residuals else None
            rel_res = (final_res / init_res) if (final_res is not None and init_res) else None
            combo_out.append({
                "preset": r["preset"],
                "preset_label": PRESET_LABELS.get(r["preset"], r["preset"]),
                "krylov": r["krylov"],
                "iterations": r.get("iterations"),
                "converged": r.get("converged"),
                "solve_time": r.get("solve_time"),
                "max_it_used": r.get("max_it_used"),
                "final_residual": final_res,
                "relative_residual": rel_res,
                "residual_history": residuals,
            })

        report["cases"].append({
            "case_name": case_name,
            "param_set": param_set,
            "description": case_db[case_name].get("description", ""),
            "param_description": params.get("description", ""),
            "k0": k0,
            "lambda0": params.get("lambda0"),
            "ndof": NDOF_LOOKUP.get(key),
            "difficulty_note": CASE_DIFFICULTY_NOTES.get(case_name, ""),
            "params": {k: v for k, v in params.items() if k != "description"},
            "combos": combo_out,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.out} ({len(report['cases'])} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
