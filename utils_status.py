# utils_status.py
import re
from datetime import datetime
from typing import Dict, Tuple, Any

def extract_status_from_filename(filename: str, mapping_lokasi: Dict[str, int]) -> Tuple[int, Dict[str, str], str, str]:
    """
    Membedah nama file dokumentasi untuk mendapatkan metadata monitoring.
    
    Args:
        filename: Nama file gambar (contoh: 08-00_Permata_20260417_0805.1111.jpg)
        mapping_lokasi: Dictionary berisi {'Nama_Lokasi': ID_Lokasi}
        
    Returns:
        Tuple berisi (loc_id, network_status_dict, display_name, formatted_time)
    """
    loc_id = 0
    matched_name = ""
    
    # 1. Identifikasi Lokasi (Case-insensitive matching)
    # Kita pakai sorting berdasarkan panjang karakter agar nama yang lebih panjang diprioritaskan
    # (Mencegah "Tasikmalaya" terdeteksi sebagai "Tasik" jika ada dua nama mirip)
    sorted_keys = sorted(mapping_lokasi.keys(), key=len, reverse=True)
    
    filename_lower = filename.lower()
    for key in sorted_keys:
        if key.lower() in filename_lower:
            loc_id = mapping_lokasi[key]
            matched_name = key
            break

    # 2. Ekstraksi Waktu (Pola: _YYYYMMDD_HHMM)
    # Default ke waktu sekarang jika regex gagal
    doc_time = datetime.now().strftime("%H:%M:00")
    time_match = re.search(r'_(\d{8})_(\d{2})(\d{2})', filename)
    if time_match:
        doc_time = f"{time_match.group(2)}:{time_match.group(3)}:00"

    # 3. Logika Status 4-Digit (Standardized Mapping)
    # Default: Semua Online
    status = {
        "connectionStatus": "online", 
        "controllerStatus": "online", 
        "nvrStatus": "online", 
        "cctvStatus": "online"
    }
    
    # Regex mencari .XXXX. di akhir sebelum ekstensi
    code_match = re.search(r'\.(\d{4})\.(?:jpe?g|JPE?G)$', filename)
    
    if code_match:
        code = code_match.group(1)
        # Mapping Digit: 1=Connection, 2=Controller, 3=NVR, 4=CCTV
        # Menggunakan list comprehension untuk efisiensi
        keys = ["connectionStatus", "controllerStatus", "nvrStatus", "cctvStatus"]
        for i, key in enumerate(keys):
            status[key] = "online" if code[i] == "1" else "offline"
        
    return loc_id, status, matched_name, doc_time