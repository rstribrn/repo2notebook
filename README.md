# repo2notebook - Repository to NotebookLM Converter

Convert any code repository into NotebookLM-compatible markdown format with automatic splitting for large repositories.

## 🎯 Features

- ✅ **NotebookLM Optimized**: Automatic compliance with NotebookLM limits (500k words, 50MB)
- ✅ **Smart Splitting**: Automatically splits large repositories into multiple parts
- ✅ **Binary Detection**: Advanced detection and filtering of binary files
- ✅ **Custom Exclusions**: Flexible `--exclude` patterns and exclude files
- ✅ **Security Scanning**: Detects sensitive files before conversion
- ✅ **Git Integration**: Automatic naming from Git remote URLs
- ✅ **Format Support**: 50+ programming languages with proper syntax highlighting
- ✅ **Gitignore Respect**: Honors your `.gitignore` patterns
- ✅ **Wrapper Script**: Secure bash wrapper with advanced validation

## 📋 Requirements

- Python 3.7+
- Bash (for wrapper script)
- Git (optional, for automatic naming)

## 🚀 Quick Start

### Basic Usage

```bash
# Convert current directory
python3 repo2notebook.py

# Convert specific directory
python3 repo2notebook.py /path/to/repo

# Auto-split large repositories
python3 repo2notebook.py --split /path/to/repo
```

### Using the Wrapper (Recommended)

```bash
# Secure conversion with safety checks
./repo2notebook-wrapper.sh /path/to/repo

# Dry-run first (recommended)
./repo2notebook-wrapper.sh --dry-run /path/to/repo

# Verbose output with auto-split
./repo2notebook-wrapper.sh --verbose --split /path/to/repo
```

## 📖 Command-Line Options

### repo2notebook.py

```bash
python3 repo2notebook.py [OPTIONS] [DIRECTORY]

Options:
  -h, --help              Show help message
  --split                 Enable auto-split for large repos (default: ON)
  --no-split              Disable splitting (error if too large)
  --max-words NUM         Maximum words per file (default: 400,000)
  --exclude PATTERN       Exclude files matching pattern (can use multiple times)
  --exclude-file FILE     Read exclude patterns from file (one per line)
```

### repo2notebook-wrapper.sh

```bash
./repo2notebook-wrapper.sh [OPTIONS] [DIRECTORY]

Options:
  -h, --help              Show help message
  -v, --verbose           Verbose output with detailed stats
  -d, --dry-run           Check only, don't run conversion
  -s, --skip-security     Skip security checks (NOT RECOMMENDED)
  -o, --open              Auto-open output file after conversion
  --split                 Enable auto-split (default: ON)
  --no-split              Disable auto-split (strict mode)
  --max-words NUM         Max words per file (default: 400,000)
  --max-files NUM         Max file count check (default: 10,000)
  --max-size MB           Max total size in MB (default: 500)
  --output-dir DIR        Output directory (default: _repo2notebook)
```

## 📊 NotebookLM Limits

The tool automatically handles NotebookLM's limits:

- **Word Limit**: 500,000 words per source (we use 400k safety margin)
- **File Size**: 50MB per source (we use 45MB safety margin)
- **Sources**: 50 sources per notebook

### Automatic Splitting

When your repository exceeds these limits:

```bash
python3 repo2notebook.py --split /large/repo
```

Output:
```
⚠ Word count (500,060) exceeds NotebookLM limit (400,000)

📦 Splitting output into multiple files...

Split into 2 parts

  Part 1/2: 350,042 words, 1.7MB
  ✓ repo-part1.md

  Part 2/2: 150,018 words, 0.7MB
  ✓ repo-part2.md

📋 Manifest: MANIFEST.md
```

Upload all parts to NotebookLM as separate sources!

## 🛡️ Security Features (Wrapper Script)

The wrapper script includes comprehensive security checks:

### Sensitive File Detection

Automatically scans for:
- SSH keys (`*.pem`, `*.key`, `id_rsa*`)
- Certificates (`*.p12`, `*.pfx`)
- Environment files (`.env*`)
- Credentials and secrets
- OAuth tokens
- Crypto wallets

### Size Validation

- Maximum file count (default: 10,000)
- Maximum repository size (default: 500MB)
- Configurable limits

### Git Status Checks

- Warns about uncommitted changes
- Lists untracked files
- Suggests cleanup

## 📁 Output Structure

### Single File Output

