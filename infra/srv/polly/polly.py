#!/usr/bin/env python3
"""Keep Transmission's peer port synchronized with Gluetun."""

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


PORT_FILE = Path(os.environ.get("GLUETUN_PORT_FILE", "/tmp/gluetun/forwarded_port"))
RPC_URL = os.environ.get(
    "TRANSMISSION_RPC_URL",
    "http://127.0.0.1:9091/transmission/rpc",
)
RPC_USERNAME = os.environ.get("TRANSMISSION_RPC_USERNAME", "")
RPC_PASSWORD = os.environ.get("TRANSMISSION_RPC_PASSWORD", "")
POLL_SECONDS = max(1, int(os.environ.get("POLL_SECONDS", "10")))
RPC_TIMEOUT_SECONDS = max(1, int(os.environ.get("RPC_TIMEOUT_SECONDS", "15")))


class TransmissionRPC:
    def __init__(self, url: str, username: str = "", password: str = "") -> None:
        self.url = url
        self.session_id = ""
        self.authorization = ""
        if username or password:
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            self.authorization = f"Basic {credentials}"

    def call(self, method: str, arguments: dict) -> dict:
        payload = json.dumps({"method": method, "arguments": arguments}).encode()

        for _ in range(2):
            headers = {"Content-Type": "application/json"}
            if self.session_id:
                headers["X-Transmission-Session-Id"] = self.session_id
            if self.authorization:
                headers["Authorization"] = self.authorization

            request = urllib.request.Request(
                self.url,
                data=payload,
                headers=headers,
                method="POST",
            )

            try:
                with urllib.request.urlopen(request, timeout=RPC_TIMEOUT_SECONDS) as response:
                    result = json.load(response)
            except urllib.error.HTTPError as error:
                if error.code == 409:
                    self.session_id = error.headers.get("X-Transmission-Session-Id", "")
                    if self.session_id:
                        continue
                raise

            if result.get("result") != "success":
                raise RuntimeError(f"Transmission RPC failed: {result.get('result')}")
            return result.get("arguments", {})

        raise RuntimeError("Transmission did not provide a usable RPC session ID")


def read_forwarded_port() -> int | None:
    try:
        value = PORT_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None

    if not value:
        return None

    port = int(value)
    if not 1 <= port <= 65535:
        raise ValueError(f"invalid forwarded port: {port}")
    return port


def set_transmission_port(client: TransmissionRPC, port: int) -> None:
    client.call(
        "session-set",
        {
            "peer-port": port,
            "peer-port-random-on-start": False,
            "port-forwarding-enabled": False,
        },
    )


def main() -> None:
    client = TransmissionRPC(RPC_URL, RPC_USERNAME, RPC_PASSWORD)
    applied_port = None
    port_available = False

    print(f"Polly watching {PORT_FILE} for Gluetun port changes", flush=True)

    while True:
        try:
            forwarded_port = read_forwarded_port()

            if forwarded_port is None:
                if port_available:
                    print("Gluetun port forwarding is unavailable; waiting for VPN", flush=True)
                port_available = False
                applied_port = None
            else:
                port_available = True
                if forwarded_port != applied_port:
                    set_transmission_port(client, forwarded_port)
                    applied_port = forwarded_port
                    print(
                        f"Transmission peer port updated to {forwarded_port}",
                        flush=True,
                    )
        except Exception as error:
            applied_port = None
            print(f"Polly synchronization failed: {error}", flush=True)

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
