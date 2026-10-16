#!/bin/bash
# Launch the full benchmark campaign detached from the terminal (resumable:
# finished jobs are skipped). Progress: results/benchmark/campaign.log
#   bash freefem/start_campaign.sh [workers]
cd "$(dirname "$0")/.."
mkdir -p results/benchmark
{
  echo "host: $(lscpu | grep -E 'Model name|モデル名' | head -1 | sed 's/.*: *//')"
  echo "freefem: $(FreeFem++-mpi -nw -v 0 /dev/null 2>&1 | grep -o 'FreeFem++ v[0-9.]*' | head -1)"
  echo "gmsh: $(gmsh --version 2>&1)"
  echo "started: $(date '+%F %T')"
} > results/benchmark/environment.txt
setsid nohup python3 freefem/run_benchmark.py --workers "${1:-5}" --budget 600 \
    --out results/benchmark >> results/benchmark/campaign.log 2>&1 < /dev/null &
echo "campaign pid $!"
