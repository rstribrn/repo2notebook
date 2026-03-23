#!/usr/bin/env python3
"""
repo2notebook - Convert any code repository to NotebookLM-compatible format

Usage:
    python repo2notebook.py [OPTIONS] [DIRECTORY]
    
Options:
    --max-words NUM      Maximum words per output file (default: 400000)
    --split              Enable automatic splitting if exceeds limit
    --no-split           Disable splitting (error if too large)
    -h, --help           Show this help message

Output: _repo2notebook/notebook.md (or multiple files if split)

GitHub: https://github.com/Appaholics/repo2notebook
License: MIT
"""

import os
import sys
import fnmatch
import argparse
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = "_repo2notebook"
GITHUB_URL = "https://github.com/rstribrn/repo2notebook"

# NotebookLM limits (with safety margin)
MAX_WORDS_PER_FILE = 400000  # NotebookLM limit is ~500k, we use 400k for safety
MAX_FILE_SIZE_MB = 45        # NotebookLM limit is 50MB, we use 45MB for safety

# Always exclude (hardcoded, cannot override)
ALWAYS_EXCLUDE_DIRS = {
    ".git", ".svn", ".hg",                          # Version control
    "node_modules", "bower_components",              # JS
    "__pycache__", ".pytest_cache", ".mypy_cache",  # Python
    "venv", ".venv", "env", ".env",                 # Python virtualenv
    "dist", "build", "out", "_build",               # Build outputs
    ".next", ".nuxt", ".expo", ".turbo",            # JS frameworks
    "target",                                        # Rust, Java
    "bin", "obj", "Debug", "Release",               # C#/.NET
    "vendor",                                        # Go, PHP, Ruby
    "Pods", "DerivedData", ".build",                # iOS/Swift
    ".idea", ".vscode", ".vs", ".fleet",            # IDEs
    ".gradle", ".maven",                            # Java build tools
    "coverage", ".nyc_output",                      # Coverage reports
    "htmlcov", ".coverage",                         # Python coverage
    "site-packages", "eggs", "sdist",               # Python packaging
    "tmp", "temp", "cache", ".cache",               # Temporary/cache
    "logs", "log",                                  # Log directories
    OUTPUT_DIR,                                      # Our own output
}

ALWAYS_EXCLUDE_FILES = {
    ".DS_Store", "Thumbs.db", "desktop.ini",        # OS files
    ".env", ".env.local", ".env.production",        # Secrets (but .env.example OK)
}

ALWAYS_EXCLUDE_PATTERNS = [
    # Lock files
    "*-lock.json",      # package-lock.json, etc.
    "*-lock.yaml",      # pnpm-lock.yaml
    "*.lock",           # Cargo.lock, poetry.lock, Gemfile.lock, composer.lock
    
    # Logs and temporary files
    "*.log",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.swo",
    "*~",               # Backup files
    
    # Compiled/Binary files
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.class",
    "*.dll",
    "*.exe",
    "*.so",
    "*.dylib",
    "*.o",
    "*.obj",
    "*.a",
    "*.lib",
    
    # Minified and bundled files
    "*.min.js",
    "*.min.css",
    "*.map",
    "*.chunk.js",
    "*.bundle.js",
    "*.bundle.css",
    
    # Test and fixture data
    "*_test.py",        # Python test files (in addition to test_*)
    "test_*.py",
    "*_test.go",        # Go test files
    "*_test.rb",        # Ruby test files
    "*.spec.js",        # JS spec files
    "*.spec.ts",
    "*.test.js",
    "*.test.ts",
    "fixtures.json",
    "mock_data.*",
    "test_data.*",
    "sample_data.*",
    
    # Documentation builds
    "_build/*",
    "_site/*",
    ".docusaurus/*",
    ".jekyll-cache/*",
    
    # Package manager files
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "Gemfile.lock",
    "composer.lock",
    "Cargo.lock",
    "go.sum",
    
    # Large generated files
    "*.sql.gz",
    "*.dump",
    "*.bak",
    "*.backup",
    
    # IDE and editor files
    "*.swp",
    "*.swo",
    "*~",
    ".project",
    ".classpath",
    ".settings",
]

