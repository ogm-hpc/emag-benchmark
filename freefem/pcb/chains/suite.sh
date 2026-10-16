#!/bin/bash
# Run chain of the whole PCB benchmark suite (settings 15, docs/pcb_usage.md):
# Core, Extended, Challenge (standard 11 combinations, 600 s) and Multi-RHS.
# The runner is resumable (finished results are skipped), so a stopped chain is
# restarted with the same command; on a machine that already has the results
# every stage returns at once (on WSL the stage mumps still adds P01-3, P05-1..3
# and P03-1..3, whose references so far are in results/pcb_ports).
#
#   bash freefem/pcb/chains/suite.sh                    # all stages, in this order
#   bash freefem/pcb/chains/suite.sh core summary       # some stages only
#   LIST=1 bash freefem/pcb/chains/suite.sh mumps core  # list the jobs, run nothing
#   WORKERS=6 DEST=docs/pcb_results/mac_m3pro bash freefem/pcb/chains/suite.sh core summary   # a Mac
#
# Stages: mesh regress mumps core extended challenge single multirhs summary.
# This is the pre-v1.0 chain (time budget 600 s, 5 parallel): it pins --k-max none.
# The v1.0 records (docs/paper_plan.md B3: K_max per combination, every job alone)
# are not run with this chain; KMAX=standard only for trials.
# Keep the PC on AC power and stop it from sleeping (docs/pcb_handoff.md, task H1).
set -u
cd "$(dirname "$0")/../../.."
export HWLOC_COMPONENTS=-gl
W=${WORKERS:-5}                    # parallel jobs of the standard runs (WSL: 5)
DEST=${DEST:-docs/pcb_results}     # summary destination (a Mac: docs/pcb_results/<host>)
GMSH_PY=${GMSH_PY:-$HOME/.venvs/pcbmesh/bin/python}   # Python with gmsh 4.15.2
KMAX=${KMAX:-none}                 # stopping rule of the runs (run --k-max; none = 600 s budget)

# CSLP+HX/GMRES is run alone (one worker, no other job) for these sets: the
# 5-parallel run stops it at 600 s (settings 15.4, 15.7, 15.8).
SINGLE=P03-1,P03-2,P03-3,P03-r1,P03-r2,P03-r8,P03-d0.7,P03-d2,P03-d5,P03-v0.2,P03-v0.5,P03-a0.6,P03-a1.2
SINGLE=$SINGLE,P04-1,P04-2,P04-3,P04-4,P06-L10,P06-L30,P06-L30_s2,P07-1,P07-4,P08-N8_s1
SINGLE=$SINGLE,P01-2_t,P01-a_f20,P01-b_L131.4
# Sets whose jobs need more memory than 5 in parallel allow (WSL, 31 GB):
# P02-b_h0.05 (MUMPS 16 GB, GMRES(300) up to 15 GB), P05-lc0.625 (CSLP+HX 5.6 GB).
BIG2=P02-b_h0.05
BIG3=P05-lc0.625
STD=$(cd freefem/pcb && python3 -c "import run_pcb_benchmark as r; print(','.join(r.PCB_DEFAULT_COMBOS))")
NO_CSLP_HX=$(echo "$STD" | tr ',' '\n' | grep -vx 'cslp_hx/gmres' | paste -sd, -)

R() { python3 freefem/pcb/run_pcb_benchmark.py run --roles '' --k-max "$KMAX" "$@" ${LIST:+--list}; }
step() { echo "=== $(date '+%F %T') $*"; }
die() { echo "!!! $*"; exit 1; }

# sets_of TIER [single|other]: parameter sets of a suite tier (comma separated),
# optionally only those in / not in $SINGLE, without $BIG2 and $BIG3 for "other"
sets_of() {
  python3 - "$1" "${2:-}" "$SINGLE" "$BIG2,$BIG3" <<'EOF'
import json, sys
tier, part, single, big = sys.argv[1], sys.argv[2], set(sys.argv[3].split(",")), set(sys.argv[4].split(","))
cases = json.load(open("freefem/pcb/pcb_case_parameters.json"))
out = [n for p in cases.values() for n, s in p["parameter_sets"].items() if s.get("suite") == tier]
if part == "single":
    out = [n for n in out if n in single]
elif part == "other":
    out = [n for n in out if n not in single and n not in big]
print(",".join(out))
EOF
}

