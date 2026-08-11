---
name: server-chatarch-bot-setup
description: Configure a managed server as a ChatArch Playground host and add a CC Connect Feishu bot. Use for bot/server hosts with uv, ChatUp, Node.js, CC Connect, Codex or Cursor Agent, and a user-level service.
version: 0.2.3
---

# Server ChatArch Bot Setup

## P0 User-Visible Link / Authorization Card Rule

- In a live Feishu/Hermes conversation with the `feishu_card` tool available, send authorization or verification URLs as a card, not as a raw text link. Prefer `feishu_card.request_authorization` for simple authorize/cancel flows.
- A card must include a navigation button for the URL and terminal feedback buttons such as `我已完成授权` / `取消`, so the agent can receive a structured result and continue.
- If cards are unavailable or the user explicitly asks for plain text, send launcher URLs, authorization URLs, verification URLs, console/settings links, QR companion links, Feishu doc links, or other user-clickable URLs as bare clickable URLs or normal Markdown links.
- Never put user-clickable URLs in inline backticks, fenced code blocks, command snippets, JSON snippets, tables with code formatting, angle brackets, or space-split text. Code highlighting makes links unclickable for this user.
- When a command prints a URL, generate/show the QR image when applicable and also provide the URL either through the authorization card or as a bare fallback link.
- Run this check before every final response that contains a link.

Use this skill when configuring a managed server from an operator Playground workspace via ordinary `ssh` commands, not Hermes SSH Mode.

This is a reusable ChatArch Skill template. Keep machine-specific hosts, Feishu credentials, API keys, proxy URLs, private key paths, and exact user IDs in task records or target-local config, not in the reusable Skill.

## Principles

- Treat user wording as dictated input: normalize likely project/tool/command/system-name transcription errors from context before searching, writing scripts, naming files, updating reports, or replying. Never persist uncorrected terms as aliases, headings, or history.
- Keep scripts, logs, copied references, and reports in the active local Playground project.
- For uv / Python / `~/.chatarch/venv` / ChatUp preinstall, load `chatarch-server-preinstall` first and follow that flow instead of inventing ad-hoc system Python or per-tool venv setup.
- Use remote `~/Playground` with capital `P` unless the target explicitly uses another workspace.
- Use ordinary local `ssh <alias> ...` and `scp` for cross-machine setup; do not switch the Hermes thread into SSH Mode unless the user explicitly asks.
- Start with redacted inventory before writes: host/user/home, `~/Playground`, `chatup`, Node.js, `cc-connect`, existing config paths, existing Feishu credentials, and service state.
- Preserve existing Feishu `app_id`/`app_secret` if present; never overwrite a working bot binding just to normalize the config.
- One managed server should normally keep one Feishu bot binding. If credentials already exist and the bot works, do not create another bot; repair missing capabilities, metadata, permissions, events, or publish state on the existing app.
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
- If replacing/removing an old unscoped global `cc-connect` package, expect npm to remove the shared `cc-connect` bin link; immediately run `npm install -g @chatarch/cc-connect@<version> --force` and verify `readlink -f $(command -v cc-connect)` resolves under `node_modules/@chatarch/cc-connect/`.
- CC Connect config defines project `playground` with `work_dir = "/home/<user>/Playground"`.
- If using Codex agent, `@openai/codex` is installed globally through npm and the agent config uses `codex`.
- If using Cursor Agent, use agent type `cursor`, prefer absolute `cmd = "/home/<user>/.local/bin/agent"`, and verify `agent models` plus a bounded print-mode smoke test.
- A user-level systemd service `~/.config/systemd/user/cc-connect.service` runs `cc-connect --config <config-path>` with `WorkingDirectory=~/Playground`.

## Feishu Bot Creation and Capability Baseline

Use this section only for generic procedure; keep concrete app IDs, secrets, user IDs, tenant names, chat IDs, and private links in task-local records or target-local config.

For a **new server with no Feishu credentials**:

- Create the bot through the standard CC Connect onboarding path and give the user the launcher/QR URL immediately. In Feishu/Hermes, present authorization/verification URLs with a `feishu_card.request_authorization` card when possible; otherwise use a bare clickable fallback link, never inline-code or code-block formatting.
- During creation, make the bot identity explicit and useful: name should identify CC Connect and the target role/workspace, description should say it is a CC Connect remote agent entrypoint, and icon/menu/help text should not contain stale product names or placeholders.
- After the user authorizes creation, continue the operator side immediately: verify credentials, write them to the target config, restart the service, and keep going until the bot can exchange real messages.
- Do not treat `app_id`/`app_secret` presence or a websocket connection as complete acceptance. They prove credentials and transport only.

For an **existing server with Feishu credentials**:

- Do not create a second bot by default.
- Verify the existing app first: tenant token, bot info, service status, websocket connection, inbound event log, outbound reply, and current project/work_dir mapping.
- If the bot is missing capabilities, fix the existing app/config instead of replacing it.

Required Feishu app baseline for CC Connect:

