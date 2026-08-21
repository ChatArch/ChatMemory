---
name: hermes-external-agent-cli-orchestration
description: Use when Hermes needs to call Codex, Cursor Agent, Claude Code, OpenCode, or another local coding-agent CLI; choose terminal/process vs delegate_task/plugin/ACP.
version: 0.1.3
tags:
  - Hermes
  - coding-agent
  - Codex
  - Cursor-Agent
  - delegation
  - terminal
related_skills:
  - hermes-platform-development
  - server-chatarch-bot-setup
  - cursor-agent-worker-orchestration
---

# Hermes External Agent CLI Orchestration

Use this skill when a Hermes session needs to invoke or design integration with an external coding-agent CLI such as Codex, Cursor Agent, Claude Code, OpenCode, or a similar local agent executable.

This skill is about **Hermes orchestrating another agent process**. For normal Hermes subagents, use `delegate_task`; for server bot deployment, also load `server-chatarch-bot-setup`.

Hermes should act as a scheduler/reviewer for this workflow: break the work into lanes, choose the right worker backend, provide self-contained prompts, supervise progress, handle resume/timeout, and independently verify outputs. Do not let a worker's self-report replace Hermes-side acceptance checks.

If the worker backend is Cursor Agent, load `cursor-agent-worker-orchestration` for the exact `agent create-chat` / `agent --resume <chat_id>` pattern. This skill stays backend-general: Cursor, Codex, Claude Code, OpenCode, custom agents, and future ACP/MCP/plugin backends are all worker options.

## Decision model

| Need | Preferred Hermes pattern |
|---|---|
| Parallel reasoning / review inside Hermes | `delegate_task` Hermes subagents |
| One bounded task through an installed coding-agent CLI | `terminal(...)` one-shot command |
| Long bounded external-agent run | `terminal(background=true, notify_on_complete=true, ...)` then `process(...)` |
| Interactive TUI/session | `terminal(background=true, pty=true, ...)` then `process(submit/log/poll)` |
| Durable first-class product integration | Hermes plugin/tool, MCP server, or ACP/provider integration |

Do not describe external-agent work as “delegation” unless you distinguish whether it is Hermes-native `delegate_task` or a separate CLI process launched through `terminal`.

## Conversation continuity / resume

Yes, many coding-agent CLIs can continue from earlier context, but there are two different mechanisms:

1. **Keep the same live CLI process open.**
   - Start an interactive session with `terminal(background=true, pty=true, ...)`.
   - Send follow-up prompts through `process(action="submit", session_id="<id>", data="...")`.
   - This is the most direct way to say “the result is not good; continue from what you just did”.
   - It only lasts while that process/session is alive; do not treat a Hermes process session ID as a durable project record.

2. **Use the CLI's own persisted conversation/session store.**
   - Cursor Agent on `zhihong.oray` should use the top-level `agent` executable, not the minimal `cursor agent` wrapper, for durable workers. The verified pattern is `CHAT_ID=$(agent create-chat | tr -d '\r' | tail -n 1)` followed by `PATH="$NODE_BIN:$PATH" agent --print --resume "$CHAT_ID" --force --trust "$prompt"`; store that `chat_id` in the run JSON and reuse it for every continuation. `cursor agent` may work for tiny one-shot probes, but do not use it for resumable release workers.
   - Cursor Agent supports `--continue`, `--resume [chatId]`, `ls`, and `resume` on the installed CLI checked on 2026-08-05; verify the active binary because help/output differs between `cursor-agent`, `cursor agent`, and top-level `agent`.
   - Codex supports `codex resume`; current help also exposes `codex exec resume` for resuming a previous exec session by id or latest session.
   - Claude Code supports `--continue`, `--resume`, `--session-id`, and `--fork-session`; session persistence can be disabled with `--no-session-persistence`.
   - OpenCode supports `--continue` / `-c`, `--session` / `-s`, `--fork`, `opencode session`, `opencode export`, and `opencode import`.

When using a persisted CLI session, store the external session id/name in the active Project `progress.md` or task notes. On the next turn, resume by id when possible instead of relying on “latest session”, because multiple agents or repos may have run since then.

Even when resuming an external CLI conversation, the parent Hermes agent must still verify the result by reading the repo state, diff, tests, or external artifact handles. Do not trust the resumed agent's memory as the sole source of truth.

## Progress following / watchdog duty

When the user asks Hermes to delegate a substantial task to an external CLI agent, Hermes remains responsible for **watching the agent work**, not only for reporting the final result.

1. **Make the agent read the governing rules itself.**
   - The delegation prompt must explicitly name the workspace rules, task project files, and relevant skills/references the CLI agent must read before acting.
   - If the task tests the external agent as executor, Hermes should not pre-summarize all norms as a substitute for the agent reading them.
