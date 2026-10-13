import os
import re
import pytest
from selenium import webdriver

from pages import OrangeHRM

# Pengaturan lewat environment variable (supaya sama untuk lokal, Grid, dan CI)
BROWSER = os.getenv("BROWSER", "firefox").lower()   # firefox / chrome
HEADLESS = os.getenv("HEADLESS", "0") == "1"
GRID_URL = os.getenv("GRID_URL")                      # contoh: http://localhost:4444


def _options():
    if BROWSER == "chrome":
        opts = webdriver.ChromeOptions()
        if HEADLESS:
            opts.add_argument("--headless=new")
    else:
        opts = webdriver.FirefoxOptions()
        if HEADLESS:
            opts.add_argument("-headless")
    return opts


@pytest.fixture
def driver():
    opts = _options()
    if GRID_URL:
        d = webdriver.Remote(command_executor=GRID_URL, options=opts)
    elif BROWSER == "chrome":
        d = webdriver.Chrome(options=opts)
    else:
        d = webdriver.Firefox(options=opts)
    d.set_window_size(1710, 1073)
    yield d
    d.quit()


@pytest.fixture
def app(driver):
    return OrangeHRM(driver)


@pytest.fixture
def logged_in(app):
    """Setiap test mulai dari kondisi sudah login, jadi test bisa jalan paralel."""
    app.login()
    app.title_of("Dashboard")
    return app


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Simpan screenshot otomatis kalau test gagal."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        d = item.funcargs.get("driver")
        if d:
            os.makedirs("screenshots", exist_ok=True)
            name = re.sub(r"[^A-Za-z0-9_.-]", "_", item.name)
            d.save_screenshot(f"screenshots/{name}.png")
