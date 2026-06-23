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
Skills/agents
Skills/common
Skills/chatarch
```

Group semantics:

- `chatarch/`: stable ChatArch-specific repository, release, governance, and package workflows.
- `common/`: stable skills intended to be available on every enabled workspace/machine, but not specific to ChatArch.
- `agents/`: shared agent-created or agent-learned skills that emerge while agents work through PRD, project, archive, and review processes. This group is intentionally lightweight until usage patterns stabilize.

Local workspace-only skills belong under `<workspace>/skills/local`. They are machine-specific or private to the current workspace and are not tracked by ChatMemory or linked from ChatMemory.

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
   <workspace>/skills/agents   -> <workspace>/core/ChatMemory/Skills/agents
   <workspace>/skills/common   -> <workspace>/core/ChatMemory/Skills/common
   <workspace>/skills/chatarch -> <workspace>/core/ChatMemory/Skills/chatarch
   ```

   Also create `<workspace>/skills/local/` as a local non-shared directory when missing. Do not link it.

5. Do not copy `SKILL.zh.md` variants into the candidate set. Each candidate skill should expose one standard `SKILL.md`.
6. Do not link all of `ChatMemory/Skills` by default.

## Current layout

```text
ChatMemory/
├── README.md
├── LICENSE
└── Skills/
    ├── agents/
    │   └── README.md
    ├── chatarch/
    │   ├── chatarch-org-pr-status/
    │   │   ├── SKILL.md
    │   │   └── scripts/
    │   ├── chatgh-pr-and-ci-workflow/
    │   │   ├── SKILL.md
    │   │   └── scripts/
    │   ├── public-repo-and-default-branch-protection/
    │   │   └── SKILL.md
    │   └── python-package-release-with-chattool-pypi/
    │       └── SKILL.md
    └── common/
        ├── feishu-collaboration-documents/
        │   └── SKILL.md
        ├── hermes-environment-notes/
        │   └── SKILL.md
        ├── hermes-slash-command-development/
        │   └── SKILL.md
        └── workspace-maintenance/
            └── SKILL.md
```

## Current shared skills

### `common/feishu-collaboration-documents`

Feishu collaboration-document convention and human-AI main document navigation.

### `common/hermes-environment-notes`

Hermes tool-session environment notes for interpreter, virtualenv, CLI config namespace, and package upload pitfalls.

### `common/hermes-slash-command-development`

Hermes slash-command development and update handoff conventions that should be available in enabled workspaces.

### `common/workspace-maintenance`

Workspace maintenance, development-process, update, and handoff conventions shared across enabled workspaces.

### `agents/`

Shared agent-created or agent-learned skills formed during PRD/project/archive/review work. This group is intentionally light on policy for now.

### `chatarch/chatarch-org-pr-status`

Quick ChatGH-based organization status workflow for finding which ChatArch repositories currently have open pull requests. Includes a reusable script that scans `chatgh repo list` and expands repositories with `open_prs > 0` using `chatgh pr list`.

### `chatarch/chatgh-pr-and-ci-workflow`

ChatGH-based PR readiness, CI triage, repository inventory, protection readback, and token-capability workflows for ChatArch repositories. Includes reusable scripts for PR readiness and repository inventory/protection snapshots.

### `chatarch/public-repo-and-default-branch-protection`

ChatArch repository visibility and default-branch protection workflow.

### `chatarch/python-package-release-with-chattool-pypi`

ChatArch Python package creation, release, and PyPI verification workflow.

## Local workspace link convention

A workspace that enables ChatMemory should link shared groups from this repository instead of copying individual skill directories:

```text
<workspace>/skills/common   -> <workspace>/core/ChatMemory/Skills/common
<workspace>/skills/chatarch -> <workspace>/core/ChatMemory/Skills/chatarch
<workspace>/skills/agents   -> <workspace>/core/ChatMemory/Skills/agents
```

The workspace may also have a local non-shared directory:

```text
<workspace>/skills/local
```

Existing standalone local links may be migrated to the grouped layout when convenient.
