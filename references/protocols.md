# Protocol Semantics and Core Selection

| Family | Expected core | H3 rule |
|---|---|---|
| VLESS TCP Vision | Xray | TCP; `h3` is not HTTP/3 |
| VLESS Encryption + XHTTP | Xray | H3 requires the XHTTP QUIC/UDP listener |
| VLESS Reality | Xray | Validate Reality parameters, not X.509 |
| VMess | Xray or sing-box | WS is not H3 |
| AnyTLS | sing-box | Do not infer QUIC from ALPN |
| Hysteria2 | sing-box | QUIC/UDP |
| TUIC | sing-box | QUIC/UDP |
| Trojan TCP | Xray or sing-box | `alpn=h3` does not make it QUIC |
| Shadowsocks | sing-box | Preserve method, UoT, and address family |

Run every node as an isolated temporary client. Require core configuration validation, startup, DNS, HTTPS egress, and cleanup. For H3, additionally inspect server UDP listeners and observe UDP traffic. Use Mihomo to validate Mihomo output rather than treating sing-box success as equivalent.
