---
name: chatgh-pr-and-ci-workflow
description: ChatArch repositories use ChatGH to inspect PR readiness, manage PR write operations, CI checks, Actions logs, repository inventory, protection status, and credential capabilities.
version: 0.1.2
tags:
  - ChatArch
  - ChatGH
  - GitHub
  - pull-requests
  - CI
  - repository-governance
---

# ChatGH PR / CI / Repository Workflow

## Scope

Use this skill for ChatArch-series GitHub operations that should run through `chatgh`:

- PR list/view/check readiness;
- PR create/comment/edit workflow through `chatgh>=0.2.6`;
- guarded PR merge only after explicit user authorization;
- CI check and Actions run/job triage;
- repository inventory and prioritization;
- default-branch protection readback;
- token capability checks and repo-local auth verification.

This belongs under `Skills/chatarch/`, not `Skills/common/`, because the commands, defaults, and governance assumptions are ChatArch-specific.

## Hard boundaries

- PR readiness is read-only. It is not merge authorization.
- Do not run a merge command unless the user explicitly asks to merge that specific PR.
- Do not print raw tokens, `.git/config` `extraHeader` values, Authorization headers, or decoded credentials.
- Do not write tokenized Git remote URLs.
- Repository visibility and branch-protection mutation are separate approval gates. This skill covers readback and triage by default.
- For ChatTool/ChatArch work, use the ChatArch venv when possible:

```bash
/Users/rexwzh/.chatarch/venv/bin/python -m chatgh.cli ...
```

If the installed command is stale, use the local source checkout:

```bash
cd ~/Playground/core/ChatGH
PYTHONPATH=src /Users/rexwzh/.chatarch/venv/bin/python -m chatgh.cli ...
```

## Workspace record

Start from the workspace root and record findings in the active project:

```bash
cd ~/Playground
sed -n '1,140p' AGENTS.md
sed -n '1,180p' projects/README.md
```

Reports should go under the active project, for example:

```text
projects/<task>/reports/chatgh-pr-readiness.md
projects/<task>/playground/chatgh-pr-checks-<repo>-<number>.json
projects/<task>/playground/chatgh-repo-inventory-<owner>.json
```

## PR readiness workflow

Use when preparing a PR status summary or deciding whether a PR can be proposed for merge review.

```bash
chatgh pr view 207 --repo cubenlp/ChatTool --json-output
chatgh pr checks 207 --repo cubenlp/ChatTool --json-output
```

Classify:

- `mergeable == true` and `mergeable_state == clean`, all checks success/skipped: ready for human merge decision.
- `mergeable_state == dirty`: branch has conflicts; update/rebase/merge target branch first.
- pending/in_progress checks: wait or poll in the outer workflow.
- failed/cancelled checks: triage logs before changing code.

Helper script:

```bash
python Skills/chatarch/chatgh-pr-and-ci-workflow/scripts/pr_readiness.py \
  --repo cubenlp/ChatTool \
  --number 207
```

Optional JSON output:

```bash
python Skills/chatarch/chatgh-pr-and-ci-workflow/scripts/pr_readiness.py \
  --repo cubenlp/ChatTool \
  --number 207 \
  --json-output > reports/pr-207-readiness.json
```

## CI triage workflow

Use when a PR check is red or incomplete.

1. Get check summary:

   ```bash
   chatgh pr checks 207 --repo cubenlp/ChatTool --json-output
   ```

2. Inspect workflow run:

   ```bash
   chatgh run view --repo cubenlp/ChatTool --run-id <RUN_ID> --json-output
   ```

3. Save failed job logs:

   ```bash
   chatgh run logs --repo cubenlp/ChatTool --job-id <JOB_ID> --tail 200 --output reports/job-<JOB_ID>.log
   ```

4. Classify the failure:

   - introduced by this PR;
   - pre-existing repository failure;
   - metadata/governance gate;
   - infrastructure/resource flake.

Do not patch code before reading the actual failing job log.

## Repository inventory workflow

Use when the user asks what ChatArch repositories are active, stale, or blocked.

```bash
chatgh repo list --owner ChatArch --limit 100 --sort updated --direction desc
chatgh repo list --owner ChatArch --limit 100 --sort updated --direction desc --json-output \
  > reports/chatarch-repo-list.json
```

Helper script:

```bash
python Skills/chatarch/chatgh-pr-and-ci-workflow/scripts/repo_inventory_snapshot.py \
  --owner ChatArch \
  --limit 100 \
  --output reports/chatarch-repo-inventory.json
```

Use inventory to prioritize open PRs/issues and recently updated repositories. Keep protection/governance checks separate.

## Repository protection readback

Single repository:

```bash
chatgh repo protection --repo ChatArch/ChatGH --json-output
```

Owner inventory:

```bash
chatgh repo protection --owner ChatArch --limit 100 --jobs 8 --json-output \
  > reports/chatarch-protection-inventory.json
```

Report configured protection separately from API/ruleset readability errors.

## Token and permission checks

Before write operations, confirm effective permissions without exposing the token:

```bash
chatgh repo-perms --repo ChatArch/ChatGH --json-output
```

Check for:

- `can_read_pr` for reading PRs;
- `can_comment_pr` for comments;
- `can_merge_pr` for merges;
- `can_view_checks` and `can_view_actions` for CI triage.

Token resolution order is:

1. explicit `--token`;
2. repo-local `.git/config` HTTPS auth header;
3. ChatEnv typed env `GITHUB_ACCESS_TOKEN`.

## PR write workflow

Available since `chatgh>=0.2.6`. Use these commands instead of ad-hoc GitHub REST snippets when creating or updating PRs:

```bash
chatgh pr create --repo owner/repo --base main --head branch --title "TITLE" --body-file BODY.md --json-output
chatgh pr comment NUMBER --repo owner/repo --body-file COMMENT.md --json-output
chatgh pr edit NUMBER --repo owner/repo --title "TITLE" --body-file BODY.md --json-output
```

Before any write operation, confirm permissions without exposing the token:

```bash
chatgh repo-perms --repo owner/repo --json-output
```

Use `chatgh pr merge` only after the user explicitly authorizes merging that exact PR and checks are green:

```bash
chatgh pr checks NUMBER --repo owner/repo --json-output
chatgh pr merge NUMBER --repo owner/repo --method squash --check --json-output
```

`pr merge` is a real mutation, not a dry run. For mergeability/readiness summaries, keep using `pr view` and `pr checks`.


## Backlog candidates for ChatGH CLI

These operations are still candidates for future promotion:

```bash
chatgh pr close NUMBER --repo owner/repo --comment-file COMMENT.md
chatgh pr ready NUMBER --repo owner/repo --json-output
```

A future `chatgh pr ready` should stay read-only. Merge readiness must remain separate from merge execution.
