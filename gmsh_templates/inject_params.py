#!/usr/bin/env python3
"""
Gmsh .geo template parameter injection script

Usage:
  python inject_params.py --case case1A --param-set standard --output case1A_std.geo
  python inject_params.py -c case2B -p medium_iris -o case2B_medium.geo
  python inject_params.py --list-cases
  python inject_params.py --list-params case1A
  python inject_params.py --list-all
"""

import json
import re
import sys
import os
from pathlib import Path
from argparse import ArgumentParser

# Get script directory
SCRIPT_DIR = Path(__file__).parent
PARAMS_FILE = SCRIPT_DIR / "case_parameters.json"
TEMPLATES_DIR = SCRIPT_DIR

def load_parameters():
    """Load case parameters from JSON file."""
    with open(PARAMS_FILE, 'r') as f:
        return json.load(f)

def find_template(case_name, cases_dict):
    """Find template file path for given case."""
    if case_name not in cases_dict:
        return None
    template_name = cases_dict[case_name]["template"]
    template_path = TEMPLATES_DIR / template_name
    return template_path if template_path.exists() else None

def substitute_parameters(geo_content, params):
    """Substitute parameter values in .geo content."""
    # Pattern: variable_name = value; or variable_name = value
    # We look for lines like: lambda0 = 1.0;
    
    for param_name, param_value in params.items():
        # Handle different value types
        if isinstance(param_value, float):
            value_str = str(param_value)
        elif isinstance(param_value, int):
            value_str = str(param_value)
        else:
            value_str = str(param_value)
        
        # Replace pattern: param_name = anything;
        # This regex matches: word = (number or expression);
        pattern = rf'^(\s*{param_name}\s*=\s*)([^;]+)(;)'
        replacement = rf'\g<1>{value_str}\g<3>'
        
        geo_content = re.sub(pattern, replacement, geo_content, flags=re.MULTILINE)
    
    return geo_content

def inject_params(case_name, param_set_name, output_path=None, cases_dict=None):
    """Main function to inject parameters."""
    
    if cases_dict is None:
        cases_dict = load_parameters()
    
    # Validate case
    if case_name not in cases_dict:
        print(f"Error: Unknown case '{case_name}'", file=sys.stderr)
        print(f"Available cases: {', '.join(cases_dict.keys())}", file=sys.stderr)
        return False
    
    case_def = cases_dict[case_name]
    param_sets = case_def.get("parameter_sets", {})
    
    # Validate param set
    if param_set_name not in param_sets:
        print(f"Error: Unknown parameter set '{param_set_name}' for case {case_name}", file=sys.stderr)
        print(f"Available sets: {', '.join(param_sets.keys())}", file=sys.stderr)
        return False
    
    # Find template
    template_path = find_template(case_name, cases_dict)
    if not template_path:
        print(f"Error: Template file not found for case {case_name}", file=sys.stderr)
        return False
    
    # Read template
    with open(template_path, 'r') as f:
        geo_content = f.read()
    
    # Get parameters for this set
    params = param_sets[param_set_name]
    
    # Substitute parameters
    new_content = substitute_parameters(geo_content, params)
    
    # Determine output path
    if output_path is None:
        param_set_safe = param_set_name.replace('/', '_')
        output_path = TEMPLATES_DIR / f"{case_name}_{param_set_safe}.geo"
    else:
        output_path = Path(output_path)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Generated: {output_path}")
    print(f"  Case: {case_name}")
    print(f"  Param set: {param_set_name} - {params.get('description', 'N/A')}")
    print(f"  Template: {template_path.name}")
    
    return True

def list_cases(cases_dict):
    """List all available cases."""
    print("Available Cases:")
    print("=" * 80)
    for case_name in sorted(cases_dict.keys()):
        case_def = cases_dict[case_name]
        desc = case_def.get("description", "N/A")
        num_sets = len(case_def.get("parameter_sets", {}))
        print(f"  {case_name:6s}  {desc:50s}  [{num_sets} param sets]")

