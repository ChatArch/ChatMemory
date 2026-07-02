---
name: chatmemory-local-branch-loop
description: Template for creating a machine-local ChatMemory/Skills refresh workflow with a long-running machine branch.
version: 0.3.0
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

## Intent

Do not apply a blanket rule such as “never rewrite history” or “always rebase”. Choose the operation by intent:

1. **Development / PR-preparation phase**
   - Preserve current work.
   - Use normal commits.
   - When preparing to push/open PR, preserve local branch information richness: do not rebase, reset, or delete commits before the work has reached `<default-branch>`.
   - Do not rebase just because `<default-branch>` moved while developing or while preparing a PR.
   - The PR needs the original branch to still contain the work being proposed to `<default-branch>`.

2. **Post-merge refresh / return-to-default-branch phase**
   - After the PR/MR has been merged to `<default-branch>`, the machine branch should be reset/refreshed to the latest `<default-branch>` so the next work batch starts cleanly from `<default-branch>`.
   - If it can fast-forward to `origin/<default-branch>`, fast-forward.
   - If it cannot fast-forward because it had unique commits, first merge those commits to `<default-branch>` through the PR/MR flow. After the PR/MR is merged and `origin/<default-branch>` contains the result, reset/refresh `<machine-branch>` to the updated default branch and push with lease.
   - This prevents the machine branch from repeatedly appearing ahead of `<default-branch>` with already-merged/stale commits and avoids accumulating conflict-prone ancestry.

The reset/force-with-lease step belongs only to the explicit post-merge refresh/return-to-default-branch phase after the work is already merged to `<default-branch>`; it is not the development update or PR-preparation mechanism.

## Complete refresh loop

1. Confirm the active backend/workspace before touching this repo.
2. Enter `<chatmemory-repo>`.
3. Check out `<machine-branch>` and inspect `git status --short --branch`.
4. If the worktree has dirty files, review and commit intended skill changes first. Do not hide dirty work behind branch switches.
5. Fetch remote state:
   ```bash
   git fetch --prune origin
   ```
6. Check whether the machine branch can fast-forward to default branch:
   ```bash
   git merge-base --is-ancestor HEAD origin/<default-branch>
   echo $?
   ```
   - exit `0`: `HEAD` is already an ancestor of `origin/<default-branch>`; fast-forward is valid.
   - nonzero: the machine branch has unique commits not in `origin/<default-branch>`; do not reset them away.
7. If fast-forward is valid, run `git merge --ff-only origin/<default-branch>` and push normally.
8. If fast-forward is not valid:
   - run validation (`git diff --check`, changed-skill frontmatter/name/reference checks, script checks when relevant)
   - push `<machine-branch>` normally
   - open/update PR/MR from `<machine-branch>` to `<default-branch>` when the user asks for合版/PR or the batch is ready
   - merge only after explicit approval
   - after merge, fetch/pull latest `<default-branch>`, then reset/refresh `<machine-branch>` to it and push with lease
9. Record conflicts/resolution in active task `progress.md` when a task record exists.

## Commands

```bash
cd <chatmemory-repo>

git checkout <machine-branch>
git status --short --branch
# If dirty, review and commit intended local changes first.

git fetch --prune origin

if git merge-base --is-ancestor HEAD origin/<default-branch>; then
  # The machine branch has no unique unmerged commits. Refresh by fast-forward only.
  git merge --ff-only origin/<default-branch>
  git push origin <machine-branch>
else
  # The machine branch has unique commits. Do not rebase/reset them before they are in default branch.
  git diff --check
  # Run changed-skill validation here.
  git push origin <machine-branch>

  # Only when requested/ready:
  chatgh pr create \
    --repo <repo-slug> \
    --base <default-branch> \
    --head <machine-branch> \
    --title "TITLE" \
    --body-file BODY.md \
    --json-output

  # Merge only after explicit approval. Then refresh the machine branch from default branch:
  git fetch --prune origin
  git checkout <default-branch>
  git pull --ff-only origin <default-branch>
  git checkout <machine-branch>
  git reset --hard <default-branch>
  git push --force-with-lease origin <machine-branch>
fi
```

`chatgh pr merge ...` is a real remote mutation. Run it only after explicit merge approval.

## Conflict handling

When preparing the PR/MR or resolving conflicts:

1. Read both sides of each conflict.
2. Preserve the current machine branch's work intent until it is merged to `<default-branch>`.
3. Preserve newer shared/default-branch changes unless they are clearly superseded.
4. Prefer placeholders over machine-specific names in shared templates.
5. Validate resolved files before committing.
6. Record what conflicted and how it was resolved in the active task `progress.md` when a task record exists.

## Boundary

This template records the shape of a machine-local branch policy. The copied local skill should contain real machine-specific paths and branch names; this template keeps placeholders so it can be reused on new machines.

Key invariant: the machine branch starts each refreshed work batch from `<default-branch>`. Development commits are preserved until merged; after they are merged, the machine branch is reset/refreshed back to `<default-branch>` so future batches do not accumulate repeated merge commits or stale branch ancestry.
