# ChatMemory

ChatMemory is a private ChatArch knowledge-memory repository.

It must remain private by default because it may contain personal workspace conventions, collaboration context, and important knowledge-memory assets.

It is intentionally a **pure Git repository**, not a Python package and not a PyPI distribution. The repository exists to keep important workspace knowledge, reusable skills, and collaboration conventions synchronized across multiple machines.

## Purpose

Use this repository to maintain durable knowledge-memory assets, including:

- stable shared skills that are safe to synchronize across machines;
- ChatArch-specific operational skills;
- collaboration-document conventions that should be available in every enabled workspace;
- workspace maintenance rules and important conventions that should move with the private ChatArch workspace setup.

## Non-goals

- Do not publish this repository to PyPI.
- Do not add Python package scaffolding unless the project direction changes explicitly.
- Do not use `setup.py`, `pyproject.toml`, `src/`, `tests/`, wheel, or sdist artifacts as part of the default repository shape.
- Do not track Playground-local PRD Task skills here; those belong under the local workspace path `Skills/prd-task`.

## Skill groups

ChatMemory may contain multiple skill groups, but `ChatTool setup workspace` should only link an explicit shared allowlist.

Default shared groups:

```text
Skills/common
Skills/chatarch
```

Group semantics:

- `common/`: stable skills intended to be available on every enabled workspace/machine.
- `chatarch/`: stable ChatArch-specific repository, release, governance, and package workflows.

Do not place machine-specific, account-specific, or sensitive local-only skills in default-linked groups. Keep those in a non-default group or in the source project until a sharing policy is clear.

## Workspace plugin model

ChatMemory is intended to be an optional install candidate in the workspace setup flow, similar to existing optional workspace modules such as ChatTool / ChatBlog.

Candidate behavior:

1. Default selection: **no / unchecked**.
2. If selected and missing locally, clone the private repository into:

   ```text
   <workspace>/core/ChatMemory
   ```

3. If already present, update it with a safe fetch + fast-forward when clean; skip update if local changes exist.
4. Link only the default shared groups into the workspace:

   ```text
   <workspace>/skills/common   -> <workspace>/core/ChatMemory/Skills/common
   <workspace>/skills/chatarch -> <workspace>/core/ChatMemory/Skills/chatarch
   ```

5. Do not copy `SKILL.zh.md` variants into the candidate set. Each candidate skill should expose one standard `SKILL.md`.
6. Do not link all of `ChatMemory/Skills` by default.

## Current layout

```text
ChatMemory/
├── README.md
├── LICENSE
└── Skills/
    ├── chatarch/
    │   ├── public-repo-and-default-branch-protection/
    │   │   └── SKILL.md
    │   └── python-package-release-with-chattool-pypi/
    │       └── SKILL.md
    ├── common/
    │   └── feishu-collaboration-documents/
    │       └── SKILL.md
    ├── hermes-slash-command-development/
    │   └── SKILL.md
    └── workspace-maintenance/
        └── SKILL.md
```

## Current shared skills

### `common/feishu-collaboration-documents`

Feishu collaboration-document convention and human-AI main document navigation.

### `chatarch/public-repo-and-default-branch-protection`

ChatArch repository visibility and default-branch protection workflow.

### `chatarch/python-package-release-with-chattool-pypi`

ChatArch Python package creation, release, and PyPI verification workflow.

## Local workspace link convention

A workspace that enables ChatMemory should link shared groups from this repository instead of copying individual skill directories:

```text
<workspace>/skills/common   -> <workspace>/core/ChatMemory/Skills/common
<workspace>/skills/chatarch -> <workspace>/core/ChatMemory/Skills/chatarch
```

Existing standalone local links may be migrated to the grouped layout when convenient.
