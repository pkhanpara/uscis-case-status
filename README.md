# USCIS Status Checker

A Python package that scrapes the USCIS website and returns the latest status for a case.

## Prerequisites

- Python 3.8+
- Chromium or Google Chrome installed
- Xvfb (`sudo apt install xvfb` on Debian/Ubuntu)

## Installation

```bash
pip install .
```

Or install in development mode:

```bash
pip install -e .
```

## Usage

### CLI

```bash
# Using the console script
uscisstatus EAC1234567890

# Or using the Python module
python -m uscisstatus EAC1234567890
```

Output:

```
Case:    EAC1234567890
Date:    01/15/2026
Status:  On January 15, 2026, your Form I-765 ...
```

Use `--help` for usage info:

```bash
uscisstatus --help
```

### Python API

```python
from uscisstatus import get_case_status

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
