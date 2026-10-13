"""Helper untuk OrangeHRM (versi sederhana dari Page Object Model)."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://opensource-demo.orangehrmlive.com"
TIMEOUT = 20


class OrangeHRM:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)  # explicit wait

    def go(self, path):
        self.driver.get(f"{BASE_URL}{path}")

    def visible(self, by, locator):
        return self.wait.until(EC.visibility_of_element_located((by, locator)))

    def click(self, by, locator):
        self.wait.until(EC.element_to_be_clickable((by, locator))).click()

    def fill(self, by, locator, text):
        el = self.visible(by, locator)
        el.clear()
        el.send_keys(text)

    def title_of(self, name):
        """Tunggu judul halaman (h6) tampil, setara 'wait for element visible' di IDE."""
        return self.visible(By.XPATH, f"//h6[normalize-space()='{name}']")

    def login(self, username="Admin", password="admin123"):
        self.go("/web/index.php/auth/login")
        self.fill(By.NAME, "username", username)
        self.fill(By.NAME, "password", password)
        self.click(By.CSS_SELECTOR, "button[type='submit']")

    def open_menu(self, menu):
        self.click(By.LINK_TEXT, menu)
