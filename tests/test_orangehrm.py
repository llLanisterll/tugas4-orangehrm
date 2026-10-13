import random
import sys
import time
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages import BASE_URL

MENUS = ["Leave", "Time", "Recruitment", "Performance",
         "Directory", "Claim", "Buzz", "Dashboard"]

# Mengisi nilai input lewat JavaScript dan memicu event 'input' supaya dikenali aplikasi (Vue).
JS_SET_VALUE = """
const el = arguments[0];
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(el, arguments[1]);
el.dispatchEvent(new Event('input', {bubbles: true}));
el.dispatchEvent(new Event('change', {bubbles: true}));
"""


# ---------- Login / Logout ----------
def test_login_valid(app):
    app.login()
    assert app.title_of("Dashboard").is_displayed()
    assert "dashboard" in app.driver.current_url


def test_login_invalid(app):
    app.login(password="salah123")
    alert = app.visible(By.CSS_SELECTOR, ".oxd-alert-content-text")
    assert "Invalid credentials" in alert.text


def test_logout(logged_in):
    a = logged_in
    a.click(By.CSS_SELECTOR, ".oxd-userdropdown-tab")
    a.click(By.LINK_TEXT, "Logout")
    a.visible(By.NAME, "username")
    assert "auth/login" in a.driver.current_url


# ---------- Menu utama terbuka ----------
@pytest.mark.parametrize("menu", MENUS)
def test_menu_terbuka(logged_in, menu):
    logged_in.open_menu(menu)
    assert logged_in.title_of(menu).is_displayed()


# ---------- Admin ----------
def test_admin_cari_user(logged_in):
    a = logged_in
    a.open_menu("Admin")
    a.title_of("User Management")
    kolom_username = ("//label[normalize-space()='Username']"
                      "/ancestor::div[contains(@class,'oxd-input-group')]//input")
    a.fill(By.XPATH, kolom_username, "Admin")
    a.click(By.XPATH, "//button[normalize-space()='Search']")
    a.wait.until(lambda d: "Admin" in d.find_element(By.CSS_SELECTOR, ".oxd-table-body").text)


def test_admin_form_tambah_user(logged_in):
    a = logged_in
    a.open_menu("Admin")
    a.click(By.XPATH, "//button[contains(normalize-space(),'Add')]")
    assert a.title_of("Add User").is_displayed()
    a.click(By.XPATH, "//button[normalize-space()='Cancel']")
    assert a.title_of("User Management").is_displayed()


