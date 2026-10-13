"""Helper untuk OrangeHRM (versi sederhana dari Page Object Model)."""
from selenium.common.exceptions import ElementClickInterceptedException
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

    def wait_loader(self):
        """Tunggu overlay loading hilang sebelum klik."""
        self.wait.until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".oxd-form-loader, .oxd-loading-spinner")))

    def click(self, by, locator):
        self.wait_loader()
        el = self.wait.until(EC.element_to_be_clickable((by, locator)))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", el)
        try:
            el.click()
        except ElementClickInterceptedException:
            # cadangan: klik lewat JavaScript kalau masih tertutup elemen lain
            self.driver.execute_script("arguments[0].click();", el)

    def fill(self, by, locator, text):
        self.wait_loader()
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