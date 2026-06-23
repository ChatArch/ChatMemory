#!/usr/bin/env python3
"""Summarize ChatGH PR readiness without mutating GitHub state.

This script shells out to `python -m chatgh.cli` so it uses the same token
resolution and output semantics as the public ChatGH CLI. It never prints raw
credentials.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any


def _chatgh_command() -> list[str]:
    override = os.environ.get("CHATGH_COMMAND")
    if override:
        return override.split()
    python = os.environ.get("CHATGH_PYTHON", sys.executable)
    return [python, "-m", "chatgh.cli"]


def _run_json(args: list[str]) -> Any:
    command = [*_chatgh_command(), *args, "--json-output"]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(command)}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"failed to parse JSON from chatgh output: {exc}") from exc


def _check_conclusion_ok(value: str | None) -> bool:
    return value in {"success", "skipped", "neutral"}


def build_summary(repo: str, number: int) -> dict[str, Any]:
    view = _run_json(["pr", "view", str(number), "--repo", repo])
    checks = _run_json(["pr", "checks", str(number), "--repo", repo])

    check_runs = checks.get("check_runs") or []
    workflows = checks.get("workflow_runs") or []
    pending = []
    failed = []
    passed = []

    for item in check_runs:
        status = item.get("status")
        conclusion = item.get("conclusion")
        name = item.get("name") or "<unnamed>"
        if status != "completed":
            pending.append(name)
        elif _check_conclusion_ok(conclusion):
            passed.append(name)
        else:
            failed.append({"name": name, "conclusion": conclusion})

    workflow_pending = [
        item.get("name") or item.get("display_title") or "<workflow>"
        for item in workflows
        if item.get("status") != "completed"
    ]
    workflow_failed = [
        {"name": item.get("name") or item.get("display_title") or "<workflow>", "conclusion": item.get("conclusion")}
        for item in workflows
        if item.get("status") == "completed" and not _check_conclusion_ok(item.get("conclusion"))
    ]

    mergeable = view.get("mergeable")
    mergeable_state = view.get("mergeable_state")
    ready = bool(
        view.get("state") == "open"
        and mergeable is True
        and mergeable_state == "clean"
        and not pending
        and not failed
        and not workflow_pending
        and not workflow_failed
    )

    blockers: list[str] = []
    if view.get("state") != "open":
        blockers.append(f"PR state is {view.get('state')}")
    if mergeable is not True or mergeable_state != "clean":
        blockers.append(f"mergeability is mergeable={mergeable} state={mergeable_state}")
    if pending:
        blockers.append("pending check runs: " + ", ".join(pending))
    if failed:
        blockers.append("failed check runs: " + ", ".join(f"{x['name']}={x['conclusion']}" for x in failed))
    if workflow_pending:
        blockers.append("pending workflows: " + ", ".join(workflow_pending))
    if workflow_failed:
        blockers.append("failed workflows: " + ", ".join(f"{x['name']}={x['conclusion']}" for x in workflow_failed))

    return {
        "repo": repo,
        "number": number,
        "url": view.get("url"),
        "title": view.get("title"),
        "state": view.get("state"),
        "base": view.get("base"),
        "head": view.get("head"),
        "head_sha": view.get("head_sha"),
        "mergeable": mergeable,
        "mergeable_state": mergeable_state,
        "ready_for_human_merge_decision": ready,
        "blockers": blockers,
        "passed_check_runs": passed,
        "pending_check_runs": pending,
        "failed_check_runs": failed,
        "pending_workflows": workflow_pending,
        "failed_workflows": workflow_failed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize ChatGH PR readiness.")
    parser.add_argument("--repo", required=True, help="Repository in owner/name form.")
    parser.add_argument("--number", required=True, type=int, help="Pull request number.")
    parser.add_argument("--json-output", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    summary = build_summary(args.repo, args.number)
    if args.json_output:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    print(f"PR: {summary['repo']} #{summary['number']}")
    print(f"Title: {summary.get('title') or ''}")
    print(f"URL: {summary.get('url') or ''}")
    print(f"Head: {summary.get('head')} @ {summary.get('head_sha')}")
    print(f"Base: {summary.get('base')}")
    print(f"Mergeable: {summary.get('mergeable')} ({summary.get('mergeable_state')})")
    print(f"Ready for human merge decision: {summary['ready_for_human_merge_decision']}")
    if summary["blockers"]:
        print("Blockers:")
        for item in summary["blockers"]:
            print(f"  - {item}")
    else:
        print("Blockers: none")


if __name__ == "__main__":
    main()
