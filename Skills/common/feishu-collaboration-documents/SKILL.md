---
name: feishu-collaboration-documents
description: Playground workspace convention for Feishu collaboration documents and the human-AI main document.
version: 0.1.0
---

# Feishu Collaboration Documents

## Main Document

The Playground workspace's human-AI collaboration main document is:

https://chatarch.feishu.cn/docx/HpiudaXjCoJ7vxxmiN2ccCMmnMe

Title observed via `lark-cli docs +fetch`:

`🤝 人机协作主文档`

Use this document as the durable navigation entry for human-facing Feishu collaboration docs.

## Current Agent Infra Blueprint Document

The current Agent Infra blueprint discussion document is:

https://chatarch.feishu.cn/docx/Z1G2duuoWoeoXexPHMBcKVTtnDh

Title:

`Agent Infra 蓝图整理`

This doc was created from:

`projects/06-18-agent-system-blueprint/playground/agent-infra-blueprint-doc.md`

It is linked from the main document under the section `Agent Infra 蓝图整理`.

## Daily Brainstorm Log Convention

When the user is brainstorming broad, incomplete, or messy ideas, use a daily Feishu log document rather than creating many small docs.

- Main document section: `每日思考 / Brainstorm 日志`
- Naming pattern: `YYYY-MM-DD｜<short topic summary>`
- Purpose: capture and compress the day's conversation.
- Main doc should keep only the dated link and a short note; details belong in the daily log.
- Current first daily log:
  - `2026-06-18｜ChatArch、人机协作与 TODO 体系 Brainstorm`
  - https://chatarch.feishu.cn/docx/JaTpddW25o7TZ0xbWUtcLvUknze

## Workflow Convention

When the user wants to discuss plans, TODOs, blueprints, or project review results collaboratively:

1. Use `lark-cli` with **user identity** for human-facing Feishu docs.
   - Create docs as user: `lark-cli docs +create --api-version v2 --as user ...`
   - Update docs as user: `lark-cli docs +update --api-version v2 --as user ...`
   - Fetch/verify docs as user: `lark-cli docs +fetch --api-version v2 --as user ...`
2. Use **bot identity** for sending Feishu chat notifications/messages after the document exists.
   - Do not create collaboration docs as bot by default.
   - Do not use a bot-created doc as a fallback unless the user explicitly approves the identity change.
3. Check user auth first:

```bash
lark-cli auth status
```

4. If user identity is expired, blocked, or unavailable, stop before doc creation and report the exact auth/keychain boundary. Do not silently fall back to bot-created docs.
5. Prefer creating a focused child doc for each substantial topic.
6. Add the child doc link back to the main document.
7. For substantial reports, do not dump plain Markdown into Feishu. Use the current `lark-cli` embedded `lark-doc` skills first:
   - `lark-cli skills read lark-doc references/lark-doc-create.md`
   - `lark-cli skills read lark-doc references/lark-doc-xml.md`
   - `lark-cli skills read lark-doc references/style/lark-doc-style.md`
   - for updates: `lark-cli skills read lark-doc references/lark-doc-update.md`
8. Prefer XML (`--doc-format xml`) for authored Feishu docs unless the user explicitly asks to import Markdown.
   - Use chapters (`h1/h2`), callouts/highlight blocks, tables, grids, and diagrams/whiteboards when they help readability.
   - Important mechanism reports should include at least one flow diagram when the process has multiple states or components.
   - If a diagram block returns warnings/degradation, do not treat the doc as final; fix the diagram and republish.
9. Fetch the doc back after create/update and verify:
   - title is correct
   - body contains intended structure
   - rich blocks/diagrams did not degrade
   - main doc contains the child link when relevant
10. If fetch/update/create hits missing user scopes, use the Common skill `lark-cli-permission-authorization` and generate a real `https://accounts.feishu.cn/oauth/v1/device/verify?...` link via `lark-cli auth login --scope ... --no-wait --json`; do not send developer-console `open.feishu.cn/app/.../auth` URLs as user-confirmable links.
11. Record final links in the active project `memory.md` and `progress.md`.

## Known CLI Compatibility Note

Installed `lark-cli` versions can differ. Check `lark-cli docs +create --help` when a command fails.

Observed forms in this workspace:

```bash
# Some installed versions expose --markdown:
lark-cli docs +create --api-version v2 --as user --title 'Title' --markdown @file.md

# Older/other observed versions accepted --content:
lark-cli docs +create --api-version v2 --as user --title 'Title' --content @file.md
lark-cli docs +update --api-version v2 --as user --doc '<url>' --command append --content @file.md
lark-cli docs +fetch --api-version v2 --as user --doc '<url>' --format pretty
```

Use the form supported by the installed binary; prefer the help output for flags, but trust validation errors from the actual command over stale notes.

### Hermes tool environment vs user's global `lark-cli`

The Playground user often runs global `lark-cli` from their normal shell, where `lark-cli config show` may report:

```text
workspace: local
Config file path: /Users/rexwzh/.lark-cli/config.json
```

Inside a Hermes tool process, the same binary can auto-detect an Agent workspace and instead report:

```text
workspace: hermes
Config file path: /Users/rexwzh/.lark-cli/hermes/config.json
```

Do not confuse these. When the user explicitly refers to their global/local `lark-cli`, first verify with:

```bash
which lark-cli
lark-cli config show
```

If Hermes workspace auto-detection is getting in the way and the task is to use the user's global/local CLI, run `lark-cli` under a minimal environment rather than opening Terminal.app or guessing config paths:

```bash
/usr/bin/env -i \
  HOME=/Users/rexwzh \
  PATH=/Users/rexwzh/.nvm/versions/node/v24.14.1/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  lark-cli config show
```

This should show the local config path when the global CLI is intended.

### Keychain blocker

In non-interactive automation contexts, `lark-cli auth status` or `docs +create` can still fail with:

```text
keychain Get failed: keychain access blocked
```

This is not the same as “not logged in” or “wrong config”; it means the process cannot read macOS Keychain. Do not fall back to bot-created docs for human-facing docs, and do not open the user's Terminal.app as a workaround. Report the boundary and ask for the preferred remediation.

The known CLI fix is:

```bash
lark-cli config keychain-downgrade
```

Only use or recommend it after user approval because it materializes the master key into a local file and changes the security boundary.
