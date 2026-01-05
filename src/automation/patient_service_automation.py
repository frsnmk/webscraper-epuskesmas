import os
import time
from automation.base_automation import BaseAutomation
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from calendar import monthrange
from datetime import datetime
from config.untils import wait_for_download_with_watchdog


class PatientServiceAutomation(BaseAutomation):
    def __init__(self, driver, base_url, username, password, logger, download_folder_location):
        self.driver = driver
        self.base_url = base_url
        self.username = username
        self.password = password
        self.logger = logger
        self.download_folder_location = download_folder_location
        self.index_file_download = 0;
    
    def login(self):
        self.driver.get(f"{self.base_url}/login")
        self.driver.find_element(By.ID, "email").send_keys(self.username)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/home")
        )
        self.logger.info("Login berhasil.")

    def navigate_to_visits(self):
        self.driver.get(f"{self.base_url}/laporanpelayananpasien")
        time.sleep(5)

    
    def fill_filter(self, start_date, end_date):
        """Mengisi filter tanggal dan klik tombol filter."""
        # Tunggu elemen 'dari_tanggal' dapat diinteraksi
        dari_tanggal = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "search[dari_tanggal]"))
        )
        self.scroll_to_element(self.driver, dari_tanggal)  # Scroll agar elemen terlihat
        dari_tanggal.clear()
        dari_tanggal.send_keys(start_date)
        self.logger.info(f"Berhasil mengisi filter tanggal {start_date}")
        # Tunggu elemen 'sampai_tanggal' dapat diinteraksi
        sampai_tanggal = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "search[sampai_tanggal]"))
        )
        self.scroll_to_element(self.driver, sampai_tanggal)  # Scroll agar elemen terlihat
        sampai_tanggal.clear()
        sampai_tanggal.send_keys(end_date)
        self.logger.info(f"Berhasil mengisi filter tanggal {end_date}")

        # Klik tombol 'tampilkan'
        tampilkan_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "button_tampilkan"))
        )
        self.scroll_to_element(self.driver, tampilkan_button)  # Scroll agar tombol terlihat
        tampilkan_button.click()
        self.logger.info(f"Mengklik tombol tampilkan")

        # Tunggu hingga data yang sesuai muncul
        expected_text = f"{start_date} - {end_date}"
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, f'''//table/thead/tr[3]/th[2][contains(text(), '{start_date} - {end_date}')]'''), expected_text) # Buat pelayanan
        )
        self.logger.info("Berhasil melakukan pengecekan tanggal yang diisi dengan tanggal yang ada di laporan dengan tanggal yang diisi")

    def show_export_modal(self):
        """Klik tombol export dan tunggu file diunduh."""
        self.driver.find_element(By.ID, "button_export").click()
        self.logger.info("Mengklik tombol export untuk memunculkan modal")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="modal"]/div/div/div[1]/h5'), "Download Laporan Harian - Pelayanan Pasien")
            )
            self.logger.info("Berhasil membuka modal")
            self.export_button()
        except:
            if self.handle_error_and_retry():
                if not self.check_or_reopen_modal():
                    self.logger.info("Modal dibuka ulang menggunakan tombol export.")
                self.export_button()
            expected_file_download_name = f"Laporan Harian - Pelayanan Pasien ({self.index_file_download}).xlsx"
            if self.wait_for_download(expected_file_download_name, self.download_folder_location):
                self.logger.info(f"File {expected_file_download_name} berhasil diunduh.")
                self.index_file_download += 1

    def get_end_date(self, month, year):
        """
        Menghitung tanggal terakhir bulan tertentu.
        Jika tanggal terakhir lebih dari hari ini, gunakan hari ini sebagai last day.
        """
        today = datetime.today()
        
        # Hitung tanggal terakhir bulan
        last_day_of_month = monthrange(year, month)[1]

        # Tentukan apakah last day melewati hari ini
        if year == today.year and month == today.month and last_day_of_month > today.day:
            last_day = today.day
        else:
            last_day = last_day_of_month

        return f"{last_day:02d}-{month:02d}-{year}"
    

    def export_button(self):
        """Mengklik semua excel di modal"""
        export_buttons = self.driver.find_elements(By.XPATH, "/html/body/div[3]/div//button[contains(text(), 'Export Excel')]")
        self.logger.info(f"Ditemukan {len(export_buttons)} tombol Export Excel.")
        for index, button in enumerate(export_buttons, start=0):
            button.click()
            if self.handle_error_and_retry():
                if not self.check_or_reopen_modal():
                    self.logger.info("Modal dibuka ulang menggunakan tombol export.")
                self.export_button()
            self.logger.info(f"Mengklik tombol Export Excel ke-{index+1}")

            expected_file_download_name = ""
            if(self.index_file_download == 0):
                expected_file_download_name = "Laporan Harian - Pelayanan Pasien.xlsx"
            else:
                expected_file_download_name = f"Laporan Harian - Pelayanan Pasien ({self.index_file_download}).xlsx"
            
            if self.wait_for_download(expected_file_download_name, self.download_folder_location):
                self.logger.info(f"File {expected_file_download_name} berhasil diunduh.")
                self.index_file_download += 1
            # time.sleep(5)  # Ganti dengan logika validasi file download jika perlu
        
        # Tutup modal
        exit_modal_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/div[1]/button"))
        )

        exit_modal_button.click()

    # def wait_for_download(self, filename, download_folder="downloads", timeout=15):
    #     """Menunggu hingga file tertentu muncul di folder download."""
    #     self.logger.info("Waiting for download...")
    #     file_path = os.path.join(download_folder, filename)
    #     self.logger.info(f"Mengecek file '{filename} di {file_path}'")
    #     for _ in range(timeout):
    #         if os.path.exists(file_path):
    #             return True  # File ditemukan
    #         time.sleep(1)  # Tunggu 3 detik sebelum cek lagi
    #     self.logger.info(f"File '{filename}' tidak ditemukan setelah {timeout} detik.")
    #     return True
    

    def wait_for_download(self, filename, download_folder="downloads", timeout=15):
        """Menunggu hingga file tertentu muncul di folder download menggunakan Watchdog."""
        return wait_for_download_with_watchdog(
            expected_filename=filename,
            download_folder=download_folder,
            timeout=timeout,
            logger=self.logger
        )


    def scroll_to_element(self, driver, element):
        """Scroll ke elemen agar terlihat di viewport."""
        driver.execute_script("arguments[0].scrollIntoView(true);", element)


    def automate_monthly_export(self, start_year, end_year):
        """Automasi export Excel per bulan."""
        for year in range(start_year, end_year + 1):  # Iterasi setiap tahun
            for month in range(1, 13):  # Iterasi setiap bulan
                # Hitung start_date dan end_date
                start_date = f"01-{month:02d}-{year}"
                end_date = self.get_end_date(month, year)

                self.logger.info(f"Processing: {start_date} to {end_date}")

                # Isi filter dengan start_date dan end_date
                self.fill_filter(start_date, end_date)

                # Klik tombol export modal
                self.show_export_modal()

    def handle_error_and_retry(self, retries=3):
        for attempt in range(1, retries+1):
            self.logger.info(f"Pengecekan error Excel ({self.index_file_download}), Mencoba Ulang Progses. Percobaan ke- {attempt}")
            if "ePuskesmas.id - 5xx" in self.driver.title:
                self.logger.info(f"Terjadi error 500 pada percobaan ke-{attempt}")
                self.logger.info(f"Mencoba Ulang Progses. Percobaan ke- {attempt}")
                self.driver.back()
                return True
            else:
                self.logger.info("Untungnya tidak ada error")
                return False
        raise Exception("Gagal mengatasi error 500 setalah beberpa percobaan")


    def check_or_reopen_modal(self):
        """
        Mengecek apakah modal pelayanan terbuka. Jika tidak, cari tombol untuk membuka modal kembali.
        """
        try:
            self.logger.info("Mengecek apakah modal pelayanan terbuka setelah browser di back...")
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, '//*[@id="modal"]/div/div/div[1]/h5'), 
                    "Download Laporan Harian - Pelayanan Pasien"
                )
            )
            self.logger.info("Modal pelayanan terbuka ...")
            return True
        except:
            self.logger.warning("Modal tidak ditemukan. Mencari tombol export untuk membuka modal...")
            # Cari tombol untuk membuka modal kembali
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "button_export"))
            )
            button.click()
            self.logger.info("Tombol export diklik untuk membuka modal ...")
            return False


