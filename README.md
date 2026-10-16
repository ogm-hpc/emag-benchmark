# emag-benchmark: iterative solver benchmark for high-frequency electromagnetic FEM

A benchmark for linear solvers of high-frequency (time-harmonic Maxwell) finite element analysis
with lowest-order Nédélec edge elements. It consists of 112 parameter sets (instances): 46 sets of
15 canonical problems (scattering, cavities and waveguides, multi-material) and 66 sets of 8
printed circuit board (PCB) problems with lumped ports. Each problem has a series of sets that
change one factor of difficulty at a time: frequency, electrical length, element size, material
contrast, loss, boundary conditions, flat elements and the distance to a resonance.

This repository holds the code that defines the benchmark (Gmsh templates, FreeFEM scripts, the
runner) and the baseline results of version 1.0. The meshes, the linear systems and the reference
solutions are released as data (below).

- Solver version: **1.0** (`PCB_SOLVER_VERSION` in `freefem/pcb/maxwell_pcb_solver.edp`).
- Data (all 112 sets: meshes, matrices, right-hand sides, reference solutions, baseline runs):
  Zenodo, <https://doi.org/10.5281/zenodo.23413640> (CC BY 4.0).
- Paper (in Japanese, with an English abstract): M. Ogino, *Construction of an Iterative Solver
  Benchmark for High-Frequency Electromagnetic Finite Element Analysis: Canonical Problems and
  Printed Circuit Boards*, submitted to Transactions of JSCES.

## Contents

| Path | Contents |
|---|---|
| `gmsh_templates/` | Gmsh templates and parameters of the canonical problems (`case_parameters.json`, `generate_all_meshes.py`) |
| `gmsh_templates/pcb/` | Gmsh templates of the PCB problems (`generate_pcb_meshes.py`) |
| `freefem/pcb/` | **The benchmark solver, version 1.0**: assembly (`maxwell_pcb_solver.edp`, `pcb_common.idp`, `pcb_port.idp`), preconditioners, the runner `run_pcb_benchmark.py`, the summary `summarize_pcb_benchmark.py`, the parameters of the PCB problems `pcb_case_parameters.json` and the export of the released data `release_data.py` |
| `freefem/` | Shared FreeFEM scripts (COCG, GMRES, preconditioners) used by `freefem/pcb/`, and the earlier solver of the canonical problems, against which `regress` checks `freefem/pcb/` |
| `pcb_problem_benchmark_settings.md` | Specification of the benchmark (Japanese) |
| `docs/formulation_and_algorithms.md` | Formulation and algorithms (Japanese) |
| `docs/pcb_usage.md` | How to run the suite (Japanese; some links point to development notes that are not in this repository) |
| `docs/results_v1/mac_m3pro/` | Baseline results of version 1.0 (`pcb_summary.csv`, `pcb_summary.md`), mesh MD5 sums (`mesh_md5.txt`), verification, mesh convergence, matrix features |

## Problems

| Problem | Configuration | Varied parameters | Sets (Core/Ext./Chal.) |
|---|---|---|---|
| case1A | PEC sphere scattering, UPML | electrical size, UPML thickness | 4 (1/3/0) |
| case1B | Dielectric sphere with Mie resonances, UPML | permittivity 4–25 | 4 (0/2/2) |
| case1C | Aperture-coupled cavity, UPML | aperture width | 3 (0/3/0) |
| case2A | Empty PEC cavity | distance to resonance | 2 (2/0/0) |
| case2B | Two chambers coupled by an iris | iris width, resonance | 4 (0/4/0) |
| case2C | Chambers coupled by a narrow slit | slit width, resonance | 4 (0/4/0) |
| case2D | Maze-shaped cavity | number of walls, resonance | 3 (0/3/0) |
| case2E | Waveguide with irises | number of irises | 2 (0/2/0) |
| case2F | TEAM 19 loaded cavity | rod material and diameter | 5 (0/5/0) |
| case3A | Two-layer dielectric cavity | permittivity contrast | 2 (1/1/0) |
| case3B | Multilayer dielectric cavity | number of layers | 2 (0/2/0) |
| case3C | Checkerboard, εr = 1/100 | number of cells | 3 (0/3/0) |
| case3D | High-permittivity rod array | array density | 2 (0/2/0) |
| case3E | Lossy inclusion in a cavity | loss tangent 0.01–1 | 3 (0/3/0) |
| case3F | Mosaic of four materials | contrast and loss | 3 (0/3/0) |
| P01 | Microstrip line | frequency, length, mesh, loss, conductor | 22 (3/19/0) |
| P02 | Thin-substrate microstrip | substrate thickness, solder resist | 4 (0/3/1) |
| P03 | Multilayer signal via | stub, return vias, via and antipad | 13 (3/10/0) |
| P04 | Multilayer board, permittivity jump | εr of alternate layers 1–100 | 4 (0/4/0) |
| P05 | Power/ground plane pair, PMC edges | frequency, gap, feed, layers, loss, mesh | 14 (3/11/0) |
| P06 | Microstrip over a slotted plane | slot length, stitching | 4 (0/4/0) |
| P07 | Differential via pair, 4 ports | asymmetry, frequency | 2 (0/1/1) |
| P08 | Parallel microstrips, 2N ports | number of lines N = 2, 4, 8 | 3 (0/3/0) |

