---
name: chatmemory-local-branch-loop
description: Local machine workflow for ChatMemory PR/MR sync and maintaining this machine's long-running branch.
version: 0.1.0
tags:
  - local
  - ChatMemory
  - GitHub
---

# ChatMemory Local Branch Loop

This is a local-only skill for this Playground machine. Do not move it into shared ChatMemory groups such as `Skills/chatarch`, `Skills/common`, or `Skills/agents`.

## Local convention

- Repo: `/home/cubebot/Playground/core/ChatMemory`
- Default branch: `main`
- This machine's long-running branch: `rex/cubelab`
- Keep this branch current by fetching and merging/fast-forwarding from `origin/main`; do not use `git reset --hard` unless the user explicitly approves it.
- Other machines may use different local long-running branch names.

## Complete loop

Treat a ChatMemory sync as one lightweight complete action:

1. Work on `rex/cubelab`.
2. Self-review the diff lightly.
3. Open or update a PR from `rex/cubelab` to `main`.
4. Merge the PR/MR when ready.
5. Sync `main`.
6. Bring `rex/cubelab` forward from the updated `main` by merge or fast-forward.
7. Push `rex/cubelab` normally; use force-with-lease only after explicit confirmation that branch history was intentionally rewritten.

## Commands

```bash
cd /home/cubebot/Playground/core/ChatMemory

git diff --check
chatgh pr create --repo ChatArch/ChatMemory --base main --head rex/cubelab --title "TITLE" --body-file BODY.md --json-output
chatgh pr merge NUMBER --repo ChatArch/ChatMemory --method squash --check --json-output

git fetch --prune origin
git checkout main
git pull --ff-only origin main
git checkout rex/cubelab
git merge --ff-only main || git merge main
git push origin rex/cubelab
```

## Boundary

This skill records machine-local branch policy. Shared ChatArch/ChatMemory skills should only describe portable repo workflows, not this machine's branch name.
