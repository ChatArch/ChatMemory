---
name: chatarch-org-pr-status
description: Quickly inspect which ChatArch repositories currently have open pull requests and summarize their PR state via ChatGH.
version: 0.1.0
tags:
  - ChatArch
  - ChatGH
  - GitHub
  - pull-requests
  - organization-status
---

# ChatArch Organization PR Status

## Scope

This is intentionally a small quick-status skill: a convenient one-command way to glance at the current ChatArch organization PR queue before deciding what to work on next. It does not change repository state and does not replace deeper PR review workflows.

Use this skill when the user asks questions like:

- “看一下 ChatArch 里面哪些项目处在 PR 状态。”
- “当前组织里哪些仓库有 MR/PR？”
- “快速看一下整个 ChatArch 当前工作状态。”
- “哪些项目还有 open PR，需要收敛？”

This is a ChatArch-specific operational workflow, so it belongs under `Skills/chatarch/package-development/`, not `Skills/common/`.

## Principle

Use ChatGH as the primary interface:

```bash
chatgh repo list --owner ChatArch --json-output
chatgh pr list --repo ChatArch/<RepoName> --state open --json-output
```

`chatgh repo list` already includes `open_prs`, so first use it as an organization-level filter. Only call `chatgh pr list` for repositories where `open_prs > 0`.

GitHub permissions can legitimately make some fields unavailable. Missing fields or per-repository PR-list failures are acceptable observations: return the fields that are visible, mark unknown counts, and preserve per-repository errors in JSON for follow-up.

## Quick command

From the workspace root:

```bash
cd ~/Playground
python Skills/chatarch/package-development/chatarch-org-pr-status/scripts/org_pr_status.py --owner ChatArch
```

For owners with repositories that have many stale PRs, keep output compact:

```bash
python Skills/chatarch/package-development/chatarch-org-pr-status/scripts/org_pr_status.py \
  --owner cubenlp \
  --pr-limit-per-repo 10
```

Write JSON for follow-up processing:

```bash
python Skills/chatarch/package-development/chatarch-org-pr-status/scripts/org_pr_status.py \
  --owner ChatArch \
  --json-output \
  --output projects/<task>/playground/chatarch-open-prs.json
```

If `chatgh` is not on PATH, install or refresh it first. If the installed command is stale, use the local ChatGH source checkout:

```bash
PYTHONPATH=core/ChatGH/src \
CHATGH_COMMAND='python -m chatgh.cli' \
python Skills/chatarch/package-development/chatarch-org-pr-status/scripts/org_pr_status.py --owner ChatArch
```

## Output interpretation

The script reports:

- total repositories scanned;
- repositories with open PRs;
- repositories where PR count is unknown because the current token/output did not expose `open_prs`;
- total open PR count;
- per-repo PR rows including number, title, URL, author, base/head, mergeable state, and updated time;
- when a repository has more PRs than `--pr-limit-per-repo`, a truncation row preserves the total count while keeping the table readable.

Use the result to decide the next workflow:

- no open PRs: organization is clear from a PR queue perspective;
- one open PR: inspect that PR with `chatgh pr view` / `chatgh pr checks` or the `chatgh-pr-and-ci-workflow` skill;
- multiple open PRs: process sequentially, not as an undifferentiated batch.

## Follow-up commands

For one PR:

```bash
chatgh pr view <NUMBER> --repo ChatArch/<RepoName> --json-output
chatgh pr checks <NUMBER> --repo ChatArch/<RepoName> --json-output
```

Or use the ChatArch readiness helper:

```bash
python Skills/chatarch/package-development/chatgh-pr-and-ci-workflow/scripts/pr_readiness.py \
  --repo ChatArch/<RepoName> \
  --number <NUMBER>
```

## Safety boundaries

- This skill is read-only.
- Do not close, merge, retarget, or comment on PRs from this status workflow.
- Do not print tokens or GitHub auth headers.
- Missing fields are acceptable when token permissions are limited; report them as unknown rather than inventing values.
- If the organization has many repositories, keep `--limit` explicit and raise it only when needed.
- Treat `open_prs` from repo inventory as a filter, then verify with `pr list` for exact details.

## Common pitfalls

- Looking only at local checkouts under `~/Playground/core`; that misses repositories not cloned locally.
- Treating `open_issues_count` as issues only; GitHub counts PRs inside the issues count, so use ChatGH’s separated `open_prs` field.
- Assuming all active work is in the `ChatArch` organization. Some related repos may live under another owner, such as `cubenlp`; run the script again with `--owner <owner>` when needed.
- Treating a status report as merge authorization. It is only an observation step.
