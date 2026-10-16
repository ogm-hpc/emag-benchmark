#!/bin/bash
# Run chain of the v1.0 records (docs/paper_plan.md B, docs/next_tasks.md M3) on
# the Mac M3 Pro: solver v1.0, every job alone (1 worker), stopping rule K_max
# per combination, all 112 sets (PCB Core, Extended, Challenge and the existing
# case1A-3F) x 11 standard combinations, plus mumps/direct references.
# The runner is resumable (finished results are skipped): a stopped chain is
# restarted with the same command.
#
#   caffeinate -i nohup bash freefem/pcb/chains/v1.sh > ~/v1.log 2>&1 &
#   bash freefem/pcb/chains/v1.sh iter summary       # some stages only
#
# Stages (in this order):
#   regress  regress (all PASS, else stop)
#   mesh     B1: PCB meshes of the 66 sets (gmsh 4.15.2); existing meshes are made
#            if missing; MD5 of the 112 meshes to $DEST/mesh_md5.txt
#   mumps    B2/B4: mumps/direct alone, solutions saved (references of B6)
#   iter     B3/B6: the 11 standard combinations alone; H(curl) error against
#            the saved references in the same run (--ref-solutions)
#   summary  docs/results_v1/mac_m3pro (results of solver 1.0 only)
# Estimate (paper_plan 4.5, 2026-10-05): mumps 1-2 h, iter 8-11 days.
# Keep the Mac on AC power; Wi-Fi may be off (checked 2026-10-05), but set it
# before starting and do not toggle it during the run.
# caffeinate -i does NOT prevent the lid-close (clamshell) sleep: on 2026-10-05
# the lid was closed 3 min into stage iter; the Mac slept and dark-woke all night,
# jobs were dropped ("host suspended") or ended in error (MPI_Finalize: OFI poll
# failed on the vanished network interface), and the timings were unusable.
# Keep the lid open, or disable sleep for the run:  sudo pmset -a disablesleep 1
# (afterwards: sudo pmset -a disablesleep 0).
set -u
cd "$(dirname "$0")/../../.."
export HWLOC_COMPONENTS=-gl
OUT=${OUT:-results/pcb_v1}
DEST=${DEST:-docs/results_v1/mac_m3pro}
SUITE=core,extended,challenge
GMSH_PY=${GMSH_PY:-$HOME/.venvs/pcbmesh/bin/python}   # Python with gmsh 4.15.2
R() { python3 freefem/pcb/run_pcb_benchmark.py run --out "$OUT" --suite "$SUITE" --workers 1 "$@"; }
step() { echo "=== $(date '+%F %T') $*"; }
die() { echo "!!! $*"; exit 1; }

stage_regress() {
  step "regress"
  python3 freefem/pcb/run_pcb_benchmark.py regress > "$OUT.regress.txt" 2>&1
  cat "$OUT.regress.txt"
  grep -qE '^([0-9]+)/\1 passed' "$OUT.regress.txt" || die "regress: not all PASS (output kept in $OUT.regress.txt)"
}

stage_mesh() {
  step "mesh: PCB $SUITE"
  "$GMSH_PY" gmsh_templates/pcb/generate_pcb_meshes.py --suite "$SUITE" || die "PCB meshes"
  [ "$(ls generated_meshes/mesh/case*.msh 2>/dev/null | wc -l)" -ge 46 ] || \
    python3 gmsh_templates/generate_all_meshes.py -o generated_meshes -p 6 || die "existing meshes"
  step "mesh: MD5 -> $DEST/mesh_md5.txt"
  mkdir -p "$DEST"
  R --list | python3 -c '
import sys, re, hashlib, pathlib
sets = []
for line in sys.stdin:
    m = re.match(r"\s+(case\w+):(\S+)\s", line) or re.match(r"\s+\S+:(\S+)\s", line)
    if not m:
        continue
    p = (pathlib.Path("generated_meshes/mesh") / f"{m.group(1)}_{m.group(2)}.msh") if m.lastindex == 2 \
        else pathlib.Path("generated_meshes/pcb/mesh") / f"{m.group(1)}.msh"
    if p not in sets:
        sets.append(p)
for p in sets:
    print(hashlib.md5(p.read_bytes()).hexdigest(), p)
' > "$DEST/mesh_md5.txt" || die "MD5"
  echo "$(wc -l < "$DEST/mesh_md5.txt") meshes"
}

stage_mumps() {
  step "mumps/direct (B2/B4), alone, solutions saved"
  R --combos mumps/direct --save-solutions || die "mumps"
}

stage_iter() {
  step "11 standard combinations (B3/B6), alone, K_max standard, H(curl) error"
  pmset -g 2>/dev/null | grep -qE "SleepDisabled\s+1" || \
    echo "!!! warning: sleep is not disabled (pmset disablesleep); keep the lid open"
  R --ref-solutions "$OUT" || die "iter"
}

stage_summary() {
  step "summary -> $DEST"
  python3 freefem/pcb/summarize_pcb_benchmark.py --out "$OUT" --dest "$DEST" || die "summary"
}

stages=${*:-regress mesh mumps iter summary}
mkdir -p "$OUT"
for s in $stages; do "stage_$s"; done
step "done: $stages"