```
_repo2notebook/
└── github-com-user-repo.md  # Full repository content
```

### Multi-Part Output (Large Repos)

```
_repo2notebook/
├── repo-part1.md            # Part 1 of repository
├── repo-part2.md            # Part 2 of repository
├── repo-part3.md            # Part 3 of repository
└── MANIFEST.md              # Instructions and overview
```

## 🎨 Supported Languages

The tool recognizes 50+ languages with proper syntax highlighting:

**Web**: JavaScript, TypeScript, HTML, CSS, SCSS, Vue, Svelte  
**Backend**: Python, Go, Rust, Java, C/C++, C#, PHP, Ruby  
**Mobile**: Swift, Kotlin, Dart  
**Data**: JSON, YAML, TOML, XML, CSV, SQL  
**Shell**: Bash, PowerShell, Batch  
**Others**: GraphQL, Terraform, Dockerfile, Protobuf, and more

## 🔧 Installation

### 1. Download the Scripts

```bash
# Clone or download both files:
# - repo2notebook.py
# - repo2notebook-wrapper.sh

# Make wrapper executable
chmod +x repo2notebook-wrapper.sh
```

### 2. Optional: Install to PATH

```bash
# Copy to local bin
mkdir -p ~/bin
cp repo2notebook.py ~/bin/
cp repo2notebook-wrapper.sh ~/bin/r2n
chmod +x ~/bin/r2n

# Add to PATH (if not already)
echo 'export PATH="$PATH:$HOME/bin"' >> ~/.bashrc
source ~/.bashrc

# Now you can use it from anywhere
r2n /path/to/any/repo
```

### 3. Create Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# repo2notebook aliases
alias r2n="repo2notebook-wrapper.sh"
alias r2n-check="repo2notebook-wrapper.sh --dry-run --verbose"
alias r2n-safe="repo2notebook-wrapper.sh --split --verbose"
```

## 📝 Examples

### Example 1: Quick Conversion

```bash
./repo2notebook-wrapper.sh /path/to/project
```

### Example 2: Safe Workflow (Recommended)

```bash
# 1. Dry-run check first
./repo2notebook-wrapper.sh --dry-run --verbose /path/to/project

# 2. Review output, then convert
./repo2notebook-wrapper.sh --split /path/to/project

# 3. Open result
cd /path/to/project/_repo2notebook
cat MANIFEST.md  # If multiple parts
```

### Example 3: Large Repository

```bash
# For repos over 400k words
python3 repo2notebook.py --split /large/repo

# Or with wrapper
./repo2notebook-wrapper.sh --split --verbose /large/repo
```

### Example 4: Custom Limits

```bash
# Smaller chunks (300k words per file)
python3 repo2notebook.py --split --max-words 300000 /path/to/repo

# With wrapper
./repo2notebook-wrapper.sh --split --max-words 300000 /path/to/repo
```

### Example 5: Strict Mode (No Splitting)

```bash
# Error if exceeds limits (won't auto-split)
python3 repo2notebook.py --no-split /path/to/repo

# With wrapper
./repo2notebook-wrapper.sh --no-split /path/to/repo
```

### Example 6: Exclude Specific Files/Patterns

```bash
# Exclude test files and logs
python3 repo2notebook.py --exclude "test_*" --exclude "*.log" /path/to/repo

# Exclude multiple patterns
python3 repo2notebook.py --exclude "*.tmp" --exclude "debug.*" --exclude "vendor/" /path/to/repo

# Use exclude file
cat > .excludes << EOF
test_*
*.log
debug.*
tmp/
vendor/
EOF

python3 repo2notebook.py --exclude-file .excludes /path/to/repo

# Combine with other options
python3 repo2notebook.py --split --exclude "test_*" --max-words 300000 /path/to/repo
```

## 🎯 Best Practices

### Before Conversion

1. **Clean your repository**
   ```bash
   git clean -fdx  # Remove untracked files
   git stash       # Stash uncommitted changes
   ```

2. **Check size first**
   ```bash
   ./repo2notebook-wrapper.sh --dry-run --verbose .
   ```

3. **Review sensitive files**
   - Remove or gitignore sensitive data
   - Check for `.env` files, keys, credentials

### During Conversion

1. **Use wrapper script** for security checks
2. **Enable auto-split** for large repos
3. **Review verbose output** to catch issues

### After Conversion

1. **Check output size**
   ```bash
   ls -lh _repo2notebook/
   ```

2. **Read MANIFEST.md** (for multi-part outputs)

3. **Upload to NotebookLM**
   - Single file: Upload one markdown file
   - Multiple parts: Upload all parts as separate sources

## 🚨 Troubleshooting

### Issue: "Word count exceeds limit"

**Solution**: Use `--split` flag to enable automatic splitting

```bash
python3 repo2notebook.py --split /path/to/repo
```

### Issue: "Too many files"

**Solution**: Increase limit or clean repository

```bash
# Increase limit
./repo2notebook-wrapper.sh --max-files 20000 /path/to/repo

