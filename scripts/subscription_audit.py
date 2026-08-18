#!/usr/bin/env python3
"""Audit a URI subscription without emitting credentials."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
from urllib.request import Request, urlopen

QUIC_SCHEMES = {"hysteria2", "hy2", "tuic"}


def read_source(source):
    if source.startswith(("http://", "https://")):
        request = Request(source, headers={"Cache-Control": "no-cache", "User-Agent": "proxy-gateway-harness"})
        with urlopen(request, timeout=30) as response:
            return response.read().decode()
    return Path(source).read_text(encoding="utf-8")


def decode_vmess(line):
    value = line[8:].split("#", 1)[0]
    value += "=" * (-len(value) % 4)
    return json.loads(base64.urlsafe_b64decode(value))


def audit(content):
    nodes = []
    errors = []
    warnings = []
    for index, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if "://" not in line:
            continue
        try:
            parsed = urlsplit(line)
            scheme = parsed.scheme.lower()
            if scheme == "vmess":
                data = decode_vmess(line)
                name = str(data.get("ps") or f"line-{index}")
                host = str(data.get("add") or "")
                port = int(data.get("port") or 0)
                transport = str(data.get("net") or "tcp")
                security = str(data.get("tls") or "none")
                alpn = str(data.get("alpn") or "")
                sni = str(data.get("sni") or "")
            else:
                query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
                name = unquote(parsed.fragment) or f"line-{index}"
                host = parsed.hostname or ""
                port = parsed.port or 0
                transport = query.get("type") or query.get("network") or ("quic" if scheme in QUIC_SCHEMES else "tcp")
                security = query.get("security") or ("tls" if scheme in QUIC_SCHEMES | {"trojan", "anytls"} else "none")
                alpn = query.get("alpn", "")
                sni = query.get("sni", "")
            real_h3 = alpn == "h3" and (transport in {"xhttp", "quic", "hysteria", "hysteria2", "tuic"} or scheme in QUIC_SCHEMES)
            if alpn == "h3" and not real_h3:
                errors.append({"line": index, "name": name, "code": "h3-without-quic", "detail": f"{scheme}/{transport} uses alpn=h3 without a QUIC transport"})
            if security in {"tls", "reality"} and not sni and scheme not in QUIC_SCHEMES:
                warnings.append({"line": index, "name": name, "code": "missing-sni"})
            nodes.append({"line": index, "name": name, "scheme": scheme, "host": host, "port": port, "transport": transport, "security": security, "alpn": alpn, "real_h3": real_h3})
        except Exception as exc:
            errors.append({"line": index, "name": f"line-{index}", "code": "parse-error", "detail": type(exc).__name__})
    return {
        "schema_version": 1,
        "artifact_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "node_count": len(nodes),
        "nodes": nodes,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--output")
    args = parser.parse_args()
    report = audit(read_source(args.source))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
