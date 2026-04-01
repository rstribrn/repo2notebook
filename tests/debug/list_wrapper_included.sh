#!/bin/bash
# Extract list of included files from wrapper will_be_excluded()
# Saves to /tmp/wrapper_included_files.txt

set -e

cd /home/rstribrn/Work/GIT/repo2notebook

# Load constants and function
eval "$(python3 generate_constants.py 2>/dev/null)"
export BINARY_EXTENSIONS DEFAULT_EXCLUDE_DIRS DEFAULT_EXCLUDE_FILES DEFAULT_EXCLUDE_PATTERNS

# Load will_be_excluded function
eval "$(sed -n '/^will_be_excluded()/,/^}/p' repo2notebook-wrapper.sh)"

repo_dir="/home/rstribrn/NESS_Projects/CZ_ISKN-2023_2026/Work/GIT_ISKN/iskn-container-support"
output_file="/tmp/wrapper_included_files.txt"

echo "Scanning: $repo_dir"
echo "This may take a minute..."

> "$output_file"

count=0
included=0
excluded=0

while IFS= read -r file; do
    count=$((count + 1))
    
    # Show progress every 500 files
    if [ $((count % 500)) -eq 0 ]; then
        echo "  Processed $count files... (included: $included, excluded: $excluded)"
    fi
    
    if ! will_be_excluded "$file" "$repo_dir"; then
        # Get relative path
        rel_path="${file#$repo_dir/}"
        echo "$rel_path" >> "$output_file"
        included=$((included + 1))
    else
        excluded=$((excluded + 1))
    fi
done < <(find "$repo_dir" -type f 2>/dev/null)

echo ""
echo "Found $included included files"
echo "Excluded $excluded files"
echo "Saved to: $output_file"
