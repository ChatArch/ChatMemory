# ChatMemory

ChatMemory is a private ChatArch workspace memory plugin for keeping important knowledge, collaboration conventions, and reusable workspace skills in a shared Git repository.

It is **not** intended to claim or publish the existing `chatmemory` name on PyPI. Treat it as a normal private source package and workspace plugin.

## Purpose

Use this repository to maintain knowledge-memory assets that should be shared across multiple machines, including:

- workspace-level skills
- collaboration-document conventions
- workspace maintenance rules
- important durable notes that should move with the private ChatArch workspace setup

## Workspace plugin model

ChatMemory is intended to be an optional install candidate in the workspace setup flow, similar to existing optional workspace modules such as ChatTool / ChatLog.

Candidate behavior:

1. Default selection: **no / unchecked**.
2. If selected and missing locally, clone the private repository into:

   ```text
   <workspace>/core/ChatMemory
   ```

3. If already present, update it with a safe fetch + fast-forward when clean; skip update if local changes exist.
4. Link its skills into the workspace, public-style:

   ```text
   <workspace>/skills/<skill-name> -> <workspace>/core/ChatMemory/Skills/<skill-name>
   ```

5. Do not copy `SKILL.zh.md` variants into the candidate set. Each candidate skill should expose one standard `SKILL.md`.

## Current skills

```text
Skills/
├── feishu-collaboration-documents/
│   └── SKILL.md
└── workspace-maintenance/
    └── SKILL.md
```

### `feishu-collaboration-documents`

Feishu collaboration-document convention and human-AI main document navigation.

### `workspace-maintenance`

Outer workspace maintenance conventions: project/archive structure, root protocol files, and `.trash` cleanup flow.

## Local development

```bash
python3 -m pytest -q
uvx --from build pyproject-build
chatpypi check --project-dir .
```
