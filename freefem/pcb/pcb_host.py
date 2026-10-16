"""Machine profile of the PCB benchmark runs (docs/pcb_handoff.md 3.1).

The WSL machine (Windows 11 + WSL, 16 cores, 31 GB) is the reference: its
results are the records in docs/pcb_results/ and its defaults are unchanged.
Macs are secondary machines: their results are not compared with WSL (the
meshes differ slightly between platforms and the computers differ), they are
published under docs/pcb_results/<host>/ and never over the WSL records.
From solver v1.0 on (docs/paper_plan.md A4) the records of the papers are the
Mac M3 Pro results in docs/results_v1/mac_m3pro/; docs/pcb_results/ is kept as
the history of the development.

On a Mac:
  * default number of parallel jobs = number of performance cores
    (hw.perflevel0.physicalcpu: Apple M1 4, Apple M3 Pro 5 or 6);
  * memory budget = MEM_FRACTION x physical memory. The peak memory of a job is
    estimated from the WSL records (peakRssGb of docs/pcb_results/*.csv, the
    largest over all rows of the same parameter set and combination) times
    MEM_MARGIN. Jobs whose estimate exceeds the budget are excluded, and the
    running jobs together stay within it (MemoryGate).
"""
from __future__ import annotations

import csv
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WSL_RESULTS = ROOT / "docs" / "pcb_results"   # pre-v1.0 records (development history, task A4)
V1_RESULTS = ROOT / "docs" / "results_v1"      # v1.0 records: V1_RESULTS / V1_RECORD_HOST only
V1_RECORD_HOST = "mac_m3pro"
V1_SOLVER_VERSION = "1.0"
MEM_FRACTION = 0.75   # share of the physical memory given to FreeFEM jobs
MEM_MARGIN = 1.2      # WSL peak RSS -> estimate on the Mac (other PETSc version, footprint vs RSS)


@dataclass
class Host:
    name: str               # "wsl" (reference) or "mac_<chip>", e.g. mac_m1, mac_m3pro
    label: str
    reference: bool         # True: results are the docs/pcb_results/ records
    perf_cores: int | None = None
    ram_gb: float | None = None

    @property
    def mem_budget_gb(self) -> float | None:
        return None if self.reference or not self.ram_gb else round(MEM_FRACTION * self.ram_gb, 1)

    def workers(self, reference_default: int) -> int:
        return reference_default if self.reference or not self.perf_cores else self.perf_cores

    @property
    def docs_dir(self) -> Path:
        return WSL_RESULTS if self.reference else WSL_RESULTS / self.name


def _sysctl(key: str) -> str:
    return subprocess.run(["sysctl", "-n", key], capture_output=True, text=True).stdout.strip()


def detect() -> Host:
    if sys.platform != "darwin":
        return Host("wsl", "Windows 11 + WSL (reference)", True)
    brand = _sysctl("machdep.cpu.brand_string") or "unknown"          # "Apple M3 Pro"
    chip = re.sub(r"[^a-z0-9]", "", brand.lower().replace("apple", "")) or "unknown"
    perf = _sysctl("hw.perflevel0.physicalcpu") or _sysctl("hw.physicalcpu")
    mem = _sysctl("hw.memsize")
    return Host(f"mac_{chip}", brand, False, int(perf) if perf.isdigit() else None,
                int(mem) / 1024 ** 3 if mem.isdigit() else None)


def _run(cmd: list, cwd: Path | None = None) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=cwd).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _petsc_version(prefixes: list) -> str | None:
    """PETSc version from petscversion.h of the complex PETSc FreeFEM uses."""
    cands = [Path(os.environ["PETSC_DIR"]) / "include"] if os.environ.get("PETSC_DIR") else []
    for p in prefixes:
        cands += [p / "ff-petsc" / "c" / "include", p.parent / "ff-petsc" / "c" / "include"]
    cands.append(Path("/usr/local/ff-petsc/c/include"))
    for inc in cands:
        h = inc / "petscversion.h"
        if h.is_file():
            v = dict(re.findall(r"#define\s+PETSC_VERSION_(MAJOR|MINOR|SUBMINOR)\s+(\d+)", h.read_text(errors="ignore")))
            if len(v) == 3:
                return f"{v['MAJOR']}.{v['MINOR']}.{v['SUBMINOR']}"
    return None


