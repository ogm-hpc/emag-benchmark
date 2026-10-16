# Installation

The runner calls `FreeFem++-mpi` (FreeFEM with PETSc), in one process. The scripts load the
complex PETSc build (`load "PETSc-complex"`) and use MUMPS; HYPRE is not used.

| | Baseline (version 1.0 records) | Also tested |
|---|---|---|
| Machine | Apple M3 Pro, 18 GB, macOS 26.6 | Apple M1 (macOS); Windows 11 + WSL (Ubuntu) |
| FreeFEM | 4.15 | 4.15 |
| PETSc (complex) | 3.23.1 | 3.24.1 (M1), 3.22.2 (WSL) |
| Gmsh | 4.15.2 | 4.15.2 |
| Python | 3.9 | 3.12 (WSL) |

Iteration counts can differ slightly between PETSc versions and machines (for example by about
0.1% for GAMG); compare with the baseline only on the released meshes.

## FreeFEM with complex PETSc

### macOS

Install the FreeFEM 4.15 package for macOS from <https://freefem.org> (it contains real and complex
PETSc with MUMPS) and put `FreeFem++-mpi` on the `PATH`.

### Linux (and WSL)

Build FreeFEM 4.15 from source with its PETSc (real and complex, with MUMPS), following the FreeFEM
documentation (<https://doc.freefem.org>, "Compilation"):

```bash
git clone --branch v4.15 https://github.com/FreeFem/FreeFem-sources.git
cd FreeFem-sources
autoreconf -i
./configure --enable-download --without-hdf5 --prefix=/usr/local
cd 3rdparty/ff-petsc && make petsc-slepc && cd ../..   # real and complex PETSc
./reconfigure
make -j 8 && sudo make install
```

On WSL, set `export HWLOC_COMPONENTS=-gl` before running FreeFEM: otherwise Open MPI can stop at
start-up when the WSLg X server does not answer.

### Check

```bash
python3 freefem/pcb/run_pcb_benchmark.py regress --update-reference   # once on a new machine
python3 freefem/pcb/run_pcb_benchmark.py regress           # all PASS
```

`regress` needs the meshes of case1A and case2A (below). It also runs the small test of the nodal
patch preconditioner (`freefem/pcb/test_npatch_toy.edp`).

## Python

The runner and the summary use the standard library only. `freefem/pcb/release_data.py` and the
matrix-feature scripts need NumPy and SciPy:

```bash
python3 -m pip install numpy scipy
```

## Gmsh (only to generate meshes)

The benchmark is defined on the released meshes (Zenodo). To generate meshes yourself:

```bash
python3 -m venv ~/.venvs/pcbmesh
~/.venvs/pcbmesh/bin/pip install gmsh==4.15.2
~/.venvs/pcbmesh/bin/python gmsh_templates/pcb/generate_pcb_meshes.py --suite core
python3 gmsh_templates/generate_all_meshes.py -o generated_meshes -c case1A,case2A   # needs the gmsh executable
```

Meshes generated on another machine or with another Gmsh version can differ slightly from the
released ones (by about 1% in the number of edges), and then the linear systems differ.
