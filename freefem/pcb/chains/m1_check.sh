#!/bin/bash
# Mac task M1 (docs/next_tasks.md): check the cloud changes of 2026-10-05 on a
# machine with FreeFEM (A2: existing sets through the PCB runner, A3: K_max
# stopping rule, full residual history, trend columns of the summary).
#
#   bash freefem/pcb/chains/m1_check.sh             # all stages, in this order
#   bash freefem/pcb/chains/m1_check.sh run verify  # some stages only
#
# Stages: mesh regress regress_all run verify. Results in results/pcb_v1_check/
# (git-ignored); verify prints PASS/FAIL per check and writes
# results/pcb_v1_check/m1_check.md (copy it to docs/pcb_results/<host>/ to keep it).
# M3 Pro: about 30-60 min (regress --all-cases and the ssor/gmres run to K_max
# 10,000 take most of it). Run it under nohup for safety:
#   nohup bash freefem/pcb/chains/m1_check.sh > /tmp/m1_check.log 2>&1 &
set -u
cd "$(dirname "$0")/../../.."
export HWLOC_COMPONENTS=-gl
OUT=${OUT:-results/pcb_v1_check}
FF=${FREEFEM_BIN:-FreeFem++-mpi}
GMSH_PY=${GMSH_PY:-$HOME/.venvs/pcbmesh/bin/python}   # Python with gmsh 4.15.2
R() { python3 freefem/pcb/run_pcb_benchmark.py run --out "$OUT" --freefem-bin "$FF" "$@"; }
step() { echo "=== $(date '+%F %T') $*"; }
die() { echo "!!! $*"; exit 1; }

stage_mesh() {
  step "mesh: existing case1A-3F (for regress --all-cases and the A2 check), PCB P05-1"
  [ -n "$(ls generated_meshes/mesh/case*.msh 2>/dev/null | head -1)" ] && \
    [ "$(ls generated_meshes/mesh/case*.msh | wc -l)" -ge 46 ] || \
    python3 gmsh_templates/generate_all_meshes.py -o generated_meshes -p 6 || die "existing meshes"
  [ -f generated_meshes/pcb/mesh/P05-1.msh ] || \
    "$GMSH_PY" gmsh_templates/pcb/generate_pcb_meshes.py --sets P05-1 || die "P05-1 mesh"
}

stage_regress() {
  step "regress (11 cases)"
  python3 freefem/pcb/run_pcb_benchmark.py regress --freefem-bin "$FF" | tee "/tmp/m1_regress.txt"
  grep -qE '^([0-9]+)/\1 passed' /tmp/m1_regress.txt || die "regress: not all PASS"
}

stage_regress_all() {
  step "regress --all-cases (53 cases)"
  python3 freefem/pcb/run_pcb_benchmark.py regress --all-cases --freefem-bin "$FF" | tee "/tmp/m1_regress_all.txt"
  grep -qE '^([0-9]+)/\1 passed' /tmp/m1_regress_all.txt || die "regress --all-cases: not all PASS"
}

stage_run() {
  local C=ssor/gmres,ssor/cocg,cslp/gmres,npatch_asm/cocg
  step "run A3: P05-1 x 4 combinations, K_max 30 (tag k30)"
  R --sets P05-1 --combos $C --k-max 30 --tag k30 || die "run k30"
  step "run A3: P05-1 x 4 combinations, standard K_max"
  R --sets P05-1 --combos $C || die "run standard"
  step "run A2: existing case1A:standard, case2A:standard (standard K_max)"
  R --sets case1A:standard,case2A:standard --combos ssor/cocg,cslp/gmres,npatch_asm/cocg || die "run existing"
  step "run A2: --suite core lists the existing Core sets"
  R --suite core --list | grep -E '^  case(1A:standard|2A:standard|2A:off_resonance|3A:high_contrast) ' \
    | awk '{print $1}' | sort -u | tee /tmp/m1_core_list.txt
  [ "$(wc -l < /tmp/m1_core_list.txt)" -eq 4 ] || die "--suite core: the 4 existing Core sets are not listed"
}

