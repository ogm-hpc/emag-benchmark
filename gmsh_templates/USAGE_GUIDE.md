# Parameter Injection Script Usage Guide

## Overview
The parameter injection system allows you to generate multiple `.geo` template files with different parameter values for performance studies and sweeps.

## Quick Reference

### Single Generation
```bash
python3 inject_params.py -c case1A -p standard -o case1A_std.geo
```

### Batch Generation (Single Case)
```bash
./inject_params.sh batch-case case1A output_dir/
```

### Batch Generation (All Cases)
```bash
./inject_params.sh batch-all generated_cases/
```

## Parameter Sets Available

### Case 1A (PEC Sphere Scattering)
- **standard**: k0*R = 2π, tPML = 1.0 λ₀
- **high_freq**: k0*R = 16π, finer mesh
- **thick_pml**: tPML = 2.0 λ₀
- **thin_pml**: tPML = 0.5 λ₀

### Case 1B (High-ε Sphere Mie Scattering)
- **mie_low_eps**: ε_r = 4, k0*R = 10
- **mie_mid_eps**: ε_r = 10, k0*R = 12
- **mie_high_eps**: ε_r = 30, k0*R = 15
- **mie_ultra_high_eps**: ε_r = 80, k0*R = 18

### Case 1C (Aperture Cavity Scattering)
- **narrow_aperture**: w = 0.1 λ₀
- **medium_aperture**: w = 0.2 λ₀
- **wide_aperture**: w = 0.5 λ₀

### Case 2A (Empty PEC Cavity)
- **standard**: Lx = 4λ₀, Ly = 2λ₀, Lz = 2λ₀

### Case 2B (Two-Chamber Cavity with Iris)
- **narrow_iris**: w = 0.02 λ₀ (high-Q resonance)
- **medium_iris**: w = 0.1 λ₀
- **wide_iris**: w = 0.5 λ₀

### Case 2C (Ultra-Narrow Slit)
- **narrow_slit**: g = λ₀/100
- **medium_slit**: g = λ₀/50
- **wide_slit**: g = λ₀/20

### Case 2D (Maze-like Cavity)
- **few_walls**: N = 5, ropen = 5%
- **many_walls**: N = 20, ropen = 20%

### Case 2E (Iris-Loaded Waveguide)
- **sparse_irises**: N = 5, p = 1.0 λ₀
- **dense_irises**: N = 20, p = 0.5 λ₀

### Case 3A (Two-Layer Dielectric)
- **low_contrast**: κ = 2
- **high_contrast**: κ = 100

### Case 3B (Multilayer Dielectric)
- **few_layers**: N = 10
- **many_layers**: N = 50

### Case 3C (3D Checkerboard)
- **coarse_check**: Nc = 4 (64 cells)
- **medium_check**: Nc = 8 (512 cells)
- **fine_check**: Nc = 16 (4096 cells)

### Case 3D (High-ε Rod Array)
- **sparse_array**: 5×5 rods
- **dense_array**: 10×10 rods

### Case 3E (Lossy Inclusion)
- **low_loss**: tan(δ) = 0.01
- **medium_loss**: tan(δ) = 0.1
- **high_loss**: tan(δ) = 1.0

### Case 3F (Mosaic Material)
- **low_contrast_no_loss**: κ = 10, v_loss = 0%
- **high_contrast_with_loss**: κ = 100, v_loss = 10%
- **ultra_contrast_high_loss**: κ = 1000, v_loss = 20%

## Scripting Examples

### Python API
```python
from inject_params import inject_params, load_parameters

cases = load_parameters()

# Generate single case
inject_params('case1A', 'standard', 'case1A_std.geo', cases)

# Loop over multiple parameter sets
for param_set in ['low_contrast', 'high_contrast']:
    inject_params('case3A', param_set, f'case3A_{param_set}.geo', cases)
```

### Shell Loop (WSL/Linux)
```bash
#!/bin/bash
for case in case1A case2B case3F; do
    python3 inject_params.py --export-params "$case" | while read param_set; do
        python3 inject_params.py -c "$case" -p "$param_set" \
            -o "generated/${case}_${param_set}.geo"
    done
done
```

### Generate and Mesh (Example)
```bash
# Generate all Case 2B variants
./inject_params.sh batch-case case2B geo_files/

# Generate meshes
cd geo_files/
for f in case2B_*.geo; do
    gmsh "$f" -3 -format msh2 -o "${f%.geo}.msh"
done
```

## Generated .geo Characteristics

| Case | Templates | Total Files | Description |
|---|---|---|---|
| 1A | 4 | 4 | PML thickness sweep (0.5-2.0 λ₀) |
| 1B | 4 | 4 | ε_r sweep (4, 10, 30, 80) |
| 1C | 3 | 3 | Aperture width sweep (0.1-0.5 λ₀) |
| 2A | 1 | 1 | Baseline cavity |
| 2B | 3 | 3 | Iris width for Q-factor studies |
| 2C | 3 | 3 | Slit width (λ₀/100 to λ₀/20) |
| 2D | 2 | 2 | Wall count & open ratio |
| 2E | 2 | 2 | Iris density in waveguide |
| 3A | 2 | 2 | Permittivity contrast |
| 3B | 2 | 2 | Layer count (10-50) |
| 3C | 3 | 3 | Checkerboard density (4×4 to 16×16) |
| 3D | 2 | 2 | Rod array density (5×5 to 10×10) |
| 3E | 3 | 3 | Loss tangent sweep |
| 3F | 3 | 3 | Contrast + loss combinations |
| **Total** | — | **36** | **All parameter combinations** |

## Performance Notes

- **Batch generation time**: ~30 seconds for all 36 templates
- **Output size**: ~120 KB (uncompressed .geo text files)
- **Template size**: 2-10 KB per .geo file
- **Mesh generation**: Parallelizable with GNU parallel or xargs

## Customization

To add new parameter sets:
1. Edit `case_parameters.json`
2. Add new entries under the desired case's `parameter_sets`
3. Include all parameters used in the template .geo file

Example:
```json
"my_custom_set": {
  "description": "Custom parameter configuration",
  "lambda0": 1.0,
  "L": 12.0,
  "R": 1.5,
  "tPML": 1.5,
  "lc": 0.1
}
```

Then inject with:
```bash
python3 inject_params.py -c case1A -p my_custom_set -o case1A_custom.geo
```
