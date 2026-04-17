# config.py
import logging

# Mapping Batch & Lokasi (Tetap sama)
ALL_BATCHES = {
    "Batch_1": {"Permata": 1, "Blibli": 19, "Jember": 37, "Gudang_Garam": 11, "Sigma": 55},
    "Batch_2": {"Cirebon": 32, "Dago": 21, "Garut": 26, "Gedebage": 31, "Kudus": 35, "Kuningan": 23},
    "Batch_3": {"Lembang": 33, "Majalengka": 38, "Pangandaran": 7, "Purwakarta": 40, "Subang": 6},
    "Batch_4": {"Djarum_Tasikmalaya": 30, "Tegal": 20, "Yudanegara": 34, "Cicadas": 17, "KHZ": 18, "Paskal": 36},
    "Batch_5": {"Khalifah": 49, "Sudirman": 16, "Padang": 15, "McD": 2}
}

SCHEDULE_JAM = ["08-00", "12-00", "16-00", "20-00", "00-00"]
BATCH_LIST = list(ALL_BATCHES.keys())

# Performa & Stabilitas
MAX_WORKERS = 5       # Jumlah batch yang di-upload bersamaan (Thread)
RETRY_COUNT = 3       # Berapa kali coba lagi kalau gagal koneksi
TIMEOUT = 15          # Batas waktu tunggu respons (detik)

# Endpoint & Auth
WEBDAV_BASE_URL = "https://drive.icon-play.com/remote.php/dav/files/noc/DOKUMENTASI/MONITORING%20HARIAN/"
API_TICKET_URL = "https://ticket.limacare.id/api/daily-monitoring/with-media"
import os
WEBDAV_USER = os.environ.get("WEBDAV_USER", "")
WEBDAV_PASS = os.environ.get("WEBDAV_PASS", "")

BULAN_INDO = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"