# ---------- PIM ----------
def test_pim_tambah_karyawan(logged_in):
    a = logged_in
    a.open_menu("PIM")
    a.title_of("PIM")
    a.click(By.XPATH, "//button[contains(normalize-space(),'Add')]")
    # Di server demo yang lambat, klik 'Add' kadang tidak diproses. Kalau form belum
    # muncul dalam 10 detik, buka halaman Add Employee langsung lewat URL.
    try:
        WebDriverWait(a.driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "firstName")))
    except TimeoutException:
        a.go("/web/index.php/pim/addEmployee")
        WebDriverWait(a.driver, 40).until(
            EC.visibility_of_element_located((By.NAME, "firstName")))
    a.fill(By.NAME, "firstName", "Budi")
    a.fill(By.NAME, "lastName", f"Test{int(time.time())}")  # nama unik tiap run

    # Employee Id terisi otomatis dan sering bentrok di situs demo bersama,
    # jadi kita isi sendiri dengan angka acak (maksimal 10 karakter).
    grup_id = ("//label[normalize-space()='Employee Id']"
               "/ancestor::div[contains(@class,'oxd-input-group')]")
    id_unik = str(random.randint(10000000, 99999999))
    kolom_id = (By.XPATH, grup_id + "//input")
    # Tunggu sampai Employee Id terisi otomatis oleh aplikasi. Kalau kita mengetik
    # sebelum itu, isinya bisa tertimpa lagi oleh nilai otomatis.
    a.wait.until(lambda d: d.find_element(*kolom_id).get_attribute("value") != "")
    modifier = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
    for percobaan in range(3):  # pastikan angka kita benar-benar tertahan di kolom
        a.wait_loader()  # form punya overlay loading; jangan berinteraksi saat masih tampil
        el = a.visible(*kolom_id)
        if percobaan == 0:
            # blok seluruh isi lalu ketik di atasnya (tanpa mengosongkan kolom lebih dulu,
            # karena kolom kosong bisa memicu aplikasi mengisi ulang Employee Id otomatis)
            el.send_keys(modifier, "a")
            el.send_keys(id_unik)
        elif percobaan == 1:
            a.driver.execute_script(JS_SET_VALUE, el, id_unik)   # cara cadangan: JavaScript
        else:
            a.fill(*kolom_id, id_unik)                           # cara biasa
        a.wait_loader()  # tunggu validasi Employee Id (overlay) selesai
        time.sleep(1)
        if a.visible(*kolom_id).get_attribute("value") == id_unik:
            break
    nilai = a.visible(*kolom_id).get_attribute("value")
    assert nilai == id_unik, f"Employee Id berisi '{nilai}', seharusnya '{id_unik}'"
    time.sleep(2)  # beri waktu validasi Employee Id (berjalan di server)
    a.wait.until(lambda d: not d.find_elements(
        By.XPATH, grup_id + "//*[contains(@class,'oxd-input-field-error-message')]"))

    a.click(By.XPATH, "//button[normalize-space()='Save']")
    # setelah Save, halaman pindah ke detail karyawan (server demo bisa lambat)
    WebDriverWait(a.driver, 40).until(EC.url_contains("viewPersonalDetails"))
    assert a.title_of("Personal Details").is_displayed()


# ---------- Leave ----------
def test_leave_list(logged_in):
    a = logged_in
    a.go("/web/index.php/leave/viewLeaveList")
    a.click(By.XPATH, "//button[normalize-space()='Search']")
    assert a.title_of("Leave").is_displayed()


# ---------- My Info ----------
def test_myinfo_simpan(logged_in):
    a = logged_in
    a.open_menu("My Info")
    a.visible(By.NAME, "firstName")
    a.click(By.XPATH, "(//button[normalize-space()='Save'])[1]")
    assert a.visible(By.CSS_SELECTOR, ".oxd-toast").is_displayed()


# ---------- Directory ----------
def test_directory_cari(logged_in):
    a = logged_in
    a.open_menu("Directory")
    a.fill(By.CSS_SELECTOR, ".oxd-autocomplete-text-input > input", "Peter")
    a.click(By.XPATH, "//button[normalize-space()='Search']")
    assert a.title_of("Directory").is_displayed()


# ---------- Maintenance ----------
def test_maintenance_konfirmasi_password(logged_in):
    a = logged_in
    a.open_menu("Maintenance")
    a.fill(By.NAME, "password", "admin123")
    a.click(By.XPATH, "//button[normalize-space()='Confirm']")
    a.wait.until(lambda d: len(d.find_elements(By.NAME, "password")) == 0)
    assert a.title_of("Maintenance").is_displayed()


# ---------- Buzz ----------
def test_buzz_buat_post(logged_in):
    a = logged_in
    teks = f"Halo automation {int(time.time())}"
    a.open_menu("Buzz")
    a.title_of("Buzz")
    # tunggu feed selesai dimuat; kalau kotak diisi terlalu cepat, teks bisa terhapus
    a.wait.until(lambda d: "Comments" in d.find_element(By.TAG_NAME, "body").text)
    kotak = (By.CSS_SELECTOR, ".oxd-buzz-post-input")
    for _ in range(3):  # pastikan teks benar-benar tertahan di kotak
        a.fill(*kotak, teks)
        if a.visible(*kotak).get_attribute("value") == teks:
            break
    a.click(By.XPATH, "//button[normalize-space()='Post']")
    # tunggu sampai post baru muncul di feed
    a.wait.until(lambda d: teks in d.find_element(By.TAG_NAME, "body").text)
    assert a.title_of("Buzz").is_displayed()