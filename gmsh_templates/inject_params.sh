#!/bin/bash
# Parameter injection wrapper for Gmsh .geo templates
# Usage: 
#   ./inject_params.sh inject 1A standard [output.geo]
#   ./inject_params.sh batch-case 1A [output_dir]
#   ./inject_params.sh batch-all [output_dir]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/inject_params.py"
PARAMS_JSON="$SCRIPT_DIR/case_parameters.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Error: Python script not found: $PYTHON_SCRIPT${NC}" >&2
    exit 1
fi

# Display usage
usage() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
  inject <case> <param-set> [output_file]
    Generate a single .geo file
    Example: $0 inject case1A standard case1A_std.geo

  batch-case <case> [output_dir]
    Generate all parameter sets for a case
    Example: $0 batch-case case2B output/

  batch-all [output_dir]
    Generate all cases and parameter sets
    Example: $0 batch-all output/

  list-cases
    List all available cases

  list-params <case>
    List parameter sets for a case

  list-all
    List all cases and parameter sets

  help
    Show this message
EOF
}

# Extract parameter set names from JSON
get_param_sets() {
    local case=$1
    python3 "$PYTHON_SCRIPT" --export-params "$case" 2>/dev/null
}

# Get all case names
get_cases() {
    python3 "$PYTHON_SCRIPT" --export-cases 2>/dev/null
}

# Inject single parameter set
inject_single() {
    local case=$1
    local param_set=$2
    local output=$3
    
    if [ -z "$case" ] || [ -z "$param_set" ]; then
        echo -e "${RED}Error: case and param-set required${NC}" >&2
        usage
        exit 1
    fi
    
    if [ -z "$output" ]; then
        python3 "$PYTHON_SCRIPT" -c "$case" -p "$param_set"
    else
        python3 "$PYTHON_SCRIPT" -c "$case" -p "$param_set" -o "$output"
    fi
}

# Batch inject for a single case
batch_case() {
    local case=$1
    local output_dir=${2:-.}
    
    if [ -z "$case" ]; then
        echo -e "${RED}Error: case required${NC}" >&2
        exit 1
    fi
    
    # Create output directory if needed
    mkdir -p "$output_dir"
    
    # Get parameter sets
    local param_sets=$(get_param_sets "$case")
    
    if [ -z "$param_sets" ]; then
        echo -e "${RED}Error: Could not determine parameter sets for case $case${NC}" >&2
        exit 1
    fi
    
    echo -e "${GREEN}Generating .geo files for case $case:${NC}"
    
    local count=0
    for param_set in $param_sets; do
        local output="$output_dir/${case}_${param_set}.geo"
        echo -n "  $param_set ... "
        python3 "$PYTHON_SCRIPT" -c "$case" -p "$param_set" -o "$output" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
            count=$((count + 1))
        else
            echo -e "${RED}✗${NC}"
        fi
    done
    
    echo -e "${GREEN}Generated $count .geo files in $output_dir${NC}"
}

# Batch inject for all cases
batch_all() {
    local output_dir=${1:-.}
    
    # Create output directory if needed
    mkdir -p "$output_dir"
    
    # Get all cases
    local cases=$(get_cases)
    
    if [ -z "$cases" ]; then
        echo -e "${RED}Error: Could not determine available cases${NC}" >&2
        exit 1
    fi
    
    echo -e "${GREEN}Generating .geo files for all cases:${NC}"
    
    local total=0
    for case in $cases; do
        echo -e "${YELLOW}[Case $case]${NC}"
        
        local param_sets=$(get_param_sets "$case")
        
        for param_set in $param_sets; do
            local output="$output_dir/${case}_${param_set}.geo"
            python3 "$PYTHON_SCRIPT" -c "$case" -p "$param_set" -o "$output" > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                echo -e "  ${GREEN}✓${NC} $param_set"
                total=$((total + 1))
            else
                echo -e "  ${RED}✗${NC} $param_set"
            fi
        done
    done
    
    echo -e "${GREEN}Generated $total .geo files in $output_dir${NC}"
}

# Main
if [ $# -eq 0 ]; then
    usage
    exit 0
fi

command=$1
shift

case "$command" in
    inject)
        inject_single "$@"
        ;;
    batch-case)
        batch_case "$@"
        ;;
    batch-all)
        batch_all "$@"
        ;;
    list-cases)
        python3 "$PYTHON_SCRIPT" --list-cases
        ;;
    list-params)
        python3 "$PYTHON_SCRIPT" --list-params "$@"
        ;;
    list-all)
        python3 "$PYTHON_SCRIPT" --list-all
        ;;
    help)
        usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$command'${NC}" >&2
        usage
        exit 1
        ;;
esac
