#!/bin/bash
# Run chain of B5 (docs/paper_plan.md B, docs/next_tasks.md M4) on the Mac
# M3 Pro: matrix features (matrix_features.py, MUMPS backend) and Ritz probes
# (run_pcb_benchmark.py ritz, 8 preconditioners) of all 112 sets (PCB Core,
# Extended, Challenge and the existing case1A-3F) on the B1 meshes, every job
# alone (1 worker). Iteration counts next to them: the v1.0 records.
# Finished sets / probes are skipped: a stopped chain is restarted with the
# same command.
#
#   caffeinate -i nohup bash freefem/pcb/chains/b5.sh > ~/b5.log 2>&1 &
#   bash freefem/pcb/chains/b5.sh ritz ritzsum       # some stages only
#
# Stages (in this order):
#   regress   regress (all PASS, else stop)
#   features  matrix_features.py --backend mumps per set -> $FEAT/<host>/
#   featsum   $DEST/matrix_features.{md,csv}
#   ritz      Ritz probes, 300 Arnoldi steps, start rhs, inner lu -> $RITZ/<host>/
#   ritzsum   $DEST/ritz_features.{md,csv}
# Estimate (2026-10-12): features ~7 h, ritz some tens of hours.
# Sleep: keep the lid open or  sudo pmset -a disablesleep 1  (see v1.sh).
set -u
cd "$(dirname "$0")/../../.."
export HWLOC_COMPONENTS=-gl
FEAT=${FEAT:-results/pcb_features_v1}
RITZ=${RITZ:-results/pcb_ritz_v1}
DEST=${DEST:-docs/results_v1/mac_m3pro}
ITERS=$DEST/pcb_summary.csv
SUITE=core,extended,challenge
CPY=${CPY:-$HOME/venvs/ff-petsc-c/bin/python}   # petsc4py on FreeFEM's complex PETSc
HOST=$(python3 -c 'import sys; sys.path.insert(0, "freefem/pcb"); import pcb_host; print(pcb_host.detect().name)')
step() { echo "=== $(date '+%F %T') $*"; }
die() { echo "!!! $*"; exit 1; }

# the 112 sets as --sets names them (P05-1, case2A:standard)
sets() {
  python3 freefem/pcb/run_pcb_benchmark.py ritz --list --suite "$SUITE" --precs gs --out "$RITZ" --force |
    awk 'NR > 1 { s = $1; if (s !~ /^case/) sub(/^[^:]*:/, "", s); print s }'
}

stage_regress() {
  step "regress"
  python3 freefem/pcb/run_pcb_benchmark.py regress > "$RITZ.regress.txt" 2>&1
  cat "$RITZ.regress.txt"
  grep -qE '^([0-9]+)/\1 passed' "$RITZ.regress.txt" || die "regress: not all PASS (output kept in $RITZ.regress.txt)"
}

stage_features() {
  local all n=0 fail=0
  all=$(sets)
  step "features: $(echo "$all" | wc -l | tr -d ' ') sets -> $FEAT/$HOST"
  for s in $all; do
    n=$((n + 1))
    [ -f "$FEAT/$HOST/${s/:/_}.json" ] && continue
    echo "--- [$n] $s $(date '+%T')"
    "$CPY" freefem/pcb/matrix_features.py --backend mumps --sets "$s" --out "$FEAT" || fail=$((fail + 1))
  done
  [ $fail -eq 0 ] || echo "!!! features: $fail sets failed (see above); continuing"
}

stage_featsum() {
  step "features summary -> $DEST"
  python3 freefem/pcb/summarize_matrix_features.py --host "$HOST" --features "$FEAT" --iters "$ITERS" \
    --out "$DEST" || die "featsum"
}

stage_ritz() {
  step "Ritz probes (B5), alone"
  pmset -g 2>/dev/null | grep -qE "SleepDisabled\s+1" || \
    echo "!!! warning: sleep is not disabled (pmset disablesleep); keep the lid open"
  python3 freefem/pcb/run_pcb_benchmark.py ritz --suite "$SUITE" --workers 1 --timeout 7200 --out "$RITZ" ||
    echo "!!! ritz: some probes failed (see above); continuing"
}

stage_ritzsum() {
  step "Ritz summary -> $DEST"
  python3 freefem/pcb/ritz_features.py summarize --host "$HOST" --src "$RITZ" --iters "$ITERS" \
    --out "$DEST" || die "ritzsum"
}

stages=${*:-regress features featsum ritz ritzsum}
mkdir -p "$FEAT" "$RITZ"
for s in $stages; do "stage_$s"; done
step "done: $stages"
