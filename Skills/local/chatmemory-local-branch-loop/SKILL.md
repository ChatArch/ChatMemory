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
4. If `origin/<default-branch>` has advanced while local also has unique commits, merge `origin/<default-branch>` into `<machine-branch>` with a normal merge commit. Resolve conflicts in that merge, keep both sides' useful information, run validation, commit the merge, and push normally.
5. If local has changes that are not on `origin/<default-branch>`, run `git diff --check`, self-review the diff lightly, push `<machine-branch>` normally, then open/update a PR from `<machine-branch>` to `<default-branch>` and merge only after explicit approval.
6. After a PR merge, sync local `<default-branch>` from `origin/<default-branch>`. Do not reset/rebase/force-push the long-running machine branch as routine cleanup; preserve its commit log as the work ledger unless the user explicitly asks to rewrite history.

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
  if [ "$behind" != "0" ]; then
    git merge --no-ff origin/<default-branch>
  fi
  git diff --check
  # Use ChatGH for PR operations; merge only after explicit approval.
  git push origin <machine-branch>
  chatgh pr create --repo <repo-slug> --base <default-branch> --head <machine-branch> --title "TITLE" --body-file BODY.md --json-output
fi
```

## Boundary

This template records the shape of a machine-local branch policy. The copied local skill should contain real machine-specific paths and branch names; this template should keep placeholders so it can be reused on new machines.

Do not use routine rebase/reset/force-push on the long-running branch. The branch history is allowed to contain normal commits and merge commits because it records the machine's ongoing work.
