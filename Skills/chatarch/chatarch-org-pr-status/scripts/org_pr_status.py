#!/usr/bin/env python3
"""Summarize repositories with open pull requests for a GitHub owner.

This script uses the public ChatGH CLI. It is read-only and never prints raw
credentials. It first calls `chatgh repo list` to find repositories where
`open_prs > 0`, then calls `chatgh pr list` for exact PR details.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


def _chatgh_command() -> list[str]:
    override = os.environ.get("CHATGH_COMMAND")
    if override:
        return shlex.split(override)
    python = os.environ.get("CHATGH_PYTHON", sys.executable)
    return [python, "-m", "chatgh.cli"]


def _run_json(args: list[str], *, required: bool = True) -> Any:
    command = [*_chatgh_command(), *args, "--json-output"]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(command)}"
        if not required:
            return {"error": message, "command": command}
        raise SystemExit(message)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        if not required:
            return {"error": f"failed to parse JSON from chatgh output: {exc}", "command": command}
        raise SystemExit(f"failed to parse JSON from chatgh output: {exc}") from exc


def _short_date(value: object) -> str:
    return str(value or "")[:10]


def _repo_name(item: dict[str, Any]) -> str:
    return str(item.get("full_name") or item.get("name") or "")


def collect_status(owner: str, limit: int, pr_limit_per_repo: int) -> dict[str, Any]:
    repos = _run_json([
        "repo",
        "list",
        "--owner",
        owner,
        "--limit",
        str(limit),
        "--sort",
        "updated",
        "--direction",
        "desc",
    ])

    repositories: list[dict[str, Any]] = []
    total_open_prs = 0
    listed_open_prs = 0
    repositories_with_unknown_pr_count = 0
    for repo in repos:
        open_prs_value = repo.get("open_prs")
        if open_prs_value is None:
            repositories_with_unknown_pr_count += 1
            continue
        open_prs = int(open_prs_value or 0)
        if open_prs <= 0:
            continue
        full_name = _repo_name(repo)
        detail_limit = min(open_prs, pr_limit_per_repo)
        prs = _run_json([
            "pr",
            "list",
            "--repo",
            full_name,
            "--state",
            "open",
            "--limit",
            str(detail_limit),
        ], required=False)
        pr_list_error = None
        if isinstance(prs, dict) and prs.get("error"):
            pr_list_error = prs["error"]
            prs = []
        total_open_prs += open_prs
        listed_open_prs += len(prs)
        repositories.append({
            "repo": full_name,
            "visibility": repo.get("visibility"),
            "repo_updated_at": repo.get("updated_at"),
            "inventory_open_prs": open_prs,
            "listed_open_prs": len(prs),
            "truncated": open_prs > len(prs),
            "pr_list_error": pr_list_error,
            "open_prs": prs,
        })

    return {
        "owner": owner,
        "repo_limit": limit,
        "repositories_scanned": len(repos),
        "repositories_with_open_prs": len(repositories),
        "repositories_with_unknown_pr_count": repositories_with_unknown_pr_count,
        "total_open_prs": total_open_prs,
        "listed_open_prs": listed_open_prs,
        "pr_limit_per_repo": pr_limit_per_repo,
        "repositories": repositories,
    }


def print_table(payload: dict[str, Any]) -> None:
    print(f"Owner: {payload['owner']}")
    print(f"Repositories scanned: {payload['repositories_scanned']}")
    print(f"Repositories with open PRs: {payload['repositories_with_open_prs']}")
    if payload.get("repositories_with_unknown_pr_count"):
        print(f"Repositories with unknown PR count: {payload['repositories_with_unknown_pr_count']}")
    print(f"Total open PRs: {payload['total_open_prs']}")
    if payload.get("listed_open_prs") != payload.get("total_open_prs"):
        print(f"Listed open PR details: {payload['listed_open_prs']} (limit per repo: {payload['pr_limit_per_repo']})")

    if payload["total_open_prs"] == 0:
        print("Open PRs: none")
        return

    print("\nOpen PRs:")
    rows: list[list[str]] = []
    for repo in payload["repositories"]:
        repo_name = repo["repo"]
        for pr in repo.get("open_prs") or []:
            rows.append([
                repo_name,
                f"#{pr.get('number')}",
                str(pr.get("title") or ""),
                str(pr.get("mergeable_state") or pr.get("mergeable") or ""),
                str(pr.get("base") or ""),
                str(pr.get("head") or ""),
                _short_date(pr.get("updated_at")),
                str(pr.get("url") or ""),
            ])
        if repo.get("truncated"):
            rows.append([
                repo_name,
                "...",
                f"{repo.get('inventory_open_prs')} total open PRs; showing {repo.get('listed_open_prs')}",
                "",
                "",
                "",
                "",
                "",
            ])
        if repo.get("pr_list_error"):
            rows.append([
                repo_name,
                "ERR",
                "PR list unavailable; see JSON pr_list_error",
                "error",
                "",
                "",
                "",
                "",
            ])

    headers = ["repo", "pr", "title", "state", "base", "head", "updated", "url"]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = min(max(widths[i], len(value)), 44 if i == 2 else 32)
    print("  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        clipped = [value[:widths[i]] for i, value in enumerate(row)]
        print("  ".join(value.ljust(widths[i]) for i, value in enumerate(clipped)))


def main() -> None:
    parser = argparse.ArgumentParser(description="List repositories with open PRs for a GitHub owner using ChatGH.")
    parser.add_argument("--owner", default="ChatArch", help="GitHub owner or organization.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum repositories to scan from repo inventory.")
    parser.add_argument("--pr-limit-per-repo", type=int, default=20, help="Maximum open PR details to list for each repository.")
    parser.add_argument("--json-output", action="store_true", help="Print JSON instead of a human table.")
    parser.add_argument("--output", help="Optional path to write JSON payload.")
    args = parser.parse_args()

    payload = collect_status(args.owner, args.limit, args.pr_limit_per_repo)

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_table(payload)
        if args.output:
            print(f"\nJSON written to: {args.output}")


if __name__ == "__main__":
    main()
