---
name: hermes-external-agent-cli-orchestration
description: Use when Hermes needs to call Codex, Cursor Agent, Claude Code, OpenCode, or another local coding-agent CLI; choose terminal/process vs delegate_task/plugin/ACP.
version: 0.1.8
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

Shared/public skills must stay host-neutral. Do not write concrete server aliases, usernames, home directories, chat ids, private proxy helper paths, or organization-internal machine names into this skill. Use placeholders such as `<workspace>`, `<node-bin-dir>`, `<proxy-helper>`, `<worker-host>`, and `<agent-command>`. Keep machine-specific command paths in the active workspace-local skill, task project notes, or run JSON that is not promoted as shared memory.

Treat SSH aliases and worker-host nicknames as relative to the current execution environment. A name that works from the operator machine may not exist on the target machine or inside the worker's shell. Shared skills should say to resolve the worker host/executable from current local notes and verify with `hostname`, `pwd`, and `command -v <agent-command>` rather than naming a concrete alias.

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
   - Cursor Agent durable workers should use the verified full worker executable for the current host, often a top-level `agent` wrapper, not an unverified lightweight wrapper. The portable pattern is `CHAT_ID=$(<agent-command> create-chat | tr -d '\r' | tail -n 1)` followed by `<agent-command> --print --resume "$CHAT_ID" --force --trust <prompt>`; store that `chat_id` in the run JSON and reuse it for every continuation. A small wrapper such as `cursor agent` may work for tiny one-shot probes, but do not use it for resumable release workers until its resume behavior is verified on that host.
   - Codex supports `codex resume`; current help also exposes `codex exec resume` for resuming a previous exec session by id or latest session. Practice on 2026-08-25 verified that `codex exec resume` uses config overrides such as `-c 'sandbox_mode="read-only"'`; do not put the normal initial-run `-s read-only` flag after the session id.
   - Claude Code supports `--continue`, `--resume`, `--session-id`, and `--fork-session`; session persistence can be disabled with `--no-session-persistence`.
   - OpenCode supports `opencode run --session <session-id> <prompt>` for explicit persisted-session continuation, plus `--continue` / `-c`, `--session` / `-s`, `--fork`, `opencode session`, `opencode export`, and `opencode import`.

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

## Codex configuration, API providers, and tools

Codex can start without a user `config.toml` when it uses its native ChatGPT login and built-in defaults. A custom API-backed Agent lane is different: it needs an effective provider configuration, a credential source, and a model/endpoint that support the requested wire protocol. Do not describe “the API works” as “Codex tools work” until the Agent loop has been exercised.

Resolve the effective Codex configuration in this order:

1. Choose the state root with `CODEX_HOME` (auth, config, profiles and session state are rooted there).
2. Load the default `$CODEX_HOME/config.toml` unless the invocation explicitly skips it.
3. Layer `$CODEX_HOME/<name>.config.toml` with `--profile <name>` when an isolated profile is selected.
4. Apply command-line settings such as `--model`, `--sandbox`, and `-c/--config key=value`; for reliable one-shot execution, put model/provider `-c` overrides on the parser after `exec`, and put continuation overrides on `exec resume`.

`codex exec --ignore-user-config` skips `$CODEX_HOME/config.toml` but still uses authentication from `CODEX_HOME`; it also removes user-configured `model_providers`, `mcp_servers`, plugins, and related tool wiring unless those are supplied through another supported layer. It is a useful minimal-config diagnostic, not a normal API-Agent launch mode. `codex exec resume` has its own option parser, so do not assume that an option accepted by the root command or the initial `exec` invocation will survive a resume boundary.

Keep these layers separate:

- **Authentication identity:** native ChatGPT/OAuth state or an API-key credential source. Changing `model_provider` does not prove that the desktop account, subscription entitlement, dots, cloud workspace, or other native features changed.
- **Model request provider:** `model_provider` selects the active provider; `[model_providers.<name>]` defines an OpenAI-compatible endpoint, `wire_api`, model discovery behavior, and an `env_key`/other supported credential source.
- **Agent tools:** built-in shell/file/browser/computer-use features, MCP servers, plugins, skills and approval/sandbox policy. A provider must support the model/tool protocol, and the effective config must actually load the relevant tool server/plugin. A successful text-only API response proves neither.

For an API-backed Agent, prefer the workspace's isolated-profile pattern:

```text
ChatEnv profile (secret value) -> child environment loader -> Codex profile
  -> codex exec --profile <api-profile> ...
```

The profile should contain only non-secret routing metadata and an `env_key` such as `OPENAI_API_KEY`; the key remains in the approved environment/secret store. A typical provider shape is:

```toml
# $CODEX_HOME/<api-profile>.config.toml
model = "<api-model>"
model_provider = "<api-provider>"

[model_providers.<api-provider>]
name = "<provider-label>"
base_url = "https://<openai-compatible-host>/v1"
wire_api = "responses"
env_key = "OPENAI_API_KEY"
requires_openai_auth = false
```

Use an owner-only wrapper or ChatEnv launcher to load the secret and invoke the profile. Do not put the key in argv, a shared skill, a project report, or the main subscription config. For a minimal API smoke, use `--ephemeral`, `--skip-git-repo-check` only outside a Git repo, and a read-only sandbox; then run a separate harmless tool smoke if the acceptance criterion is Agent/tool execution.

The recent Token Plan/Codex workspace pattern follows this design: a named ChatEnv API profile, a separate Codex config profile, a small wrapper that runs `codex --profile ...`, and a bounded `codex exec` smoke. That is a configuration-isolation pattern, not permission to replace the user's native subscription login. Never add `forced_login_method="api"` to the same `CODEX_HOME` that contains a ChatGPT login; an auth-mode conflict can trigger logout and delete the live native auth cache.

