# Release Gates

Block publication when a required node has a parse error, field mismatch, invalid certificate, failed core check, failed HTTPS probe, unproven H3 claim, or failed TUN smoke test.

Before publication, save the Sub-Store state, generated artifacts, report bundle, and a rollback identifier. Write candidates to temporary files, fsync where appropriate, and replace atomically. After publication, download the public URL with cache bypass, verify its hash and node count, then probe it again.

Reports must state protocol counts, pass/fail/block counts, failure stages, baseline differences, decision, publication status, and rollback target. Never call a syntactically valid subscription operationally healthy.
