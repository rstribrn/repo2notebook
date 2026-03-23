#!/bin/bash

# ============================================================================
# repo2notebook-wrapper.sh
# Secure wrapper for repo2notebook.py with advanced security checks
# ============================================================================

set -e  # Exit on error
set -o pipefail  # Pipe failures

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO2NOTEBOOK_SCRIPT="${SCRIPT_DIR}/repo2notebook.py"

# Security limits
MAX_FILE_COUNT=10000
MAX_TOTAL_SIZE_MB=500
MAX_SINGLE_FILE_MB=10

# Default values
DRY_RUN=false
VERBOSE=false
SKIP_SECURITY_CHECK=false
AUTO_OPEN=false
AUTO_SPLIT=true
MAX_WORDS=400000
OUTPUT_DIR="_repo2notebook"
EXCLUDE_PATTERNS=()
EXCLUDE_FILE=""

# Sensitive file/directory patterns (in addition to .gitignore)
SENSITIVE_PATTERNS=(
    "*.pem"
    "*.key"
    "*.p12"
    "*.pfx"
    "*id_rsa*"
    "*id_dsa*"
    "*.env"
    "*.env.local"
    "*.env.production"
    "*.env.staging"
    "*secret*"
    "*password*"
    "*credentials*"
    "*auth_token*"
    "*.ovpn"
    "*oauth*"
    "*.kdbx"
    "*.asc"
    "*wallet.dat"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  repo2notebook Wrapper v${VERSION}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

print_usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [DIRECTORY]

Secure wrapper for repo2notebook.py with advanced security checks.

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Verbose output
    -d, --dry-run           Check only, don't run conversion
    -s, --skip-security     Skip security checks (NOT RECOMMENDED)
    -o, --open              Automatically open output file
    --split                 Enable auto-split for large repos (default: ON)
    --no-split              Disable auto-split (error if too large)
    --max-words NUM         Max words per file (default: ${MAX_WORDS})
    --exclude PATTERN       Exclude files matching pattern (can use multiple times)
    --exclude-file FILE     Read exclude patterns from file (one per line)
    --max-files NUM         Max number of files (default: ${MAX_FILE_COUNT})
    --max-size MB           Max total size in MB (default: ${MAX_TOTAL_SIZE_MB})
    --output-dir DIR        Output directory (default: ${OUTPUT_DIR})

DIRECTORY:
    Path to repository (default: current directory)

EXAMPLES:
    # First run dry-run check
    $(basename "$0") --dry-run /path/to/repo

    # Normal run with verbose output and auto-split
    $(basename "$0") --verbose --split /path/to/repo

    # Disable splitting (strict mode)
    $(basename "$0") --no-split .

    # Custom word limit
    $(basename "$0") --max-words 300000 /path/to/repo

    # Exclude specific patterns
    $(basename "$0") --exclude "test_*" --exclude "*.log" /path/to/repo

    # Use exclude file
    $(basename "$0") --exclude-file .excludes /path/to/repo

EOF
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${MAGENTA}→${NC} $*"
    fi
}