stage_verify() {
  step "summary and checks"
  python3 freefem/pcb/summarize_pcb_benchmark.py --out "$OUT" --dest "$OUT/summary" || die "summary"
  python3 - "$OUT" <<'EOF'
import json, sys, time
from pathlib import Path
out = Path(sys.argv[1])
runs = {p.name[:-5]: json.loads(p.read_text()) for p in (out / "runs").glob("*.json")}
lines, n_fail = [], 0
def check(name, ok, detail):
    global n_fail
    n_fail += not ok
    lines.append(f"| {'PASS' if ok else 'FAIL'} | {name} | {detail} |")
combos = ["ssor_gmres", "ssor_cocg", "cslp_gmres", "npatch_asm_cocg"]
for c in combos:
    r = runs.get(f"P05_P05-1@k30__{c}")
    if r is None:
        check(f"P05-1@k30 {c}", False, "no result"); continue
    ok = (r["status"] == "max_it" and r["iterations"] == 30 and r.get("history_full")
          and len(r["history"]) == 31 and (r.get("stop_rule") or {}).get("k_max") == 30)
    check(f"P05-1@k30 {c}", ok, f"status {r['status']}, it {r['iterations']}, history {len(r['history'])} "
          f"points (full {r.get('history_full')}), stop_rule {r.get('stop_rule')}")
expect = {"ssor_gmres": ("max_it", 10000)}
for c in combos:
    r = runs.get(f"P05_P05-1__{c}")
    if r is None:
        check(f"P05-1 {c}", False, "no result"); continue
    st, it = expect.get(c, ("converged", None))
    ok = r["status"] == st and (it is None or r["iterations"] == it) and r.get("history_full") \
        and len(r["history"]) == r["iterations"] + 1
    check(f"P05-1 {c} (standard K_max)", ok,
          f"status {r['status']} (expected {st}), it {r['iterations']}, history {len(r['history'])} points, "
          f"wall {r['wall']:.0f} s, K_max {(r.get('stop_rule') or {}).get('k_max')}")
for case in ("case1A", "case2A"):
    for c in ("ssor_cocg", "cslp_gmres", "npatch_asm_cocg"):
        r = runs.get(f"{case}_standard__{c}")
        if r is None:
            check(f"{case}:standard {c}", False, "no result"); continue
        pcb = r.get("pcb") or {}
        # case1A:standard cslp/gmres stagnates (old benchmark: timeout at 687 it,
        # relres 0.26; Mac 2026-10-05: K_max 3000, relres 0.15, rho_cyc 0.996)
        st = "max_it" if (case, c) == ("case1A", "cslp_gmres") else "converged"
        ok = r["status"] == st and pcb.get("benchmark") == "existing" and pcb.get("solver_version")
        check(f"{case}:standard {c} (A2)", ok,
              f"status {r['status']} (expected {st}), it {r['iterations']}, wall {r['wall']:.0f} s, "
              f"solver {pcb.get('solver_version')}, length {pcb.get('length_unit')}")
md = (out / "summary" / "pcb_summary.md").read_text()
check("summary: table of the capped results", "上限に達した結果の補足情報" in md, "pcb_summary.md")
check("summary: existing sets as <case>:<set>", "case2A:standard" in md, "pcb_summary.md")
rep = [f"# M1 確認（A2・A3、{time.strftime('%Y-%m-%d %H:%M')}）", "",
       "`bash freefem/pcb/chains/m1_check.sh`。全段階を流したときは、regress・regress --all-cases が先の段階で全件 PASS している（失敗ならそこで止まる）。", "",
       "| 判定 | 項目 | 内容 |", "|---|---|---|"] + lines + ["",
       f"**{len(lines) - n_fail}/{len(lines)} PASS**", "",
       "参考: case1A:standard npatch_asm/cocg は WSL で 1013 反復（作業P。メッシュが違うので一致は求めない）。"]
(out / "m1_check.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
print("\n".join(rep))
sys.exit(1 if n_fail else 0)
EOF
}

stages=${*:-mesh regress regress_all run verify}
for s in $stages; do
  "stage_$s" || die "stage $s failed"
done
step "done"
