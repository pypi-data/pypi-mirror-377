#!/usr/bin/env python3
"""
Serve a file or piped input and print ONLY the public Cloudflare Tunnel URL.

Usage:
    python app.py path/to/file.txt
    cat file.txt | python app.py

Options:
    --port PORT    Local port to serve (default 8080)
    --timeout SEC  Seconds to wait for cloudflared URL (default 30)

Requirements:
- Python 3.7+
- cloudflared installed and in PATH
"""

import argparse
import http.server
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import re
from pathlib import Path

CLOUDFLARED_CMD = "cloudflared"
DEFAULT_PORT = 8080
DEFAULT_TIMEOUT = 30

def err(msg):
    print(msg, file=sys.stderr, flush=True)

def find_trycloudflare_url(logfile, timeout, poll_interval=1.0):
    pattern = re.compile(r'(https?://[a-zA-Z0-9-]+\.trycloudflare\.com)')
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(logfile):
            try:
                with open(logfile, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                m = pattern.search(txt)
                if m:
                    return m.group(1)
            except Exception:
                pass
        time.sleep(poll_interval)
    return None

def start_cloudflared(port, logfile):
    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    try:
        open(logfile, "w").close()
    except Exception:
        pass
    cmd = [CLOUDFLARED_CMD, "tunnel", "--url", f"http://localhost:{port}", "--logfile", logfile]
    try:
        FNULL = open(os.devnull, "w")
        p = subprocess.Popen(cmd, stdout=FNULL, stderr=FNULL, start_new_session=True)
        FNULL.close()
        return p
    except FileNotFoundError:
        raise FileNotFoundError("cloudflared not found in PATH")
    except Exception as e:
        raise

class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress all HTTP server logs

def serve_dir(directory, port):
    os.chdir(directory)
    handler = SilentHTTPRequestHandler
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        try:
            server.server_close()
        except Exception:
            pass

def main():
    ap = argparse.ArgumentParser(description="Serve a file or stdin input and print ONLY the Cloudflare public URL.")
    ap.add_argument("file", nargs="?", help="File to serve (optional if piping)")
    ap.add_argument("--port", "-p", type=int, default=DEFAULT_PORT, help="Local port (default 8080)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Seconds to wait for cloudflared URL")
    ap.add_argument("--logdir", default=os.path.join(os.path.expanduser("~"), ".cloudflared_logs"), help="Directory for cloudflared logfile")
    args = ap.parse_args()

    tmpdir = tempfile.mkdtemp(prefix="servefile_")

    # Detect stdin input
    if not sys.stdin.isatty():
        dest = Path(tmpdir) / "stdin_input.txt"
        try:
            with open(dest, "wb") as f:
                f.write(sys.stdin.buffer.read())
        except Exception as e:
            err(f"[-] Failed to read from stdin: {e}")
            shutil.rmtree(tmpdir, ignore_errors=True)
            return 3
    elif args.file:
        filepath = Path(args.file).expanduser().resolve()
        if not filepath.exists():
            err(f"[-] File not found: {filepath}")
            shutil.rmtree(tmpdir, ignore_errors=True)
            return 2
        dest = Path(tmpdir) / filepath.name
        try:
            shutil.copy2(filepath, dest)
        except Exception as e:
            err(f"[-] Failed to copy file: {e}")
            shutil.rmtree(tmpdir, ignore_errors=True)
            return 3
    else:
        err("[-] No input provided. Use a file argument or pipe data into stdin.")
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 1

    logfile = os.path.join(args.logdir, "servefile_cf.log")
    try:
        cf_proc = start_cloudflared(args.port, logfile)
    except FileNotFoundError:
        err("[-] cloudflared not found. Install and ensure it's in PATH.")
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 4
    except Exception as e:
        err(f"[-] Failed to start cloudflared: {e}")
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 5

    # start server
    server_thread = threading.Thread(target=serve_dir, args=(tmpdir, args.port), daemon=True)
    server_thread.start()

    time.sleep(0.5)

    public_root = find_trycloudflare_url(logfile, timeout=args.timeout)
    if not public_root:
        err("[-] Could not find Cloudflare Tunnel URL within timeout.")
        err(f"    Check cloudflared logfile: {logfile}")
        try:
            cf_proc.terminate()
        except Exception:
            pass
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 6

    # Build file URL
    file_url = public_root.rstrip("/") + "/" + dest.name
    print(file_url, flush=True)  # ONLY output

    # keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            cf_proc.terminate()
        except Exception:
            pass
        shutil.rmtree(tmpdir, ignore_errors=True)

    return 0

if __name__ == "__main__":
    sys.exit(main())