human_readable_size() {
    local bytes=$1
    local units=("B" "KB" "MB" "GB" "TB")
    local unit=0
    local size=$bytes
    
    while [ "$size" -ge 1024 ] && [ "$unit" -lt 4 ]; do
        size=$((size / 1024))
        unit=$((unit + 1))
    done
    
    echo "$size ${units[$unit]}"
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

check_dependencies() {
    log_verbose "Checking dependencies..."
    
    local missing_deps=()
    
    # Python 3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # repo2notebook.py
    if [ ! -f "$REPO2NOTEBOOK_SCRIPT" ]; then
        log_error "repo2notebook.py not found: $REPO2NOTEBOOK_SCRIPT"
        return 1
    fi
    
    # Optional: git
    if ! command -v git &> /dev/null; then
        log_warning "git not installed (optional for repository name detection)"
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    log_verbose "All dependencies OK"
    return 0
}

validate_directory() {
    local dir="$1"
    
    log_verbose "Validating directory: $dir"
    
    if [ ! -d "$dir" ]; then
        log_error "Directory does not exist: $dir"
        return 1
    fi
    
    if [ ! -r "$dir" ]; then
        log_error "Directory is not readable: $dir"
        return 1
    fi
    
    log_verbose "Directory valid"
    return 0
}

# ============================================================================
# SECURITY CHECKS
# ============================================================================

scan_sensitive_files() {
    local repo_dir="$1"
    local found_sensitive=()
    
    log_info "Scanning for sensitive files..."
    
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        while IFS= read -r -d '' file; do
            local rel_path="${file#$repo_dir/}"
            found_sensitive+=("$rel_path")
        done < <(find "$repo_dir" -type f -name "$pattern" -print0 2>/dev/null)
    done
    
    if [ ${#found_sensitive[@]} -gt 0 ]; then
        log_warning "Found ${#found_sensitive[@]} potentially sensitive files:"
        for file in "${found_sensitive[@]}"; do
            echo -e "  ${YELLOW}•${NC} $file"
        done
        echo
        
        if [ "$SKIP_SECURITY_CHECK" = false ]; then
            read -p "Continue anyway? (yes/no): " -r
            echo
            if [[ ! $REPLY =~ ^[Yy]es?$ ]]; then
                log_info "Cancelled by user"
                return 1
            fi
        fi
    else
        log_success "No sensitive files found"
    fi
    
    return 0
}

check_repository_size() {
    local repo_dir="$1"
    
    log_info "Analyzing repository size..."
    
    # File count
    local file_count=$(find "$repo_dir" -type f | wc -l)
    log_verbose "Total file count: $file_count"
    
    if [ "$file_count" -gt "$MAX_FILE_COUNT" ]; then
        log_error "Too many files: $file_count (max: $MAX_FILE_COUNT)"
        log_info "Increase limit with: --max-files $file_count"
        return 1
    fi
    
    # Total size
    local total_size=$(du -sb "$repo_dir" 2>/dev/null | cut -f1)
    local total_mb=$((total_size / 1024 / 1024))
    log_verbose "Total size: $(human_readable_size $total_size)"
    
    if [ "$total_mb" -gt "$MAX_TOTAL_SIZE_MB" ]; then
        log_error "Repository too large: ${total_mb}MB (max: ${MAX_TOTAL_SIZE_MB}MB)"
        log_info "Increase limit with: --max-size $total_mb"
        return 1
    fi
    
    # Largest files
    log_verbose "Top 5 largest files:"
    find "$repo_dir" -type f -exec du -h {} + 2>/dev/null | \
        sort -rh | head -5 | while read -r size file; do
        log_verbose "  $size - ${file#$repo_dir/}"
    done
    
    log_success "Repository size OK: $file_count files, ${total_mb}MB"
    return 0
}

check_git_status() {
    local repo_dir="$1"
    
    if [ ! -d "$repo_dir/.git" ]; then
        log_verbose "Not a Git repository, skipping git checks"
        return 0
    fi
    
    log_info "Checking Git status..."
    
    cd "$repo_dir"
    
    # Uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log_warning "Repository has uncommitted changes"
        log_verbose "Tip: Commit or stash your changes"
    fi
    
    # Untracked files
    local untracked=$(git ls-files --others --exclude-standard | wc -l)
    if [ "$untracked" -gt 0 ]; then
        log_warning "Repository has $untracked untracked files"
    fi
    
    cd - > /dev/null
    
    return 0
}

# ============================================================================
# STATISTICS AND REPORTING
# ============================================================================

generate_preview() {
    local repo_dir="$1"
    
    log_info "Generating preview..."
    echo
    echo -e "${CYAN}┌─────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC}  Repository Summary                     ${CYAN}│${NC}"
    echo -e "${CYAN}└─────────────────────────────────────────┘${NC}"
    echo
    
    # Overall statistics
    local total_files=$(find "$repo_dir" -type f | wc -l)
    local total_dirs=$(find "$repo_dir" -type d | wc -l)
    local total_size=$(du -sh "$repo_dir" 2>/dev/null | cut -f1)
    
    echo -e "  📁 Directories: ${GREEN}$total_dirs${NC}"
    echo -e "  📄 Files: ${GREEN}$total_files${NC}"
    echo -e "  💾 Size: ${GREEN}$total_size${NC}"
    echo
    
    # Breakdown by extension
    echo -e "${CYAN}Files by type:${NC}"
    find "$repo_dir" -type f -name "*.*" | \
        sed 's/.*\.//' | \
        sort | uniq -c | \
        sort -rn | head -10 | \
        while read count ext; do
            printf "  %-15s %5d files\n" ".$ext" "$count"
        done
    echo
    
    # Top directories by size
    echo -e "${CYAN}Top 5 largest directories:${NC}"
    du -h "$repo_dir"/* 2>/dev/null | \
        sort -rh | head -5 | \
        while read size dir; do
            printf "  %-10s %s\n" "$size" "$(basename "$dir")"
        done
    echo
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

run_repo2notebook() {
    local repo_dir="$1"
    
    log_info "Running repo2notebook.py..."
    
    # Build command with options
    local cmd="python3 \"$REPO2NOTEBOOK_SCRIPT\" \"$repo_dir\""
    
    if [ "$AUTO_SPLIT" = true ]; then
        cmd="$cmd --split"
    else
        cmd="$cmd --no-split"
    fi
    
    if [ "$MAX_WORDS" != "400000" ]; then
        cmd="$cmd --max-words $MAX_WORDS"
    fi
    
    # Add exclude patterns
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        cmd="$cmd --exclude \"$pattern\""
    done
    
    # Add exclude file
    if [ -n "$EXCLUDE_FILE" ]; then
        cmd="$cmd --exclude-file \"$EXCLUDE_FILE\""
    fi
    
    log_verbose "Command: $cmd"
    echo
    
    # Run Python script
    if eval "$cmd"; then
        log_success "Conversion completed!"
        
        # Check for multiple output files (split mode)
        local output_files=$(find "$repo_dir/$OUTPUT_DIR" -name "*.md" -type f ! -name "MANIFEST.md")
        local file_count=$(echo "$output_files" | wc -l)
        
        if [ "$file_count" -gt 1 ]; then
            # Multiple files - split mode
            log_info "Generated $file_count part files"
            
            echo
            echo -e "${CYAN}┌─────────────────────────────────────────┐${NC}"
            echo -e "${CYAN}│${NC}  Multi-Part Output                      ${CYAN}│${NC}"
            echo -e "${CYAN}└─────────────────────────────────────────┘${NC}"
            echo
            
            local total_size=0
            local total_words=0
            
            echo "$output_files" | while read output_file; do
                if [ -f "$output_file" ]; then
                    local file_size=$(du -h "$output_file" | cut -f1)
                    local word_count=$(wc -w < "$output_file" 2>/dev/null || echo "0")
                    total_words=$((total_words + word_count))
                    
                    echo -e "  📄 $(basename "$output_file")"
                    echo -e "     Size: ${GREEN}$file_size${NC}, Words: ${GREEN}$(printf "%'d" $word_count)${NC}"
                fi
            done
            
            # Check for manifest
            local manifest_file="$repo_dir/$OUTPUT_DIR/MANIFEST.md"
            if [ -f "$manifest_file" ]; then
                echo
                echo -e "  📋 Manifest: ${GREEN}MANIFEST.md${NC}"
                echo
                echo -e "${YELLOW}Instructions:${NC}"
                echo -e "  Upload all part files to NotebookLM as separate sources"
                echo -e "  See MANIFEST.md for detailed instructions"
            fi
            
            # Auto-open manifest if requested
            if [ "$AUTO_OPEN" = true ] && [ -f "$manifest_file" ]; then
                log_info "Opening manifest file..."
                case "$(uname -s)" in
                    Darwin*)    open "$manifest_file" ;;
                    Linux*)     xdg-open "$manifest_file" 2>/dev/null || log_warning "Cannot auto-open" ;;
                    *)          log_warning "Auto-open not supported on this OS" ;;
                esac
            fi
            
        else
            # Single file
            local output_file=$(echo "$output_files" | head -1)
            
            if [ -n "$output_file" ] && [ -f "$output_file" ]; then
                local file_size=$(du -h "$output_file" | cut -f1)
                local word_count=$(wc -w < "$output_file")
                
                echo
                echo -e "${CYAN}┌─────────────────────────────────────────┐${NC}"
                echo -e "${CYAN}│${NC}  Output                                 ${CYAN}│${NC}"
                echo -e "${CYAN}└─────────────────────────────────────────┘${NC}"
                echo
                echo -e "  📄 File: ${GREEN}$(basename "$output_file")${NC}"
                echo -e "  💾 Size: ${GREEN}$file_size${NC}"
                echo -e "  📝 Words: ${GREEN}$(printf "%'d" $word_count)${NC}"
                echo
                
                # Auto-open
                if [ "$AUTO_OPEN" = true ]; then
                    log_info "Opening output file..."
                    case "$(uname -s)" in
                        Darwin*)    open "$output_file" ;;
                        Linux*)     xdg-open "$output_file" 2>/dev/null || log_warning "Cannot auto-open" ;;
                        *)          log_warning "Auto-open not supported on this OS" ;;
                    esac
                fi
            fi
        fi
        
        return 0
    else
        log_error "Error running repo2notebook.py"
        return 1
    fi
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    print_header
    
    # Parse arguments
    REPO_DIR="."
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                print_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -s|--skip-security)
                SKIP_SECURITY_CHECK=true
                log_warning "Security checks skipped!"
                shift
                ;;
            -o|--open)
                AUTO_OPEN=true
                shift
                ;;
            --split)
                AUTO_SPLIT=true
                shift
                ;;
            --no-split)
                AUTO_SPLIT=false
                shift
                ;;
            --max-words)
                MAX_WORDS="$2"
                shift 2
                ;;
            --exclude)
                EXCLUDE_PATTERNS+=("$2")
                shift 2
                ;;
            --exclude-file)
                EXCLUDE_FILE="$2"
                shift 2
                ;;
            --max-files)
                MAX_FILE_COUNT="$2"
                shift 2
                ;;
            --max-size)
                MAX_TOTAL_SIZE_MB="$2"
                shift 2
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -*)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
            *)
                REPO_DIR="$1"
                shift
                ;;
        esac
    done
    
    # Get absolute path
    REPO_DIR=$(cd "$REPO_DIR" && pwd)
    
    log_info "Repository: ${CYAN}$REPO_DIR${NC}"
    if [ "$AUTO_SPLIT" = true ]; then
        log_verbose "Auto-split: ${GREEN}enabled${NC} (max words: $MAX_WORDS)"
    else
        log_verbose "Auto-split: ${YELLOW}disabled${NC} (strict mode)"
    fi
    
    # Display exclude patterns if any
    if [ ${#EXCLUDE_PATTERNS[@]} -gt 0 ]; then
        log_verbose "Exclude patterns: ${#EXCLUDE_PATTERNS[@]}"
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            log_verbose "  • $pattern"
        done
    fi
    
    if [ -n "$EXCLUDE_FILE" ]; then
        log_verbose "Exclude file: $EXCLUDE_FILE"
    fi
    echo
    
    # Check dependencies
    check_dependencies || exit 1
    
    # Validate directory
    validate_directory "$REPO_DIR" || exit 1
    
    # Security checks
    if [ "$SKIP_SECURITY_CHECK" = false ]; then
        scan_sensitive_files "$REPO_DIR" || exit 1
        check_repository_size "$REPO_DIR" || exit 1
        check_git_status "$REPO_DIR" || exit 1
    fi
    
    # Preview statistics
    if [ "$VERBOSE" = true ] || [ "$DRY_RUN" = true ]; then
        generate_preview "$REPO_DIR"
    fi
    
    # Dry-run - check only
    if [ "$DRY_RUN" = true ]; then
        log_success "Dry-run completed. Repository is ready for conversion."
        echo
        log_info "To run conversion, remove --dry-run parameter"
        exit 0
    fi
    
    # Confirmation before running
    echo -e "${YELLOW}Continue with conversion?${NC}"
    read -p "Press Enter to continue, Ctrl+C to cancel..."
    echo
    
    # Run conversion
    run_repo2notebook "$REPO_DIR" || exit 1
    
    echo
    log_success "All done! ✨"
    echo
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
