#!/bin/bash
# Batch mesh generation script for all Cases 1A-3F
# Usage:
#   ./generate_all_meshes.sh [options]
#   ./generate_all_meshes.sh --output meshes/ --parallel 4 --verbose
#   ./generate_all_meshes.sh --cases case1A,case2B --list-only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INJECT_SCRIPT="$SCRIPT_DIR/inject_params.py"
PARAMS_JSON="$SCRIPT_DIR/case_parameters.json"

# Defaults
OUTPUT_DIR="./generated_meshes"
GMSH_EXE="gmsh"
PARALLEL_JOBS=1
VERBOSE=0
DRY_RUN=0
LIST_ONLY=0
CASES_FILTER=""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Statistics
TOTAL_TASKS=0
SUCCESS_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -g|--gmsh)
            GMSH_EXE="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL_JOBS="$2"
            shift 2
            ;;
        -c|--cases)
            CASES_FILTER="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --list-only)
            LIST_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

usage() {
    cat << EOF
Usage: $0 [options]

Options:
  -o, --output DIR           Output directory (default: ./generated_meshes)
  -g, --gmsh PATH            Path to gmsh executable (default: gmsh)
  -p, --parallel N           Number of parallel jobs (default: 1)
  -c, --cases CASE1,CASE2    Filter specific cases (e.g., case1A,case2B)
  -v, --verbose              Verbose output
  --dry-run                  Show what would be done without executing
  --list-only                List all cases and parameter sets, then exit
  -h, --help                 Show this help message

Examples:
  $0 --output ./meshes --parallel 4
  $0 --cases case1A,case2B --verbose
  $0 --list-only
EOF
}

log() {
    local level=$1
    shift
    local msg="$*"
    local ts=$(date "+%H:%M:%S")
    
    if [ "$VERBOSE" -eq 1 ] || [ "$level" = "ERROR" ] || [ "$level" = "WARNING" ]; then
        case "$level" in
            INFO)    echo -e "${BLUE}[${ts}]${NC} INFO:    $msg" ;;
            WARNING) echo -e "${YELLOW}[${ts}]${NC} WARNING: $msg" ;;
            ERROR)   echo -e "${RED}[${ts}]${NC} ERROR:   $msg" >&2 ;;
            SUCCESS) echo -e "${GREEN}[${ts}]${NC} SUCCESS: $msg" ;;
            *)       echo -e "[${ts}] $msg" ;;
        esac
    fi
}

# Extract cases and parameter sets from JSON
get_all_cases() {
    python3 "$INJECT_SCRIPT" --export-cases 2>/dev/null || true
}

get_param_sets() {
    local case=$1
    python3 "$INJECT_SCRIPT" --export-params "$case" 2>/dev/null || true
}

# Generate .geo file
generate_geo() {
    local case=$1
    local param_set=$2
    local geo_file="$GEO_DIR/${case}_${param_set}.geo"
    
    if [ "$DRY_RUN" -eq 1 ]; then
        log INFO "[DRY-RUN] Would generate: $geo_file"
        return 0
    fi
    
    if [ -f "$geo_file" ]; then
        log INFO "Already exists: $geo_file"
        return 0
    fi
    
    if python3 "$INJECT_SCRIPT" -c "$case" -p "$param_set" -o "$geo_file" > /dev/null 2>&1; then
        log INFO "Generated: $geo_file"
        echo "$geo_file"
        return 0
    else
        log ERROR "Failed to generate: $geo_file"
        return 1
    fi
}

# Generate .msh from .geo
generate_mesh() {
    local geo_file=$1
    local msh_file="$MESH_DIR/$(basename "${geo_file%.geo}.msh")"
    
    if [ "$DRY_RUN" -eq 1 ]; then
        log INFO "[DRY-RUN] Would mesh: $geo_file"
        return 0
    fi
    
    if [ -f "$msh_file" ]; then
        log INFO "Mesh already exists: $msh_file"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
        return 0
    fi
    
    log INFO "Meshing: $(basename $geo_file) -> $(basename $msh_file)"
    
    if timeout 300 "$GMSH_EXE" "$geo_file" -3 -format msh2 -o "$msh_file" > /dev/null 2>&1; then
        local size=$(du -h "$msh_file" | cut -f1)
        log SUCCESS "✓ $msh_file ($size)"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        return 0
    else
        log ERROR "gmsh failed for $(basename $geo_file)"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        return 1
    fi
}

# Process a single case:param_set pair
process_task() {
    local case=$1
    local param_set=$2
    
    local geo_file=$(generate_geo "$case" "$param_set")
    if [ -z "$geo_file" ]; then
        return 1
    fi
    
    generate_mesh "$geo_file"
}

# Main generation loop (sequential)
generate_sequential() {
    log INFO "Generating meshes sequentially..."
    
    local all_cases=$(get_all_cases)
    local task_count=0
    
    for case in $all_cases; do
        # Filter cases if specified
        if [ -n "$CASES_FILTER" ]; then
            if [[ ! "$CASES_FILTER" =~ "$case" ]]; then
                continue
            fi
        fi
        
        local param_sets=$(get_param_sets "$case")
        
        for param_set in $param_sets; do
            task_count=$((task_count + 1))
            log INFO "[$task_count/$TOTAL_TASKS] Processing $case:$param_set"
            process_task "$case" "$param_set" || true
        done
    done
}