2. **Set a visible progress cadence.**
   - Immediately report dispatch: command shape, workdir, process/session id, and the first expected milestone.
   - For long-running tasks, check `process(action="poll")`, `process(action="log")`, and, when useful, a read-only process tree / repo status every few minutes or at user-requested cadence.
   - User-facing updates should say what is known now: running/exited, latest output, active child command if visible, files/projects changed, and whether progress is healthy, blocked, or suspiciously silent.
3. **Classify silence as a state, not as progress.**
   - If the agent runs for an extended period with no new logs, no active child command, and no repo/task-file changes, report it as likely stalled or non-observable.
   - Do not keep waiting silently until the final timeout.
4. **Interrupt by conversation when needed.**
   - If the same CLI process is interactive and under `pty=true`, send a corrective follow-up with `process(action="submit")`.
   - If the one-shot process has exited, resume by explicit external session id when available (`--resume <id>`), otherwise `--continue`/tool-specific latest-session only with the risk stated.
   - If the one-shot process is still running but non-interactive and non-observable, ask before terminating it unless the user has already authorized restart/termination for this task. Then restart with an observable mode and a first-milestone prompt.
5. **Do not take over implementation.**
   - If progress is bad, Hermes should prompt/resume/restart the external agent with clearer instructions or safety boundaries. Hermes may inspect for acceptance, but should not start editing the package itself when the user explicitly delegated development to the external agent.
6. **Treat user steering as an executable follow-up.**
   - If the user gives new authorization or narrows scope mid-run (for example “this repo can be public” or “this can stop now”), send that instruction into the live external-agent PTY promptly, and require the agent to record it in the active project before any side effect.
   - Do not keep debating a blocker after the user has supplied the missing authorization; translate it into the next concrete agent instruction.
7. **Separate completion from process liveness.**
   - A task can be complete while the interactive agent is still waiting at an “add follow-up” prompt.
   - When the user asks “还没好吗/可以结束了吗/收尾”, immediately verify the external artifacts yourself. If the acceptance readback passes, gracefully close the agent stdin with `process(action="close")`, capture its exit code and resume id, and report the final status.
   - Do not continue polling for additional agent prose once the real deliverables are verified.

## Baseline workflow

1. **Resolve the target executable and auth state without exposing secrets.**
   - Check binary path/version/help/status/model list where available.
   - Redact tokens, API keys, OAuth files, provider URLs with credentials, and private host details.
2. **Set a narrow working directory.**
   - Always pass `workdir` to `terminal`.
   - In a Git repo, inspect `git status --short --branch` first and understand dirty state before launching an agent that can edit files.
   - For parallel runs, use separate worktrees/workdirs.
3. **Prefer one-shot/print modes for bounded tasks.**
   - They exit cleanly, are easier to verify, and avoid TUI prompt handling.
4. **Use Hermes-managed process lifecycle.**
   - Do not use shell `&`, `nohup`, `setsid`, or detached daemons for agent jobs.
   - For bounded long tasks, use `background=true` with `notify_on_complete=true`.
   - Inspect/drive background work only through `process(action="poll"|"log"|"wait"|"submit"|"write"|"close")`.
5. **Verify external-agent claims.**
   - Treat external-agent output as a self-report.
   - Before reporting success, the parent Hermes agent must verify concrete handles: re-read changed files, inspect `git diff`, run targeted tests/checks, or fetch/read back external artifacts.

## One-shot command templates

### Codex CLI

Codex is interactive enough that Hermes should generally call it with `pty=true`. Codex also requires a Git repo for execution tasks.

Do not assume Codex is installed just because it is a possible fallback. Verify `command -v codex`, `codex --help` or `codex --version`, auth/status, and one bounded smoke before assigning work. On `zhihong.oray`, Codex CLI was observed absent during the Chat-series rollout; use Cursor `agent` or another verified external agent instead of promising a Codex lane there.

```python
terminal(
    command="codex exec --sandbox workspace-write 'Implement <task>. Report changed files and tests.'",
    workdir="/path/to/repo",
    pty=True,
    timeout=600,
)
```

For long bounded Codex jobs:

```python
terminal(
    command="codex exec --sandbox workspace-write 'Refactor <scope>. Keep changes focused.'",
    workdir="/path/to/repo",
    background=True,
    notify_on_complete=True,
    pty=True,
)
```

Current Codex CLI guidance prefers `--sandbox workspace-write`; legacy `--full-auto` is deprecated, and yolo/full-access modes require explicit risk acceptance.

### Cursor Agent

Hermes does not currently have a first-class Cursor Agent tool/provider in the official docs/source. Treat Cursor Agent as an external CLI unless a project supplies a plugin/MCP/ACP wrapper.

On `zhihong.oray`, use this durable worker pattern for long tasks:

