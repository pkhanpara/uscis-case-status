# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python package that scrapes the USCIS website to retrieve case status information. USCIS sits
behind Cloudflare, which blocks headless browsers, so the package drives a *headful* Chrome via
`undetected_chromedriver` on a throwaway Xvfb virtual display. It returns a dict with `status`
(message text) and `date` (last update date as MM/DD/YYYY).

## Setup & Install

```bash
pip install -e .
```

Dependencies: `undetected-chromedriver`, `selenium`. Also requires system `Xvfb`
(`sudo apt install xvfb`) and a Chrome/Chromium installation.

## Usage

```bash
uscis-case-status SRC1234567890        # console script
python3 -m uscis_case_status SRC1234567890   # equivalent
```

```python
from uscis_case_status import get_case_status
get_case_status("SRC1234567890")  # -> {'status': ..., 'date': '06/17/2026'}
```

## Architecture

Single-module package: all scraping logic lives in `uscis_case_status/__init__.py`, with the CLI
in `uscis_case_status/__main__.py`.

- `get_case_status(case_id)` — public API. Starts the browser, fills the receipt-number field,
  clicks **Check Status**, waits for a `<p>` containing the case ID, and regex-extracts the
  date from the status text. Raises `ValueError` if the case ID is invalid or the date can't be
  parsed. Runs inside `with _browser() as driver:`, so the browser always tears down.
- `_browser()` — a `@contextmanager` owning the browser lifecycle. It holds the Xvfb process and
  the previous `DISPLAY` in its own scope and, on exit, quits the driver, reaps the server and
  restores `DISPLAY` — including when `uc.Chrome()` itself fails.
- `_start_xvfb()` / `_stop_xvfb()` — virtual display lifecycle.
- `_find_chrome()` / `_chrome_major_version()` — locate the browser and derive the version to
  pin `undetected_chromedriver` to.

Parsing uses Selenium locators (`By`, `WebDriverWait`) against the live DOM — there is no
separate HTML-parsing step and no lxml dependency.

### Gotchas

- **Never hardcode an Xvfb display number.** `Xvfb :99` collides with any other server already
  on that display (`xvfb-run -a` commonly takes `:99`+), and the resulting failure surfaces as a
  misleading `chrome not reachable` from chromedriver — Chrome connects to the *other* server,
  fails MIT-MAGIC-COOKIE auth, and exits before opening its DevTools port. `_start_xvfb()` uses
  `Xvfb -displayfd` to let Xvfb pick a free display and report it back.
- **Don't point `binary_location` at a snap wrapper.** `/snap/bin/chromium` and
  `/usr/bin/chromium-browser` re-exec into snap confinement, which Selenium cannot attach to.
  `_is_launchable()` filters them out in favour of the real ELF binary inside the snap.

## Testing

There is no unit test suite. Two things guard the code instead:

- **CI** — `.github/workflows/pylint.yml` runs `pylint` over every tracked `*.py` on push
  (Python 3.8/3.9/3.10). It installs the package first, so the lint sees the real selenium and
  undetected-chromedriver APIs; without that every import is a bogus `E0401`.
- **A pre-commit hook** — `.githooks/pre-commit`, activated once per clone with
  `git config core.hooksPath .githooks`. It runs pylint on every commit, plus two live checks that
  only fire when the commit stages a `*.py` file (~1-2 min, needs network, Chrome and Xvfb): a
  known-good receipt number must return a `MM/DD/YYYY` date, and a bogus one must exit non-zero with
  a friendly `Error:` line rather than a traceback. It then confirms no Xvfb server leaked, which is
  what regresses if browser teardown breaks. Escape hatches: `SKIP_BROWSER_TESTS=1 git commit ...`
  for the slow half, `git commit --no-verify` for all of it.

To check for leaked servers by hand: `ps -eo args | grep '^Xvfb'`.

Note the hook checks the **working tree**, not the staged snapshot — after a partial `git add -p` it
validates code that isn't exactly what's being committed. Stashing unstaged changes around the run
was considered and rejected: a failed `stash pop` can lose work, a worse failure mode than this gap.
