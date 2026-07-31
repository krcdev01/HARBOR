import json
import os
import sys
import time
import urllib.parse
import urllib.request
import http.cookiejar
from typing import Any


QB_BASE_URL = os.environ["QB_URL"].rstrip("/")
QB_USERNAME = os.environ["QB_USERNAME"]
QB_PASSWORD = os.environ["QB_PASSWORD"]

# This is the actual fix:
# - ratio 0
# - action = remove torrent
# - seeding time 0 as backup
# - queueing disabled
DESIRED_PREFS = {
    "max_ratio_enabled": True,
    "max_ratio": 0,
    "max_ratio_act": 1,
    "max_seeding_time_enabled": True,
    "max_seeding_time": 0,
    "queueing_enabled": False,
}


class QBClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password

        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

    def _post_form(self, path: str, data: dict[str, Any]) -> str:
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=encoded,
            method="POST",
        )
        with self.opener.open(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")

    def _get_json(self, path: str) -> dict[str, Any]:
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            method="GET",
        )
        with self.opener.open(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    def login(self) -> None:
        result = self._post_form(
            "/api/v2/auth/login",
            {"username": self.username, "password": self.password},
        ).strip()
        if result != "Ok.":
            raise RuntimeError(f"qBittorrent login failed: {result!r}")

    def get_preferences(self) -> dict[str, Any]:
        return self._get_json("/api/v2/app/preferences")

    def set_preferences(self, prefs: dict[str, Any]) -> None:
        self._post_form(
            "/api/v2/app/setPreferences",
            {"json": json.dumps(prefs, separators=(",", ":"))},
        )


def enforce_qb_policy(max_wait_seconds: int = 180) -> None:
    deadline = time.time() + max_wait_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            client = QBClient(QB_BASE_URL, QB_USERNAME, QB_PASSWORD)
            client.login()

            current = client.get_preferences()
            updates = {
                key: value
                for key, value in DESIRED_PREFS.items()
                if current.get(key) != value
            }

            if updates:
                client.set_preferences(updates)

            verified = client.get_preferences()
            failures = {
                key: (verified.get(key), value)
                for key, value in DESIRED_PREFS.items()
                if verified.get(key) != value
            }

            if failures:
                raise RuntimeError(f"qBittorrent preference verification failed: {failures}")

            print("qBittorrent policy enforced successfully", flush=True)
            return

        except Exception as exc:
            last_error = exc
            time.sleep(5)

    raise RuntimeError(f"Unable to enforce qBittorrent policy within timeout: {last_error}")


if __name__ == "__main__":
    try:
        enforce_qb_policy()
    except Exception as exc:
        print(str(exc), file=sys.stderr, flush=True)
        sys.exit(1)