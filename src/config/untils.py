import logging
import os

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