# Main generation loop (parallel using GNU parallel or xargs)
generate_parallel() {
    log INFO "Generating meshes with $PARALLEL_JOBS parallel jobs..."
    
    local all_cases=$(get_all_cases)
    local task_list=$(mktemp)
    
    # Build task list
    for case in $all_cases; do
        if [ -n "$CASES_FILTER" ]; then
            if [[ ! "$CASES_FILTER" =~ "$case" ]]; then
                continue
            fi
        fi
        
        local param_sets=$(get_param_sets "$case")
        for param_set in $param_sets; do
            echo "$case $param_set"
        done
    done > "$task_list"
    
    TOTAL_TASKS=$(wc -l < "$task_list")
    
    if command -v parallel &> /dev/null; then
        # Use GNU parallel if available
        log INFO "Using GNU parallel for batch processing"
        cat "$task_list" | parallel --jobs "$PARALLEL_JOBS" \
            "bash $SCRIPT_DIR/generate_all_meshes.sh --single {1} {2} --output $OUTPUT_DIR --gmsh $GMSH_EXE"
    else
        # Fallback to xargs
        log INFO "GNU parallel not found, using xargs with max_procs"
        cat "$task_list" | xargs -P "$PARALLEL_JOBS" -I {} bash -c \
            "bash $SCRIPT_DIR/generate_all_meshes.sh --single {} --output $OUTPUT_DIR --gmsh $GMSH_EXE"
    fi
    
    rm "$task_list"
}

# Single task processing mode (called from parallel)
process_single_mode() {
    local case=$1
    local param_set=$2
    
    # Initialize directories (quiet)
    mkdir -p "$GEO_DIR" "$MESH_DIR"
    
    process_task "$case" "$param_set"
}

# List only mode
list_mode() {
    echo "Available Cases and Parameter Sets"
    echo "========================================"
    
    local all_cases=$(get_all_cases)
    local total=0
    
    for case in $all_cases; do
        echo ""
        echo -e "${BLUE}$case${NC}:"
        local param_sets=$(get_param_sets "$case")
        for param_set in $param_sets; do
            echo "  • $param_set"
            total=$((total + 1))
        done
    done
    
    echo ""
    echo "========================================"
    echo "Total: $total parameter sets across $(echo $all_cases | wc -w) cases"
}

# ==============================================================================
# Main Script Logic
# ==============================================================================

# Handle --single mode (internal use for parallel execution)
if [ "$1" = "--single" ]; then
    OUTPUT_DIR="$4"
    GMSH_EXE="${6:-gmsh}"
    GEO_DIR="$OUTPUT_DIR/geo"
    MESH_DIR="$OUTPUT_DIR/mesh"
    mkdir -p "$GEO_DIR" "$MESH_DIR"
    process_single_mode "$2" "$3"
    exit $?
fi

# Check if gmsh is available
if ! command -v "$GMSH_EXE" &> /dev/null; then
    log ERROR "gmsh executable not found: $GMSH_EXE"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$INJECT_SCRIPT" ]; then
    log ERROR "inject_params.py not found: $INJECT_SCRIPT"
    exit 1
fi

# Setup output directories
GEO_DIR="$OUTPUT_DIR/geo"
MESH_DIR="$OUTPUT_DIR/mesh"

if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$GEO_DIR" "$MESH_DIR"
    log INFO "Output directories: $OUTPUT_DIR"
fi

# Handle list-only mode
if [ "$LIST_ONLY" -eq 1 ]; then
    list_mode
    exit 0
fi

# Count total tasks
log INFO "Counting tasks..."
local all_cases=$(get_all_cases)
TOTAL_TASKS=0
for case in $all_cases; do
    if [ -n "$CASES_FILTER" ]; then
        if [[ ! "$CASES_FILTER" =~ "$case" ]]; then
            continue
        fi
    fi
    
    local param_sets=$(get_param_sets "$case")
    for param_set in $param_sets; do
        TOTAL_TASKS=$((TOTAL_TASKS + 1))
    done
done

log INFO "Will generate $TOTAL_TASKS meshes"

# Start generation
START_TIME=$(date +%s)

if [ "$PARALLEL_JOBS" -gt 1 ] && command -v parallel &> /dev/null; then
    generate_parallel
else
    generate_sequential
fi

# Print summary
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================"
echo "Generation Summary"
echo "========================================"
echo -e "Total tasks:     $TOTAL_TASKS"
echo -e "Success:         ${GREEN}$SUCCESS_COUNT${NC}"
echo -e "Failed:          ${RED}$FAILED_COUNT${NC}"
echo -e "Skipped:         $SKIPPED_COUNT"
echo -e "Elapsed time:    ${MINUTES}m ${SECONDS}s"
echo ""
echo "Output directories:"
echo "  .geo files: $GEO_DIR"
echo "  .msh files: $MESH_DIR"

if [ "$DRY_RUN" -eq 0 ]; then
    GEO_COUNT=$(find "$GEO_DIR" -name "*.geo" 2>/dev/null | wc -l)
    MESH_COUNT=$(find "$MESH_DIR" -name "*.msh" 2>/dev/null | wc -l)
    echo ""
    echo "Generated files:"
    echo "  .geo: $GEO_COUNT"
    echo "  .msh: $MESH_COUNT"
fi

echo "========================================"

exit 0