def environment(freefem_bin: str) -> dict:
    """Execution environment of a run (settings 13.4), best effort: missing
    items are None. FreeFEM's version is the lib/ff++/<version> directory of
    its installation, PETSc's from petscversion.h."""
    exe = shutil.which(freefem_bin)
    exe_real = Path(exe).resolve() if exe else None
    prefixes = [exe_real.parent.parent] if exe_real else []
    ff_ver = None
    for p in prefixes:
        vers = sorted(d.name for d in (p / "lib" / "ff++").glob("*") if d.is_dir()) if (p / "lib" / "ff++").is_dir() else []
        ff_ver = vers[-1] if vers else None
    cpu = _sysctl("machdep.cpu.brand_string") if sys.platform == "darwin" else ""
    mem_gb = None
    if not cpu and Path("/proc/cpuinfo").is_file():
        m = re.search(r"model name\s*:\s*(.+)", Path("/proc/cpuinfo").read_text(errors="ignore"))
        cpu = m.group(1).strip() if m else ""
    if sys.platform == "darwin":
        mem = _sysctl("hw.memsize")
        mem_gb = round(int(mem) / 1024 ** 3, 1) if mem.isdigit() else None
    elif Path("/proc/meminfo").is_file():
        m = re.search(r"MemTotal:\s*(\d+)", Path("/proc/meminfo").read_text())
        mem_gb = round(int(m.group(1)) / 1024 ** 2, 1) if m else None
    commit = _run(["git", "rev-parse", "HEAD"], ROOT) or None
    dirty = bool(_run(["git", "status", "--porcelain", "--untracked-files=no"], ROOT)) if commit else None
    return dict(os=platform.platform(), cpu=cpu or None, cpu_count=os.cpu_count(), memory_gb=mem_gb,
                python=platform.python_version(), freefem=str(exe_real) if exe_real else freefem_bin,
                freefem_version=ff_ver, petsc_version=_petsc_version(prefixes),
                mpi_processes=1, omp_num_threads=os.environ.get("OMP_NUM_THREADS"),
                hwloc_components=os.environ.get("HWLOC_COMPONENTS"),
                git_commit=commit, git_dirty=dirty, command_line=" ".join(sys.argv))


def wsl_peak_rss() -> dict:
    """{(paramSet, 'preset/krylov'): largest WSL peak RSS [GB]} over all recorded runs."""
    peak = {}
    for name in ("pcb_summary.csv", "pcb_summary_variants.csv"):
        path = WSL_RESULTS / name
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                try:
                    v = float(r["peakRssGb"])
                except (KeyError, ValueError):
                    continue
                k = (r["paramSet"], f"{r['preset']}/{r['krylov']}")
                peak[k] = max(peak.get(k, 0.0), v)
    return peak


def estimate_gb(peak: dict, pset: str, combo: str) -> tuple:
    """(estimate [GB] or None, source): the WSL record of the set and
    combination, else the largest WSL record of the set, else unknown."""
    if (pset, combo) in peak:
        return MEM_MARGIN * peak[(pset, combo)], "wsl"
    same_set = [v for (s, _), v in peak.items() if s == pset]
    if same_set:
        return MEM_MARGIN * max(same_set), "wsl-set-max"
    return None, "unknown"


class MemoryGate:
    """Admits jobs in submission order (ticket) while the sum of their
    estimates stays within the budget; an unknown estimate takes the whole
    budget (the job runs alone)."""

    def __init__(self, budget_gb: float):
        self.budget, self.used, self.next = budget_gb, 0.0, 0
        self.cv = threading.Condition()

    def acquire(self, ticket: int, gb: float | None) -> float:
        need = self.budget if gb is None else min(gb, self.budget)
        with self.cv:
            self.cv.wait_for(lambda: self.next == ticket and self.used + need <= self.budget + 1e-9)
            self.used += need
            self.next += 1
            self.cv.notify_all()
        return need

    def release(self, gb: float) -> None:
        with self.cv:
            self.used -= gb
            self.cv.notify_all()
