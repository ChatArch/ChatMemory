# ChatMemory

ChatMemory is a private ChatArch knowledge-memory repository.

It must remain private by default because it may contain personal workspace conventions, collaboration context, and important knowledge-memory assets.

It is intentionally a **pure Git repository**, not a Python package and not a PyPI distribution. The repository exists to keep important workspace knowledge, reusable skills, and collaboration conventions synchronized across multiple machines.

## Purpose

Use this repository to maintain durable knowledge-memory assets, including:

- workspace-level skills
- collaboration-document conventions
- workspace maintenance rules
- important notes and conventions that should move with the private ChatArch workspace setup

## Non-goals

- Do not publish this repository to PyPI.
- Do not add Python package scaffolding unless the project direction changes explicitly.
- Do not use `setup.py`, `pyproject.toml`, `src/`, `tests/`, wheel, or sdist artifacts as part of the default repository shape.

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

## Current layout

```text
ChatMemory/
├── README.md
├── LICENSE
└── Skills/
    ├── feishu-collaboration-documents/
    │   └── SKILL.md
    └── workspace-maintenance/
        └── SKILL.md
```

## Current skills

### `feishu-collaboration-documents`

Feishu collaboration-document convention and human-AI main document navigation.

### `workspace-maintenance`

Outer workspace maintenance conventions: project/archive structure, root protocol files, and `.trash` cleanup flow.

## Local workspace link convention

A workspace that enables ChatMemory should link skills from this repository instead of copying them:

```text
<workspace>/skills/feishu-collaboration-documents -> <workspace>/core/ChatMemory/Skills/feishu-collaboration-documents
<workspace>/skills/workspace-maintenance -> <workspace>/core/ChatMemory/Skills/workspace-maintenance
```
