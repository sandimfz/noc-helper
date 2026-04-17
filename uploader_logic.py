# uploader_logic.py
import json, re
from datetime import datetime
from requests.auth import HTTPBasicAuth
from utils_status import extract_status_from_filename
import config

def process_single_batch(session, jam_batch, bearer_token, kerusakan_map):
    now = datetime.now()
    mapping_lokasi = next((val for key, val in config.ALL_BATCHES.items() if key in jam_batch), None)
    
    if not mapping_lokasi:
        return f"SKIP: No mapping for {jam_batch}"

    folder_path = f"{now.year}/{config.BULAN_INDO[now.month-1]}/{now.strftime('%d-%m-%Y')}/{jam_batch}"
    webdav_url = f"{config.WEBDAV_BASE_URL}{folder_path}/"
    auth = HTTPBasicAuth(config.WEBDAV_USER, config.WEBDAV_PASS)

    try:
        # 1. Ambil List File (PROPFIND)
        res = session.request("PROPFIND", webdav_url, auth=auth, headers={"Depth": "1"}, timeout=config.TIMEOUT)
        if res.status_code not in [200, 207]:
            return f"NOT FOUND: {folder_path}"

        all_files = list(set(re.findall(r'([^/]+\.[jJ][pP][eE]?[gG])', res.text)))
        all_files.sort(key=lambda x: (re.search(r'\.\d{4}\.', x) is not None, x), reverse=True)

        queue = {}
        for fname in all_files:
            loc_id, net_status, led_name, ext_time = extract_status_from_filename(fname, mapping_lokasi)
            if loc_id != 0:
                if loc_id not in queue:
                    queue[loc_id] = {"binaries": [], "status": net_status, "led_name": led_name, "time": ext_time}
                
                # Download gambar menggunakan session yang sama
                img_get = session.get(webdav_url + fname, auth=auth, timeout=config.TIMEOUT)
                if img_get.status_code == 200:
                    queue[loc_id]["binaries"].append(('files', (fname, img_get.content, 'image/jpeg')))

        # 2. Kirim ke API Limacare
        headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}
        results = {"success": 0, "fails": []}

        for lid, item in queue.items():
            v_status, catatan = "normal", ""
            display_name_low = item['led_name'].lower()

            for web_loc, note in kerusakan_map.items():
                if display_name_low in web_loc or web_loc in display_name_low:
                    v_status, catatan = "tidak_normal", note
                    break

            payload = {
                "locationId": lid, "documentationDate": now.strftime("%Y-%m-%d"),
                "documentationTime": item["time"], "source": "cctv",
                "plnTokenRemaining": "0", "videotronStatus": v_status,
                "notes": catatan, "networkStatus": item["status"]
            }

            resp = session.post(
                config.API_TICKET_URL, 
                headers=headers, data={'data': json.dumps(payload)}, 
                files=item["binaries"], timeout=30
            )

            if resp.status_code in [200, 201]:
                results["success"] += 1
            else:
                results["fails"].append(item['led_name'])

        fail_info = f", gagal: {len(results['fails'])} {', '.join(results['fails'])}" if results['fails'] else ""
        return f"Gambar berhasil di upload di {results['success']} lokasi{fail_info}"

    except Exception as e:
        return f"ERROR: {str(e)}"