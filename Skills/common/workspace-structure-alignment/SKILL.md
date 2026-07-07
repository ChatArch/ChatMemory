---
name: workspace-structure-alignment
description: Align an older human-AI collaboration workspace to the latest ChatUp workspace scaffold, shared ChatMemory skill layout, and Markdown conventions.
version: 0.2.2
reference:
  - workspace-maintenance: "outer workspace cleanup, discussion/discard routing, archive review, and .trash safety-buffer rules"
---

# Workspace Structure Alignment

Use this skill when an existing machine or old workspace must be brought up to the current `chatup workspace` shape.

Typical triggers:

- a machine was set up with an older workspace template
- root files such as `AGENTS.md`, `ARCHIVE.md`, `TODO.md`, or `projects/README.md` are stale
- `projects/` contains old task/case Markdown that no longer follows the current roles for `PRD.md`, `progress.md`, `memory.md`, `reports/`, `scripts/`, or `playground/`
- `skills/` still uses old copied or topic-level skill folders instead of the current ChatMemory shared groups
- `public/`, `discussion/`, `discard/`, `archive/`, `.trash/`, or `core/` are missing or inconsistent
- after using this workflow, the latest workspace template itself changed and this skill must be updated

## Core principle

Treat this skill as a rolling migration playbook for the latest `chatup workspace` template.

The source of truth is not memory or a single machine's current files. Re-check the current implementation and templates before editing an old workspace:

```bash
# In a ChatUp checkout or installed environment
chatup workspace <workspace-root> --language zh --dry-run -I
```

If source is available, also inspect these current files:

```text
core/ChatUp/src/chatup/setup/workspace/core.py
core/ChatUp/src/chatup/setup/workspace/cli.py
core/ChatUp/src/chatup/setup/workspace/options.py
core/ChatUp/src/chatup/setup/workspace/render.py
core/ChatUp/src/chatup/setup/workspace/templates/default/zh/AGENTS.md
core/ChatUp/src/chatup/setup/workspace/templates/default/zh/projects/README.md
core/ChatUp/tests/test_workspace_setup.py
```

When the template evolves, update this skill in the same pass. Do not let the skill become a historical snapshot.

## Current baseline shape

The current base workspace is a wrapper around source repositories and human-facing collaboration records:

```text
<workspace>/
  AGENTS.md
  TODO.md
  ARCHIVE.md
  .trash/
  projects/
    README.md
  discussion/
    MM-DD-<topic>/
      card.md
      PRD.md
      progress.md
      reports/
      Items/
  archive/
    index.md
    YYYY-MM-DD/
  discard/
  core/
  scripts/
    README.md
  skills/
    README.md -> core/ChatMemory/Skills/README.md   # when ChatMemory is enabled
    agents -> core/ChatMemory/Skills/agents         # symlink
    chatarch -> core/ChatMemory/Skills/chatarch     # symlink
    common -> core/ChatMemory/Skills/common         # symlink
    local/                                         # real local-only directory, not symlink
      README.md
  public/
    README.md
```

Important current conventions:

- `projects/` holds active work. Old inactive work goes to `archive/YYYY-MM-DD/`, where `YYYY-MM-DD` is the date when archiving happens, and `archive/index.md` records what moved.
- The directory protocol has two basic project-like item types: Project items and Discussion items. `discussion/` holds Discussion items; each Discussion uses `discussion/MM-DD-<topic>/card.md` to describe the topic, absorption goal, current judgment, and `Items/` classification logic. Use `Items/` when a Discussion item temporarily absorbs other items for correction, routing, or synthesis.
- A completed Discussion should handle and clear its concrete `Items/`, then keep `card.md`, `progress.md`, or reports as the record instead of nesting Discussions recursively.
- `discard/` is the soft-delete/recycle area for tasks explicitly deleted by the user or judged no longer valuable. `.trash/` remains a low-level safety buffer, not a main lifecycle area.
- `core/` holds source repositories. Do not copy source repos into individual projects.
- `scripts/` is for reusable workspace-level maintenance scripts. Task-specific scripts belong under the task project.
- `public/` is for public-facing publish artifacts or links. With ChatBlog enabled, `public/chatblog` links to `core/ChatBlog/docs`.
- `skills/local/` is private/local. Shared skills come from ChatMemory groups: `chatarch`, `common`, and `agents`.
- ChatArch topic skills such as `package-development` and `package-review` live under `skills/chatarch/`, not as top-level `skills/package-development` or `skills/package-review`.