Treat provider discovery and provider entitlement as separate gates. A successful `GET /models` only proves that the endpoint and credential can answer a catalogue request; it does not prove that the selected model is purchased/eligible for Responses or for the Agent loop. Run one exact-model `codex exec` smoke and classify `403 AccessDenied.Unpurchased` as a provider entitlement blocker, not as a Codex tool/config success. Also verify that the profile file exists in the active `CODEX_HOME`: a wrapper and a ChatEnv secret without its matching `<name>.config.toml` are an incomplete launch path. If the model smoke succeeds, run a separate harmless tool smoke; keep text-call, Agent-loop, and tool-use verdicts distinct.

For OpenAI's subscription-granted API credits, distinguish a successful Codex API-key Agent run from the billing bucket. The current benefit terms exclude Codex usage made through an API key. A completed `codex exec` call with an OpenAI project key proves the technical route and tool loop only; it does not prove that gifted credits paid for it. Inspect the exact organization's billing/credit-grant ledger separately before claiming a deduction source, and never use `codex login`/logout or overwrite native auth to perform this test. For a bounded check, use an owner-only key file, a separate `CODEX_HOME` without `auth.json`, ephemeral exec, a read-only sandbox, and per-command provider overrides; compare native auth/config hashes before and after.

## One-shot command templates

### Codex CLI

Codex `exec` one-shots do not need a PTY for bounded automation. Use a PTY only for interactive Codex sessions you intend to steer live.

Do not assume Codex is installed just because it is a possible fallback. Verify `command -v codex`, `codex --help` or `codex --version`, auth/status, and one bounded smoke before assigning work. If Codex is absent on the current host, first check whether a Node/nvm install is present but missing from the non-login PATH; otherwise use another verified external agent instead of promising a Codex lane there.

```python
terminal(
    command="codex exec --skip-git-repo-check -s read-only -c 'approval_policy=\"never\"' 'Reply exactly CODEX_SMOKE_OK. Do not use tools.'",
    workdir="/path/to/repo-or-scratch",
    timeout=300,
)
```

For long bounded Codex jobs:

```python
terminal(
    command="codex exec -s workspace-write 'Refactor <scope>. Keep changes focused.'",
    workdir="/path/to/repo",
    background=True,
    notify_on_complete=True,
)
```

Resume a previous `codex exec` session by explicit id:

```python
terminal(
    command="codex exec resume --skip-git-repo-check -c 'sandbox_mode=\"read-only\"' -c 'approval_policy=\"never\"' <session-id> 'Reply exactly CODEX_RESUME_OK. Do not use tools.'",
    workdir="/path/to/repo-or-scratch",
    timeout=300,
)
```

Practice correction: `codex exec resume` has its own option parser. Do not put the initial-run `-s read-only` flag after `<session-id>`; use `-c 'sandbox_mode="read-only"'` for resume smokes unless the active CLI help says otherwise.

Current Codex CLI guidance prefers `--sandbox workspace-write` / `-s workspace-write`; legacy `--full-auto` is deprecated, and yolo/full-access modes require explicit risk acceptance.

### Cursor Agent

Hermes does not currently have a first-class Cursor Agent tool/provider in the official docs/source. Treat Cursor Agent as an external CLI unless a project supplies a plugin/MCP/ACP wrapper.

For durable Cursor worker chats, prefer an explicit CLI-native chat id. If the host requires Node or proxy setup, fill placeholders from workspace-local notes rather than shared skills:

```bash
[ -n "${NODE_BIN:-}" ] && PATH="$NODE_BIN:$PATH"
[ -n "${PROXY_HELPER:-}" ] && source "$PROXY_HELPER"
CHAT_ID=$(<agent-command> create-chat | tr -d '\r' | tail -n 1)
PROMPT=/path/to/prompt.txt
prompt=$(PROMPT="$PROMPT" python - <<'PY'
import os
from pathlib import Path
print(Path(os.environ["PROMPT"]).read_text())
PY
)
<agent-command> --print --resume "$CHAT_ID" --force --trust "$prompt"
```

Some installs expose the same worker as `agent`, `cursor-agent`, or a wrapper command. Resolve the active binary in the target shell and store it with the `chat_id` so future resumes use the same execution context.

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

For OpenCode, prefer `opencode run` for one-shot automation and `opencode run --session <session-id>` for explicit continuation; reserve the TUI for iterative work:

```python
terminal(command="opencode run --format json 'Complete <task> and report tests.'", workdir="/path/to/repo", timeout=600)
terminal(command="opencode run --format json --session <session-id> 'Continue with <follow-up>.'", workdir="/path/to/repo", timeout=600)
```

Parse `sessionID` from the JSON events emitted by `--format json` and store it in the worker registry. Prefer explicit `--session <session-id>` over `--continue` when multiple repos or agents may have run.

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

- `references/codex-cursor-opencode-run-resume.md` — 2026-08-25 practice-verified run/resume templates for Codex, Cursor Agent, and OpenCode, including Codex `exec resume` option-shape correction, Cursor `create-chat`/`--resume`, OpenCode JSON `sessionID`, and supervisor verification rules.
- `references/hermes-official-external-agent-patterns.md` — source/docs evidence for this workflow and the current Cursor Agent gap.
- `references/interactive-agent-supervision-and-closeout.md` — session-derived supervision loop: interactive PTY steering, mid-run authorization follow-up, independent acceptance readback, graceful EOF closeout, and avoiding over-watching after completion.
- `references/multi-worker-pr-orchestration.md` — group-task pattern for supervising multiple external CLI workers through explicit worktrees, durable CLI-native chat/session ids, resume loops, checkpoint reports, supervisor verification, and PR gates.
