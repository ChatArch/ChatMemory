---
name: hermes-slash-command-development
description: Add or update Hermes slash commands safely: registry, gateway dispatch, Feishu thread helpers, tests, aliases, and verification.
version: 0.1.0
---

# Hermes Slash Command Development

Use this skill when adding or changing a Hermes slash command in the Hermes source tree.

This workspace skill is for the user's Playground collaboration workflow. Do not confuse it with Hermes runtime skills under `~/.hermes/skills/` or Hermes repository built-in skills under `core/hermes/skills/`.

## First: establish the workspace

1. Start at `~/Playground`.
2. Read `AGENTS.md`.
3. Read `projects/README.md`.
4. Confirm the active project under `~/Playground/projects/`.
5. Record work in that project's `PRD.md` and `progress.md`.
6. Confirm the source checkout and branch before editing. For the live Hermes checkout this may be `~/.hermes/hermes-agent`; for repo work it may be `~/Playground/core/hermes`.

## Command contract checklist

Before editing code, define:

- command name and aliases
- CLI, gateway, or both
- platform scope, e.g. Feishu-only
- argument grammar and usage string
- whether the command starts agent work
- behavior while an agent is already running
- behavior during gateway restart/drain
- session/thread retargeting behavior
- permissions/admin gating if relevant
- where artifacts are stored

For command names and aliases, always check collisions first:

```bash
python3 - <<'PY'
from hermes_cli.commands import resolve_command
from agent.skill_commands import resolve_skill_command_key
from agent.skill_bundles import resolve_bundle_command_key
for name in ['candidate', 'alias']:
    print(name, resolve_command(name), resolve_skill_command_key(name), resolve_bundle_command_key(name))
PY
```

Also check `origin/main` when the current branch already contains experimental changes.

## Registry changes

Edit `hermes_cli/commands.py`:

1. Add a `CommandDef(...)` to `COMMAND_REGISTRY`.
2. Set `gateway_only=True` or `cli_only=True` correctly.
3. Set `args_hint` so `/commands` and platform menus are readable.
4. Set `aliases=(...)` only after confirming they are not occupied.
5. Set `subcommands=(...)` for verb-style commands.
6. If the command has a dedicated running-agent gateway handler, add both canonical name and aliases to `ACTIVE_SESSION_BYPASS_COMMANDS` when tests/introspection require bypass visibility.

Example:

```python
CommandDef(
    "template",
    "Use, create, update, or list thread templates",
    "Tools & Skills",
    aliases=("tpl",),
    gateway_only=True,
    args_hint="<name|list|create|update|use> [instruction...]",
    subcommands=("list", "create", "update", "use"),
)
```

## Gateway dispatch

Edit `gateway/run.py` in both paths:

1. Running-agent fast path before normal busy handling.
2. Cold-path slash command dispatch when no agent is active.

Use `resolve_command()` and canonical names; aliases should resolve to the canonical command.

## Feishu thread commands

For any command that should run in a Feishu thread, do not duplicate `/thread` logic. Use or create a shared helper that does the common sequence:

1. Check Feishu platform.
2. If already in a Feishu thread, optionally reset that thread session.
3. If invoked from a parent chat, call the adapter's `create_thread(...)`.
4. Retarget `event.source` to the thread source.
5. Set `event.text` to the payload that should reach the agent.
6. Recompute the session key from the retargeted source.
7. Dispatch through `_dispatch_event_to_agent(...)`.
8. If a seed message was created, edit it to the final answer when possible.
9. Release the stale parent-chat session guard after retargeting.

The platform-specific API belongs in the adapter; command semantics belong in `gateway/run.py` or a focused gateway slash module.

## Template command pattern

For `/template`, keep private templates separate from official Hermes skills:

- Store templates under `~/.hermes/templates/<name>/SKILL.md`.
- Reuse SKILL.md shape: YAML frontmatter plus instruction body.
- Do not store these under `~/.hermes/skills/`, because Hermes auto-scans that tree and exposes `/<skill-name>` dynamic commands.
- `/template <name> ...` defaults to use.
- `/template list` lists available private templates without starting a thread or agent turn.
- `/template use <name> ...` explicitly uses a template.
- `/template create <name> ...` starts a thread with instructions to create the private template.
- `/template update <name> ...` starts a thread with instructions to update the private template.

Recommended syntax:

```text
/template <name> [instruction...]
/template list
/template use <name> [instruction...]
/template create <name> [instruction...]
/template update <name> [instruction...]
```

Aliases should be short but checked first. In this project:

- `/t` aliases `/thread`
- `/tpl` aliases `/template`

## TDD workflow

1. Write focused failing tests first.
2. Run the single new test file and confirm RED is the expected missing behavior.
3. Implement the smallest code path that passes.
4. Add related regression tests for aliases, active-session bypass, unknown commands, and existing behavior.
5. Run focused tests.
6. Run syntax and diff hygiene.

Useful commands:

```bash
python3 -m pytest tests/gateway/test_template_command.py -q -o 'addopts='
python3 -m pytest tests/gateway/test_thread_command.py tests/gateway/test_command_bypass_active_session.py -q -o 'addopts='
python3 -m py_compile hermes_cli/commands.py gateway/run.py tests/gateway/test_template_command.py
git diff --check
```

## Project record updates

For this user's current QLP/Ambient-Hermes setup, source pushes may go directly over the SSH remote when explicitly authorized; do not force a GitHub PR/MR path unless the user asks for one. ChatMemory-backed skill updates can use the default Chat Emb configuration and should be committed to the ChatMemory Git repo when they change shared workflow knowledge.

After each substantive step, update the active project `progress.md` with:

- branch and git status
- files changed
- RED test output
- GREEN test output
- verification commands
- design decisions and tradeoffs
- remaining work

Keep `PRD.md` for stable requirements and accepted design, not noisy logs.

## Pitfalls

- Do not confuse `~/Playground/Skills` with Hermes runtime skills or built-in repo skills.
- Do not write workflow documentation into Hermes official `skills/` unless explicitly asked.
- Do not put private templates under `~/.hermes/skills/` unless you intentionally want dynamic slash commands for each template.
- Do not add aliases without checking `resolve_command`, dynamic skill commands, and bundle aliases.
- Do not retarget a Feishu event to a thread while keeping the parent session key.
- Do not start new work during gateway drain/restart.
- Do not stop after code compiles; run focused behavior tests.
