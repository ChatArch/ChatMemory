---
name: chatmemory-local-branch-loop
description: Template for a machine-local ChatMemory/Skills refresh workflow.
version: 0.6.3
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

Treat a user request such as “刷新 Skills” or “同步 ChatMemory/Skills” as one continuous refresh loop: publish local skill changes, squash them into `<default-branch>`, then reset the machine branch back to `origin/<default-branch>` unless there is a real blocker such as conflicts, failing validation, unclear ownership of pre-existing changes, or an explicit user instruction to stop before merge.

A dirty Git worktree is a blocker to resolve, not a normal state to carry across completed tasks. At every meaningful milestone and before ending a task, review `git status`/`git diff`, validate, stage exact logical changes, commit them with a purpose-revealing message, and verify clean status. Never leave known agent-authored changes dirty for the next session or person to reconstruct. If ownership or intent is unclear, stop and ask rather than resetting or guessing.

Before publishing, review the recent updates instead of only checking that Markdown parses. A refresh should catch stale instructions, accidental truncation artifacts, inconsistent templates, and missing index updates before they become shared memory.

## Pre-publish review gate

Run this gate before staging or pushing local skill changes:

1. Read branch state and split the scope into two buckets:
   - committed branch delta against `origin/<default-branch>`;
   - uncommitted dirty diff on `<machine-branch>`.
2. Resolve dirty state instead of carrying it forward:
   - review and commit known, completed, agent-authored changes in focused logical commits;
   - preserve changes whose ownership or intent is unclear and stop for confirmation;
   - never reset, checkout, clean, or overwrite files just to make status appear clean.
3. Review changed `SKILL.md` files for:
   - broken placeholders or truncation artifacts such as `...` inside real keys or commands;
   - new requirements that are not reflected in scaffold/validation sections;
   - version or release instructions that contradict the new flow;
   - machine-specific names, paths, tokens, chat IDs, message IDs, or Feishu/Lark document URLs in shared skill groups.
4. If a blocker is found, patch the skill before committing. If the fix would change another person's unrelated work, stop and report the conflict instead.
5. Stage only the files that belong to this refresh.
6. Commit each coherent update promptly. Before declaring the refresh complete, `git status --short --branch` must show no uncommitted changes.

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
   - Merge the PR with **squash** so `<default-branch>` gets one clean commit. All PR merges to the default branch must use squash. This is part of the normal refresh request; do not pause for a separate merge confirmation unless a blocker appears.
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
  # Run changed-skill validation here before committing/pushing.
  git push origin <machine-branch>

  chatgh pr create \
    --repo <repo-slug> \
    --base <default-branch> \
    --head <machine-branch> \
    --title "TITLE" \
    --body-file BODY.md \
    --json-output

  # Squash merge as part of the refresh loop unless a blocker appeared.
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

## Validation commands

Use a lightweight validation pass for normal skill-only updates:

```bash
git diff --check

python3 - <<'PY'
from pathlib import Path
missing = []
for path in Path('Skills').rglob('SKILL.md'):
    lines = path.read_text(encoding='utf-8').splitlines()
    if not lines or lines[0] != '---':
        missing.append((str(path), 'missing opening frontmatter'))
        continue
    try:
        end = lines[1:].index('---') + 1
    except ValueError:
        missing.append((str(path), 'missing closing frontmatter'))
        continue
    frontmatter = '\n'.join(lines[1:end])
    if 'name:' not in frontmatter or 'description:' not in frontmatter:
        missing.append((str(path), 'missing name/description'))
print('frontmatter_issues', missing)
raise SystemExit(1 if missing else 0)
PY

python3 - <<'PY'
from pathlib import Path
import re

names = {}
for path in Path('Skills').rglob('SKILL.md'):
    text = path.read_text(encoding='utf-8')
    match = re.search(r'^name:\s*([^\n]+)', text, re.M)
    if match:
        names[match.group(1).strip().strip('"').strip("'")] = path

issues = []
for path in Path('Skills').rglob('SKILL.md'):
    lines = path.read_text(encoding='utf-8').splitlines()
    if not lines or lines[0] != '---':
        continue
    try:
        end = lines[1:].index('---') + 1
    except ValueError:
        continue
    in_reference = False
    for line in lines[1:end]:
        if re.match(r'^reference:\s*$', line):
            in_reference = True
            continue
        if in_reference:
            if line and not line.startswith(' ') and not line.startswith('-'):
                in_reference = False
                continue
            match = re.match(r'^\s*-\s*([^:]+):', line)
            if match:
                key = match.group(1).strip().strip('"').strip("'")
                if key not in names:
                    issues.append((str(path), key))
print('reference_issues', issues)
raise SystemExit(1 if issues else 0)
PY
```

For updates that touch scripts, generated examples, or package workflow commands, also run the relevant script/package tests instead of treating the Markdown validation as enough.

## Notes

- Keep Git log until PR merge because it carries the work being proposed.
- Squash when merging upward so the default branch stays clean.
- Refresh/rebase-align the machine branch only after the squash merge, so the next PR starts from remote default branch.
- A plain refresh request already authorizes the full loop: push/open PR, squash merge, fetch default branch, reset the machine branch to `origin/<default-branch>`, and force-with-lease the refreshed machine branch.
- If recent-update review finds blockers, fix them before push/merge or stop with a review report.
