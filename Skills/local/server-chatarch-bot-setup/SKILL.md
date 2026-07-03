---
name: server-chatarch-bot-setup
description: Configure a managed server as a ChatArch Playground host and add a CC Connect Feishu bot. Use for bot/server hosts with uv, ChatUp, Node.js, CC Connect, Codex or Cursor Agent, and a user-level service.
version: 0.2.0
---

# Server ChatArch Bot Setup

Use this skill when configuring a managed server from the local Playground machine via ordinary `ssh` commands, not Hermes SSH Mode.

This is a copy-and-adapt local Skill template. Keep machine-specific hosts, Feishu credentials, API keys, proxy URLs, private key paths, and exact user IDs in task records or target-local config, not in the reusable Skill.

## Principles

- Keep scripts, logs, copied references, and reports in the active local Playground project.
- Use remote `~/Playground` with capital `P` unless the target explicitly uses another workspace.
- Use ordinary local `ssh <alias> ...` and `scp` for cross-machine setup; do not switch the Hermes thread into SSH Mode unless the user explicitly asks.
- Start with redacted inventory before writes: host/user/home, `~/Playground`, `chatup`, Node.js, `cc-connect`, existing config paths, existing Feishu credentials, and service state.
- Preserve existing Feishu `app_id`/`app_secret` if present; never overwrite a working bot binding just to normalize the config.
- Do not hardcode proxy credentials, model API keys, Feishu secrets, or provider tokens into reusable scripts or reports.
- For any remote config rewrite, first make a timestamped backup on the target and record only the backup path.

## Standard Target State

On the remote server:

- `~/Playground` exists and is initialized by `chatup workspace` when needed.
- `~/.local/bin/uv` is installed.
- `~/.chatarch/venv` uses Python 3.12 and has seeded pip.
- `~/.chatarch/env.sh` is sourced by `.bashrc` and `.profile`, making the ChatArch Python environment default for login shells.
- `chatup` is installed in the ChatArch venv.
- Node.js >= 20 exists; install through `chatup nodejs -I` when needed.
- `cc-connect` is installed through `chatup cc-connect -I` or a known internal package path such as `@chatarch/cc-connect`.
- CC Connect config defines project `playground` with `work_dir = "/home/<user>/Playground"`.
- If using Codex agent, `@openai/codex` is installed globally through npm and the agent config uses `codex`.
- If using Cursor Agent, use agent type `cursor`, prefer absolute `cmd = "/home/<user>/.local/bin/agent"`, and verify `agent models` plus a bounded print-mode smoke test.
- A user-level systemd service `~/.config/systemd/user/cc-connect.service` runs `cc-connect --config <config-path>` with `WorkingDirectory=~/Playground`.

## Procedure

1. Create or reuse a local task under `~/Playground/projects/` and record the target host plus acceptance criteria in `PRD.md` and `progress.md`.
2. Inspect the target with ordinary SSH, not SSH Mode.
3. Run a redacted inventory for Python/uv/ChatUp/Node/npm/CC Connect/agent/service/config paths.
4. Locate existing configs without printing secrets:
   - `~/.cc-connect/config.toml`
   - `~/.chatarch/cc-connect/config.toml`
   - `~/.config/cc-connect/config.toml`
   - `~/.config/systemd/user/cc-connect.service`
5. Print only structural keys: section names, project names, agent type, mode, `work_dir`, service `ExecStart`, and whether Feishu credentials are present.
6. If the target lacks the base environment, run the project-local setup script or follow the manual order: install uv → Python 3.12 venv → ChatArch env.sh → ChatUp → Node.js → CC Connect → workspace → selected agent CLI.
7. Before changing target config, make timestamped backups under `~/.chatarch/backups/`.
8. Write or patch config so the project is `playground` and `work_dir` is the remote `~/Playground`. Preserve existing Feishu app credentials if they exist.
9. Configure or update a user-level systemd service with explicit `WorkingDirectory`, `PATH`, and `ExecStart=<cc-connect-bin> --config <config-path>`.
10. If Feishu credentials are absent, run `cc-connect feishu setup --project playground --qr-image "$HOME/Playground/playground/feishu-qr.png" --timeout 600` and send the launcher URL to the user.
11. After credentials exist, `daemon-reload`, `enable`, `restart`, inspect status, then run a real messaging smoke test.

## Verification Checklist

- `~/Playground` exists on the remote target.
- `uv --version`, `chatup --version`, `node --version`, `npm --version`, and `cc-connect --version` work.
- Selected agent CLI works (`codex --version` or `agent --version` / `agent models`).
- CC Connect config exists at the intended path and has mode `0600`.
- Config has project `playground`, correct agent type, and `work_dir = "/home/<user>/Playground"`.
- Feishu credentials are present or onboarding URL has been handed to the user.
- `systemctl --user is-enabled cc-connect.service` returns `enabled`.
- `systemctl --user is-active cc-connect.service` returns `active` after credentials are in place.
- A real outbound/inbound Feishu smoke test is performed before claiming the bot is usable.

## Pitfalls

- Non-interactive SSH may not load nvm; source `~/.nvm/nvm.sh` before using `node`, `npm`, `cc-connect`, `codex`, or `agent`.
- `proxy on` may not exist for a target user. Prefer a runtime `PROXY_URL` variable for scripts.
- `cc-connect daemon install` may look in the current directory for `config.toml`; pass `--config` or write an explicit user service.
- The CC Connect service will fail until Feishu `app_id` and `app_secret` are created/bound.
- Avoid leaving secrets in local logs; redact API keys, app secrets, and proxy credentials.
- Do not assume a target with `~/.cc-connect/config.toml` is already aligned with the current workspace convention; inspect project name and `work_dir` first.
- For target migrations, preserve existing Feishu credentials even if moving from old config path `~/.cc-connect/config.toml` to newer `~/.chatarch/cc-connect/config.toml`.
