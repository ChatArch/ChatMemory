---
name: cursor-agent-worker-orchestration
description: "Use when Hermes must run Cursor Agent as an external worker: create/resume chats, supervise, and verify results."
version: 0.1.0
related_skills:
  - hermes-external-agent-cli-orchestration
---

# Cursor Agent Worker Orchestration

Use this skill when Hermes needs to call Cursor Agent as a worker rather than perform the work directly. Hermes is the dispatcher/reviewer; Cursor is the executor.

## Role Boundary

- Hermes defines the task, repo/worktree, allowed side effects, report contract, and acceptance gates.
- Cursor Agent performs the implementation/release/checking assigned in its prompt.
- Hermes supervises the process and independently verifies Cursor's claims before reporting success.
- Do not call this Hermes `delegate_task`: this is an external CLI process launched through `terminal` / `process`.

## Active Binary Rule

Resolve the active Cursor Agent executable before running a task. On `zhihong.oray`, long-running workers should use the top-level `agent` executable with the known Node path, not the small `cursor agent` smoke wrapper.

Smoke:

```bash
NODE_BIN=/home/zhihong/Playground/projects/08-06-manim-exploration/playground/tools/node-v20.19.0-linux-x64/bin
PATH="$NODE_BIN:$PATH" agent --version
PATH="$NODE_BIN:$PATH" agent --print --trust 'Reply exactly: CURSOR_AGENT_SMOKE_OK'
```

If a machine only has `cursor-agent` or `cursor agent`, verify a real `--print` smoke and resume support before assigning durable work. Do not assume all wrapper names behave the same.

## Durable Worker Pattern

For each repo or lane, create one Cursor chat and persist it:

```bash
NODE_BIN=/home/zhihong/Playground/projects/08-06-manim-exploration/playground/tools/node-v20.19.0-linux-x64/bin
CHAT_ID=$(agent create-chat | tr -d '\r' | tail -n 1)
```

Run a prompt file through that same chat:

```bash
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

Store this metadata in run JSON:

- repo / package / CLI command
- workdir or isolated worktree
- branch and target version, when relevant
- prompt path and report path
- Cursor `chat_id`
- Hermes process session id
- current stage and last external readback

## Prompt Contract

A worker prompt should be self-contained and include:

- exact task class and non-goals
- repo/worktree path and dirty-state rules
- allowed side effects and hard blockers
- secrets redaction rules
- external tools to use, with exact command paths when PATH may be stale
- required local gates and external readbacks
- final report path and required PASS/BLOCKED fields

For release work, the prompt must state whether the worker is only local/evidence or full-flow. Only full-flow prompts may authorize push, PR, merge, tag, publish, and clean-install verification.

## Supervision Loop

1. Start Cursor as `terminal(background=true, notify_on_complete=true, pty=true)` for long bounded work.
2. Report dispatch immediately with process id, chat id, workdir, and first expected milestone.
3. Poll/log periodically; if silent, inspect repo status and process tree before deciding whether it is healthy or stalled.
4. If the process exits normally, read its report and verify artifacts yourself.
5. If the process times out or is killed, inspect real state before resuming:
   - local worktree status
   - remote branch and PRs
   - tags and workflow runs
   - registry/PyPI/package state when relevant
   - report file existence and completeness
6. Resume with the same `chat_id`; do not create duplicate chats, branches, PRs, or tags.

## Verification Rule

Cursor output is a self-report. Before telling the user a task succeeded, Hermes must independently verify concrete evidence: changed files, tests, git state, PR/check status, workflow runs, registry entries, clean install, or other external handles.

## Common Pitfalls

- Using `cursor agent` for a long resumable worker when the top-level `agent` is required.
- Losing the `chat_id`, then starting a fresh chat and duplicating side effects.
- Treating `kill_all` as failure without checking whether PR/tag/workflow/PyPI side effects already happened.
- Trusting `PASS` text without reading the required report and external state.
- Passing secrets in the prompt or printing values from `.env`, proxy config, auth JSON, or token stores.
