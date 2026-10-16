# Gmsh minimal templates for Case 1A to 3F

This folder contains one minimal .geo template per benchmark case, plus parameter injection scripts for batch processing.

## Design rules (2026-09-28)

- Every mesh resolves the LOCAL wavelength lambda0/sqrt(eps_r) with >= 6 points: `lc = lambda_local / 8`
  (gmsh's mean edge length comes out ~1.3 lc). Check with `python3 freefem/mesh_quality.py`.
- Size budget ~0.13M Edge03d DOF per mesh (one solve incl. setup must fit 600 s; see BENCHMARK_HANDOVER.md).
- Per-material refinement uses `Field = Constant` with `VolumesList` and `IncludeBoundary = 1`.
  Do NOT combine `MeshSize{PointsOf{...}}` with `Mesh.CharacteristicLengthFromPoints = 0`: gmsh then ignores
  the point sizes (this silently produced uniform coarse meshes for case3C/3D/3F before 2026-09-28).
- Open cases (1A/1B/1C) tag only the outer face of the PML shell as `OuterBoundary` (PEC-backed in the solver).
- `lambda0` also scales template geometry: to move the operating frequency without touching the mesh, set
  `k0` (or `k0R` for 1A/1B) in case_parameters.json instead.
- `generate_all_meshes.py` skips meshes that already exist: delete the .msh files you want regenerated.

## Files

### Templates
- Case 1A: case1A_pec_sphere_scattering.geo
- Case 1B: case1B_high_eps_sphere_mie.geo
- Case 1C: case1C_aperture_cavity_scattering.geo
- Case 2A: case2A_empty_pec_cavity.geo
- Case 2B: case2B_two_chamber_iris.geo
- Case 2C: case2C_ultra_narrow_slit.geo
- Case 2D: case2D_maze_cavity.geo
- Case 2E: case2E_iris_waveguide.geo
- Case 3A: case3A_two_layer_dielectric_cavity.geo
- Case 3B: case3B_multilayer_dielectric.geo
- Case 3C: case3C_checkerboard.geo
- Case 3D: case3D_high_eps_rod_array.geo
- Case 3E: case3E_lossy_inclusion_cavity.geo
- Case 3F: case3F_mosaic_material_cavity.geo

### Parameter Injection
- `case_parameters.json` — Parameter definitions for all cases and parameter sets
- `inject_params.py` — Python script for parameter substitution
- `inject_params.sh` — Bash wrapper for batch processing (WSL-friendly)

## Quick Start

### 1. List available cases
```bash
python3 inject_params.py --list-cases
# or
./inject_params.sh list-cases
```

### 2. List parameter sets for a case
```bash
python3 inject_params.py --list-params case1A
# or
./inject_params.sh list-params case1A
```

### 3. Generate a single .geo file
```bash
python3 inject_params.py -c case1A -p standard -o case1A_std.geo
# or
./inject_params.sh inject case1A standard case1A_std.geo
```

### 4. Batch generate all parameter sets for a case
```bash
./inject_params.sh batch-case case2B output_dir/
```

### 5. Batch generate all cases and parameter sets
```bash
./inject_params.sh batch-all generated_meshes/
```

## Generate mesh (example)
After parameter injection, generate the mesh with gmsh:
```bash
gmsh case1A_std.geo -3 -format msh2 -o case1A_std.msh
```

## Python API Usage
```python
from inject_params import load_parameters, inject_params

cases = load_parameters()
inject_params('case1A', 'standard', 'output/case1A.geo', cases)
```

## Notes
- These are minimal templates for geometry and region tagging.
- Physical group names are set up for FreeFEM++ integration.
- Mesh sizes (lc, lcNear, lcFar) are tuned as defaults; adjust as needed for your solver.
- Some complex cases (2D, 2E, 3D, 3F) use deterministic spatial indexing to avoid randomness in geometry generation.

