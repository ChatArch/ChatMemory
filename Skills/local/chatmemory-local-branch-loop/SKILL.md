---
name: chatmemory-local-branch-loop
description: Template for creating a machine-local ChatMemory PR/MR sync skill and maintaining that machine's long-running branch.
version: 0.1.0
tags:
  - local
  - ChatMemory
  - GitHub
---

# ChatMemory Local Branch Loop Template

This is a copy-and-adapt template for a machine-local skill. Do not link it directly into a workspace's active skill set, and do not move it into shared ChatMemory groups such as `Skills/chatarch`, `Skills/common`, or `Skills/agents`.

Create a workspace-local copy such as `<workspace>/skills/local/chatmemory-local-branch-loop/SKILL.md`, then replace every placeholder below with that machine's real values before use.

## Template variables

- `<workspace>`: the machine's Playground or equivalent workspace root, for example `~/Playground`.
- `<chatmemory-repo>`: the local ChatMemory checkout path, usually `<workspace>/core/ChatMemory`.
- `<default-branch>`: the ChatMemory default branch, usually `main`.
- `<machine-branch>`: this machine's long-running ChatMemory branch, for example `<user-or-machine>/chatmemory-local`.
- `<repo-slug>`: the remote repository slug, usually `ChatArch/ChatMemory`.

## Local convention to fill in after copying

- Repo: `<chatmemory-repo>`
- Default branch: `<default-branch>`
- This machine's long-running branch: `<machine-branch>`
- Other machines may use different local long-running branch names.

## Complete loop

Treat a ChatMemory sync as one lightweight complete action. Start with a fetch and compare `<machine-branch>` against `origin/<default-branch>` before deciding whether a PR is needed:

1. Work on `<machine-branch>` and check the worktree. If `git status --short` shows dirty files, review the diff first and either commit the intended skill changes or pause before moving branches.
2. Fetch `origin`, then compute `behind ahead` with `git rev-list --left-right --count origin/<default-branch>...HEAD`.
3. If local is **not ahead** of `origin/<default-branch>` (`ahead == 0`), there are no local changes to PR. Fast-forward directly to `origin/<default-branch>`, update local `<default-branch>`, and push `<machine-branch>` normally if it moved.
4. If `origin/<default-branch>` is ahead while local has no unique commits, use the same direct fast-forward path; do not open a PR just to refresh the branch.
5. Otherwise local has changes that are not on `origin/<default-branch>`: run `git diff --check`, self-review the diff lightly, open/update a PR from `<machine-branch>` to `<default-branch>`, and merge only after explicit approval.
6. After a PR merge and explicit branch-refresh approval, sync local `<default-branch>` from `origin/<default-branch>`, reset/overwrite `<machine-branch>` from the updated `<default-branch>`, then force-push `<machine-branch>` with lease.

## Commands

```bash
cd <chatmemory-repo>

git checkout <machine-branch>
git status --short
git fetch --prune origin
read behind ahead <<EOF
$(git rev-list --left-right --count origin/<default-branch>...HEAD)
EOF

if [ "$ahead" = "0" ]; then
  git merge --ff-only origin/<default-branch>
  git checkout <default-branch>
  git pull --ff-only origin <default-branch>
  git checkout <machine-branch>
  git push origin <machine-branch>
else
  git diff --check origin/<default-branch>...HEAD
  # Use ChatGH for PR operations; merge only after explicit approval.
  chatgh pr create --repo <repo-slug> --base <default-branch> --head <machine-branch> --title "TITLE" --body-file BODY.md --json-output
  chatgh pr merge NUMBER --repo <repo-slug> --method squash --check --json-output

  git fetch --prune origin
  git checkout <default-branch>
  git pull --ff-only origin <default-branch>
  git checkout <machine-branch>
  git reset --hard <default-branch>
  git push --force-with-lease origin <machine-branch>
fi
```

## Boundary

This template records the shape of a machine-local branch policy. The copied local skill should contain real machine-specific paths and branch names; this template should keep placeholders so it can be reused on new machines.
