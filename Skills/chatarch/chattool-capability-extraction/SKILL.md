---
name: chattool-capability-extraction
description: ChatArch workflow for extracting useful ChatTool interfaces into standalone Python packages such as ChatPyPI.
version: 0.1.0
status: draft
owner: ChatArch
source_project: ChatTool
---

# ChatTool Capability Extraction

## Purpose

Use this skill when splitting a useful ChatTool command/interface into an independent ChatArch Python package.

Initial target: extract `chattool pypi` / `chatpypi` into a standalone ChatPyPI package.

This skill is intentionally created early as a draft. Fill in concrete details as the ChatPyPI extraction is practiced and verified.

## Related skills to load

- `workspace-task-kickoff` — establish `~/Playground` and create the task record first.
- `chattool-capability-extraction` in Hermes local skills, if available — local procedure draft and candidate rubric.
- `extracting-capabilities-to-packages` — general multi-phase extraction workflow.
- `python-package-release-with-chattool-pypi` — current ChatArch package scaffold/release workflow.
- `chatgh-pr-and-ci-workflow` — ChatArch PR/CI/repository workflow through ChatGH.

## Current known extractions

- GitHub helper surface: ChatTool GitHub functionality has been extracted to `ChatGH` / `chatgh`.
- Setup/bootstrap surface: ChatTool setup functionality has been extracted to `ChatUp` / `chatup`; `chattool setup` is no longer a ChatTool command in ChatTool 7.1.0.

## Candidate selection rubric

A ChatTool capability is a good extraction candidate when:

1. The command has a clear product/domain boundary.
2. It already has, or naturally deserves, a first-level CLI binary.
3. Source code is concentrated in one module tree such as `src/chattool/tools/<name>/`.
4. Tests are already grouped under `tests/cli-tests/<name>/` and/or `tests/mock-cli-tests/<name>/`.
5. Config/env ownership can be delegated to canonical ChatArch packages such as ChatEnv.
6. Interactive CLI behavior can reuse ChatStyle rather than copying ChatTool internals.
7. ChatTool can remove the embedded logic or depend on the new package without breaking unrelated commands.

## First concrete target: ChatPyPI

Known source surface in ChatTool:

- CLI group: `chattool pypi`
- Shortcut CLI: `chatpypi`
- Source tree: `src/chattool/tools/pypi/`
- Main functions: scaffold/build/check/probe/upload Python packages
- Test families:
  - `tests/mock-cli-tests/pypi/`
  - `tests/cli-tests/pypi/`
  - `tests/mock-cli-tests/client/test_chatpypi_shortcut_basic.*`

Expected target shape:

- GitHub repo: `ChatArch/ChatPyPI` unless renamed by user.
- PyPI distribution: confirm exact name before registry operations; do not guess a hyphenated name.
- Python module: likely `chatpypi`.
- CLI: `chatpypi`.

## Standard extraction phases

### Phase 0 — task and isolated workspace

1. Start at `~/Playground`; read `AGENTS.md` and `projects/README.md`.
2. Create a task under the active extraction topic, for example:

```text
projects/chatup-setup-split/05-chatpypi-extraction/
  PRD.md
  progress.md
  reports/
  playground/
```

3. To avoid polluting long-lived checkouts, clone fresh working copies under the task `playground/`:

```bash
git clone ~/Playground/core/ChatTool playground/ChatTool
# Create or clone ChatPyPI under playground/ChatPyPI for the extraction spike.
```

Do not modify `~/Playground/core/ChatTool` directly during early extraction practice.

### Phase 1 — bootstrap or prepare standalone package

1. Confirm exact names: repo, PyPI distribution, module, CLI, initial version.
2. Check whether GitHub repo and PyPI project already exist.
3. Scaffold/harden the standalone package.
4. Add minimum CLI smoke: `--help`, `--version`, and a simple non-mutating command.
5. Add CI and tag-driven publish workflow, but do not tag/publish without explicit user approval.

### Phase 2 — migrate the capability

1. Inventory ChatTool source, docs, tests, and shortcut wrappers.
2. Move implementation and tests into the standalone package.
3. Keep a preserve / retarget / delete table:
   - preserve user-facing CLI behavior;
   - retarget imports/config/docs to canonical ChatArch packages;
   - delete parent-only shims or obsolete assets.
4. Run tests, build, twine check, wheel/package-data checks, and CLI smoke.

### Phase 3 — update parent ChatTool

Only after the standalone package is working and, if needed, published:

1. Remove embedded implementation from ChatTool or replace with an intentional wrapper.
2. Remove parent-managed aliases that duplicate real standalone CLIs.
3. Update ChatTool dependencies/extras, docs, tests, CI smoke lists, and changelog.
4. Use PR flow; merge and release are separate user approval gates.

## Hard boundaries

- Do not create repositories, push branches, change visibility, configure branch protection, tag, or publish unless the user explicitly approves that concrete action.
- Do not print tokens or auth headers.
- Merge is not release.
- Keep source mutations in task-local clones until the user asks to apply them to canonical `core/` checkouts or remote repositories.

## Fill in after practice

As ChatPyPI extraction proceeds, add:

- exact command compatibility table;
- file migration map;
- dependency decisions;
- tests moved/added;
- parent cleanup checklist;
- release and rollback notes;
- pitfalls discovered during the actual split.
