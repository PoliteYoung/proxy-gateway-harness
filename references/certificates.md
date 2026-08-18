# ygkkk Certificate Integration

Use the installed ygkkk certificate workflow as an integration point rather than assuming a fixed upstream URL or filesystem layout.

1. Locate the installed script, its upstream repository, revision, renewal job, certificate paths, and deployment hooks.
2. Verify domain certificates with `openssl x509 -ext subjectAltName`; require the expected DNS SAN.
3. Verify IP certificates separately; require the exact IPv4/IPv6 SAN.
4. Compare certificate and private-key public keys before deployment.
5. Point AGSBX and x-ui at explicit domain or IP certificate paths. Do not infer certificate type from a filename.
6. After renewal, validate first, replace atomically, run core configuration checks, restart only affected services, and execute required probes.
7. Retain the old certificate until post-restart probes pass. IP certificates can be short-lived, so monitor their expiry more frequently.

Never commit certificates, private keys, account material, DNS API tokens, or real renewal logs.
