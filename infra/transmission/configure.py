#!/usr/bin/env python3
"""Prepare Transmission's media download directories and session paths."""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


RPC_URL = os.environ.get(
    "TRANSMISSION_RPC_URL",
    "http://127.0.0.1:9091/transmission/rpc",
)
TV_DOWNLOAD_DIR = Path(os.environ.get("TV_DOWNLOAD_DIR", "/tv/downloads"))
MOVIES_DOWNLOAD_DIR = Path(os.environ.get("MOVIES_DOWNLOAD_DIR", "/movies/downloads"))
PUID = int(os.environ.get("PUID", "1000"))
PGID = int(os.environ.get("PGID", "1000"))
STARTUP_TIMEOUT_SECONDS = int(os.environ.get("STARTUP_TIMEOUT_SECONDS", "120"))


def prepare_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    os.chown(path, PUID, PGID)
    path.chmod(0o775)


def rpc_call(method: str, arguments: dict) -> None:
    session_id = ""
    payload = json.dumps({"method": method, "arguments": arguments}).encode()

    for _ in range(2):
        headers = {"Content-Type": "application/json"}
        if session_id:
            headers["X-Transmission-Session-Id"] = session_id

        request = urllib.request.Request(
            RPC_URL,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 409:
                session_id = error.headers.get("X-Transmission-Session-Id", "")
                if session_id:
                    continue
            raise

        if result.get("result") != "success":
            raise RuntimeError(f"Transmission RPC failed: {result.get('result')}")
        return

    raise RuntimeError("Transmission did not provide a usable RPC session ID")


def configure_transmission() -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    last_error = None

    while time.monotonic() < deadline:
        try:
            rpc_call(
                "session-set",
                {
                    "download-dir": str(TV_DOWNLOAD_DIR),
                    "incomplete-dir-enabled": False,
                    "watch-dir-enabled": False,
                },
            )
            return
        except Exception as error:
            last_error = error
            time.sleep(2)

    raise RuntimeError(f"Transmission was not configurable before timeout: {last_error}")


def main() -> None:
    prepare_directory(TV_DOWNLOAD_DIR)
    prepare_directory(MOVIES_DOWNLOAD_DIR)
    configure_transmission()
    print(
        f"Transmission directories ready: {TV_DOWNLOAD_DIR}, {MOVIES_DOWNLOAD_DIR}",
        flush=True,
    )


if __name__ == "__main__":
    main()
