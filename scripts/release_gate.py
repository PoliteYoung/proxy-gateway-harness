#!/usr/bin/env python3
"""Combine static and runtime JSON reports into a release decision."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+")
    parser.add_argument("--output")
    args = parser.parse_args()
    blockers = []
    summaries = []
    for filename in args.reports:
        report = json.loads(Path(filename).read_text(encoding="utf-8"))
        failed = len(report.get("errors", [])) + int(report.get("failed_count", 0))
        if report.get("blocked"):
            failed += 1
        summaries.append({"report": filename, "failed": failed})
        if failed:
            blockers.append(filename)
    result = {"schema_version": 1, "decision": "PASS" if not blockers else "FAIL", "blockers": blockers, "reports": summaries}
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
