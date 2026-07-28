# USCIS Status Checker

A Python package that scrapes the USCIS website and returns the latest status for a case.

## Prerequisites

- Python 3.8+
- Chromium or Google Chrome installed
- Xvfb (`sudo apt install xvfb` on Debian/Ubuntu)

## Installation

```bash
pip install uscis-case-status
```

Or install from source:

```bash
pip install .
```

### As an agent skill

This repo ships a [SKILL.md](SKILL.md) so coding agents (Claude Code, Cursor, Codex, etc.) can check case status for you. Install it with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills add pkhanpara/uscis-case-status
```

Useful variants:

```bash
# Install for a specific agent
npx skills add pkhanpara/uscis-case-status -a claude-code

# Install globally (user directory) instead of the current project
npx skills add pkhanpara/uscis-case-status -g -y
```

The skill shells out to `python -m uscis_case_status`, so install the package (above) as well.

## Usage

### CLI

```bash
# Using the console script
uscis-case-status EAC1234567890

# Or using the Python module
python -m uscis_case_status EAC1234567890
```

Output:

```
Case:    EAC1234567890
Date:    01/15/2026
Status:  On January 15, 2026, your Form I-765 ...
```

Use `--help` for usage info:

```bash
uscis-case-status --help
```

### Python API

```python
from uscis_case_status import get_case_status

result = get_case_status("EAC1234567890")
print(result["date"])    # e.g. "01/15/2026"
print(result["status"])  # Full status message text
```

`get_case_status()` returns a dict with:

- `date` — the date the status was last updated (MM/DD/YYYY)
- `status` — the full status message text

Raises `ValueError` if the case ID is invalid or the status cannot be parsed.

## Building a Wheel

```bash
pip install build
python -m build --wheel
```

The `.whl` file will be in the `dist/` directory.
