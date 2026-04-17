import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import config
from uploader_logic import process_single_batch

def create_smart_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=config.RETRY_COUNT,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def parse_kerusakan(raw_input):
    k_map = {}
    if ":" in raw_input:
        for pair in raw_input.split(";"):
            if ":" in pair:
                loc, note = pair.split(":", 1)
                k_map[loc.strip().lower().replace("_", " ")] = note.strip()
    return k_map

def check_session(session, bearer_token):
    res = session.get("https://ticket.limacare.id/api/locations/29",
                      headers={"Authorization": f"Bearer {bearer_token}"}, timeout=config.TIMEOUT)
    if res.status_code == 401:
        print("Anda harus logout dan login kembali.")
        return False
    return True

def main():
    if len(sys.argv) < 3:
        print("Argumen kurang! Format: <token> <batch/ALL> <keterangan>")
        return

    bearer_token, batch_input = sys.argv[1], sys.argv[2]
    keterangan_raw = sys.argv[3] if len(sys.argv) > 3 else ""
    kerusakan_map = parse_kerusakan(keterangan_raw)

    tasks = []
    if batch_input.upper() == "ALL":
        tasks = [f"{j}_{b}" for j in config.SCHEDULE_JAM for b in config.BATCH_LIST]
    elif "_ALL" in batch_input.upper():
        jam = batch_input.split("_")[0]
        tasks = [f"{jam}_{b}" for b in config.BATCH_LIST]
    else:
        tasks = [batch_input]

    with create_smart_session() as session:
        if not check_session(session, bearer_token):
            return
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            future_to_task = {
                executor.submit(process_single_batch, session, t, bearer_token, kerusakan_map): t
                for t in tasks
            }
            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    jam, batch = task_name.split("_", 1)
                    label = f"{jam} {batch.replace('_', ' ')}"
                    print(f"{label} {future.result()}")
                except Exception as e:
                    jam, batch = task_name.split("_", 1)
                    print(f"{jam} {batch.replace('_', ' ')} Error: {e}")

if __name__ == "__main__":
    main()
