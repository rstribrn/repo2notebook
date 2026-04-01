#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
constants.py - All configuration constants for repo2notebook

This module centralizes all configuration to avoid duplication between
repo2notebook.py and repo2notebook-wrapper.sh.
"""

# ============================================================================
# OUTPUT & METADATA
# ============================================================================

OUTPUT_DIR = "_repo2notebook"
GITHUB_URL = "https://github.com/rstribrn/repo2notebook"


# ============================================================================
# LIMITS - Core (repo2notebook.py)
# ============================================================================

# NotebookLM limits with safety margin
MAX_WORDS_PER_FILE = 400000  # NotebookLM limit is ~500k, we use 400k for safety
MAX_FILE_SIZE_MB = 45        # NotebookLM limit is 50MB, we use 45MB for safety


# ============================================================================
# LIMITS - Wrapper (security/validation)
# ============================================================================

MAX_FILE_COUNT = 10000
MAX_TOTAL_SIZE_MB = 500
MAX_SINGLE_FILE_MB = 10


# ============================================================================
# TOKEN ESTIMATION
# ============================================================================

# Default ratio: tokens ≈ 0.75 × words for English text
DEFAULT_TOKEN_RATIO = 0.75


# ============================================================================
# ALWAYS EXCLUDE - Hardcoded in Python core (cannot override)
# ============================================================================

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
    # OS files
    ".DS_Store", "Thumbs.db", "desktop.ini",
    
    # Environment/Secrets (but .env.example OK)
    ".env", ".env.local", ".env.production", ".env.staging",
    
    # Build/IDE files
    ".project",              # Eclipse project file
    ".classpath",            # Eclipse classpath
    ".factorypath",          # Eclipse factory path
    
    # Docker/Container
    ".dockerignore",         # Docker ignore rules
    ".maven-dockerexclude",  # Maven Docker excludes
    ".helmignore",           # Helm ignore rules
    
    # Git/CI/CD
    ".gitattributes",        # Git attributes
    ".gitlab-ci.yml",        # GitLab CI config (use gitlab-ci.yml without dot instead)
    
    # Placeholders (empty marker files)
    ".maven-placeholder",
    ".graalvm-placeholder",
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


# ============================================================================
# WRAPPER DEFAULT EXCLUDES (for will_be_excluded preview)
# ============================================================================

# Note: These are used by the wrapper's will_be_excluded() function.
# They should be kept in sync with ALWAYS_EXCLUDE_* but are separate
# because wrapper implements its own matching logic (not using Python code).

DEFAULT_EXCLUDE_DIRS = [
    ".git", ".svn", ".hg",
    "node_modules", "bower_components",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "venv", ".venv", "env", ".env",
    "dist", "build", "out", "_build",
    ".next", ".nuxt", ".expo", ".turbo",
    "target", "bin", "obj", "Debug", "Release",
    "vendor", "Pods", "DerivedData", ".build",
    ".idea", ".vscode", ".vs", ".fleet",
    ".gradle", ".maven",
    "coverage", ".nyc_output", "htmlcov", ".coverage",
    "site-packages", "eggs", "sdist",
    "tmp", "temp", "cache", ".cache",
    "logs", "log",
    OUTPUT_DIR,
]

DEFAULT_EXCLUDE_FILES = [
    ".DS_Store", "Thumbs.db", "desktop.ini",
    ".env", ".env.local", ".env.production",
]

DEFAULT_EXCLUDE_PATTERNS = [
    "*.lock", "*-lock.json", "*-lock.yaml",
    "*.log", "*.tmp", "*.temp", "*.swp", "*.swo", "*~",
    "*.pyc", "*.pyo", "*.pyd", "*.class", "*.dll", "*.exe", "*.so", "*.dylib",
    "*.o", "*.obj", "*.a", "*.lib",
    "*.min.js", "*.min.css", "*.map", "*.chunk.js", "*.bundle.js", "*.bundle.css",
    "*_test.py", "test_*.py", "*_test.go", "*_test.rb",
    "*.spec.js", "*.spec.ts", "*.test.js", "*.test.ts",
    "fixtures.json", "mock_data.*", "test_data.*", "sample_data.*",
    "*.sql.gz", "*.dump", "*.bak", "*.backup",
]


# ============================================================================
# BINARY EXTENSIONS
# ============================================================================

# Used for quick extension-based binary detection
# 70+ file types automatically excluded

BINARY_EXTENSIONS = (
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
    # Oracle Fusion Middleware (Forms, Reports, Libraries)
    ".fmb", ".fmx",         # Oracle Forms Module (binary source, executable)
    ".mmb", ".mmx",         # Oracle Menu Module (binary source, executable)
    ".pll", ".plx",         # Oracle PL/SQL Library (source, executable)
    ".rdf", ".rep", ".rex", # Oracle Reports (definition, template, executable)
    ".olb",                 # Oracle Object Library
    ".ogd",                 # Oracle Graphics Display
    # Other binary
    ".bin", ".dat", ".pak", ".iso", ".img", ".dmg",
)


# ============================================================================
# SENSITIVE FILE PATTERNS
# ============================================================================

# Patterns for security scanner (in addition to .gitignore)
SENSITIVE_PATTERNS = [
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*id_rsa*",
    "*id_dsa*",
    "*.env",
    "*.env.local",
    "*.env.production",
    "*.env.staging",
    "*secret*",
    "*password*",
    "*credentials*",
    "*auth_token*",
    "*.ovpn",
    "*oauth*",
    "*.kdbx",
    "*.asc",
    "*wallet.dat",
]


# ============================================================================
# EXTENSION TO LANGUAGE MAPPING
# ============================================================================

# For markdown code block syntax highlighting
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
