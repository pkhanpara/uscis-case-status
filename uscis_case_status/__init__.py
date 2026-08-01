import re
import os
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

CASE_DATE_PATTERN = r"[A-Za-z]+\s\d+,\s\d+"
URL = "https://egov.uscis.gov/casestatus/mycasestatus.do"


def _start_xvfb():
    """Start Xvfb on a free display and return (process, ':<n>').

    -displayfd lets Xvfb pick the first unused display itself and write the
    number back to us, so we never collide with another Xvfb already on the
    machine (e.g. one started by xvfb-run -a).
    """
    read_fd, write_fd = os.pipe()
    try:
        xvfb = subprocess.Popen(
            ["Xvfb", "-displayfd", str(write_fd), "-screen", "0", "1920x1080x24"],
            pass_fds=(write_fd,),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        os.close(read_fd)
        os.close(write_fd)
        raise RuntimeError("Xvfb is required; install with: sudo apt install xvfb")
    os.close(write_fd)

    # Blocks until Xvfb is listening, or returns empty if it died first
    with os.fdopen(read_fd) as f:
        display_num = f.readline().strip()

    if not display_num:
        xvfb.terminate()
        err = xvfb.stderr.read().decode(errors="replace").strip()
        raise RuntimeError(f"Xvfb failed to start: {err}")

    return xvfb, f":{display_num}"


def _get_driver():
    # Cloudflare blocks headless browsers, so we use a virtual display
    xvfb, display = _start_xvfb()
    prev_display = os.environ.get("DISPLAY")
    os.environ["DISPLAY"] = display

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/snap/chromium/current/usr/lib/chromium-browser/chrome"
    try:
        driver = uc.Chrome(options=options, version_main=150)
    except Exception:
        _stop_xvfb(xvfb, prev_display)
        raise
    driver._xvfb = xvfb
    driver._prev_display = prev_display
    return driver


def _stop_xvfb(xvfb, prev_display):
    if prev_display is None:
        os.environ.pop("DISPLAY", None)
    else:
        os.environ["DISPLAY"] = prev_display
    xvfb.terminate()
    try:
        xvfb.wait(timeout=5)
    except subprocess.TimeoutExpired:
        xvfb.kill()
        xvfb.wait()


def _quit_driver(driver):
    driver.quit()
    if hasattr(driver, "_xvfb"):
        _stop_xvfb(driver._xvfb, getattr(driver, "_prev_display", None))


def get_case_status(case_id):
    driver = _get_driver()
    try:
        driver.get(URL)

        wait = WebDriverWait(driver, 15)

        # Wait for the receipt number input field
        receipt_input = wait.until(
            EC.presence_of_element_located((By.ID, "receipt_number"))
        )
        receipt_input.clear()
        receipt_input.send_keys(case_id)

        # Click the Check Status button
        check_button = driver.find_element(
            By.XPATH, "//button[@type='submit' and contains(text(), 'Check Status')]"
        )
        check_button.click()

        # Wait for the status paragraph containing the case ID to appear
        wait.until(
            lambda d: any(
                case_id in p.text for p in d.find_elements(By.TAG_NAME, "p")
            )
        )

        # Extract the status message
        status_message = ""
        for p in driver.find_elements(By.TAG_NAME, "p"):
            text = p.text.strip()
            if case_id in text:
                status_message = text
                break

        if not status_message:
            raise ValueError("Please make sure your case id is valid")

        p = re.search(CASE_DATE_PATTERN, status_message)
        if p is not None:
            match = p.group(0)
            last_update_date = datetime.strptime(match, "%B %d, %Y")
            last_update_date = last_update_date.strftime("%m/%d/%Y")
            return {"status": status_message, "date": last_update_date}
        else:
            raise ValueError("Could not parse date from status message")
    finally:
        _quit_driver(driver)
