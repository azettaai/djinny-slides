#!/usr/bin/env python3
"""
Local dev server: encrypts the HTML slides then serves the site on port 8080.

Usage:
    python server.py                      # default password 'yatkernel'
    DECKPASSWORD=mypassword python server.py # custom password
"""
import os
import sys
import subprocess
import http.server
import socketserver
from pathlib import Path

PORT = 8080
ROOT = Path(__file__).parent


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        status = args[1] if len(args) > 1 else "?"
        print(f"  {status}  {args[0]}")


def main():
    password = os.environ.get("DECKPASSWORD", "yatkernel")
    env = {**os.environ, "DECKPASSWORD": password}

    print("[server] Encrypting slides...")
    result = subprocess.run(
        [sys.executable, str(ROOT / "encrypt.py")],
        env=env,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("[server] Encryption failed — aborting.")
        sys.exit(1)

    os.chdir(ROOT / "docs")
    print(f"\n[server] Listening on http://localhost:{PORT}")
    print(f"[server]   Landing page  →  http://localhost:{PORT}/")
    print(f"[server]   Client deck   →  http://localhost:{PORT}/client.html")
    print(f"[server]   Pitch deck    →  http://localhost:{PORT}/pitch.html")
    print("[server]   Ctrl-C to stop\n")

    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
