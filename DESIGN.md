# Design

## Problem

The USCIS case status page at `egov.uscis.gov` is behind Cloudflare bot protection and renders as a Next.js single-page application. This means:

1. Simple HTTP requests (e.g. `requests.post()`) are blocked by Cloudflare with a 403.
2. Standard headless Chrome via Selenium is detected as a bot and blocked.
3. The page content is rendered client-side by JavaScript, so raw HTML responses don't contain the status data.

## Approach

### Bypassing Cloudflare

We use [undetected-chromedriver](https://github.com/ultrafuck/undetected-chromedriver), a patched version of Selenium's ChromeDriver that avoids common bot-detection signals (e.g. `navigator.webdriver` flags, ChromeDriver-specific DOM artifacts).

Cloudflare also fingerprints headless browser environments. To avoid this, we run Chrome in **non-headless mode** behind [Xvfb](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml), a virtual X11 framebuffer. This gives Chrome a real display to render into without requiring an actual monitor, making it indistinguishable from a normal desktop browser session.

### Scraping the Status Page

The USCIS site is a Next.js app. The flow is:

1. Navigate to the case status URL.
2. Wait for the `receipt_number` input field to appear (the page loads asynchronously).
3. Enter the case ID and click the "Check Status" submit button.
4. Wait for the result by polling for a `<p>` element that contains the case ID in its text.
5. Extract the status message text and parse the date using a regex pattern (`Month DD, YYYY`).

### Architecture

```
uscisstatus/
  __init__.py    # Core logic: _get_driver(), _quit_driver(), get_case_status()
  __main__.py    # CLI entry point (argparse)
```

- `_get_driver()` — Starts Xvfb, configures undetected-chromedriver, and returns a browser instance. The Xvfb process is attached to the driver for cleanup.
- `_quit_driver(driver)` — Closes the browser and terminates the Xvfb process.
- `get_case_status(case_id)` — The public API. Drives the browser through the form submission flow, extracts the status text, parses the date, and returns `{"status": ..., "date": ...}`.
