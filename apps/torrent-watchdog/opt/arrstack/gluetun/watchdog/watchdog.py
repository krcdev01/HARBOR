import json
import os
import time
from pathlib import Path
from qb_policy import enforce_qb_policy

import requests

QB_URL = os.environ["QB_URL"].rstrip("/")
QB_USERNAME = os.environ["QB_USERNAME"]
QB_PASSWORD = os.environ["QB_PASSWORD"]
GLUETUN_CONTROL_URL = os.environ["GLUETUN_CONTROL_URL"].rstrip("/")

LOOP_SECONDS = int(os.environ.get("LOOP_SECONDS", "300"))
STALL_MINUTES = int(os.environ.get("STALL_MINUTES", "20"))
NEAR_END_PROGRESS = float(os.environ.get("NEAR_END_PROGRESS", "0.98"))
MIN_DOWNLOAD_BPS = int(os.environ.get("MIN_DOWNLOAD_BPS", "10240"))
REANNOUNCE_RETRIES = int(os.environ.get("REANNOUNCE_RETRIES", "2"))
ROTATE_COOLDOWN_MINUTES = int(os.environ.get("ROTATE_COOLDOWN_MINUTES", "30"))

STATE_FILE = Path("/tmp/torrent_watchdog_state.json")
SESSION = requests.Session()


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "stuck_counts": {},
        "last_rotate_ts": 0,
    }


def save_state(state):
    STATE_FILE.write_text(json.dumps(state))


def qb_login():
    response = SESSION.post(
        f"{QB_URL}/api/v2/auth/login",
        data={"username": QB_USERNAME, "password": QB_PASSWORD},
        timeout=20,
    )
    response.raise_for_status()
    if response.text.strip() != "Ok.":
        raise RuntimeError("qBittorrent login failed")


def qb_get_torrents():
    response = SESSION.get(f"{QB_URL}/api/v2/torrents/info", timeout=30)
    response.raise_for_status()
    return response.json()


def qb_reannounce(hashes):
    if not hashes:
        return
    response = SESSION.post(
        f"{QB_URL}/api/v2/torrents/reannounce",
        data={"hashes": "|".join(hashes)},
        timeout=30,
    )
    response.raise_for_status()


def gluetun_rotate():
    stop_response = requests.put(
        f"{GLUETUN_CONTROL_URL}/v1/vpn/status",
        json={"status": "stopped"},
        timeout=20,
    )
    stop_response.raise_for_status()

    time.sleep(8)

    start_response = requests.put(
        f"{GLUETUN_CONTROL_URL}/v1/vpn/status",
        json={"status": "running"},
        timeout=20,
    )
    start_response.raise_for_status()


def find_stuck_torrents(torrents):
    now = time.time()
    stuck = []

    for torrent in torrents:
        torrent_hash = torrent.get("hash")
        if not torrent_hash:
            continue

        progress = float(torrent.get("progress", 0))
        dlspeed = int(torrent.get("dlspeed", 0))
        state = str(torrent.get("state", ""))
        completion_on = int(torrent.get("completion_on", 0))
        last_activity = int(torrent.get("last_activity", 0))
        added_on = int(torrent.get("added_on", 0))
        name = torrent.get("name", "")

        if completion_on > 0:
            continue

        if progress < NEAR_END_PROGRESS:
            continue

        if dlspeed > MIN_DOWNLOAD_BPS:
            continue

        if state not in {"downloading", "stalledDL", "forcedDL", "queuedDL", "metaDL"}:
            continue

        reference_time = last_activity if last_activity > 0 else added_on
        if reference_time <= 0:
            continue

        stalled_for_minutes = (now - reference_time) / 60
        if stalled_for_minutes < STALL_MINUTES:
            continue

        stuck.append({"hash": torrent_hash, "name": name})

    return stuck


def main():
    enforce_qb_policy()
    # existing watchdog startup / monitoring loop continues here
    
    state = load_state()

    while True:
        try:
            qb_login()
            torrents = qb_get_torrents()
            stuck = find_stuck_torrents(torrents)
            current_hashes = {item["hash"] for item in stuck}

            for item in stuck:
                torrent_hash = item["hash"]
                state["stuck_counts"][torrent_hash] = state["stuck_counts"].get(torrent_hash, 0) + 1

            for existing_hash in list(state["stuck_counts"].keys()):
                if existing_hash not in current_hashes:
                    del state["stuck_counts"][existing_hash]

            if stuck:
                hashes = [item["hash"] for item in stuck]
                qb_reannounce(hashes)

                for item in stuck:
                    print(f"Reannounced stuck torrent: {item['name']} [{item['hash']}]")

                need_rotate = any(
                    count >= REANNOUNCE_RETRIES
                    for count in state["stuck_counts"].values()
                )
                cooldown_ok = (time.time() - state["last_rotate_ts"]) >= (ROTATE_COOLDOWN_MINUTES * 60)

                if need_rotate and cooldown_ok:
                    print("Persistent stall detected. Rotating VPN server.")
                    gluetun_rotate()
                    state["last_rotate_ts"] = time.time()

            else:
                print("No stuck torrents matched the watchdog rule.")

            save_state(state)

        except Exception as exc:
            print(f"Watchdog error: {exc}")

        time.sleep(LOOP_SECONDS)


if __name__ == "__main__":
    main()