## Project/case Markdown baseline

A current execution project is minimal at the root:

```text
<project>/
  PRD.md        # stable goal, scope, constraints, completion criteria
  progress.md   # chronological status and proof; update after substantive actions
  memory.md     # local context, only when useful
  .trash/
  reports/      # named reports, not generic report.md when avoidable
  scripts/      # project-local scripts
  playground/   # scratch/output/runtime files; not /tmp
  reference/    # local references/examples
```

For topic group directories:

```text
projects/<topic>/
  README.md
  .trash/
  <task-or-case>/
    PRD.md
    progress.md
```

The topic directory is an index layer, not an execution project. Do not scatter `reports/`, `playground/`, or task artifacts directly in the topic root.

## Alignment workflow

### 1. Confirm target and source

1. Confirm the active backend and target workspace root.
2. Read target `AGENTS.md` first if it exists.
3. Read target `projects/README.md`, `ARCHIVE.md`, and `archive/index.md` if present.
4. Check whether the target already has `discussion/` and `discard/`; older workspaces may not.
5. Locate the current ChatUp implementation or installed `chatup` command.
6. Run a dry-run plan for the target when possible:

```bash
chatup workspace <workspace-root> --language zh --with-memory --dry-run -I
```

Use `--with-chattool`, `--with-chatblog`, or custom `--*-source` flags only when those modules are intended for the target workspace.

### 2. Inventory before editing

Record the current shape before changes:

```bash
cd <workspace-root>
pwd
git -C core/ChatMemory status --short --branch 2>/dev/null || true
git -C core/ChatUp status --short --branch 2>/dev/null || true
python3 - <<'PY'
from pathlib import Path
root = Path('.').resolve()
for rel in ['AGENTS.md','TODO.md','ARCHIVE.md','projects/README.md','archive/index.md','scripts/README.md','public/README.md','skills/README.md']:
    p = root / rel
    print(rel, 'exists=' + str(p.exists()), 'symlink=' + str(p.is_symlink()))
for rel in ['.trash','projects','discussion','archive','discard','core','scripts','skills','public','skills/local']:
    p = root / rel
    print(rel, 'exists=' + str(p.exists()), 'dir=' + str(p.is_dir()), 'symlink=' + str(p.is_symlink()))
for rel in ['skills/agents','skills/chatarch','skills/common','public/chatblog']:
    p = root / rel
    print(rel, 'exists=' + str(p.exists()), 'symlink=' + str(p.is_symlink()), 'target=' + (str(p.resolve()) if p.exists() or p.is_symlink() else ''))
PY
```

Keep this inventory in a task report or `progress.md` when the alignment is part of a workspace task.

### 3. Apply root scaffold non-destructively

Create missing base directories:

```text
.trash/
projects/
discussion/
archive/
discard/
core/
scripts/
skills/
public/
```

For root protocol files, prefer a reviewed patch over blind overwrite:

- `AGENTS.md`: current workspace entry and workflow contract
- `TODO.md`: near-term workspace TODO note
- `ARCHIVE.md`: archive procedure guide
- `projects/README.md`: project naming, topic grouping, lifecycle areas, file roles
- `archive/index.md`: archive contents index
- `scripts/README.md`: workspace-level scripts convention
- `public/README.md`: public artifact convention

If an existing file conflicts, move the old file to the nearest `.trash/` with a timestamped name before replacing or rewrite it in-place with the preserved local facts. Do not delete.

### 4. Align ChatMemory shared skills

When the target should use shared skills:

1. Ensure `core/ChatMemory` exists and is a git checkout, or clone it from the configured source.
2. If the checkout is dirty, do not force-update it. Review or skip the update.
3. Ensure `core/ChatMemory/Skills/` exists.
4. Link the shared groups:

```text
skills/README.md -> core/ChatMemory/Skills/README.md
skills/agents    -> core/ChatMemory/Skills/agents
skills/chatarch  -> core/ChatMemory/Skills/chatarch
skills/common    -> core/ChatMemory/Skills/common
```

5. Ensure `skills/local/` is a real directory, not a symlink. Add a local README explaining that private/machine-specific skills stay there.
6. If old top-level topic links such as `skills/package-development` or `skills/package-review` exist, move them to `.trash/` after confirming their content is now reachable under `skills/chatarch/`.

Never replace an existing non-symlink `skills/<shared-group>` path without review. Move-first into `.trash/` keeps rollback possible.

### 5. Align optional module links

Current optional modules:

