import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

import polly


class TransmissionHandler(BaseHTTPRequestHandler):
    requests = []

    def do_POST(self):
        if self.headers.get("X-Transmission-Session-Id") != "test-session":
            self.send_response(409)
            self.send_header("X-Transmission-Session-Id", "test-session")
            self.end_headers()
            return

        length = int(self.headers["Content-Length"])
        self.__class__.requests.append(json.loads(self.rfile.read(length)))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"result":"success","arguments":{}}')

    def log_message(self, _format, *_args):
        pass


class PollyTests(unittest.TestCase):
    def test_reads_valid_forwarded_port(self):
        with tempfile.TemporaryDirectory() as directory:
            port_file = Path(directory) / "forwarded_port"
            port_file.write_text("45678\n", encoding="utf-8")
            with patch.object(polly, "PORT_FILE", port_file):
                self.assertEqual(polly.read_forwarded_port(), 45678)

    def test_empty_forwarded_port_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            port_file = Path(directory) / "forwarded_port"
            port_file.write_text("", encoding="utf-8")
            with patch.object(polly, "PORT_FILE", port_file):
                self.assertIsNone(polly.read_forwarded_port())

    def test_updates_transmission_after_session_handshake(self):
        TransmissionHandler.requests = []
        server = HTTPServer(("127.0.0.1", 0), TransmissionHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = polly.TransmissionRPC(
                f"http://127.0.0.1:{server.server_port}/transmission/rpc"
            )
            polly.set_transmission_port(client, 45678)
        finally:
            server.shutdown()
            thread.join()

        self.assertEqual(
            TransmissionHandler.requests,
            [
                {
                    "method": "session-set",
                    "arguments": {
                        "peer-port": 45678,
                        "peer-port-random-on-start": False,
                        "port-forwarding-enabled": False,
                    },
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