# Or clean repository
git clean -fdx
```

### Issue: Sensitive files detected

**Solution**: Add to `.gitignore` or skip security checks (not recommended)

```bash
# Add to .gitignore
echo "*.env" >> .gitignore
echo "*.key" >> .gitignore

# Or skip (USE WITH CAUTION)
./repo2notebook-wrapper.sh --skip-security /path/to/repo
```

### Issue: Output too large for NotebookLM

**Solution**: Reduce `--max-words` or exclude more files

```bash
# Smaller chunks
python3 repo2notebook.py --split --max-words 300000 /path/to/repo

# Or exclude more in .gitignore
echo "docs/" >> .gitignore
echo "tests/" >> .gitignore
```

## 📦 What Gets Included?

### ✅ Included

- Source code (all supported languages)
- Configuration files (`.json`, `.yaml`, `.toml`, etc.)
- Documentation (`.md`, `.rst`, `.txt`)
- Build files (`Makefile`, `CMakeLists.txt`, etc.)
- Example environment files (`.env.example`)

### ❌ Excluded (Automatic)

- Version control (`.git/`, `.svn/`)
- Dependencies (`node_modules/`, `vendor/`, `venv/`)
- Build outputs (`dist/`, `build/`, `target/`)
- IDE files (`.idea/`, `.vscode/`)
- Lock files (`*-lock.json`, `*.lock`)
- Binary files (`.exe`, `.dll`, `.so`, `.pyc`)
- Hidden files (except `.env.example`, `.gitignore`)
- Minified files (`*.min.js`, `*.min.css`)
- Large files (detected automatically)

### 🎯 Additional Exclusions

Files matching your `.gitignore` patterns are also excluded.

### 🔧 Custom Exclusions

Use `--exclude` to add your own patterns:

```bash
# Exclude test files
python3 repo2notebook.py --exclude "test_*" --exclude "*_test.py"

# Exclude logs and temporary files
python3 repo2notebook.py --exclude "*.log" --exclude "*.tmp" --exclude "cache/"

# Use an exclude file (one pattern per line)
cat > .repo2notebook-exclude << EOF
# Custom excludes
test_*
*_test.py
*.log
*.tmp
fixtures/
mock_data/
EOF

python3 repo2notebook.py --exclude-file .repo2notebook-exclude
```

Patterns support wildcards (`*`, `?`) and work like `.gitignore` patterns.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Links

- **GitHub**: https://github.com/Appaholics/repo2notebook
- **NotebookLM**: https://notebooklm.google.com

## 💡 Tips

- **Large repos**: Always use `--split` flag
- **Private repos**: Use wrapper script for security checks
- **First time**: Run `--dry-run` to preview
- **Multiple projects**: Upload each as separate NotebookLM sources
- **Updates**: Re-run on same repo to generate fresh version

## 🎓 Use Cases

1. **Code Review**: Upload repo to NotebookLM for AI-assisted review
2. **Documentation**: Generate searchable code documentation
3. **Onboarding**: Help new team members understand codebase
4. **Analysis**: Use NotebookLM to analyze patterns and structure
5. **Backup**: Create readable backup of your code

## 📊 Statistics Example

```bash
./repo2notebook-wrapper.sh --verbose --dry-run /path/to/repo
```

Output:
```
┌─────────────────────────────────────────┐
│  Repository Summary                     │
└─────────────────────────────────────────┘

  📁 Directories: 45
  📄 Files: 234
  💾 Size: 12MB

Files by type:
  .js               89 files
  .py               45 files
  .json             23 files
  .md               12 files
  
Top 5 largest directories:
  4.5M       src/
  2.1M       docs/
  1.8M       tests/
  890K       config/
  456K       scripts/
```

---

**Made with ❤️ for NotebookLM users**