# Extension to language mapping for markdown code blocks
EXT_TO_LANG = {
    # JavaScript/TypeScript
    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    # Python
    ".py": "python", ".pyw": "python", ".pyi": "python",
    # Systems
    ".go": "go",
    ".rs": "rust",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    # Mobile
    ".swift": "swift",
    ".kt": "kotlin", ".kts": "kotlin",
    ".java": "java",
    ".dart": "dart",
    # .NET
    ".cs": "csharp",
    ".fs": "fsharp",
    ".vb": "vb",
    # Web
    ".html": "html", ".htm": "html",
    ".css": "css",
    ".scss": "scss", ".sass": "sass", ".less": "less",
    ".vue": "vue",
    ".svelte": "svelte",
    # Data
    ".json": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".csv": "csv",
    # Shell
    ".sh": "bash", ".bash": "bash", ".zsh": "zsh",
    ".ps1": "powershell", ".psm1": "powershell",
    ".bat": "batch", ".cmd": "batch",
    # Other
    ".sql": "sql",
    ".graphql": "graphql", ".gql": "graphql",
    ".md": "markdown", ".markdown": "markdown",
    ".r": "r", ".R": "r",
    ".rb": "ruby",
    ".php": "php",
    ".pl": "perl", ".pm": "perl",
    ".lua": "lua",
    ".ex": "elixir", ".exs": "elixir",
    ".erl": "erlang",
    ".hs": "haskell",
    ".scala": "scala",
    ".clj": "clojure",
    ".groovy": "groovy",
    ".tf": "terraform",
    ".dockerfile": "dockerfile",
    ".nginx": "nginx",
    ".proto": "protobuf",
}

# ============================================================================
# OUTPUT FILENAME
# ============================================================================

def get_output_filename(repo_path: Path) -> str:
    """Generate output filename from git remote or folder name."""
    
    # Try to get git remote URL
    git_config = repo_path / ".git" / "config"
    if git_config.exists():
        try:
            with open(git_config, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse remote URL (supports both https and ssh formats)
            import re
            
            # Match: url = https://github.com/owner/repo.git
            # Match: url = git@github.com:owner/repo.git
            patterns = [
                r'url\s*=\s*https?://([^/]+)/([^/]+)/([^/\s]+?)(?:\.git)?$',
                r'url\s*=\s*git@([^:]+):([^/]+)/([^/\s]+?)(?:\.git)?$',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.MULTILINE)
                if match:
                    host = match.group(1).replace(".", "-")  # github.com -> github-com
                    owner = match.group(2)
                    repo = match.group(3)
                    return f"{host}-{owner}-{repo}.md"
        except Exception:
            pass
    
    # Fallback: use folder name
    return f"{repo_path.name}.md"


# ============================================================================
# GITIGNORE PARSER
# ============================================================================

def parse_gitignore(repo_path: Path) -> list[str]:
    """Parse .gitignore and return list of patterns."""
    gitignore_path = repo_path / ".gitignore"
    patterns = []
    
    if gitignore_path.exists():
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception:
            pass
    
    return patterns


def matches_gitignore(path: str, patterns: list[str]) -> bool:
    """Check if path matches any gitignore pattern."""
    # Normalize path separators
    path = path.replace("\\", "/")
    
    for pattern in patterns:
        # Remove leading/trailing slashes for matching
        clean_pattern = pattern.strip("/")
        
        # Directory pattern (ends with /)
        if pattern.endswith("/"):
            if fnmatch.fnmatch(path, clean_pattern + "*") or \
               fnmatch.fnmatch(path, "*/" + clean_pattern + "*"):
                return True
        
        # File/directory pattern
        if fnmatch.fnmatch(path, clean_pattern) or \
           fnmatch.fnmatch(path, "*/" + clean_pattern) or \
           fnmatch.fnmatch(os.path.basename(path), clean_pattern):
            return True
    
    return False

# ============================================================================
# FILE FILTERING
# ============================================================================

def should_exclude_dir(dir_name: str) -> bool:
    """Check if directory should be excluded."""
    return dir_name in ALWAYS_EXCLUDE_DIRS or dir_name.startswith(".")


def should_exclude_file(file_name: str) -> bool:
    """Check if file should be excluded based on name/pattern."""
    # Exact match
    if file_name in ALWAYS_EXCLUDE_FILES:
        return True
    
    # Pattern match
    for pattern in ALWAYS_EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    
    # Hidden files (except some config files we want)
    if file_name.startswith(".") and file_name not in {".env.example", ".gitignore"}:
        return True
    
    return False


def is_binary_file(file_path: Path) -> bool:
    """Check if file is binary (cannot be converted to text)."""
    # Known binary extensions
    binary_extensions = {
        # Images
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp", ".tiff", ".tif",
        # Videos
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm", ".m4v",
        # Audio
        ".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a",
        # Archives
        ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz", ".tgz",
        # Executables
        ".exe", ".dll", ".so", ".dylib", ".app", ".deb", ".rpm", ".apk",
        # Compiled
        ".o", ".obj", ".class", ".pyc", ".pyo", ".elc",
        # Documents (binary formats)
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".odt", ".ods", ".odp",
        # Databases
        ".db", ".sqlite", ".sqlite3", ".mdb",
        # Fonts
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        # Java keystores and certificates
        ".jks", ".keystore", ".truststore", ".cer", ".crt", ".der",
        ".p7b", ".p7c", ".p12", ".pfx", ".pem",
        # Other binary
        ".bin", ".dat", ".pak", ".iso", ".img", ".dmg",
    }
    
    ext = file_path.suffix.lower()
    
    if ext in binary_extensions:
        return True
    
    # Try to read first bytes to detect binary
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8192)  # Read more bytes for better detection
            
            # Check for null bytes (strong indicator of binary)
            if b"\x00" in chunk:
                return True
            
            # Check for high ratio of non-text bytes
            # Text files should have mostly printable ASCII/UTF-8
            non_text_bytes = sum(1 for byte in chunk if byte < 0x20 and byte not in (0x09, 0x0A, 0x0D))
            if len(chunk) > 0 and non_text_bytes / len(chunk) > 0.3:
                return True
            
            return False
            
    except Exception:
        # If we can't read it, assume binary
        return True


