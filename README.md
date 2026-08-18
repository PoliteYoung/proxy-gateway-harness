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

## Invoke the skill

Call the skill explicitly with `$proxy-gateway-harness`. For a new VPS, use
three separate stages so inspection, deployment, and publication remain
reviewable.

### 1. Read-only preflight

```text
$proxy-gateway-harness bootstrap

This is a new Linux VPS. Perform a read-only preflight. Inspect the OS,
architecture, systemd, root access, public IPv4/IPv6, DNS, occupied TCP/UDP
ports, firewall, and domain resolution. Propose a certificate, protocol, and
port matrix. Do not install services or execute remote scripts yet.
```

### 2. Build a candidate gateway

```text
$proxy-gateway-harness bootstrap

Use the approved preflight plan to build a candidate gateway with the ygkkk
domain/IP certificate workflow, AGSBX, x-ui, Xray, and sing-box. Pin and
checksum every installer before execution. Configure Sub-Store sources
separately. Keep H2 and real H3/QUIC distinct. Back up before each mutation,
validate configs before restart, and do not publish the production
subscription yet.
```

Provide the domain, desired IPv4/IPv6 behavior, Sub-Store location, and whether
firewall changes are authorized. Keep credentials out of the prompt whenever
Codex can discover them securely on the host.

### 3. Validate and publish

```text
$proxy-gateway-harness audit probe publish

Treat running server configs as truth and the cache-bypassed Sub-Store public
artifact as the acceptance target. Trace every node through source,
collection, URI, sing-box, and Mihomo outputs. Test each published node with
the corresponding core, verify certificate SAN/SNI, prove H3 uses UDP/QUIC,
and run bounded TUN smoke tests. Block publication if any required gate fails.
If all gates pass, publish atomically, download the public URL again, retest,
and report the rollback point.
```

To audit an existing subscription without changing the host:

```text
$proxy-gateway-harness audit probe

Audit and test this Sub-Store subscription with the corresponding cores:
https://example.com/subscription
Do not modify services or publish anything.
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

## Prepare a Linux VPS

For an existing VPS, copy the Ansible example inventory and variables, pin a
release or immutable commit, then run:

```bash
cd ansible
cp inventory.example.yml inventory.yml
cp group_vars/all.yml.example group_vars/all.yml
ansible-playbook -i inventory.yml site.yml --check --diff
ansible-playbook -i inventory.yml site.yml
```

For a new VPS, customize `cloud-init/proxy-gateway.yaml.example` by replacing
`PINNED_COMMIT` with a full commit hash before supplying it as user data.

Both methods prepare the host and install the Skill. They do not run ygkkk,
AGSBX, or x-ui installers unless the operator explicitly supplies audited,
SHA-256-pinned installer metadata.

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
