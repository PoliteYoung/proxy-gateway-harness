# Proxy Gateway Harness

A Codex skill for building and validating multi-protocol proxy gateways on
`amd64` and `arm64` Linux VPS hosts.

It connects the full delivery chain:

```text
ygkkk certificates -> AGSBX / x-ui -> Xray / sing-box
                   -> Sub-Store -> URI / sing-box / Mihomo
                   -> core probes -> release gate -> rollback
```

## What it covers

- Domain and IP certificate integration with the ygkkk certificate workflow
- AGSBX and x-ui deployment guidance
- Xray, sing-box, and Mihomo configuration validation
- Sub-Store source traceability and field-preserving conversion
- Detection of false H3 claims such as `alpn=h3` on a TCP-only transport
- Isolated HTTPS egress probes using the appropriate client core
- TUN smoke-test requirements
- Atomic publication, public URL verification, and rollback gates

Supported protocol families include VLESS Vision, VLESS Encryption with
XHTTP, Reality, VMess, AnyTLS, Hysteria2, TUIC, Trojan, and Shadowsocks.

## Install as a Codex skill

Clone the repository into the Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/PoliteYoung/proxy-gateway-harness.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/proxy-gateway-harness"
```

Restart Codex or open a new task so the skill is discovered. Example request:

```text
Use proxy-gateway-harness to audit this Linux VPS, build the protocol matrix,
validate the Sub-Store output, and publish only if every required gate passes.
```

## Bundled tools

Audit a URI subscription:

```bash
python3 scripts/subscription_audit.py subscription.txt \
  --output static-report.json
```

Probe every concrete outbound in a sing-box configuration:

```bash
python3 scripts/probe_singbox.py \
  --config candidate-singbox.json \
  --binary /path/to/sing-box \
  --output singbox-probe.json
```

Apply the release gate:

```bash
python3 scripts/release_gate.py \
  static-report.json singbox-probe.json \
  --output release-decision.json
```

## Safety model

The repository does not contain server credentials or automatic remote
installer execution. Inspect and pin third-party installers before running
them. Keep subscription tokens, UUIDs, passwords, private keys, Reality keys,
VLESS Encryption values, SSH credentials, certificates, and Sub-Store
databases out of Git.

Server configuration is treated as the source of truth, Sub-Store as the
publication authority, and the cache-bypassed public subscription as the final
acceptance artifact.

## Validation

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py
```

## License

MIT