def is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file that can be converted to markdown."""
    # First check if it's binary
    if is_binary_file(file_path):
        return False
    
    # Known text extensions
    text_extensions = set(EXT_TO_LANG.keys()) | {
        ".txt", ".rst", ".ini", ".cfg", ".conf", ".config",
        ".editorconfig", ".gitattributes", ".gitignore",
        ".prettierrc", ".eslintrc", ".babelrc",
        ".env.example", ".env.sample", ".env.template",
        ".htaccess", ".npmrc", ".yarnrc",
        "Makefile", "Dockerfile", "Containerfile",
        "Procfile", "Gemfile", "Rakefile",
        "CMakeLists.txt", "requirements.txt", "constraints.txt",
    }
    
    ext = file_path.suffix.lower()
    name = file_path.name
    
    if ext in text_extensions or name in text_extensions:
        return True
    
    # No extension - check if it's a known config file
    if not ext and name in {"Makefile", "Dockerfile", "Procfile", "Gemfile", "Rakefile"}:
        return True
    
    # For other files, assume text if not detected as binary above
    return True


def get_language(file_path: Path) -> str:
    """Get markdown language identifier for file."""
    ext = file_path.suffix.lower()
    name = file_path.name.lower()
    
    # Special files without extension
    if name == "dockerfile" or name == "containerfile":
        return "dockerfile"
    if name == "makefile":
        return "makefile"
    if name == "gemfile" or name == "rakefile":
        return "ruby"
    if name == "procfile":
        return "yaml"
    
    return EXT_TO_LANG.get(ext, "")

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def collect_files(repo_path: Path, exclude_patterns: list[str] = None) -> tuple[list[Path], dict]:
    """Collect all files to process. Returns (files, stats)."""
    gitignore_patterns = parse_gitignore(repo_path)
    exclude_patterns = exclude_patterns or []
    files = []
    stats = {
        "total_scanned": 0,
        "excluded_dir": 0,
        "excluded_file": 0,
        "excluded_gitignore": 0,
        "excluded_binary": 0,
        "excluded_non_text": 0,
        "excluded_custom": 0,
        "included": 0,
    }
    
    for root, dirs, filenames in os.walk(repo_path):
        # Filter directories in-place to prevent descending
        original_dirs = dirs.copy()
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]
        stats["excluded_dir"] += len(original_dirs) - len(dirs)
        
        rel_root = Path(root).relative_to(repo_path)
        
        for filename in filenames:
            stats["total_scanned"] += 1
            
            # Skip excluded files
            if should_exclude_file(filename):
                stats["excluded_file"] += 1
                continue
            
            file_path = Path(root) / filename
            rel_path = rel_root / filename if str(rel_root) != "." else Path(filename)
            rel_path_str = str(rel_path)
            
            # Check custom exclude patterns
            if exclude_patterns and matches_gitignore(rel_path_str, exclude_patterns):
                stats["excluded_custom"] += 1
                continue
            
            # Skip gitignore matches
            if matches_gitignore(rel_path_str, gitignore_patterns):
                stats["excluded_gitignore"] += 1
                continue
            
            # Check if binary
            if is_binary_file(file_path):
                stats["excluded_binary"] += 1
                continue
            
            # Skip non-text files
            if not is_text_file(file_path):
                stats["excluded_non_text"] += 1
                continue
            
            files.append(file_path)
            stats["included"] += 1
    
    # Sort for consistent output
    files.sort(key=lambda p: str(p.relative_to(repo_path)).lower())
    return files, stats


def print_collection_stats(stats: dict):
    """Print statistics about file collection."""
    print(f"Scanned {stats['total_scanned']} files:")
    print(f"  • Included: {stats['included']} files")
    
    excluded_total = (stats['excluded_dir'] + stats['excluded_file'] + 
                     stats['excluded_gitignore'] + stats['excluded_binary'] + 
                     stats['excluded_non_text'] + stats['excluded_custom'])
    
    if excluded_total > 0:
        print(f"  • Excluded: {excluded_total} files/dirs")
        if stats['excluded_dir'] > 0:
            print(f"    - {stats['excluded_dir']} directories (node_modules, .git, etc.)")
        if stats['excluded_file'] > 0:
            print(f"    - {stats['excluded_file']} files (lock files, .DS_Store, etc.)")
        if stats['excluded_custom'] > 0:
            print(f"    - {stats['excluded_custom']} files (custom exclude patterns)")
        if stats['excluded_gitignore'] > 0:
            print(f"    - {stats['excluded_gitignore']} files (gitignore patterns)")
        if stats['excluded_binary'] > 0:
            print(f"    - {stats['excluded_binary']} binary files (images, executables, etc.)")
        if stats['excluded_non_text'] > 0:
            print(f"    - {stats['excluded_non_text']} non-text files")


def read_file_content(file_path: Path) -> str | None:
    """Read file content, return None if failed."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            return None
    
    return None