```bash
NODE_BIN=/home/zhihong/Playground/projects/08-06-manim-exploration/playground/tools/node-v20.19.0-linux-x64/bin
CHAT_ID=$(agent create-chat | tr -d '\r' | tail -n 1)
PROMPT=/path/to/prompt.txt
prompt=$(PROMPT="$PROMPT" python - <<'PY'
import os
from pathlib import Path
print(Path(os.environ["PROMPT"]).read_text())
PY
)
source /home/zhihong/Playground/.env
source /home/zhihong/Playground/projects/devops/08-15-proxy-on-bin-scripts/scripts/proxy_on
PATH="$NODE_BIN:$PATH" agent --print --resume "$CHAT_ID" --force --trust "$prompt"
```

For each repo/worker, persist `chat_id`, worktree path, release branch, prompt path, report path, and process session id in a run JSON. After timeout or `kill_all`, inspect real external state (PRs, remote branches, tags, workflow runs, PyPI, report files) before resuming with the same `chat_id`. Never blindly restart a new Cursor chat for the same repo.

Smoke test:

```python
terminal(
    command="agent --print --trust '请只回答：CURSOR_AGENT_SMOKE_OK。不要使用工具。'",
    workdir="/path/to/workspace",
    timeout=120,
)
```

Bounded task:

```python
terminal(
    command="agent --print --trust '在当前仓库完成 <task>；结束时列出改动文件和验证命令。'",
    workdir="/path/to/repo",
    timeout=600,
)
```

If an interactive Cursor Agent session is required, start it as a managed background PTY and drive it with `process`:

```python
terminal(command="agent", workdir="/path/to/repo", background=True, pty=True)
process(action="submit", session_id="<id>", data="<prompt>")
process(action="log", session_id="<id>")
```

Only use `--trust` or equivalent approval-bypass flags when the working directory and task scope are safe and intentional.

### Claude Code / OpenCode

For Claude Code, prefer print mode for single tasks and set a bounded turn budget / allowed tools where applicable:

```python
terminal(
    command="claude -p --max-turns 10 --allowedTools Read,Edit,Bash 'Complete <task> and summarize verification.'",
    workdir="/path/to/repo",
    timeout=600,
)
```

For OpenCode, prefer `opencode run` for one-shot automation; reserve the TUI for iterative work:

```python
terminal(command="opencode run 'Complete <task> and report tests.'", workdir="/path/to/repo", timeout=600)
```

## Background / interactive management

- Use `background=true, notify_on_complete=true` for long bounded jobs.
- Use `pty=true` for interactive terminal apps such as Codex, Claude Code TUI, OpenCode TUI, or an interactive Cursor session.
- Use `process(action="poll")` for status and new output, `process(action="log")` for full output, and `process(action="wait")` when it is acceptable to block until completion.
- Use `process(action="submit")` only for expected prompts. If a command expects EOF after stdin, send data with `process(action="write")` and then `process(action="close")`.
- If an interactive agent has completed the real task and is only waiting for more follow-up, close stdin gracefully with `process(action="close")`; do not treat the still-open prompt as evidence that the task is unfinished.
- Do not kill slow agent sessions by default; first inspect logs/progress. Use the tool/process manager or a graceful exit path, and follow the user's service/process safety preferences.

## Safety and verification rules

1. Keep prompts narrow: concrete repo, scope, allowed files, acceptance criteria, and required verification output.
2. Do not pass secrets in prompts. If the external agent needs credentials, rely on its existing auth store or environment and do not print credential files.
3. Separate parallel work with worktrees/workdirs.
4. Do not let multiple external agents edit the same checkout concurrently.
5. After the external agent finishes, verify with the parent Hermes agent:
   - `git status --short --branch`
   - `git diff --check`
   - targeted tests/lints/builds for touched code
   - read-back of any external URL/file/document claimed as created or updated
6. Report real tool output and residual risks, not only the external agent's summary.

## When to make it first-class

Start with a skill plus `terminal/process` when the workflow is just a CLI invocation pattern. Build a Hermes plugin/tool, MCP server, or ACP/provider integration when any of these are true:

- the CLI needs structured arguments/results rather than shell text;
- repeated use requires redaction, credential handling, or custom output parsing;
- the agent should appear as a model/provider backend rather than a one-off subprocess;
- the workflow needs UI cards, approvals, streaming status, or policy gates beyond what `terminal/process` provide.

Copilot ACP is the built-in reference pattern for an external-process provider: Hermes starts a local ACP subprocess and routes model calls through that protocol. That does not imply Cursor Agent is supported the same way unless an explicit Cursor-compatible wrapper exists.

## References

- `references/hermes-official-external-agent-patterns.md` — source/docs evidence for this workflow and the current Cursor Agent gap.
- `references/interactive-agent-supervision-and-closeout.md` — session-derived supervision loop: interactive PTY steering, mid-run authorization follow-up, independent acceptance readback, graceful EOF closeout, and avoiding over-watching after completion.
