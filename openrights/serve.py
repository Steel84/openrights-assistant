from __future__ import annotations

import socket
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Ports reserved for other services on this server (Docker WordPress, etc.)
RESERVED_PORTS = {80, 443, 8080}


def lan_address() -> str | None:
    """Best-effort local address, so a phone on the same Wi-Fi can reach it."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("192.0.2.1", 53))  # reserved, never sends traffic
            return probe.getsockname()[0]
        except OSError:
            return None


def serve(root: Path, port: int = 8000) -> None:
    if port in RESERVED_PORTS:
        print(f"ERROR: port {port} is reserved (used by web-agregator.ru / Caddy / Docker).")
        print("Use --port 8090 for dev or --port 8000 (default) for local demo.")
        sys.exit(1)
    if not (root / "app/data/index.js").exists():
        raise SystemExit("Archive not exported. Run: python -m openrights ingest && python -m openrights export-web")
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    with ThreadingHTTPServer(("0.0.0.0", port), handler) as server:
        address = lan_address()
        print(f"Open on this computer:  http://localhost:{port}/app/")
        if address:
            print(f"Open on your phone:     http://{address}:{port}/app/   (same Wi-Fi)")
        else:
            print("Open on your phone:     no LAN address detected")
        print("Install it from the browser menu, then switch the phone to airplane mode to prove it is offline.")
        print("Stop with Ctrl+C.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