def generate_markdown(repo_path: Path, files: list[Path]) -> tuple[str, int]:
    """Generate markdown content from files. Returns (content, word_count)."""
    repo_name = repo_path.name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"# Repository: {repo_name}",
        f"",
        f"Generated: {timestamp}",
        f"",
        f"Total files: {len(files)}",
        f"",
        f"---",
        f"",
    ]
    
    word_count = 0
    
    for file_path in files:
        rel_path = file_path.relative_to(repo_path)
        content = read_file_content(file_path)
        
        if content is None:
            continue
        
        language = get_language(file_path)
        
        lines.append(f"## File: {rel_path}")
        lines.append("")
        lines.append(f"```{language}")
        lines.append(content.rstrip())
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        word_count += len(content.split())
    
    return "\n".join(lines), word_count


def split_files_into_chunks(files: list[Path], repo_path: Path, max_words: int) -> list[list[Path]]:
    """Split files into chunks that fit within word limit."""
    chunks = []
    current_chunk = []
    current_words = 0
    
    for file_path in files:
        content = read_file_content(file_path)
        if content is None:
            continue
        
        file_words = len(content.split())
        
        # If single file exceeds limit, put it in its own chunk
        if file_words > max_words:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_words = 0
            chunks.append([file_path])
            continue
        
        # If adding this file would exceed limit, start new chunk
        if current_words + file_words > max_words:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [file_path]
            current_words = file_words
        else:
            current_chunk.append(file_path)
            current_words += file_words
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def generate_split_markdown(repo_path: Path, files: list[Path], part_num: int, total_parts: int) -> tuple[str, int]:
    """Generate markdown content for a split part."""
    repo_name = repo_path.name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"# Repository: {repo_name} (Part {part_num}/{total_parts})",
        f"",
        f"Generated: {timestamp}",
        f"",
        f"Files in this part: {len(files)}",
        f"",
        f"---",
        f"",
    ]
    
    word_count = 0
    
    for file_path in files:
        rel_path = file_path.relative_to(repo_path)
        content = read_file_content(file_path)
        
        if content is None:
            continue
        
        language = get_language(file_path)
        
        lines.append(f"## File: {rel_path}")
        lines.append("")
        lines.append(f"```{language}")
        lines.append(content.rstrip())
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        word_count += len(content.split())
    
    return "\n".join(lines), word_count


