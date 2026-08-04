# Hermes official external-agent CLI patterns

Date checked: 2026-08-05.

## What was checked

Local Hermes source/docs checkout:

- `website/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex.md`
- `website/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code.md`
- `website/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode.md`
- `website/docs/user-guide/features/delegation.md`
- `website/docs/guides/delegation-patterns.md`
- `website/docs/integrations/providers.md`
- `tools/terminal_tool.py`
- `tools/process_registry.py`
- `tools/delegate_tool.py`
- `hermes_cli/runtime_provider.py`
- `hermes_cli/auth.py`

Installed local CLI help was also inspected for Cursor Agent, Codex, Claude Code, and OpenCode resume/continue flags.

## Findings

### Official Hermes pattern for Codex / Claude Code / OpenCode

Hermes's bundled autonomous-agent skills treat these tools as external CLI processes orchestrated through Hermes `terminal` and `process` tools, not as dedicated first-class Hermes tools.

Common pattern:

1. prefer one-shot/print/run/exec modes for bounded tasks;
2. use `pty=true` for interactive terminal apps;
3. use `background=true` plus `notify_on_complete=true` for long bounded jobs;
4. manage background work via `process(action="poll"|"log"|"wait"|"submit")`;
5. verify the external agent's claims by reading files/diffs/tests/artifacts in the parent Hermes agent.

### Hermes-native delegation is separate

`delegate_task` creates Hermes subagents with isolated conversations, terminal sessions, and toolsets. It is the right primitive for Hermes-native parallel reasoning or review.

It is not the same as launching Codex, Cursor Agent, Claude Code, or OpenCode. External agent CLIs are subprocesses launched through `terminal` unless a plugin/provider/MCP/ACP wrapper exists.

### Cursor Agent gap

Searches for `cursor-agent`, `Cursor Agent`, and related terms in Hermes official docs/source found no first-class Cursor Agent skill, provider, or tool. The only source hit was a release-script co-author ignore pattern, not an integration.

Therefore Cursor Agent should currently be treated as a generic external CLI in Hermes:

```python
terminal(
    command="cursor-agent --print --mode ask --trust '<task>'",
    workdir="/path/to/repo",
    timeout=600,
)
```

For interactive use, start a managed background PTY and continue via `process(action="submit")`.

### External-process provider precedent

Hermes does have a first-class external-process provider pattern for GitHub Copilot ACP:

```bash
hermes chat --provider copilot-acp --model copilot-acp
```

The provider starts a local `copilot --acp --stdio` subprocess. Source-level runtime resolution propagates command/args into agent construction.

This is evidence that a future Cursor wrapper could be implemented as a plugin/provider/ACP-style integration, but it is not currently built in.

## Conversation continuity / resume support checked locally

Many coding-agent CLIs have their own session persistence. Use explicit session IDs where possible; “latest session” is convenient but unsafe when multiple repos or agents have run.

- Cursor Agent help shows:
  - `--continue`
  - `--resume [chatId]`
  - `ls` — resume a chat session / list selectable sessions
  - `resume` — resume the latest chat session
- Codex help shows:
  - `codex resume`
  - `codex exec resume` for a previous session by id or latest session
  - `codex fork` for forking a previous interactive session
- Claude Code help shows:
  - `--continue`
  - `--resume [value]`
  - `--session-id <uuid>`
  - `--fork-session`
  - `--no-session-persistence` to disable persistence
- OpenCode help and bundled skill show:
  - `--continue` / `-c`
  - `--session` / `-s`
  - `--fork`
  - `opencode session`
  - `opencode export` / `opencode import`

## Recommended answer to “can it continue?”

Yes, but distinguish two layers:

1. **Same live process:** keep the CLI running under `terminal(background=true, pty=true)` and send follow-up prompts through `process(action="submit")`. This is best for immediate iterative correction.
2. **CLI-persisted session:** use the tool's own resume/continue/session flags after the process exits. Record the external session id/name in the active Project notes so future turns resume the intended conversation.

In both cases, Hermes should verify repo state and outputs itself after the external agent claims completion.
