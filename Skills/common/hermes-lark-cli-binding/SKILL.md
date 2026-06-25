---
name: hermes-lark-cli-binding
description: Install Lark CLI and bind it to the same Feishu/Lark app used by Hermes Agent on this machine.
version: 0.1.0
---

# Hermes → Lark CLI Binding

Use this skill when setting up a machine after Hermes Agent Feishu/Lark gateway configuration and the user wants `lark-cli` to use the same Feishu/Lark app/bot as Hermes.

## Goal

Keep these aligned on each machine:

- Hermes Feishu gateway credentials: `~/.hermes/.env` with `FEISHU_APP_ID` / `FEISHU_APP_SECRET`.
- Lark CLI app binding: same app/bot as Hermes, usually under the Hermes-aware CLI workspace.

Do **not** manually print or copy raw app secrets in chat or logs. Prefer `lark-cli config bind --source hermes`, which reads the Hermes config and stores the CLI-side secret using its own storage policy, such as macOS Keychain.

## Install `lark-cli`

Check whether it is already installed:

```bash
command -v lark-cli
lark-cli --version
```

If missing and Node/npm is available, install the official CLI package:

```bash
npm install -g @larksuite/cli
command -v lark-cli
lark-cli --version
```

If npm/node is missing, install Node first using the user's preferred machine setup path, then repeat the CLI install. Do not install into a random project-local `node_modules` unless that is explicitly intended.

## Bind Lark CLI to Hermes' Feishu app

After Hermes Feishu/Lark gateway has been configured on the machine, bind the CLI to the same app:

```bash
lark-cli config bind --source hermes --identity bot-only
```

Use `bot-only` by default. It uses the bot/app identity and avoids user impersonation. It is enough for bot-side API calls and for confirming the CLI is pointed at the same Feishu robot.

Only use user identity when the task explicitly needs personal user resources such as user-owned Docs, Drive, Calendar, Mail, etc. In that case ask/confirm the broader identity boundary, then bind or switch policy deliberately:

```bash
lark-cli config bind --source hermes --identity user-default
```

If switching an already-bound same app from `bot-only` to `user-default`, the installed CLI may require `--force` or may prefer `lark-cli config strict-mode`; check `lark-cli config bind --help` and `lark-cli config strict-mode --help` on the target machine.

## Verify

Run safe verification commands that do not expose secrets:

```bash
lark-cli doctor
lark-cli config show
lark-cli auth status --verify
```

Expected healthy signs:

- `doctor` passes `config_file`, `app_resolved`, and `bot_identity`.
- `config show` reports the same app ID as Hermes' `FEISHU_APP_ID`.
- `auth status --verify` shows bot identity `ready` / `verified`.

Inside a Hermes tool process, `lark-cli` may intentionally auto-detect an agent workspace and use:

```text
~/.lark-cli/hermes/config.json
```

rather than the user's normal shell/global config path. This is expected when binding the Hermes app. If the user asks about the normal/global CLI config instead, verify the intended environment before diagnosing.

## Manual fallback when `config bind` is unavailable

Prefer upgrading `lark-cli` first. If the installed version does not have `config bind`, use the non-echoing secret path:

```bash
# Review commands before running. Do not print the secret.
set -a
. ~/.hermes/.env
set +a
printf '%s' "$FEISHU_APP_SECRET" | lark-cli config init \
  --app-id "$FEISHU_APP_ID" \
  --app-secret-stdin \
  --brand "${FEISHU_DOMAIN:-feishu}"
```

Then verify with `lark-cli doctor` and `lark-cli config show`.

## Pitfalls

- Do not paste `FEISHU_APP_SECRET` into chat, docs, or command output.
- Do not assume Lark CLI and Hermes store credentials the same way: Hermes commonly uses `.env`; Lark CLI may store a keychain reference.
- Do not default to `user-default`. It expands the security boundary and may require OAuth login.
- When running from inside Hermes, a CLI workspace named `hermes` is normal and often desired for this workflow.
- If macOS Keychain blocks non-interactive access, report that boundary directly; do not silently downgrade keychain storage unless the user approves.
