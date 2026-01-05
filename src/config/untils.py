import logging
import os
import time
from watchdog.observers import Observer
from config.download_handler import DownloadHandler

def setup_logger(log_file="automation.log", log_level=logging.INFO):
    """Mengatur logger untuk mencetak log ke file."""
    # Pastikan folder untuk file log ada
    log_folder = os.path.dirname(log_file)
    if log_folder and not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Konfigurasi logger
    logging.basicConfig(
        filename=log_file,            # Nama file log
        filemode="a",                 # Mode append untuk menambahkan log baru
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=log_level               # Level log (INFO, DEBUG, ERROR, dll.)
    )
    logger = logging.getLogger()
    return logger



def wait_for_download_with_watchdog(expected_filename, download_folder="downloads", timeout=15, logger=None):
    """
    Menunggu hingga file tertentu muncul di folder download menggunakan Watchdog.
    """
    event_handler = DownloadHandler(expected_filename, logger)
    observer = Observer()
    observer.schedule(event_handler, download_folder, recursive=False)
    observer.start()

    try:
        start_time = time.time()
        while not event_handler.file_found:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                if logger:
                    logger.info(f"File '{expected_filename}' tidak ditemukan setelah {timeout} detik.")
                return False  # File tidak ditemukan dalam waktu yang diberikan
            time.sleep(1)  # Tunggu sebelum cek lagi
        return True  # File ditemukan
    finally:
        observer.stop()
        observer.join()

