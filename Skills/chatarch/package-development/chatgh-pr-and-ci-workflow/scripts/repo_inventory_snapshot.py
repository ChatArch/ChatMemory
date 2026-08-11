#!/usr/bin/env python3
"""Capture ChatGH repository inventory and protection snapshots.

The script is read-only. It writes JSON reports when --output is provided and
prints a compact human summary to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
from typing import Any


def _chatgh_command() -> list[str]:
    override = os.environ.get("CHATGH_COMMAND")
    if override:
        return shlex.split(override)
    return ["chatgh"]


def _run_json(args: list[str]) -> Any:
    command = [*_chatgh_command(), *args, "--json-output"]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(command)}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"failed to parse JSON from chatgh output: {exc}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture ChatGH repo inventory/protection snapshots.")
    parser.add_argument("--owner", required=True, help="GitHub owner or organization.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum repositories to inspect.")
    parser.add_argument("--jobs", type=int, default=8, help="Concurrent protection checks.")
    parser.add_argument("--output", help="Write combined JSON snapshot to this path.")
    parser.add_argument("--skip-protection", action="store_true", help="Only capture repo list.")
    args = parser.parse_args()

    repos = _run_json([
        "repo",
        "list",
        "--owner",
        args.owner,
        "--limit",
        str(args.limit),
        "--sort",
        "updated",
        "--direction",
        "desc",
    ])
    protection = [] if args.skip_protection else _run_json([
        "repo",
        "protection",
        "--owner",
        args.owner,
        "--limit",
        str(args.limit),
        "--jobs",
        str(args.jobs),
    ])

    payload = {
        "owner": args.owner,
        "limit": args.limit,
        "repo_count": len(repos),
        "repos": repos,
        "protection": protection,
    }

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote snapshot: {output}")

    open_pr_total = sum(int(item.get("open_prs") or 0) for item in repos)
    open_issue_total = sum(int(item.get("open_issues") or 0) for item in repos)
    print(f"Owner: {args.owner}")
    print(f"Repositories: {len(repos)}")
    print(f"Open PRs: {open_pr_total}")
    print(f"Open issues: {open_issue_total}")
    if protection:
        protected = sum(1 for item in protection if item.get("default_branch_protected") is True)
        errors = sum(1 for item in protection if item.get("errors"))
        print(f"Protected default branches: {protected}/{len(protection)}")
        print(f"Protection readback errors: {errors}")

    print("Recent repositories:")
    for item in repos[:10]:
        print(
            f"  - {item.get('full_name')} "
            f"vis={item.get('visibility')} "
            f"prs={item.get('open_prs')} "
            f"issues={item.get('open_issues')} "
            f"updated={str(item.get('updated_at') or '')[:10]}"
        )


if __name__ == "__main__":
    main()
