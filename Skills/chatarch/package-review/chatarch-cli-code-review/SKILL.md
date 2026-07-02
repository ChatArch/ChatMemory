---
name: chatarch-cli-code-review
description: Review completed ChatArch CLI repositories for concise CLI design, decoupled code structure, ChatStyle compliance, reusable Python APIs, security hygiene, and accurate tests.
version: 0.2.0
reference:
  - chatarch-cli-package-conventions: "Defines ChatArch CLI package conventions, ChatEnv/ChatStyle integration, and thin CLI adapter expectations."
  - chatenv-provider-workflow: "Use when reviewing ChatEnv provider registration, schema, and discovery behavior in existing packages."
---

# ChatArch CLI Repository Review

Use this skill when reviewing a completed or near-completed ChatArch-series CLI repository, especially repositories created from the ChatArch / ChatPyPI package workflow.

This is a **repo-level review** skill. It does not define one package's product-specific command names. Package-specific CLI trees belong in that package's PRD or design docs. This skill defines the common review dimensions that every ChatArch CLI repository should satisfy.

## The Six Review Points

### 1. CLI tree is concise and clear

Every review must inspect the actual command tree from live help and include a compact tree in the review result.

```bash
<cli> --help
<cli> <group> --help
```

Review checks:

- The CLI tree is simple enough for a user to understand quickly.
- Top-level commands match the package PRD and user-facing docs.
- Command grouping is not duplicated, confusing, or full of leftover placeholders.
- Command names are justified by the package's own domain language; this skill does not impose a global banned-word or required-word list.
- README, docs, and tests describe the same command surface that `--help` exposes.
- Placeholder or reserved commands do not exit successfully unless they are truly implemented.

Review output should include a compact tree:

```text
<cli>
├── <command>
├── <group>
│   ├── <subcommand>
│   └── <subcommand>
└── <command>
```

### 2. Code is decoupled and layered

The repository should be maintainable and extensible. Do not accept a design where all real behavior is concentrated in one large CLI file.

Review checks:

- `cli.py` is a thin adapter for argument parsing, ChatStyle interaction, and result rendering.
- Business/domain logic lives in importable modules.
- Config/schema code, local path helpers, network/API calls, filesystem IO, subprocess/service operations, and result formatting are separated where the package scope requires it.
- Side effects are isolated in clear functions/modules.
- The code layout makes future extension possible without repeatedly editing one huge file.

The exact file names are package-specific, but a healthy shape often looks like:

```text
src/<package>/
├── cli.py
├── config.py
├── constants.py
├── paths.py
├── <domain>.py
└── ...
```

### 3. CLI interaction follows ChatStyle

If the CLI asks for values, confirms writes, or supports interactive/non-interactive operation, it should follow ChatStyle conventions instead of inventing a package-local interaction style.

Review checks:

- Interactive commands follow the shared `-i` / `-I` pattern where applicable.
- Required values can be resolved through CLI args/options, environment variable names, defaults, or ChatStyle prompts.
- `CommandSchema` / `resolve_command_inputs` or equivalent ChatStyle helpers are used when appropriate.
- Non-interactive mode fails cleanly when required values are missing.
- Write/destructive operations require confirmation or an explicit flag such as `--yes` / `--force`.
- Success, warning, and error output follow the package's ChatStyle rendering conventions.

### 4. CLI capabilities have reusable Python APIs

A ChatArch CLI repository should also be a usable Python package. Core capabilities must be callable without shelling out to the CLI.

Review checks:

- Each major CLI capability has an importable Python function or service object behind it.
- Python APIs accept typed parameters, not pre-parsed argv strings.
- Python APIs return structured values such as dataclasses, typed objects, or dictionaries.
- Python APIs do not print as their primary behavior; CLI code renders returned results.
- CLI commands do not reuse behavior by calling other Click/Typer command callbacks.
- Tests cover Python APIs directly, with separate CLI smoke tests for command wiring and help text.
- The same capability could be reused by another ChatArch package, an agent tool, MCP adapter, or automation.

Preferred pattern:

```python
# src/<package>/<domain>.py
def perform_action(...):
    ...
    return ActionResult(...)

# src/<package>/cli.py
def action_command(...):
    result = perform_action(...)
    render_result(result)
```

### 5. Secrets and private information are protected

ChatArch repositories, docs, tests, fixtures, and shared skills should be safe to publish unless the repository is explicitly scoped otherwise.

Review checks:

- No API keys, tokens, passwords, auth strings, cookies, private keys, or session payloads are committed.
- No real personal/machine paths, account IDs, chat IDs, app IDs, tenant-specific links, or private document links appear in public/shared files.
- CLI output, logs, errors, test fixtures, and docs redact sensitive values.
- Sensitive package config is marked as sensitive in ChatEnv when ChatEnv is used.
- Package-local config does not store secrets or cross-machine operator values.
- Security/private-context scans are run on changed files, and on the full repository when the review touches docs, config, fixtures, or shared skills.

### 6. Tests and gates accurately cover the repository

The review should confirm that tests cover the actual package contract, not only a happy-path CLI string.

Review checks:

- Unit tests cover core Python APIs.
- CLI smoke tests cover `--help`, `--version`, and important command wiring.
- Tests cover important failure paths, not only successful examples.
- ChatEnv provider discovery and sensitive-field behavior are tested when the package integrates with ChatEnv.
- ChatStyle non-interactive and confirmation behavior are tested when the package has interactive commands.
- Docs/README command examples match the actual CLI.
- Build/package checks pass when the repository is release-intended.

Typical gates:

```bash
git diff --check
python -m pytest -q
python -m build
python -m twine check dist/*
```

Use the package's actual tooling when it differs from these examples.

## Standard Verdict Format

```text
Review verdict: pass / blocked / needs-scope-confirmation

CLI tree:
<compact tree>

Blockers:
- ...

Suggestions:
- ...

Checks run:
- ...

Notes:
- ...
```

## Common Blockers

- The CLI tree is unclear, duplicated, undocumented, or inconsistent with the package PRD.
- `cli.py` contains most of the package's business logic.
- Core behavior cannot be imported and called from Python.
- CLI commands reuse behavior by calling other CLI command callbacks.
- Interactive behavior ignores ChatStyle conventions.
- Secrets or private information appear in repo files, logs, output, docs, tests, or fixtures.
- Tests only cover superficial CLI output and do not cover reusable Python APIs.
- Placeholder commands exit successfully and can mislead automation.
