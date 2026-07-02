---
name: chatarch-cli-code-review
description: Review ChatArch Python CLI packages for clean CLI surface, ChatEnv/ChatStyle compliance, importable Python APIs, and decoupled implementation structure.
version: 0.1.0
reference:
  - chatarch-cli-package-conventions: "Defines ChatArch CLI package conventions, ChatEnv/ChatStyle integration, and thin CLI adapter expectations."
  - chatenv-provider-workflow: "Use when reviewing ChatEnv provider registration, schema, and discovery behavior in existing packages."
---

# ChatArch CLI Code Review

Use this skill when reviewing a ChatArch Python CLI package, especially before or during a refactor that changes CLI trees, ChatEnv usage, ChatStyle interaction, or internal module structure.

This is a review skill, not an implementation skill. It describes the normal review standard to apply to ChatArch CLI packages such as ChatGH, ChatPyPI, and other organization tools.

## Core Review Standard

A ChatArch CLI package must satisfy four baseline expectations:

1. **Clean operator-facing CLI tree** — commands match the user's mental model, not old implementation details.
2. **ChatEnv compliance** — shared, profile-like, or sensitive operator config uses ChatEnv; package-local config stores only machine-local runtime facts.
3. **ChatStyle compliance** — interactive commands use the shared `-i/-I` pattern, `CommandSchema`, `resolve_command_inputs`, confirmations, and render helpers.
4. **Reusable Python API** — each major CLI capability has an importable Python function/API behind it, and `cli.py` is a thin adapter.

If a PR violates any of these, treat it as a blocker unless the user explicitly scoped the PR to a narrower transitional step.

## 1. CLI Surface Review

Review the actual command tree from live help, not only docs:

```bash
<command> --help
<command> <group> --help
```

Check:

- The main tree contains only user-facing nouns and actions.
- Implementation nouns such as `engine`, `daemon`, `internal`, `legacy`, or `docker` are absent unless they are truly user concepts.
- Historical compatibility aliases are not kept in `0.x` packages just because they once existed.
- Placeholder/reserved commands do not exit 0 and do not appear as normal supported features.
- Command names avoid vague terms when a clearer noun exists: prefer `check` over `verify`, concrete runtime names over abstract implementation nouns, and short accepted nouns such as `sub` when that is the product language.

For a `0.x` ChatArch CLI, do not preserve noisy old command surfaces merely for compatibility. Removing old entries is acceptable when the PR intentionally cleans the interface.

### Review Questions

- Can a new operator understand the command tree without knowing implementation history?
- Are low-frequency utilities separated from the daily path?
- Are lifecycle operations grouped under the thing they operate on?
- Does the help text match actual behavior and implemented defaults?
- Are docs/tests updated to the same command tree?

## 2. ChatEnv Boundary Review

Classify each config field before accepting it.

ChatEnv should hold:

- subscription URLs
- API endpoints or external service base URLs that are not machine-local runtime layout
- credentials, auth strings, tokens, account selectors
- cross-run or profile-scoped operator preferences

Package-local config should hold:

- runtime paths
- pid/log/cache paths
- ports
- bind/listen host
- advertised host/IP
- local binary path and selected local backend
- other machine-specific runtime layout facts

Review checks:

- `src/<package>/config.py` exposes a `BaseEnvConfig` subclass when package-owned env values exist.
- Sensitive fields use `is_sensitive=True`.
- `pyproject.toml` registers `[project.entry-points."chatenv.configs"]`.
- CLI setters use `EnvStore.load_active/save_active` or equivalent ChatEnv store APIs.
- The package does not hand-render `.env` files, reimplement profile paths, or add custom dotenv quoting/parsing.
- Local config files do not contain secrets or subscription URLs.
- CLI output shows booleans/masked values, never raw secrets.
- Tests use task-local `CHATARCH_HOME`/package home and prove secrets stay out of package-local config.

## 3. ChatStyle Interaction Review

Commands with optional user input, confirmations, or destructive writes should use ChatStyle.

Review checks:

- Interactive mode uses the shared `-i/-I` convention.
- Required values can be supplied by CLI args/options, environment variable names, defaults, or prompts through `CommandSchema` / `resolve_command_inputs`.
- Non-interactive mode fails cleanly when required values are missing.
- Destructive/write operations require confirmation or an explicit `-y/--yes` / `--force`.
- Success/warning output uses shared render helpers where applicable.
- Secret values are accepted via env-var-name options when practical, so they do not land in shell history.