- ChatTool: `core/ChatTool`; skill content should come from ChatMemory shared groups, not old ChatTool-local copied skills.
- ChatBlog: `core/ChatBlog`; `public/chatblog` links to `core/ChatBlog/docs`, creating `docs/README.md` if missing.
- ChatMemory: `core/ChatMemory` plus `skills/README.md`, `skills/{chatarch,common,agents}`, and real `skills/local/`.

Use the same dirty-check rule for each source repo: if local changes exist, skip or ask before updating.

### 6. Review old projects/cases

Do not bulk rewrite every old project automatically. Review and update only active or user-selected projects/cases.

For each active project/case:

1. Identify whether it is an execution project or a topic index.
2. Ensure execution project roots use `PRD.md` and `progress.md` as the main control files.
3. Move generic reports, scripts, scratch outputs, and references into `reports/`, `scripts/`, `playground/`, or `reference/` as appropriate.
4. Add `.trash/` before any cleanup.
5. If a topic root contains task artifacts, create or update `projects/<topic>/README.md` and move artifacts into a child project after review.
6. Preserve user-written history. Prefer small patches and move-first cleanup over regenerated Markdown.
7. If several projects need to be digested together or user correction should become a reusable decision sample, create or update a `discussion/MM-DD-<topic>/` node, write/update its `card.md`, and move absorbed projects into `Items/` after review.
8. When the Discussion completes, handle and clear `Items/`, then update `card.md`, `progress.md`, or reports with the result.
9. If a task is explicitly deleted or judged no longer valuable, move it to `discard/` rather than physical deletion.
10. When an inactive project is truly old, follow the archive flow: collect candidates, model-review, move to `archive/YYYY-MM-DD/` using the date when archiving happens, then update `archive/index.md`.

### 7. Verify the final shape

After changes, verify with commands and file reads, not visual guesswork:

```bash
cd <workspace-root>
python3 - <<'PY'
from pathlib import Path
root = Path('.').resolve()
required_dirs = ['.trash','projects','discussion','archive','discard','core','scripts','skills','public']
required_files = ['AGENTS.md','TODO.md','ARCHIVE.md','projects/README.md','archive/index.md','scripts/README.md','public/README.md']
missing = [p for p in required_dirs if not (root/p).is_dir()]
missing += [p for p in required_files if not (root/p).exists()]
print('missing:', missing)
for rel in ['skills/README.md','skills/agents','skills/chatarch','skills/common']:
    p = root / rel
    print(rel, 'symlink=' + str(p.is_symlink()), 'target=' + (str(p.resolve()) if p.exists() or p.is_symlink() else ''))
local = root / 'skills' / 'local'
print('skills/local real_dir=', local.is_dir() and not local.is_symlink())
PY
```

Also run any project-specific validation that the alignment touched, for example `git diff --check` in the ChatMemory repo if shared skills were edited.

## Updating this skill itself

This skill must be updated whenever the latest scaffold changes. During each alignment pass:

1. Compare this skill against current ChatUp implementation/templates and ChatMemory `Skills/README.md`.
2. If `BASE_DIRS`, root files, linked skill groups, optional modules, or project Markdown roles changed, patch this `SKILL.md` in the same branch.
3. Update `Skills/common/README.md` if the skill name, purpose, or grouping changes.
4. Run a frontmatter/name/reference validation for changed skills.
5. Keep examples generic: use `<workspace-root>`, `<chatmemory-repo>`, `<source-repo>`, and placeholders. Do not write machine-private paths, tenant IDs, app IDs, tokens, chat IDs, or real private document links into shared skills.

## Boundaries and pitfalls

- Do not confuse target workspace alignment with source-code feature work in ChatUp. If ChatUp itself needs code/template changes, treat that as a separate source-repo task.
- Do not overwrite dirty source checkouts. The ChatUp implementation skips dirty repos; the manual alignment should be at least as conservative.
- Do not turn every old folder into an active project. Archive candidates need human/model review and `archive/index.md` updates.
- Do not replace non-symlink directories under `skills/` or `public/` without moving the old path to `.trash/` first.
- Do not hard-code one machine's branch, home path, Feishu/Lark document, or credential layout in shared skills.

## Completion report

A good final report includes:

- target workspace root
- source template checked: installed `chatup` version or ChatUp source path/branch
- files/directories created or patched
- symlinks created or skipped
- old paths moved to `.trash/`
- active projects/cases reviewed and any Markdown role updates
- verification command output summary
- whether this skill was updated because the template changed
