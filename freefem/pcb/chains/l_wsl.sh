#!/bin/bash
# Task L-6 (WSL, the reference machine): run chain of the PCB benchmark-suite
# work (docs/pcb_handoff.md, task L). Prepared and checked on the M3 Pro Mac
# (L-1 to L-5); on WSL it only has to be run:
#
#   cd <repository> && git pull
#   bash freefem/pcb/chains/l_wsl.sh            # all stages, in this order
#   bash freefem/pcb/chains/l_wsl.sh p08        # or some stages only
#   LIST=1 bash freefem/pcb/chains/l_wsl.sh mumps std p03single p08   # dry run
#
# Stages: mesh regress mumps std p03single p08. The runner is resumable
# (finished results are skipped), so a stopped chain can be restarted with the
# same command. Keep the PC on AC power and stop it from sleeping (handoff,
# task H1 "評価の結果").
set -u
cd "$(dirname "$0")/../../.."
export HWLOC_COMPONENTS=-gl

P03=P03-r1,P03-r2,P03-r8,P03-d0.7,P03-d2,P03-d5,P03-v0.2,P03-v0.5,P03-a0.6,P03-a1.2
P05=P05-g0.1,P05-g1.0,P05-fc,P05-fe,P05-n1,P05-n4,P05-td1e-4,P05-td1e-2,P05-lc1.25,P05-lc0.625
# Standard combinations except cslp_hx/gmres (P03: run alone, settings 15.4).
NO_CSLP_HX=gs/gmres,ssor/gmres,ssor/cocg,amg_gamg/gmres,amg_gamg/cocg,accel_ic/gmres,accel_ic/cocg,cslp/gmres,hx/gmres
# P08-N8_s1 (16 ports): budget per independent solve (u1) and total budget of
# one --mrhs job; set from the Mac pre-check (task L-4).
# Set from the Mac pre-check (task L-4): port 1 converges in 226 iterations,
# about 617 s on WSL alone, so 600 s would cut the baseline (user decision
# 2026-10-02: 900 s per port, recorded as a separate condition).
P08_U1_BUDGET=900
P08_MRHS_BUDGET=14400

# LIST=1: only list the jobs of the run stages (no meshing, no regress).
R() { python3 freefem/pcb/run_pcb_benchmark.py run --roles '' "$@" ${LIST:+--list}; }
step() { echo "=== $(date '+%F %T') $*"; }
die() { echo "!!! $*"; exit 1; }

stage_mesh() {
  step "mesh: task L sets (venv gmsh 4.15.2)"
  ~/.venvs/pcbmesh/bin/python gmsh_templates/pcb/generate_pcb_meshes.py --sets P03-1,$P03,$P05 \
    || die "mesh generation failed (see the [FAIL] lines)"
  python3 - <<'EOF' || die "edge counts differ from the Mac by more than 1 %"
import json, sys
ref = json.load(open("freefem/pcb/chains/l_mesh_ref_mac.json"))["edges"]
bad = 0
for r in json.load(open("generated_meshes/pcb/mesh_report.json")):
    m = ref.get(r["set"])
    d = (r["edges"] - m) / m
    flag = "" if abs(d) <= 0.01 and not r["errors"] else "  <-- check"
    bad += bool(flag)
    print(f"  {r['set']:12s} wsl {r['edges']:8d}  mac {m:8d}  {100*d:+.2f} %{flag}")
sys.exit(1 if bad else 0)
EOF
}

stage_regress() {
  step "regress"
  python3 freefem/pcb/run_pcb_benchmark.py regress | tee /tmp/l_regress.txt
  grep -q '^8/8 passed' /tmp/l_regress.txt || die "regress: not all PASS"
}

stage_mumps() {
  step "mumps: references (P05 one port; P03 both ports in one job)"
  R --sets $P05 --combos mumps/direct --workers 5
  R --sets $P03 --combos mumps/direct --mrhs shared --workers 4
}

stage_std() {
  step "std: standard combinations, 5 workers (P03 without cslp_hx/gmres)"
  R --sets ${P05%,P05-lc0.625} --workers 5
  # P05-lc0.625 (485k edges): cslp_hx 6.1 GB on the Mac; 3 workers keep the
  # sum of its 10 combinations well inside 31 GB.
  R --sets P05-lc0.625 --workers 3
  R --sets $P03 --combos $NO_CSLP_HX --workers 5
}

stage_p03single() {
  step "p03single: P03 cslp_hx/gmres alone (settings 15.4)"
  R --sets $P03 --combos cslp_hx/gmres --workers 1
}

stage_p08() {
  step "p08: P08-N8_s1 multiple right-hand sides, everything alone (handoff H1)"
  case "$P08_U1_BUDGET$P08_MRHS_BUDGET" in *__*) die "P08 budgets not set (task L-4)";; esac
  R --sets P08-N8_s1 --combos mumps/direct --mrhs shared --workers 1 --budget $P08_MRHS_BUDGET
  R --sets P08-N8_s1 --combos cslp_hx/gmres --port all --tag u1 --workers 1 --budget $P08_U1_BUDGET
  R --sets P08-N8_s1 --combos cslp_hx/gmres --mrhs shared --workers 1 --budget $P08_MRHS_BUDGET
  R --sets P08-N8_s1 --combos cslp_hx/gmres --mrhs block --workers 1 --budget $P08_MRHS_BUDGET
  R --sets P08-N8_s1 --combos cslp_hx/gmres --mrhs gcro --workers 1 --budget $P08_MRHS_BUDGET
  R --sets P08-N8_s1 --combos cslp_hx/gmres --mrhs gcro --mrhs-recycle 10 --mrhs-recycle-max 40 \
    --workers 1 --budget $P08_MRHS_BUDGET
}

stages=${*:-mesh regress mumps std p03single p08}
for s in $stages; do
  "stage_$s" || die "stage $s failed"
done
step "done"