def check_notebooklm_limits(content: str, word_count: int) -> tuple[bool, str]:
    """Check if content meets NotebookLM limits. Returns (is_valid, warning_message)."""
    size_mb = len(content.encode('utf-8')) / (1024 * 1024)
    
    warnings = []
    is_valid = True
    
    if word_count > MAX_WORDS_PER_FILE:
        warnings.append(f"⚠ Word count ({word_count:,}) exceeds NotebookLM limit ({MAX_WORDS_PER_FILE:,})")
        is_valid = False
    
    if size_mb > MAX_FILE_SIZE_MB:
        warnings.append(f"⚠ File size ({size_mb:.1f}MB) exceeds NotebookLM limit ({MAX_FILE_SIZE_MB}MB)")
        is_valid = False
    
    if not is_valid and warnings:
        return False, "\n".join(warnings)
    
    return True, ""


def generate_manifest(repo_path: Path, output_files: list[Path], total_words: int):
    """Generate a manifest file listing all output parts."""
    manifest_content = [
        f"# Repository Conversion Manifest",
        f"",
        f"Repository: {repo_path.name}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total words: {total_words:,}",
        f"Total parts: {len(output_files)}",
        f"",
        f"## Output Files",
        f"",
    ]
    
    for i, output_file in enumerate(output_files, 1):
        size_mb = output_file.stat().st_size / (1024 * 1024)
        manifest_content.append(f"{i}. `{output_file.name}` ({size_mb:.1f}MB)")
    
    manifest_content.extend([
        f"",
        f"## Instructions",
        f"",
        f"Upload all parts to NotebookLM as separate sources:",
        f"1. Open NotebookLM (notebooklm.google.com)",
        f"2. Create a new notebook",
        f"3. Upload each part file as a separate source",
        f"4. NotebookLM will combine them for unified search and analysis",
        f"",
    ])
    
    return "\n".join(manifest_content)


