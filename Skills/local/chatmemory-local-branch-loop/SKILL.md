---
name: chatmemory-local-branch-loop
description: Template for a machine-local ChatMemory/Skills refresh workflow.
version: 0.6.0
tags:
  - local
  - ChatMemory
  - GitHub
---

# ChatMemory Local Branch Loop Template

Copy this template into a machine's workspace-local `skills/local/`, then replace placeholders with that machine's values.

Variables:

- `<chatmemory-repo>`: local ChatMemory checkout path.
- `<default-branch>`: default branch, usually `main`.
- `<machine-branch>`: this machine's ChatMemory branch.
- `<repo-slug>`: remote repository slug, usually `ChatArch/ChatMemory`.

For normal ChatMemory/Skills maintenance, each machine should commit directly on its own long-running machine branch. Do not create extra `feat/...` or `docs/...` branches unless the user explicitly asks for a temporary branch; if such a branch is used, delete it after its PR/MR is merged.

## Refresh rule

There are only two cases after `git fetch --prune origin`:

1. **Can fast-forward first**
   - `<machine-branch>` has no unique local work.
   - Fast-forward to `origin/<default-branch>`.
   - Push `<machine-branch>` normally if it moved.

2. **Cannot fast-forward first**
   - `<machine-branch>` has local work.
   - Keep the local Git log until the PR is merged; do not rebase/reset/clean those commits before merge.
   - Push `<machine-branch>` and open/update PR to `<default-branch>`.
   - Merge the PR with **squash** so `<default-branch>` gets one clean commit. All PR merges to the default branch must use squash.
   - After the squash merge lands on `origin/<default-branch>`, refresh `<machine-branch>` back to `origin/<default-branch>` for the next PR.

## Commands

```bash
cd <chatmemory-repo>

git checkout <machine-branch>
git status --short --branch
# If dirty, review and commit intended local changes first.

git fetch --prune origin

if git merge-base --is-ancestor HEAD origin/<default-branch>; then
  # Case 1: can fast-forward first.
  git merge --ff-only origin/<default-branch>
  git push origin <machine-branch>
else
  # Case 2: cannot fast-forward first; preserve logs for PR.
  git diff --check
  # Run changed-skill validation here.
  git push origin <machine-branch>

  chatgh pr create \
    --repo <repo-slug> \
    --base <default-branch> \
    --head <machine-branch> \
    --title "TITLE" \
    --body-file BODY.md \
    --json-output

  # Merge only after explicit approval. Use squash.
  chatgh pr merge NUMBER \
    --repo <repo-slug> \
    --method squash \
    --check \
    --json-output

  # After squash merge, align the machine branch back to remote default branch for the next PR.
  git fetch --prune origin
  git checkout <default-branch>
  git pull --ff-only origin <default-branch>
  git checkout <machine-branch>
  git reset --hard origin/<default-branch>
  git push --force-with-lease origin <machine-branch>
fi
```

## Notes

- Keep Git log until PR merge because it carries the work being proposed.
- Squash when merging upward so the default branch stays clean.
- Refresh/rebase-align the machine branch only after the squash merge, so the next PR starts from remote default branch.
