---
name: chatmemory-local-branch-loop
description: Local machine workflow for ChatMemory PR/MR sync and returning to the machine's long-running branch.
version: 0.1.0
tags:
  - local
  - ChatMemory
  - GitHub
---

# ChatMemory Local Branch Loop

This is a local-only skill for this Playground machine. Do not move it into shared ChatMemory groups such as `Skills/chatarch`, `Skills/common`, or `Skills/agents`.

## Local convention

- Repo: `/Users/rexwzh/Playground/core/ChatMemory`
- Default branch: `main`
- This machine's long-running branch: `rex/chatmini`
- Other machines may use different local long-running branch names.

## Complete loop

Treat a ChatMemory sync as one lightweight complete action:

1. Work on `rex/chatmini`.
2. Self-review the diff lightly.
3. Open or update a PR from `rex/chatmini` to `main`.
4. Merge the PR/MR when ready.
5. Sync `main`.
6. Reset/overwrite `rex/chatmini` from the updated `main`.
7. Force-push `rex/chatmini` with lease.

## Commands

```bash
cd /Users/rexwzh/Playground/core/ChatMemory

git diff --check
chatgh pr create --repo ChatArch/ChatMemory --base main --head rex/chatmini --title "TITLE" --body-file BODY.md --json-output
chatgh pr merge NUMBER --repo ChatArch/ChatMemory --method squash --check --json-output

git fetch --prune origin
git checkout main
git pull --ff-only origin main
git checkout rex/chatmini
git reset --hard main
git push --force-with-lease origin rex/chatmini
```

## Boundary

This skill records machine-local branch policy. Shared ChatArch/ChatMemory skills should only describe portable repo workflows, not this machine's branch name.
