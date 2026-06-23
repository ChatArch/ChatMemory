---
name: hermes-environment-notes
description: Common environment notes for running workspace tools from inside Hermes Agent sessions.
version: 0.1.0
---

# Hermes Environment Notes

Use this skill when a task runs workspace CLIs, package tooling, auth helpers, or project checks from inside a Hermes Agent tool session.

## Core Rule

Do not assume a command invoked from Hermes uses the same interpreter, virtualenv, config namespace, or credential lookup path as the user's normal shell.

Before relying on an installed CLI or helper, verify the live execution context and choose the environment intentionally.

## Checklist

1. Confirm workspace root and project/repo root first.
2. Check the command path when behavior matters:

```bash
command -v <tool>
<tool> --help
```

3. For Python package tasks, prefer the project virtualenv for build/check/upload commands:

```bash
uv venv .venv
. .venv/bin/activate
uv pip install -e '.[dev]'
python -m pytest -q
python -m build
python -m twine check dist/*
```

4. When a helper command wraps Python tooling, verify which Python it uses before assuming project dependencies are available.
5. Do not print secrets, `.pypirc`, GitHub PATs, PyPI tokens, or raw auth headers. Record only credential source and safe status.
6. If a CLI has workspace-aware config, compare the Hermes tool environment with the user's intended global/local environment before diagnosing auth or config problems.

## Known Pitfalls

### `chattool pypi upload` may use Hermes' own venv

In the observed macOS Hermes setup, `chattool` can resolve to a binary under Hermes' runtime venv, for example:

```text
~/.hermes/hermes-agent/venv/bin/chattool
```

That means:

- `chattool pypi upload` may execute with Hermes' Python environment, not the package repository's `.venv`.
- If Hermes' runtime venv lacks `twine`, upload can fail with:

```text
No module named twine
```

For local PyPI credential fallback after project build/check has already passed, prefer the project venv explicitly:

```bash
. .venv/bin/activate
python -m twine upload dist/*
```

This keeps the upload using the same environment that installed and verified `twine` for the package.

### `chattool` / `chatgh` / `chatenv` may come from different environments

In ChatArch workspaces, common command sources can include:

- Hermes runtime venv, e.g. `~/.hermes/hermes-agent/venv/bin/...`
- ChatArch development venv, e.g. `~/.chatarch/venv/bin/...`
- A repo-local `.venv/bin/...`
- A user-global shell install

When a command's behavior or feature set seems stale, first inspect the active binary and, if needed, run the source checkout with an explicit Python path or venv. Do not silently install packages into Hermes' own runtime venv unless that is the intended target.

### Config namespace can differ under Hermes

Some CLIs auto-detect that they are running under an agent/Hermes context and switch config namespaces. For example, a user-global CLI may use one config path in a normal shell and a separate Hermes config path inside a Hermes tool process.

When the user asks about their normal/global CLI config, verify from a minimal or intended environment rather than assuming the Hermes tool process sees the same config.

## Verification Pattern

For a package release or CLI task, capture safe environment facts in the task log:

```bash
command -v chattool || true
command -v chatgh || true
python -V
python -m pip show twine 2>/dev/null || true
```

Then run the actual gate in the selected environment and record the real outputs, such as `pytest`, `build`, `twine check`, upload result, GitHub Actions status, or clean install verification.
