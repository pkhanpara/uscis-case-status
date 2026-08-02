# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-08-01

First stable release. The public API — `get_case_status(case_id)` returning
`{"status": ..., "date": ...}` — is now considered stable.

### Added

- `SKILL.md` agent skill definition, installable with `npx skills add pkhanpara/uscis-case-status`.
- Automatic Chrome/Chromium discovery on `PATH` (`chromium`, `chromium-browser`,
  `google-chrome`, `google-chrome-stable`), with the snap path as a fallback.
- Automatic Chrome major-version detection to pin `undetected-chromedriver`.
- Pylint GitHub Actions workflow across Python 3.8/3.9/3.10, running with the package installed
  so third-party imports resolve.
- Optional pre-commit hook (`.githooks/pre-commit`) that lints and, for Python commits, runs the
  scraper against the live site for a valid and an invalid receipt number and checks that no Xvfb
  server leaked. Enable with `git config core.hooksPath .githooks`; skip the slow half with
  `SKIP_BROWSER_TESTS=1`.
- Module and function docstrings throughout.

### Changed

- Xvfb is started with `-displayfd` and allocates a free display instead of hardcoding `:99`.
- Chrome is resolved before Xvfb starts, so a missing browser fails fast without leaking a
  display server.
- Browser lifetime is managed by a `_browser()` context manager, replacing the internal
  `_get_driver()` / `_quit_driver()` pair and the `_xvfb` / `_prev_display` attributes stashed on
  the driver. `DISPLAY` restore and Xvfb reaping now happen in one `finally`, covering a failed
  `uc.Chrome()` startup as well.

### Fixed

- `chrome not reachable` failures when another Xvfb already occupied display `:99`.
- Snap wrapper scripts being selected as the browser binary, which Selenium cannot drive.
- Silent failure when Xvfb is not installed; now reports
  `Xvfb is required; install with: sudo apt install xvfb`.
- Removed the `sleep(1)` race between starting Xvfb and launching Chrome.

[1.0.0]: https://github.com/pkhanpara/uscis-case-status/releases/tag/v1.0.0
