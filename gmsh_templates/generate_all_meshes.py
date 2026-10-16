#!/usr/bin/env python3
"""
Batch mesh generation for all Cases 1A-3F with parameter sweeps

Usage:
  python3 generate_all_meshes.py --output meshes/ [--parallel 4] [--verbose]
  python3 generate_all_meshes.py --cases case1A,case2B,case3F --output meshes/
  python3 generate_all_meshes.py --dry-run --list-only
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

# Get script directory
SCRIPT_DIR = Path(__file__).parent
PARAMS_JSON = SCRIPT_DIR / "case_parameters.json"
INJECT_SCRIPT = SCRIPT_DIR / "inject_params.py"

class MeshGenerator:
    def __init__(self, output_dir, gmsh_exe="gmsh", verbose=False, dry_run=False, mesh_timeout=1800):
        self.output_dir = Path(output_dir)
        self.gmsh_exe = gmsh_exe
        self.verbose = verbose
        self.dry_run = dry_run
        self.mesh_timeout = mesh_timeout
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        # Create output directory
        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.geo_dir = self.output_dir / "geo"
            self.mesh_dir = self.output_dir / "mesh"
            self.geo_dir.mkdir(exist_ok=True)
            self.mesh_dir.mkdir(exist_ok=True)
        else:
            self.geo_dir = self.output_dir / "geo"
            self.mesh_dir = self.output_dir / "mesh"
    
    def log(self, msg, level="INFO"):
        """Log message with timestamp."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {level:8s} {msg}")
    
    def load_cases(self):
        """Load case definitions from JSON."""
        try:
            with open(PARAMS_JSON, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Failed to load parameters: {e}", "ERROR")
            return None
    
    def generate_geo(self, case_name, param_set_name):
        """Generate .geo file using inject_params.py."""
        geo_filename = f"{case_name}_{param_set_name}.geo"
        geo_path = self.geo_dir / geo_filename
        
        if self.dry_run:
            self.log(f"[DRY-RUN] Would generate: {geo_path}")
            return geo_path
        
        try:
            result = subprocess.run(
                ["python3", str(INJECT_SCRIPT), "-c", case_name, "-p", param_set_name, "-o", str(geo_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.log(f"Failed to generate {geo_filename}: {result.stderr}", "ERROR")
                self.stats["errors"].append(f"inject_params failed for {case_name}:{param_set_name}")
                return None
            
            if geo_path.exists():
                self.log(f"Generated: {geo_path}")
                return geo_path
            else:
                self.log(f"Output file not created: {geo_path}", "ERROR")
                return None
        
        except subprocess.TimeoutExpired:
            self.log(f"Timeout generating {geo_filename}", "ERROR")
            return None
        except Exception as e:
            self.log(f"Exception generating {geo_filename}: {e}", "ERROR")
            return None
    
    def generate_mesh(self, geo_path):
        """Generate .msh from .geo using gmsh."""
        msh_path = self.mesh_dir / (geo_path.stem + ".msh")
        
        if self.dry_run:
            self.log(f"[DRY-RUN] Would mesh: {geo_path}")
            return msh_path
        
        if msh_path.exists():
            self.log(f"Mesh already exists, skipping: {msh_path}")
            self.stats["skipped"] += 1
            return msh_path
        
        try:
            self.log(f"Meshing: {geo_path.name} -> {msh_path.name}")
            
            result = subprocess.run(
                [self.gmsh_exe, str(geo_path), "-3", "-format", "msh2", "-o", str(msh_path)],
                capture_output=True,
                text=True,
                timeout=self.mesh_timeout
            )
            
            if result.returncode != 0:
                self.log(f"gmsh failed for {geo_path.name}: {result.stderr}", "ERROR")
                self.stats["errors"].append(f"gmsh failed for {geo_path.name}")
                return None
            
            if msh_path.exists():
                size_mb = msh_path.stat().st_size / (1024*1024)
                self.log(f"✓ Mesh created: {msh_path} ({size_mb:.1f} MB)")
                self.stats["success"] += 1
                return msh_path
            else:
                self.log(f"Mesh output not created: {msh_path}", "ERROR")
                return None
        
        except subprocess.TimeoutExpired:
            self.log(f"Timeout meshing {geo_path.name} (>{self.mesh_timeout}s)", "ERROR")
            self.stats["errors"].append(f"gmsh timeout for {geo_path.name}")
            return None
        except Exception as e:
            self.log(f"Exception meshing {geo_path.name}: {e}", "ERROR")
            return None
    
    def generate_all(self, cases_to_generate=None):
        """Generate all .geo and .msh files."""
        cases_dict = self.load_cases()
        if not cases_dict:
            return False
        
        # Filter cases if specified
        if cases_to_generate:
            filtered = {k: v for k, v in cases_dict.items() if k in cases_to_generate}
            if not filtered:
                self.log(f"No matching cases found for: {cases_to_generate}", "ERROR")
                return False
            cases_dict = filtered
        
        # Collect all (case, param_set) pairs
        tasks = []
        for case_name in sorted(cases_dict.keys()):
            param_sets = cases_dict[case_name].get("parameter_sets", {})
            for param_set_name in sorted(param_sets.keys()):
                tasks.append((case_name, param_set_name))
        
        self.stats["total"] = len(tasks)
        self.log(f"Will generate {len(tasks)} templates and meshes")
        
        if self.dry_run:
            for case_name, param_set_name in tasks:
                self.log(f"[DRY-RUN] {case_name}:{param_set_name}")
            return True
        
        # Generate sequentially or in parallel depending on gmsh availability
        for i, (case_name, param_set_name) in enumerate(tasks, 1):
            self.log(f"\n[{i}/{len(tasks)}] Case {case_name}:{param_set_name}")
            
            # Generate .geo
            geo_path = self.generate_geo(case_name, param_set_name)
            if not geo_path:
                self.stats["failed"] += 1
                continue
            
            # Generate .msh
            msh_path = self.generate_mesh(geo_path)
            if not msh_path:
                self.stats["failed"] += 1
        
        return True
    
    def generate_parallel(self, cases_to_generate=None, num_workers=4):
        """Generate meshes in parallel using ThreadPoolExecutor."""
        cases_dict = self.load_cases()
        if not cases_dict:
            return False
        
        # Filter cases
        if cases_to_generate:
            filtered = {k: v for k, v in cases_dict.items() if k in cases_to_generate}
            if not filtered:
                self.log(f"No matching cases found", "ERROR")
                return False
            cases_dict = filtered
        
        # Collect tasks
        tasks = []
        for case_name in sorted(cases_dict.keys()):
            param_sets = cases_dict[case_name].get("parameter_sets", {})
            for param_set_name in sorted(param_sets.keys()):
                tasks.append((case_name, param_set_name))
        
        self.stats["total"] = len(tasks)
        self.log(f"Will generate {len(tasks)} meshes (parallel, {num_workers} workers)")
        
        completed = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {}
            
            for case_name, param_set_name in tasks:
                geo_path = self.generate_geo(case_name, param_set_name)
                if geo_path:
                    future = executor.submit(self.generate_mesh, geo_path)
                    futures[future] = (case_name, param_set_name)
            
            for future in as_completed(futures):
                case_name, param_set_name = futures[future]
                try:
                    result = future.result()
                    if result:
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    self.log(f"Exception for {case_name}:{param_set_name}: {e}", "ERROR")
                    failed += 1
        
        self.stats["success"] = completed
        self.stats["failed"] = failed
        return True
    
    def print_summary(self):
        """Print generation summary."""
        print("\n" + "="*80)
        print("GENERATION SUMMARY")
        print("="*80)
        print(f"Total tasks:     {self.stats['total']}")
        print(f"Successful:      {self.stats['success']}")
        print(f"Failed:          {self.stats['failed']}")
        print(f"Skipped:         {self.stats['skipped']}")
        
        if self.stats["errors"]:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:10]:
                print(f"  - {error}")
            if len(self.stats["errors"]) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")
        
        print(f"\nOutput directory: {self.output_dir}")
        if not self.dry_run:
            geo_count = len(list(self.geo_dir.glob("*.geo")))
            mesh_count = len(list(self.mesh_dir.glob("*.msh")))
            print(f"Generated .geo files:  {geo_count}")
            print(f"Generated .msh files:  {mesh_count}")
        
        print("="*80)

def main():
    parser = ArgumentParser(description="Generate meshes for all benchmark cases")
    
    parser.add_argument("-o", "--output", type=str, default="./generated_meshes",
                        help="Output directory for .geo and .msh files")
    parser.add_argument("-c", "--cases", type=str, default=None,
                        help="Comma-separated list of cases to generate (e.g., 'case1A,case2B,case3F')")
    parser.add_argument("-g", "--gmsh", type=str, default="gmsh",
                        help="Path to gmsh executable")
    parser.add_argument("-p", "--parallel", type=int, default=1,
                        help="Number of parallel workers (default: 1, sequential)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without executing")
    parser.add_argument("--list-only", action="store_true",
                        help="List all cases and parameter sets, then exit")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Per-mesh gmsh timeout in seconds (default: 1800)")
    
    args = parser.parse_args()
    
    # Handle list-only
    if args.list_only:
        gen = MeshGenerator(args.output, gmsh_exe=args.gmsh, verbose=True)
        cases_dict = gen.load_cases()
        if not cases_dict:
            sys.exit(1)
        
        print("Available Cases and Parameter Sets")
        print("="*80)
        total = 0
        for case_name in sorted(cases_dict.keys()):
            param_sets = cases_dict[case_name].get("parameter_sets", {})
            print(f"\n{case_name}:")
            for param_set_name in sorted(param_sets.keys()):
                desc = param_sets[param_set_name].get("description", "N/A")
                print(f"  • {param_set_name:30s} - {desc}")
                total += 1
        print(f"\nTotal: {total} parameter sets across {len(cases_dict)} cases")
        sys.exit(0)
    
    # Parse cases filter
    cases_filter = None
    if args.cases:
        cases_filter = [c.strip() for c in args.cases.split(",")]
    
    # Create generator
    gen = MeshGenerator(args.output, gmsh_exe=args.gmsh, verbose=args.verbose,
                        dry_run=args.dry_run, mesh_timeout=args.timeout)
    
    # Generate meshes
    print(f"Starting mesh generation at {datetime.now()}")
    start_time = time.time()
    
    if args.parallel > 1:
        success = gen.generate_parallel(cases_to_generate=cases_filter, num_workers=args.parallel)
    else:
        success = gen.generate_all(cases_to_generate=cases_filter)
    
    elapsed = time.time() - start_time
    
    # Print summary
    gen.print_summary()
    print(f"Elapsed time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
