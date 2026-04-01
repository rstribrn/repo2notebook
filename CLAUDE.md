# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔧 Common Commands

### Development & Testing
- Run all tests: `./tests/run_tests.sh`
- Run specific test: `python3 -m pytest tests/unit/test_exclude_patterns.py -v`
- Linting: No formal linting setup, but code follows consistent style

### Usage Examples
- Basic conversion: `python3 repo2notebook.py /path/to/repo`
- Recommended (with wrapper): `./repo2notebook-wrapper.sh /path/to/repo`
- Dry-run first: `./repo2notebook-wrapper.sh --dry-run --verbose /path/to/repo`
- Large repos (auto-split): `./repo2notebook-wrapper.sh --split --verbose /path/to/repo`
- Custom exclusions: `./repo2notebook-wrapper.sh --exclude "test_*" --exclude "*.log" /path/to/repo`
- Strict mode (no splitting): `./repo2notebook-wrapper.sh --no-split /path/to/repo`

### Project Structure
- `repo2notebook.py`: Main conversion script
- `repo2notebook-wrapper.sh`: Secure wrapper with security checks
- `tests/`: Unit and integration tests
- `_repo2notebook/`: Output directory (generated)
- `.repo2notebookignore`: Custom exclusion patterns (like .gitignore)

### Architecture Overview
The tool has two main components:
1. **Core converter** (`repo2notebook.py`): Processes files, applies exclusions, splits large outputs
2. **Security wrapper** (`repo2notebook-wrapper.sh`): Adds sensitive file detection, size validation, git status checks

Key features:
- Automatic splitting when output exceeds NotebookLM limits (400k words safety margin)
- Binary file detection (70+ types including images, videos, executables, Java keystores)
- Respects `.gitignore` and `.repo2notebookignore` files
- Security scanning for SSH keys, certificates, environment files, credentials
- Supports 50+ languages with proper syntax highlighting in markdown output

### Output Format
- Single file: `_repo2notebook/github-user-repo.md`
- Multi-part (large repos): `_repo2notebook/repo-part[N].md` + `MANIFEST.md`
- MANIFEST.md contains instructions for uploading parts to NotebookLM as separate sources

### Best Practices
1. Always run `--dry-run --verbose` first to preview what will be processed
2. Use the wrapper script for security checks (especially important for private repos)
3. Enable `--split` for large repositories (default behavior)
4. Review output in `_repo2notebook/` before uploading to NotebookLM
5. For iterative work, clean output directory: `rm -rf _repo2notebook/`