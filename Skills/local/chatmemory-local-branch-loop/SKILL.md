---
name: chatmemory-local-branch-loop
description: Template for creating a machine-local ChatMemory PR/MR sync skill and maintaining that machine's long-running branch without rewriting history.
version: 0.2.0
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

## Policy

The machine branch is a long-running work ledger. Preserve its visible history.

Default sync policy:

- Use normal commits for local skill updates.
- When `<default-branch>` advances, merge `origin/<default-branch>` into `<machine-branch>` with a normal merge commit if the machine branch has unique commits.
- Resolve conflicts in that merge commit, keeping useful information from both sides.
- Push the machine branch normally.
- Do not rewrite the long branch as routine cleanup.

Do **not** use routine rebase, reset, or force-push on `<machine-branch>`. Only rewrite history when the user explicitly asks for that specific operation and accepts the audit tradeoff.

Keep `<default-branch>` clean: update it only by fast-forwarding from `origin/<default-branch>` or by the reviewed PR/MR merge result.

## Complete loop

Treat a ChatMemory sync as one lightweight complete action. Start with a fetch and compare `<machine-branch>` against `origin/<default-branch>` before deciding whether a PR is needed:

1. Check workspace/backend and enter `<chatmemory-repo>`.
2. Check out `<machine-branch>` and inspect `git status --short --branch`.
3. If the worktree has dirty changes, review and commit intended skill changes before integrating remote updates. Do not switch branches with unreviewed dirty work.
4. Fetch `origin`, then compute `behind ahead` with `git rev-list --left-right --count origin/<default-branch>...HEAD`.
5. If `ahead == 0`, there are no local commits to preserve. Fast-forward `<machine-branch>` to `origin/<default-branch>` and push normally if it moved. This is a fast-forward, not a history rewrite.
6. If `behind != 0` and `ahead != 0`, merge `origin/<default-branch>` into `<machine-branch>` with a normal merge commit, resolve conflicts, validate, and commit the merge.
7. Run validation, usually:
   - `git diff --check`
   - changed-skill frontmatter/name/reference sanity checks
   - any task-specific checks for touched helper scripts
8. Push `<machine-branch>` normally.
9. Open or update a PR/MR from `<machine-branch>` to `<default-branch>` only when the user asks for合版/PR, or when the batch is ready and the workflow calls for review.
10. Merge PR/MR only after explicit approval. After merge, fast-forward local `<default-branch>` from `origin/<default-branch>`. Keep `<machine-branch>` history unless the user explicitly asks to archive or reset it.

## Commands

```bash
cd <chatmemory-repo>

git checkout <machine-branch>
git status --short --branch

# If dirty, review and commit intended local changes first.
# Do not hide dirty work behind branch switches or history rewrites.

git fetch --prune origin
read behind ahead <<EOF
$(git rev-list --left-right --count origin/<default-branch>...HEAD)
EOF
printf 'behind=%s ahead=%s\n' "$behind" "$ahead"

if [ "$ahead" = "0" ]; then
  # No local commits to preserve. Move forward only.
  git merge --ff-only origin/<default-branch>
else
  if [ "$behind" != "0" ]; then
    # Preserve the branch work log with a normal merge commit.
    git merge --no-ff origin/<default-branch>
  fi
  git diff --check
  # Run changed-skill validation here.
  git push origin <machine-branch>
fi
```

PR/MR step, only when requested or ready:

```bash
chatgh pr create \
  --repo <repo-slug> \
  --base <default-branch> \
  --head <machine-branch> \
  --title "TITLE" \
  --body-file BODY.md \
  --json-output
```

`chatgh pr merge ...` is a real remote mutation. Run it only after explicit merge approval.

## Conflict handling

When a merge from `origin/<default-branch>` conflicts:

1. Read both sides of each conflict.
2. Preserve the current machine branch's work log and intent.
3. Preserve newer shared/main changes unless they are clearly superseded.
4. Prefer generic shared-template placeholders over machine-specific names in shared templates.
5. Validate the resolved files before committing the merge.
6. Record what conflicted and how it was resolved in the active task `progress.md` when a task record exists.

## Boundary

This template records the shape of a machine-local branch policy. The copied local skill should contain real machine-specific paths and branch names; this template should keep placeholders so it can be reused on new machines.

The key invariant: `<machine-branch>` is an auditable work ledger. Normal commits and merge commits are allowed and expected; routine history rewriting is not.