## 4. Python API and Decoupling Review

A CLI command should not be the only stable integration surface.

Review checks:

- `cli.py` is a thin adapter around importable Python functions.
- Domain modules own business logic, IO orchestration, parsing, and structured results.
- Python APIs accept typed parameters, not pre-parsed `argv` strings.
- Python APIs return dataclasses/dicts/structured results rather than printing directly.
- CLI commands render API results; APIs do not call Click command callbacks.
- Tests cover Python APIs directly and add CLI smoke tests for help/argument wiring.
- Side effects are isolated by module and support dry-run/planning where useful.

A good package layout looks like:

```text
src/<package>/
├── cli.py              # thin Click/Typer adapter
├── config.py           # ChatEnv schema only
├── constants.py        # constants
├── paths.py            # local path/config helpers
├── <domain>.py         # domain APIs
└── ...
```

Avoid one giant `cli.py` that contains config parsing, HTTP calls, YAML manipulation, subprocess management, and Click commands together.

## 5. Service / Runtime Review

For CLIs that manage a local service or runtime:

- The concrete runtime or domain name should appear in the CLI instead of abstract implementation nouns.
- Install/update of the binary is separate from config/subscription updates.
- Autostart/daemon install is an option on runtime install/uninstall when possible.
- Status reports installed/running/autostart/config state and never prints secrets.
- Logs are redacted.
- Tests never write to real service roots or system directories; use task-local homes.
- Real smoke tests are clearly separate from unit tests and report only non-sensitive conclusions.

## 6. Review Procedure

1. **Establish workspace and repo state**
   - read workspace rules when applicable
   - confirm repository path, branch, dirty status, and target PR/commit range
2. **Read command surface**
   - run live `--help` for root and command groups
   - compare to intended user mental model
3. **Inspect structure**
   - list modules and identify whether `cli.py` is too large or business-heavy
   - check whether domain APIs exist and are importable
4. **Inspect ChatEnv/ChatStyle use**
   - read `config.py`, `pyproject.toml`, CLI setters, interactive commands
5. **Inspect tests**
   - ensure CLI tree, Python APIs, ChatEnv boundaries, and secret redaction are tested
6. **Run gates**
   - `git diff --check`
   - relevant unit tests
   - secret/private-context scan for changed files
   - independent review when changes are non-trivial
7. **Return a structured verdict**
   - blockers
   - suggestions
   - tests run
   - whether the PR is ready, needs patching, or needs scope clarification

## 7. Standard Verdict Shape

Use this concise report shape:

```text
Review verdict: pass / blocked / needs-scope-confirmation

Blockers:
- ...

Suggestions:
- ...

Checks run:
- ...

Notes:
- ...
```

## 8. Common Blockers

- Root CLI still exposes redundant old commands after a cleanup PR.
- A `0.x` package keeps old aliases that contradict the intended interface.
- `cli.py` remains the business-logic dumping ground.
- A command calls another Click command's `.callback()` instead of a Python API.
- ChatEnv values are written by custom `.env` rendering.
- Machine-local ports/hosts are stored in ChatEnv when they belong in local config.
- Secrets appear in local config, logs, CLI output, tests, fixtures, or docs.
- Interactive behavior is hand-rolled rather than ChatStyle-backed.
- Tests only cover CLI text and not importable Python APIs.
- Placeholder/reserved commands look successful to automation.

## 9. Generic Service-CLI Review Addendum

For service-oriented ChatArch CLIs, keep the public command tree organized around the user's domain model. A typical shape is:

```text
<tool>
├── init
├── status
├── <domain>
│   ├── set
│   ├── status
│   └── update
├── <runtime>
│   ├── install
│   ├── uninstall
│   ├── update
│   ├── start
│   ├── stop
│   ├── restart
│   ├── status
│   └── logs
└── check
    ├── health
    └── external
```

In `0.x`, keep the command surface aligned with the current product model. Implementation details should live behind Python APIs rather than becoming separate top-level nouns.

When reviewing a concrete package, write the package-specific target tree in that package's PRD or project docs, not in this shared generic skill.

Expected importable APIs should cover each major capability, for example:

```python
set_domain_config(...)
update_domain_state(...)
install_runtime(...)
start_runtime(...)
stop_runtime(...)
restart_runtime(...)
get_runtime_status(...)
check_health(...)
get_status(...)
```