def update_gitignore(repo_path: Path):
    """Add our output to .gitignore."""
    gitignore_path = repo_path / ".gitignore"
    marker = "# repo2notebook"
    entries_to_add = [
        "",
        marker,
        f"# {GITHUB_URL}",
        f"{OUTPUT_DIR}/",
        "repo2notebook.py",
    ]
    
    # Read existing content
    existing_content = ""
    if gitignore_path.exists():
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
        except Exception:
            pass
    
    # Check if already added
    if marker in existing_content:
        return False
    
    # Append our entries
    try:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\n".join(entries_to_add))
            f.write("\n")
        return True
    except Exception:
        return False


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Convert code repository to NotebookLM-compatible format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Process current directory
  %(prog)s /path/to/repo       # Process specific directory
  %(prog)s --split .           # Auto-split if exceeds limits
  %(prog)s --max-words 300000  # Custom word limit
  %(prog)s --exclude "*.log" --exclude "test_*"  # Exclude patterns
  %(prog)s --exclude-file .excludes  # Read patterns from file
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Path to repository (default: current directory)'
    )
    
    parser.add_argument(
        '--max-words',
        type=int,
        default=MAX_WORDS_PER_FILE,
        help=f'Maximum words per output file (default: {MAX_WORDS_PER_FILE:,})'
    )
    
    parser.add_argument(
        '--split',
        action='store_true',
        help='Enable automatic splitting if exceeds limit'
    )
    
    parser.add_argument(
        '--no-split',
        action='store_true',
        help='Disable splitting (error if too large)'
    )
    
    parser.add_argument(
        '--exclude',
        action='append',
        metavar='PATTERN',
        help='Exclude files/directories matching pattern (can be used multiple times)'
    )
    
    parser.add_argument(
        '--exclude-file',
        metavar='FILE',
        help='Read exclude patterns from file (one pattern per line)'
    )
    
    args = parser.parse_args()
    
    # Determine repo path
    repo_path = Path(args.directory).resolve()
    max_words = args.max_words
    auto_split = args.split or not args.no_split  # Default is True unless --no-split
    
    # Collect exclude patterns
    exclude_patterns = []
    if args.exclude:
        exclude_patterns.extend(args.exclude)
    
    if args.exclude_file:
        exclude_file_path = Path(args.exclude_file)
        if not exclude_file_path.exists():
            print(f"Error: Exclude file does not exist: {exclude_file_path}")
            sys.exit(1)
        
        try:
            with open(exclude_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        exclude_patterns.append(line)
        except Exception as e:
            print(f"Error reading exclude file: {e}")
            sys.exit(1)
    
    # Validate
    if not repo_path.exists():
        print(f"Error: Path does not exist: {repo_path}")
        sys.exit(1)
    
    if not repo_path.is_dir():
        print(f"Error: Path is not a directory: {repo_path}")
        sys.exit(1)
    
    print(f"Processing: {repo_path}")
    
    if exclude_patterns:
        print(f"Custom exclude patterns: {len(exclude_patterns)}")
        if len(exclude_patterns) <= 5:
            for pattern in exclude_patterns:
                print(f"  • {pattern}")
        else:
            for pattern in exclude_patterns[:5]:
                print(f"  • {pattern}")
            print(f"  • ... and {len(exclude_patterns) - 5} more")
    
    print()
    
    # Collect files
    print("Scanning files...")
    files, stats = collect_files(repo_path, exclude_patterns)
    print_collection_stats(stats)
    print()
    
    if not files:
        print("No files found to process.")
        sys.exit(0)
    
    # Create output directory
    output_dir = repo_path / OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    
    # Generate markdown (check if splitting needed)
    print("Generating markdown...")
    content, word_count = generate_markdown(repo_path, files)
    
    # Check NotebookLM limits
    is_valid, warning = check_notebooklm_limits(content, word_count)
    
    if not is_valid:
        print(warning)
        print()
        
        if not auto_split:
            print("❌ Output exceeds NotebookLM limits!")
            print()
            print("Options:")
            print("  1. Run with --split to automatically split into multiple files")
            print("  2. Run with --max-words <number> to set custom limit")
            print("  3. Manually reduce repository size")
            sys.exit(1)
        
        print("📦 Splitting output into multiple files...")
        print()
        
        # Split files into chunks
        chunks = split_files_into_chunks(files, repo_path, max_words)
        print(f"Split into {len(chunks)} parts")
        print()
        
        # Generate each part
        output_files = []
        total_words = 0
        
        for i, chunk_files in enumerate(chunks, 1):
            part_content, part_words = generate_split_markdown(
                repo_path, chunk_files, i, len(chunks)
            )
            
            total_words += part_words
            
            # Generate filename
            output_filename = get_output_filename(repo_path)
            base_name = output_filename.rsplit('.', 1)[0]
            ext = output_filename.rsplit('.', 1)[1] if '.' in output_filename else 'md'
            part_filename = f"{base_name}-part{i}.{ext}"
            
            output_path = output_dir / part_filename
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(part_content)
            
            output_files.append(output_path)
            
            size_mb = len(part_content.encode('utf-8')) / (1024 * 1024)
            print(f"  Part {i}/{len(chunks)}: {part_words:,} words, {size_mb:.1f}MB")
            print(f"  ✓ {output_path}")
            print()
        
        # Generate manifest
        manifest_content = generate_manifest(repo_path, output_files, total_words)
        manifest_path = output_dir / "MANIFEST.md"
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest_content)
        
        print(f"📋 Manifest: {manifest_path}")
        print()
        print(f"Total word count: {total_words:,}")
        print()
        print("✅ Done! Upload all parts to NotebookLM as separate sources.")
        
    else:
        # Single file output (fits within limits)
        print(f"Word count: {word_count:,}")
        
        size_mb = len(content.encode('utf-8')) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB * 0.8 or word_count > max_words * 0.8:
            print(f"⚠ Warning: Approaching NotebookLM limits ({size_mb:.1f}MB, {word_count:,} words)")
            print(f"   Consider using --split for better NotebookLM compatibility")
        print()
        
        # Write output
        output_filename = get_output_filename(repo_path)
        output_path = output_dir / output_filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✓ Output: {output_path}")
        print()
        print("✅ Done! Upload the markdown file to NotebookLM.")
    
    # Update .gitignore
    if update_gitignore(repo_path):
        print(f"✓ Updated .gitignore")


if __name__ == "__main__":
    main()