- Bot capability enabled, with CC Connect-specific name, description, and icon.
- Permissions/scopes needed for normal chat: receive private messages, receive group @ messages, send messages as bot, and read basic user/chat metadata needed by the adapter. Avoid requesting broad/sensitive scopes unless the concrete feature requires them.
- Event subscription uses long connection and includes `im.message.receive_v1`.
- Card callback `card.action.trigger` is configured when interactive cards are enabled; otherwise set `enable_feishu_card = false` in CC Connect config so users get text fallback instead of broken card buttons.
- App version is created/published and availability is set so the intended users can talk to the bot.
- Optional bot menu entries should map to CC Connect commands such as `/help`, `/status`, `/new`, `/list`, `/stop`, `/model`, `/mode`, `/whoami`, and `/doctor`.

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
10. If Feishu credentials are absent, run `cc-connect feishu setup --project playground --qr-image "$HOME/Playground/playground/feishu-qr.png" --timeout 600`. Send the launcher/verification URL through `feishu_card.request_authorization` when the current conversation supports cards; include the QR image if generated. Use a bare clickable URL only as the fallback path.
11. After the user clicks the authorization card's completion button or otherwise confirms browser-side completion, verify and complete the baseline above before claiming success. If onboarding did not preconfigure all permissions/events/publish state, provide the needed authorization/settings link as an authorization card when possible, or as a bare clickable fallback link, then resume verification.
12. If Feishu credentials already exist, skip onboarding. Probe the current app and service, then repair missing capability/permission/event/publish/menu/help metadata on the existing app.
13. After credentials exist, `daemon-reload`, `enable`, `restart`, inspect status, then run a real messaging smoke test.

## Authorization Card Pattern

When the setup command yields a user-facing verification URL and this conversation has `feishu_card`, send an authorization card instead of pasting only a link:

```json
{
  "action": "request_authorization",
  "title": "CC Connect 飞书授权",
  "body": "请点击按钮打开授权页面。完成浏览器里的授权后，回到这里点击“我已完成授权”；如果不继续，请点击“取消”。",
  "verification_url": "https://example.com/verify",
  "flow_id": "cc-connect-feishu-setup-<short-id>"
}
```

Rules:

- `verification_url` is the exact URL printed by onboarding or the developer console; do not store tokens from it in reusable docs.
- `flow_id` is a short non-secret correlation ID for this attempt.
- Treat a click on `我已完成授权` as a prompt to verify, not as proof. Continue by checking credentials, app publish state, event subscription, service status, and a real message smoke test.
- If the user clicks `取消`, stop the privileged setup path and explain what remains blocked.

## Verification Checklist

- `~/Playground` exists on the remote target.
- `uv --version`, `chatup --version`, `node --version`, `npm --version`, and `cc-connect --version` work.
- Selected agent CLI works (`codex --version` or `agent --version` / `agent models`).
- CC Connect config exists at the intended path and has mode `0600`.
- Config has project `playground`, correct agent type, and `work_dir = "/home/<user>/Playground"`.
- Feishu credentials are present or onboarding URL has been handed to the user.
- `systemctl --user is-enabled cc-connect.service` returns `enabled`.
- `systemctl --user is-active cc-connect.service` returns `active` after credentials are in place.
- Feishu logs show a real inbound `im.message.receive_v1` event for the configured app and CC Connect logs show `message received`, `processing message`, and `turn complete` or an equivalent successful reply path.
- A real Feishu smoke test is performed before claiming the bot is usable: user sends `/help`, `/status`, or a short normal message, and the bot replies in the expected chat.

## Pitfalls

- Non-interactive SSH may not load nvm; source `~/.nvm/nvm.sh` before using `node`, `npm`, `cc-connect`, `codex`, or `agent`.
- `proxy on` may not exist for a target user. Prefer a runtime `PROXY_URL` variable for scripts.
- `cc-connect daemon install` may look in the current directory for `config.toml`; pass `--config` or write an explicit user service.
- The CC Connect service will fail until Feishu `app_id` and `app_secret` are created/bound.
- A successful `cc-connect feishu setup/new` can still leave the app incomplete. Always check app capability, permissions, long-connection event subscription, card callback, publish state, and availability.
- Do not create another bot to fix a partially configured existing one unless the user explicitly asks. Prefer repairing the current app and config.
- Avoid leaving secrets in local logs; redact API keys, app secrets, Feishu IDs/open IDs when they are not needed, proxy credentials, access keys, tickets, and connection IDs.
- Do not assume a target with `~/.cc-connect/config.toml` is already aligned with the current workspace convention; inspect project name and `work_dir` first.
- For target migrations, preserve existing Feishu credentials even if moving from old config path `~/.cc-connect/config.toml` to newer `~/.chatarch/cc-connect/config.toml`.

## Final Link/Card Checklist

- Before sending any launcher URL, authorization/settings link, verification URL, console URL, or Feishu doc link, first decide whether the current Feishu/Hermes conversation can use an authorization card.
- If `feishu_card` is available, use `request_authorization` or a `request_interaction` link card with terminal feedback buttons.
- If card delivery is unavailable, make the URL a bare clickable URL or normal Markdown link.
- Do not wrap user-clickable links in backticks, code blocks, command output, JSON, tables, angle brackets, or split them with spaces.
- If a QR image is generated, include both the QR image and either the authorization card or the bare fallback URL.
