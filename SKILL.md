---
name: proxy-gateway-harness
description: Build, audit, test, and publish multi-protocol proxy gateways on amd64 or arm64 Linux VPS hosts using ygkkk certificate automation, AGSBX, x-ui, Xray, sing-box, Mihomo, and Sub-Store. Use when provisioning a new proxy VPS, synchronizing domain or IP certificates, diagnosing subscription conversion loss, validating H3/QUIC claims, testing published nodes with corresponding cores or TUN, or enforcing atomic publication and rollback gates.
---

# Proxy Gateway Harness

Treat server configuration as truth, Sub-Store as the publication authority, and a public subscription downloaded after publication as the acceptance artifact.

## Operating modes

- Use `bootstrap` to prepare a root-managed, systemd-based amd64/arm64 Linux VPS. Read [references/bootstrap.md](references/bootstrap.md) and [references/certificates.md](references/certificates.md).
- Use `audit` to inventory running x-ui, AGSBX, Xray, and sing-box services and trace nodes through Sub-Store. Read [references/substore.md](references/substore.md).
- Use `probe` to test candidate or public artifacts with the core that accurately represents each protocol. Read [references/protocols.md](references/protocols.md).
- Use `publish` only after every required gate passes. Read [references/release.md](references/release.md).

## Mandatory workflow

1. Detect architecture, init system, privileges, occupied TCP/UDP ports, firewall, and public IP versions.
2. Back up current service databases and configurations before mutation. Never print secrets.
3. Inventory actual running configurations. Do not infer protocol parameters from node names.
4. Build a normalized protocol matrix containing source, address, port, IP version, protocol, transport, TCP/UDP, security, SNI, ALPN, certificate SAN type, Flow, Encryption presence, and stability tier.
5. Generate candidate Sub-Store sources and URI, sing-box, and Mihomo artifacts outside the live publication path.
6. Run `scripts/subscription_audit.py` against the candidate URI. Treat every error as a release blocker.
7. Run syntax checks and isolated HTTPS egress probes with Xray, sing-box, and Mihomo. Test the exact published fields; do not let one core silently normalize a configuration on behalf of another.
8. Prove H3 using a QUIC-capable transport, a UDP listener, and observed UDP traffic. `alpn=h3` alone is insufficient.
9. Run bounded TUN smoke tests where supported and always restore routes, DNS, processes, and interfaces.
10. Compare candidate and baseline, then run `scripts/release_gate.py`. Publish atomically only on PASS.
11. Download the public URL with cache bypass and repeat validation. Roll back automatically on failure.

## Safety rules

- Never commit subscription tokens, UUIDs, passwords, private keys, Reality private keys, VLESS Encryption values, SSH credentials, or Sub-Store databases.
- Never pipe an unpinned remote script into a shell. Inspect the ygkkk, AGSBX, and x-ui installers, pin a revision, and verify a checksum first.
- Keep domain certificates and IP certificates distinct. Verify SANs and key matching with OpenSSL.
- Do not enable `allowInsecure` or skip certificate verification to turn a failure into a pass.
- Preserve an existing working version when any required node fails.
- Put experimental combinations in a separate subscription.

## Bundled tools

- `scripts/subscription_audit.py`: fetch or read a URI subscription, normalize non-secret metadata, and reject impossible H3 combinations or missing TLS identity.
- `scripts/probe_singbox.py`: load each real outbound from a generated sing-box configuration in isolation and perform HTTPS egress tests.
- `scripts/release_gate.py`: combine static and probe reports into a deterministic publication decision.

Reports must contain protocol-matrix counts, passes, failures, blockers, artifact hashes, baseline differences, publication decision, and rollback identifier.

For repeatable provisioning, use `ansible/site.yml` after copying and reviewing the example inventory and variables. For a fresh VPS, customize `cloud-init/proxy-gateway.yaml.example` with an immutable commit. Both paths prepare the host; neither runs unreviewed third-party installers by default.
