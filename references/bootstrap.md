# Linux VPS Bootstrap

## Preconditions

Require root, systemd, curl, OpenSSL, Python 3, outbound HTTPS, a public address, and controllable TCP/UDP firewall rules. Detect `amd64` or `arm64`; reject unsupported architectures instead of guessing binaries.

## Sequence

1. Record OS, architecture, public IPv4/IPv6, DNS, occupied ports, firewall, and current services.
2. Download ygkkk, AGSBX, and x-ui installers to disk. Inspect them, pin revisions, record SHA-256, then execute locally. Never use `curl | sh`.
3. Install x-ui for stateful Xray inbounds and AGSBX for sing-box protocols. Keep custom modern Xray in a separate systemd unit when x-ui cannot model it faithfully.
4. Allocate TCP and UDP independently. The same numeric port may be used by separate TCP and UDP listeners.
5. Deploy a small supported matrix first: VLESS XHTTP TLS H2/H3, VLESS Reality Vision, AnyTLS, Hysteria2, TUIC, and one compatibility protocol.
6. Add Sub-Store only after direct source nodes pass their corresponding cores.

Do not promise support for NAT-only machines, macOS, Windows, containers without TUN privileges, or non-systemd distributions without adapting the workflow.
