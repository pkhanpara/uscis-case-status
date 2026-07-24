# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python package that scrapes the USCIS website to retrieve case status information. It uses Selenium (headless Chrome) to load the case status page and lxml to parse the response, returning a dict with `status` (message text) and `date` (last update date as MM/DD/YYYY).

## Setup & Install

```bash
pip install -e .
```

Dependencies: `selenium`, `lxml`. Requires Chromium/Chrome installed (currently hardcoded to `/snap/chromium/current/usr/lib/chromium-browser/chrome`).

## Architecture

Single-module package: all logic lives in `uscis_case_status/__init__.py`.

- `get_case_status(case_id)` — public API. Launches headless Chrome, submits the case ID to the USCIS form, parses the result page with lxml xpath, extracts the status message and date, returns `{'status': ..., 'date': ...}`.
- `_get_driver()` — internal helper that configures and returns a headless Chrome WebDriver instance.

There are no tests, no CLI entry point, and no CI configuration.
