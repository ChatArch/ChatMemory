# Codex, Cursor Agent, and OpenCode run/resume patterns

Date verified: 2026-08-25.

Use this reference when Hermes supervises one of the common external coding-agent CLIs. These commands are intentionally host-neutral: replace `<repo>`, `<prompt>`, `<session-id>`, `<chat-id>`, and `<nvm-sh>` with the current execution context. Do not publish concrete host aliases, account paths, auth files, or tokens in shared skills.

## Common preflight

1. Resolve the command in the same shell context that will run the worker:
   ```bash
   command -v codex || true
   command -v cursor-agent || true
   command -v agent || true
   command -v opencode || true
   ```
2. If Node-based CLIs are installed under nvm but are missing from non-login PATH, source nvm before checking them:
   ```bash
   [ -s "<nvm-sh>" ] && . "<nvm-sh>"
   ```
3. Check versions/help, not secrets:
   ```bash
   codex --version && codex exec --help && codex exec resume --help
   cursor-agent --version && cursor-agent --help
   opencode --version && opencode run --help && opencode session --help
   ```
4. Use a scratch repo for smokes that need git context:
   ```bash
   mkdir -p <scratch> && cd <scratch> && git init
   ```

## Codex CLI

One-shot smoke:

```bash
codex exec --skip-git-repo-check \
  -s read-only \
  -c 'approval_policy="never"' \
  'Reply exactly CODEX_SMOKE_OK. Do not use tools.'
```

Expected evidence:

- output includes the requested fixed string;
- output prints a `session id:` line;
- sandbox and approval settings match the requested no-edit smoke.

Resume an exec session by explicit id:

```bash
codex exec resume --skip-git-repo-check \
  -c 'sandbox_mode="read-only"' \
  -c 'approval_policy="never"' \
  <session-id> \
  'Reply exactly CODEX_RESUME_OK. Do not use tools.'
```

Important correction from practice: `codex exec resume` does not accept the normal `-s read-only` sandbox flag after the session id. For resume smokes, use config overrides such as `-c 'sandbox_mode="read-only"'` and `-c 'approval_policy="never"'`, or check the active CLI help for the supported option shape. For coding tasks, still prefer `codex exec -s workspace-write '<task>'` for the initial one-shot run.

Interactive Codex sessions are different:

```bash
codex resume <session-id> '<follow-up prompt>'
```

Use `terminal(background=true, pty=true)` only for interactive sessions that need live steering. Plain `codex exec` and `codex exec resume` are easier to supervise as non-PTY one-shots.

## Cursor Agent

Prefer the active Cursor Agent binary that supports durable chats in the target context. Some installs expose both `cursor-agent` and a top-level `agent` command; verify both, then choose one and record it in the worker registry.

Create a durable chat and run the first prompt:

```bash
CHAT_ID=$(agent create-chat | tr -d '\r' | tail -n 1)
agent --print --resume "$CHAT_ID" --force --trust \
  'Reply exactly CURSOR_SMOKE_OK. Do not use tools.'
```

Resume the same chat by explicit id:

```bash
agent --print --resume "$CHAT_ID" --force --trust \
  'Reply exactly CURSOR_RESUME_OK. Do not use tools.'
```

Evidence from practice:

- the first and second calls both return the requested fixed strings;
- the same `CHAT_ID` is reused;
- the command exits cleanly in print mode.

Authentication blocker shape:

```text
Authentication required. Please run '<agent-command> login' first, or set CURSOR_API_KEY environment variable.
```

Treat this as a setup blocker for that execution context. Do not copy tokens or auth files into a prompt. If setup is required, use a local/private bootstrap path and then rerun a real `--print` smoke.

For long worker lanes, store these fields in the project registry/progress file:

- agent command used (`agent` or `cursor-agent`);
- `chat_id`;
- repo/worktree path;
- prompt path;
- report path;
- Hermes process session id;
- current state and old/stale process ids.

If a live Cursor process remains open, continue with `process(action="submit")`. If it has exited or was killed, resume by `--resume <chat-id>` after inspecting repo/report/PR state.

## OpenCode CLI

One-shot smoke with machine-readable events:

```bash
opencode run --format json \
  'Reply exactly OPENCODE_SMOKE_OK. Do not use tools.'
```

Parse the `sessionID` from any JSON event:

```bash
SESSION_ID=$(python3 - <<'PY'
import json, sys
for line in sys.stdin:
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if obj.get("sessionID"):
        print(obj["sessionID"])
        break
PY
)
```

Resume by explicit session id:

```bash
opencode run --format json --session "$SESSION_ID" \
  'Reply exactly OPENCODE_RESUME_OK. Do not use tools.'
```

`--continue` / `-c` continues the latest session, but explicit `--session <id>` is safer when multiple workers or repositories are active. `opencode session list` is for inspecting sessions; use `opencode export` / `opencode import` only when moving session state deliberately.

For the interactive OpenCode TUI:

```bash
opencode
```

Run it with `terminal(background=true, pty=true)` and drive it with `process(action="submit")`. Exit with Ctrl-C (`process(action="write", data="\x03")`) or `process(action="kill")`; do not type `/exit`, which is not the intended OpenCode exit path.

## Supervisor rule

A successful external-agent response is still a self-report. Before marking a lane complete, Hermes must independently verify the concrete state: git status, diff, tests, PR/check runs, deployment readback, or produced files. Resume prompts should include the observed state so the external agent does not duplicate side effects.