Tiers: **Core** (13 sets, always evaluated), **Extended** (95), **Challenge** (4 sets on which at
most two of the standard combinations converged). The tier of a set is its `"suite"` in
`gmsh_templates/case_parameters.json` and `freefem/pcb/pcb_case_parameters.json`.

## Standard solver combinations (version 1.0)

Zero initial guess; converged when the true relative residual ‖b − Ax‖/‖b‖ ≤ 1e-8. A run stops at
convergence or at the iteration cap K_max; there is no time limit. One process, one thread.

| Combination | K_max | Remark |
|---|---|---|
| Gauss–Seidel + GMRES | 10,000 | forward sweep |
| SSOR + GMRES | 10,000 | |
| SSOR + COCG | 50,000 | |
| GAMG + GMRES | 10,000 | one V-cycle |
| GAMG + COCG | 50,000 | one V-cycle |
| Accelerated IC(0) + GMRES | 10,000 | α = 1.5 |
| Accelerated IC(0) + COCG | 50,000 | α = 1.5 |
| CSLP + GMRES | 3,000 | variable (inner GMRES), (β1, β2) = (1, 0.5) |
| HX + GMRES | 10,000 | variable, three terms |
| CSLP+HX + GMRES | 1,000 | variable, two terms |
| Nodal patch + COCG | 50,000 | additive |

GMRES: right preconditioning, restart 300, modified Gram–Schmidt (flexible GMRES for the variable
preconditioners). COCG is hand-written (PETSc's CG stops at the sign changes of indefinite systems).
The baseline results were measured on an Apple M3 Pro (18 GB, macOS 26.6) with FreeFEM 4.15,
complex PETSc 3.23.1 and MUMPS 5.7.3.

## Requirements

- FreeFEM 4.15 with complex PETSc (MUMPS; HYPRE is not used), as `FreeFem++-mpi` on the `PATH`
- Python 3.9 or later; NumPy and SciPy for `release_data.py` and the feature scripts
- Gmsh 4.15.2 (Python module `gmsh`) only to generate the meshes yourself

See [INSTALL.md](INSTALL.md).

## Usage

The benchmark is defined on the released meshes: Gmsh can produce slightly different meshes on
other machines or versions, and then the matrices differ. To solve the released linear systems,
download the sets from Zenodo, unpack them into one folder and pass it with `--release-dir`.

```bash
R="python3 freefem/pcb/run_pcb_benchmark.py run"
$R --suite core --release-dir emag_benchmark_v1.0 --list           # the jobs (no FreeFEM)
$R --suite core --release-dir emag_benchmark_v1.0 --out results/core   # 13 sets x 11 combinations
$R --sets P05-1,case2A:standard --combos npatch_asm/cocg --release-dir emag_benchmark_v1.0 --out results/try
$R --sets P05-1 --release-dir emag_benchmark_v1.0 --show-config P05-1:hx/gmres   # generated configuration
python3 freefem/pcb/summarize_pcb_benchmark.py --out results/core --dest results/core/summary
```

- Sets are named as in the data: `P05-1`, and `case2A:standard` for the canonical ones (folder
  `case2A_standard`). `--suite core,extended,challenge`, `--problems P01,case2A` and `--combos
  preset/krylov,...` select the jobs; the reference direct solve is `mumps/direct`.
- Results: `<out>/runs/*.json` (status, iterations, full residual history, times, peak memory,
  S-parameters of the PCB problems), and the environment in `<out>/meta.json`.
- Run one job at a time to compare times with the baseline: `--workers 1` (the default on Linux;
  on a Mac the default is the number of performance cores).

To generate the meshes instead (not identical to the released ones on other machines):

```bash
python3 gmsh_templates/pcb/generate_pcb_meshes.py --suite core        # generated_meshes/pcb/mesh/
python3 gmsh_templates/generate_all_meshes.py -o generated_meshes      # generated_meshes/mesh/
```

### Regression check

`regress` solves two canonical problems with `freefem/pcb/` and with the earlier solver in
`freefem/` and checks that the residual histories and solutions agree; it also checks the nodal
patch preconditioner against stored references. It needs the meshes of case1A and case2A in
`generated_meshes/mesh/` (`python3 gmsh_templates/generate_all_meshes.py -o generated_meshes -c
case1A,case2A`). The stored references depend on the machine (the mesh changes): on a new machine
run `regress --update-reference` once, then `regress`.

```bash
python3 freefem/pcb/run_pcb_benchmark.py regress
```

## Reporting results

A new solver can be compared with the baseline if it solves the same linear systems (the released
files, or the meshes of `--release-dir`) to the same criterion (true relative residual ≤ 1e-8 from a
zero initial guess). Report the iterations, the time to solution including the set-up, the peak
memory, the machine and whether the run reached a cap. A Challenge set solved by a new solver stays
in the Challenge tier.

## Citation

See [CITATION.cff](CITATION.cff). Please cite the paper and the data set (Zenodo DOI above).

## License

The code is released under the MIT License (see [LICENSE](LICENSE)). The data on Zenodo are
released under CC BY 4.0. FreeFEM (LGPL), PETSc (BSD) and Gmsh (GPL) are not included.
