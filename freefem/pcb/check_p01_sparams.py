#!/usr/bin/env python3
"""P01/P02 lumped-port check (pcb_problem_benchmark_settings.md 3.3, 5.6; handoff tasks C, J-1).

Compares the S-parameters of P01 result JSONs (run_pcb_benchmark.py run, E2
excitation, usually --combos mumps/direct) with transmission-line theory: a
line of length L with the quasi-static Hammerstad-Jensen Z0 and eps_eff
(zero-thickness strip) and dielectric loss, between two R = 50 Ohm ports.

The lumped ports add parasitics that the line model does not have (the port
face of height h is a short series inductance, the strip ends a fringing
capacitance), so agreement is approximate; the check is the magnitude of
S21, the phase of S21 (electrical length) and mesh convergence.

eps_eff from the S21 phase: the eps_eff for which the phase of the line
model's S21 (air impedance Z01 of Hammerstad-Jensen kept, Z0 = Z01/sqrt(eps_eff))
equals the FEM phase. The roots are 2 pi apart in beta L; the root is chosen
by continuity in the electrical length f*L over the results of the same
cross-section (eps_eff_by_continuity), starting from the one nearest to the
Hammerstad-Jensen eps_eff. With a strongly mismatched line (P02-a,
Z0 of a few Ohm) the S21 phase is not beta L, hence the full line model.

Conductor loss (conductorModel "sibc", handoff task I): the attenuation
constant from the power absorbed by the SIBC faces (SIBC_CHECK lines),
alpha_c = P_c / (L * P_avail * (1 + |S21|^2)) with P_avail = |I|^2 R/8 (1 A
Norton source; the mean line power of a matched line is P_avail(1+|S21|^2)/2),
against the Pucel/Gupta closed form for a strip of thickness --t (default the
0.035 mm copper of settings 5.5) and the wide-strip estimate R_s/(Z0 w). The
FEM trace has zero thickness: its edge current ~ 1/sqrt(distance) makes the
strip loss grow like log(1/element size) under refinement, so the FEM value is
compared for its trend (coarse/medium/fine), not against a tolerance. The
change of |S21| against the PEC result of the same set (name without _sibc)
is printed too.

  python3 freefem/pcb/check_p01_sparams.py                       # results/pcb_benchmark
  python3 freefem/pcb/check_p01_sparams.py --out results/pcb_ports --combo mumps_direct
  python3 freefem/pcb/check_p01_sparams.py --problem P02            # thin substrates (h, w per set)
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ETA0 = 376.730313668
C0_MM_GHZ = 299.792458
MU0 = 1.25663706212e-6
DEFAULT_SIGMA = 5.8e7
NP_TO_DB = 20 / math.log(10)


def hammerstad_jensen(w: float, h: float, eps_r: float) -> tuple:
    """(Z0 [Ohm], eps_eff) of a zero-thickness microstrip (Hammerstad-Jensen 1980)."""
    u = w / h
    a = 1 + math.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) / 49 + math.log(1 + (u / 18.1) ** 3) / 18.7
    b = 0.564 * ((eps_r - 0.9) / (eps_r + 3)) ** 0.053
    eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 10 / u) ** (-a * b)
    fu = 6 + (2 * math.pi - 6) * math.exp(-(30.666 / u) ** 0.7528)
    z01 = ETA0 / (2 * math.pi) * math.log(fu / u + math.sqrt(1 + 4 / u ** 2))
    return z01 / math.sqrt(eps_eff), eps_eff


def line_sparams(f_ghz: float, L: float, w: float, h: float, eps_r: float, tan_d: float,
                 R: float = 50.0) -> tuple:
    """(S11, S21, Z0, eps_eff) of the line between two R ports (lengths in mm)."""
    z0, ee = hammerstad_jensen(w, h, eps_r)
    k0 = 2 * math.pi * f_ghz / C0_MM_GHZ
    beta = k0 * math.sqrt(ee)
    alpha = k0 * eps_r * (ee - 1) * tan_d / (2 * math.sqrt(ee) * (eps_r - 1))   # Np/mm
    gl = complex(alpha, beta) * L
    A = D = cmath.cosh(gl)
    B = z0 * cmath.sinh(gl)
    C = cmath.sinh(gl) / z0
    den = A + B / R + C * R + D
    return (A + B / R - C * R - D) / den, 2 / den, z0, ee


def eps_eff_from_phase(s21: complex, f_ghz: float, L: float, w: float, h: float, eps_r: float,
                       tan_d: float, R: float = 50.0, near: float | None = None) -> float | None:
    """eps_eff in [1, 1.5 eps_r] whose line-model S21 has the phase of s21, the
    root nearest to `near` (default: the Hammerstad-Jensen value; None if no
    root). The range goes beyond eps_r because the port parasitics lengthen the
    line electrically."""
    roots = eps_eff_roots(s21, f_ghz, L, w, h, eps_r, tan_d, R)
    target = near if near is not None else hammerstad_jensen(w, h, eps_r)[1]
    return min(roots, key=lambda e: abs(e - target)) if roots else None


def eps_eff_roots(s21: complex, f_ghz: float, L: float, w: float, h: float, eps_r: float,
                  tan_d: float, R: float = 50.0) -> list:
    """All eps_eff in [1, 1.5 eps_r] whose line-model S21 has the phase of s21
    (about 2 pi apart in beta L: for a line of several wavelengths they are
    close together, see main for the choice by continuity)."""
    z0_hj, ee_hj = hammerstad_jensen(w, h, eps_r)
    z01 = z0_hj * math.sqrt(ee_hj)
    k0 = 2 * math.pi * f_ghz / C0_MM_GHZ

    def dphase(ee: float) -> float:
        beta = k0 * math.sqrt(ee)
        alpha = k0 * eps_r * (ee - 1) * tan_d / (2 * math.sqrt(ee) * (eps_r - 1)) if eps_r > 1 else 0.0
        gl = complex(alpha, beta) * L
        z0 = z01 / math.sqrt(ee)
        a = cmath.cosh(gl)
        b, c = z0 * cmath.sinh(gl), cmath.sinh(gl) / z0
        return cmath.phase((2 / (a + b / R + c * R + a)) / s21)   # wrapped difference to the FEM phase

    n = 4000
    grid = [1 + (1.5 * eps_r - 1) * k / n for k in range(n + 1)]
    vals = [dphase(e) for e in grid]
    roots = []
    for k in range(n):
        v0, v1 = vals[k], vals[k + 1]
        if v0 == 0:
            roots.append(grid[k])
        elif v0 * v1 < 0 and abs(v0 - v1) < math.pi:   # a sign change, not a 2 pi wrap
            lo, hi = grid[k], grid[k + 1]
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if dphase(lo) * dphase(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            roots.append(0.5 * (lo + hi))
    return roots


def eps_eff_by_continuity(results: dict, sets: dict) -> dict:
    """{file name: eps_eff from the S21 phase}. The phase fixes eps_eff only up
    to steps of 2 pi in beta L, and for lines of several wavelengths (P01-b
    L = 131.4 mm, P01-a 20 GHz) the roots are about 0.4-0.8 apart, closer than
    the port parasitics shift eps_eff. The root is therefore chosen by
    continuity: results of the same cross-section (h, w, eps_r) are taken in
    the order of their electrical length f*L, the first one with the root
    nearest to Hammerstad-Jensen, each next one with the root nearest to the
    previous choice."""
    groups = {}
    for name, r in results.items():
        s = ((r.get("pcb") or {}).get("ports") or {}).get("S") or {}
        exc = (r.get("pcb") or {}).get("excited_port", "Port1")[-1]
        key = f"S{'2' if exc == '1' else '1'}{exc}"
        if key not in s:
            continue
        p = sets[r["param_set"].split("@")[0]]
        f = r["pcb"].get("freq_GHz", p["freqGHz"])
        groups.setdefault((p["h"], p["w"], p["epsSub"]), []).append((f * p["L"], name, complex(*s[key]), f, p))
    out = {}
    for (h, w, er), items in groups.items():
        prev = None
        for _, name, s21, f, p in sorted(items, key=lambda t: t[0]):
            roots = eps_eff_roots(s21, f, p["L"], w, h, er, p["tanDelta"])
            target = prev if prev is not None else hammerstad_jensen(w, h, er)[1]
            out[name] = min(roots, key=lambda e: abs(e - target)) if roots else None
            prev = out[name] if out[name] is not None else prev
    return out


def surface_resistance(f_ghz: float, sigma: float) -> float:
    return math.sqrt(math.pi * f_ghz * 1e9 * MU0 / sigma)


def conductor_loss_pucel(f_ghz: float, w: float, h: float, t: float, eps_r: float, sigma: float) -> float:
    """Conductor attenuation [Np/mm] of a microstrip of thickness t (Pucel et al.
    1968 in the form of Gupta/Garg/Bahl, 'Microstrip Lines and Slotlines')."""
    rs = surface_resistance(f_ghz, sigma)
    z0, ee = hammerstad_jensen(w, h, eps_r)
    b = h if w / h >= 1 / (2 * math.pi) else 2 * math.pi * w
    dw = t / math.pi * (1 + math.log((2 * h if w / h >= 1 / (2 * math.pi) else 4 * math.pi * w) / t))
    we = w + dw
    a = 1 + h / we * (1 + math.log(2 * b / t) / math.pi)
    u = we / h
    if w / h <= 1:
        db = 1.38 * a * rs / (h * z0) * (32 - u ** 2) / (32 + u ** 2)
    else:
        db = 6.1e-5 * a * rs * z0 * ee / h * (u + 0.667 * u / (u + 1.444))
    return db / NP_TO_DB


def conductor_loss_report(r: dict, p: dict, f_ghz: float, s21, t: float, pec_s21) -> None:
    ports = r["pcb"]["ports"]
    sig = r["pcb"].get("sigma") or DEFAULT_SIGMA
    chk = ports.get("sibc_check") or {}
    if not chk:
        print("   SIBC: no SIBC_CHECK lines in the result")
        return
    pc = sum(d["power_W"] for d in chk.values())
    p_av = ports.get("current_A", 1.0) ** 2 * 50.0 / 8
    a_fem = pc / (p["L"] * p_av * (1 + abs(s21) ** 2))
    z0, _ = hammerstad_jensen(p["w"], p["h"], p["epsSub"])
    a_puc = conductor_loss_pucel(f_ghz, p["w"], p["h"], t, p["epsSub"], sig)
    a_wide = surface_resistance(f_ghz, sig) / (z0 * p["w"])
    parts = ", ".join(f"label {lab} {100 * d['power_W'] / pc:.0f} %" for lab, d in chk.items())
    print(f"   SIBC sigma={sig:g}: P_c = {pc:.4e} W ({parts}); alpha_c FEM {1e3 * NP_TO_DB * a_fem:.3f} dB/m"
          f" | Pucel (t={t} mm) {1e3 * NP_TO_DB * a_puc:.3f} dB/m, FEM/Pucel {a_fem / a_puc:.2f}"
          f" | wide strip Rs/(Z0 w) {1e3 * NP_TO_DB * a_wide:.3f} dB/m")
    if pec_s21 is not None:
        d = 20 * math.log10(abs(s21)) - 20 * math.log10(abs(pec_s21))
        print(f"   |S21| SIBC - PEC = {d:+.5f} dB (conductor loss over L: FEM {-NP_TO_DB * a_fem * p['L']:+.5f} dB,"
              f" Pucel {-NP_TO_DB * a_puc * p['L']:+.5f} dB)")


def fmt(s: complex) -> str:
    return f"{abs(s):.4f} ({20 * math.log10(max(abs(s), 1e-300)):7.2f} dB) {math.degrees(cmath.phase(s)):8.2f} deg"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "pcb_benchmark")
    ap.add_argument("--combo", default="mumps_direct", help="preset_krylov part of the result names")
    ap.add_argument("--t", type=float, default=0.035, help="strip thickness [mm] of the closed-form conductor loss")
    ap.add_argument("--problem", default="P01", help="P01 or P02 (same microstrip layout and parameter names)")
    args = ap.parse_args()
    params_db = json.loads((ROOT / "freefem" / "pcb" / "pcb_case_parameters.json").read_text(encoding="utf-8"))
    sets = params_db[args.problem]["parameter_sets"]
    files = sorted((args.out / "runs").glob(f"{args.problem}_*__{args.combo}.json"))
    if not files:
        print(f"no {args.problem} results for {args.combo} in {args.out / 'runs'}")
        return 1
    results = {fp.name: json.loads(fp.read_text(encoding="utf-8")) for fp in files}
    ee_choice = eps_eff_by_continuity(results, sets)
    for fp in files:
        r = results[fp.name]
        ports = (r.get("pcb") or {}).get("ports") or {}
        if not ports.get("S"):
            print(f"{fp.name}: no S-parameters (status {r.get('status')})")
            continue
        pset = r["param_set"].split("@")[0]
        p = sets[pset]
        f_ghz = r["pcb"].get("freq_GHz", p["freqGHz"])   # run --freq changes it
        s11, s21, z0, ee = line_sparams(f_ghz, p["L"], p["w"], p["h"], p["epsSub"], p["tanDelta"])
        print(f"== {r['param_set']}  f={f_ghz} GHz  NDOF={r['ndof']}  status={r['status']}  "
              f"(line: Z0={z0:.2f} Ohm, eps_eff={ee:.3f}, L/lambda_g="
              f"{p['L'] * f_ghz * math.sqrt(ee) / C0_MM_GHZ:.3f})")
        exc = r["pcb"]["excited_port"][-1]
        other = "2" if exc == "1" else "1"
        ref = {f"S{exc}{exc}": s11, f"S{other}{exc}": s21}
        for k, v in sorted(ports["S"].items()):
            s = complex(*v)
            line = f"   {k}  FEM {fmt(s)}"
            if k in ref:
                line += f" | line {fmt(ref[k])} | |diff| {abs(s - ref[k]):.4f}"
            print(line)
        s21_key = f"S{other}{exc}"
        if s21_key in ports["S"]:
            ee_fem = ee_choice.get(fp.name)
            print(f"   eps_eff from the {s21_key} phase: "
                  + (f"{ee_fem:.3f} (Hammerstad-Jensen {ee:.3f}, {100 * (ee_fem / ee - 1):+.1f} %)"
                     if ee_fem is not None else "no root in [1, 1.5 eps_r]"))
        if r["pcb"].get("conductor_model") == "sibc":
            s21_fem = complex(*ports["S"]["S21"]) if "S21" in ports["S"] else None
            pec_name = fp.name.replace("_sibc", "", 1)
            pec_r = results.get(pec_name) if pec_name != fp.name else None
            pec_s = ((pec_r or {}).get("pcb") or {}).get("ports") or {}
            pec_s21 = complex(*pec_s["S"]["S21"]) if pec_s.get("S", {}).get("S21") else None
            if s21_fem is not None:
                conductor_loss_report(r, p, f_ghz, s21_fem, args.t, pec_s21)
        pec = ports.get("pec_check") or {}
        for lab, d in pec.items():
            print(f"   PEC {lab}: rms E_t {d['rms_Et']:.2e}  rms E {d['rms_E']:.2e}")
        for name, v in ports.get("voltage", {}).items():
            print(f"   {name}: V = {complex(v['re'], v['im']):.5f} V, face area {v['area']:.4f} mm^2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
