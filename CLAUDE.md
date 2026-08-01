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
  parsed. Always tears the browser down in a `finally`.
- `_get_driver()` / `_quit_driver(driver)` — browser lifecycle. The driver carries `_xvfb` and
  `_prev_display` attributes so teardown can reap the server and restore `DISPLAY`.
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

There are no automated tests and no CI. Verify changes by running the CLI against a real receipt
number and confirming no Xvfb servers leak (`ps -eo args | grep '^Xvfb'`).
