"""Serve the built dashboard and print every route to screenshot. No new dependency.

    python tools/routes.py            # serve on 8080 and list routes
    python tools/routes.py --list     # list only, do not serve
"""
import argparse
import functools
import http.server
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "web" / "dist"
ROUTES = ["/", "/ledger", "/exits", "/fields", "/warning", "/predict", "/drivers",
          "/assistant", "/model-card", "/project/705410"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if not DIST.exists():
        print(f"no build at {DIST}; run npm run build in web/ first", file=sys.stderr)
        return 1
    base = f"http://localhost:{a.port}"
    for r in ROUTES:
        print(f"{base}/#{r}")
    print(f"\nchecklist: {ROOT / 'docs' / 'SCREEN-CHECKLIST.md'}")
    if a.list:
        return 0
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with socketserver.TCPServer(("", a.port), handler) as httpd:
        print(f"\nserving {DIST} at {base} — ctrl-c to stop")
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
