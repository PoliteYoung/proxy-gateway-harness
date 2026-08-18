#!/usr/bin/env python3
"""Probe every concrete outbound in a sing-box configuration."""

import argparse
import json
import os
import signal
import socket
import subprocess
import tempfile
import time
from pathlib import Path


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def probe(binary, outbound, timeout):
    port = free_port()
    config = {
        "log": {"level": "warn"},
        "inbounds": [{"type": "socks", "tag": "probe-in", "listen": "127.0.0.1", "listen_port": port}],
        "outbounds": [outbound, {"type": "direct", "tag": "direct"}],
        "route": {"final": outbound["tag"]},
    }
    with tempfile.TemporaryDirectory(prefix="proxy-harness-") as directory:
        path = Path(directory) / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        checked = subprocess.run([binary, "check", "-c", str(path)], capture_output=True, text=True, timeout=timeout)
        if checked.returncode:
            return False, "config-check"
        process = subprocess.Popen([binary, "run", "-c", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            time.sleep(0.5)
            result = subprocess.run([
                "curl", "-fsS", "--max-time", str(timeout), "--socks5-hostname",
                f"127.0.0.1:{port}", "https://api.ipify.org",
            ], capture_output=True, text=True)
            return (True, result.stdout.strip()) if result.returncode == 0 else (False, f"curl-{result.returncode}")
        finally:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=2)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--binary", default="sing-box")
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--output")
    args = parser.parse_args()
    data = json.loads(Path(args.config).read_text(encoding="utf-8"))
    outbounds = [item for item in data.get("outbounds", []) if item.get("server") and item.get("tag")]
    results = []
    for outbound in outbounds:
        passed, detail = probe(args.binary, outbound, args.timeout)
        results.append({"tag": outbound["tag"], "type": outbound.get("type"), "passed": passed, "detail": detail})
    report = {"schema_version": 1, "core": "sing-box", "total": len(results), "passed_count": sum(item["passed"] for item in results), "failed_count": sum(not item["passed"] for item in results), "results": results}
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
