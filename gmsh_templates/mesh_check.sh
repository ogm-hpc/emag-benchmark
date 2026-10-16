#!/bin/bash
# Mesh a list of .geo files and report per-file success/failure with gmsh's error output.
cd "$(dirname "$0")/../generated_meshes" || exit 1

for f in "$@"; do
  name=$(basename "$f" .geo)
  echo "=== $name ==="
  timeout 300 gmsh "$f" -3 -format msh2 -o "mesh/$name.msh" > "mesh/$name.log" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "OK rc=$rc"
  else
    echo "FAIL rc=$rc"
    tail -20 "mesh/$name.log"
  fi
done