stage_mesh() {
  step "mesh: Core, Extended, Challenge (gmsh 4.15.2)"
  "$GMSH_PY" gmsh_templates/pcb/generate_pcb_meshes.py --suite core,extended,challenge \
    || die "mesh generation failed (see the [FAIL] lines)"
}

stage_regress() {
  step "regress"
  python3 freefem/pcb/run_pcb_benchmark.py regress | tee /tmp/suite_regress.txt
  grep -qE '^([0-9]+)/\1 passed' /tmp/suite_regress.txt || die "regress: not all PASS"
}

stage_mumps() {
  step "mumps: references of Core, Extended, Challenge (P03: both ports in one job)"
  local all p03 rest
  all=$(sets_of core),$(sets_of extended),$(sets_of challenge)
  p03=$(echo "$all" | tr ',' '\n' | grep '^P03-' | paste -sd, -)
  rest=$(echo "$all" | tr ',' '\n' | grep -v '^P03-' | grep -vx "$BIG2" | paste -sd, -)
  R --sets $BIG2 --combos mumps/direct --workers 1
  R --sets "$rest" --combos mumps/direct --workers $W
  R --sets "$p03" --combos mumps/direct --mrhs shared --workers 4 --k-max none
}

# std TIER: the standard combinations of a tier
std() {
  local tier=$1 other single
  other=$(sets_of "$tier" other); single=$(sets_of "$tier" single)
  [ -n "$other" ] && R --sets "$other" --combos "$STD" --workers $W
  [ -n "$single" ] && R --sets "$single" --combos "$NO_CSLP_HX" --workers $W
  for s in ${BIG2//,/ } ${BIG3//,/ }; do
    case ",$(sets_of "$tier")," in *",$s,"*)
      R --sets "$s" --combos "$STD" --workers $([ "$s" = "$BIG2" ] && echo 2 || echo 3);;
    esac
  done
}

stage_core()      { step "core: 9 sets x 11 combinations";      std core; }
stage_extended()  { step "extended: 52 sets x 11 combinations"; std extended; }
stage_challenge() { step "challenge: 6 sets x 11 combinations"; std challenge; }

stage_single() {
  step "single: CSLP+HX/GMRES alone for the large sets"
  R --sets "$SINGLE" --combos cslp_hx/gmres --workers 1
}

stage_multirhs() {
  step "multirhs: P07-1, P08-N4_s1, P08-N8_s1, everything alone (settings 12.2)"
  python3 - <<'EOF' > /tmp/suite_mrhs.txt
import json
cases = json.load(open("freefem/pcb/pcb_case_parameters.json"))
for p in cases.values():
    for n, s in p["parameter_sets"].items():
        if "multiRhsBudgetPerPort" in s:
            print(n, s["multiRhsBudgetPerPort"], len(p["ports"]))
EOF
  while read -r set per nports; do
    local B=$((per * nports))
    R --sets "$set" --combos mumps/direct --mrhs shared --workers 1 --budget $B --k-max none
    R --sets "$set" --combos cslp_hx/gmres --port all --tag u1 --workers 1 --budget $per --k-max none
    for m in shared block gcro; do
      R --sets "$set" --combos cslp_hx/gmres --mrhs $m --workers 1 --budget $B --k-max none
    done
  done < /tmp/suite_mrhs.txt
}

stage_summary() {
  step "summary -> $DEST"
  python3 freefem/pcb/summarize_pcb_benchmark.py --dest "$DEST"
}

stages=${*:-mesh regress mumps core extended challenge single multirhs summary}
for s in $stages; do
  "stage_$s" || die "stage $s failed"
done
step "done"