def list_params(case_name, cases_dict):
    """List parameter sets for a case."""
    if case_name not in cases_dict:
        print(f"Error: Unknown case '{case_name}'", file=sys.stderr)
        return
    
    case_def = cases_dict[case_name]
    desc = case_def.get("description", "N/A")
    param_sets = case_def.get("parameter_sets", {})
    
    print(f"Parameter Sets for {case_name}: {desc}")
    print("=" * 80)
    
    for set_name in sorted(param_sets.keys()):
        set_def = param_sets[set_name]
        set_desc = set_def.get("description", "N/A")
        params = {k: v for k, v in set_def.items() if k != "description"}
        
        print(f"\n  {set_name}:")
        print(f"    Description: {set_desc}")
        print(f"    Parameters:")
        for pname, pval in sorted(params.items()):
            print(f"      {pname:15s} = {pval}")

def list_all(cases_dict):
    """List all cases and parameter sets."""
    print("All Cases and Parameter Sets")
    print("=" * 80)
    
    for case_name in sorted(cases_dict.keys()):
        case_def = cases_dict[case_name]
        desc = case_def.get("description", "N/A")
        param_sets = case_def.get("parameter_sets", {})
        
        print(f"\n{case_name}: {desc}")
        print(f"  Parameter Sets ({len(param_sets)}):")
        
        for set_name in sorted(param_sets.keys()):
            set_def = param_sets[set_name]
            set_desc = set_def.get("description", "N/A")
            print(f"    • {set_name:30s} - {set_desc}")

def export_param_sets_csv(cases_dict, case_name=None):
    """Export parameter set names as CSV for shell scripting."""
    if case_name:
        if case_name not in cases_dict:
            return
        param_sets = cases_dict[case_name].get("parameter_sets", {})
        for set_name in sorted(param_sets.keys()):
            print(set_name)
    else:
        for cn in sorted(cases_dict.keys()):
            print(cn)

def export_cases_csv(cases_dict):
    """Export case names as CSV for shell scripting."""
    for case_name in sorted(cases_dict.keys()):
        print(case_name)

def main():
    parser = ArgumentParser(description="Inject parameters into Gmsh .geo templates")
    
    # Subcommands
    group = parser.add_mutually_exclusive_group(required=False)
    
    # Inject mode
    parser.add_argument('-c', '--case', type=str, help='Case name (e.g., 1A, 2B, 3F)')
    parser.add_argument('-p', '--param-set', type=str, dest='param_set', help='Parameter set name')
    parser.add_argument('-o', '--output', type=str, help='Output .geo file path')
    
    # List modes
    group.add_argument('--list-cases', action='store_true', help='List all available cases')
    group.add_argument('--list-params', type=str, metavar='CASE', help='List parameter sets for a case')
    group.add_argument('--list-all', action='store_true', help='List all cases and parameter sets')
    
    # Export modes (for shell scripting)
    group.add_argument('--export-cases', action='store_true', help='Export case names (one per line, for scripting)')
    group.add_argument('--export-params', type=str, metavar='CASE', help='Export param set names for case (one per line, for scripting)')
    
    args = parser.parse_args()
    
    # Load parameters
    try:
        cases_dict = load_parameters()
    except FileNotFoundError:
        print(f"Error: Parameters file not found: {PARAMS_FILE}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse parameters file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle list modes
    if args.list_cases:
        list_cases(cases_dict)
        sys.exit(0)
    
    if args.list_params:
        list_params(args.list_params, cases_dict)
        sys.exit(0)
    
    if args.list_all:
        list_all(cases_dict)
        sys.exit(0)
    
    # Handle export modes (for shell scripting)
    if args.export_cases:
        export_cases_csv(cases_dict)
        sys.exit(0)
    
    if args.export_params:
        export_param_sets_csv(cases_dict, args.export_params)
        sys.exit(0)
    
    # Handle injection mode
    if not args.case or not args.param_set:
        parser.print_help()
        sys.exit(1)
    
    success = inject_params(args.case, args.param_set, args.output, cases_dict)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
