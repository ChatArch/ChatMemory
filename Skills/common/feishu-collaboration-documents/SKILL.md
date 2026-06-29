---
name: feishu-collaboration-documents
description: Shared workflow for Feishu/Lark collaboration documents without workspace-specific links. Put concrete document URLs and group conventions in a local skill.
version: 0.2.0
---

# Feishu Collaboration Documents

Use this public/shared skill when creating, updating, or verifying Feishu/Lark documents for human-AI collaboration.

Do not store tenant-specific Feishu document URLs, group chat IDs, app IDs, bot IDs, or private collaboration conventions in this shared skill. Keep those in a local/private skill for the target machine or tenant.

## Local Configuration Required

Before creating or linking collaboration docs, load or create a local skill that defines the local workspace conventions, for example:

- main collaboration document URL: `<LOCAL_MAIN_DOC_URL>`
- section names for child links: `<LOCAL_SECTION_NAME>`
- preferred chat/group for notifications: `<LOCAL_CHAT_ID_OR_NAME>`
- local bot/app identity notes: `<LOCAL_APP_PROFILE_NOTES>`

If the local skill is missing, ask the user where links should be attached instead of guessing or writing a private URL into this shared skill.

## Daily Brainstorm Log Convention

When the user is brainstorming broad, incomplete, or messy ideas, prefer a daily Feishu log document rather than creating many small docs. Keep this as a convention, while filling local destinations from the local skill.

- Main document section: `<LOCAL_BRAINSTORM_SECTION>`
- Naming pattern: `YYYY-MM-DD | <short topic summary>`
- Purpose: capture and compress the day's conversation.
- Main doc should keep only the dated link and a short note; details belong in the daily log.

## Workflow Convention

When the user wants to discuss plans, TODOs, blueprints, or project review results collaboratively:

1. Load the local collaboration-documents skill or local project memory to get the current main doc URL and section conventions.
2. Use `lark-cli` with **user identity** for human-facing Feishu docs.
   - Create docs as user: `lark-cli docs +create --api-version v2 --as user ...`
   - Update docs as user: `lark-cli docs +update --api-version v2 --as user ...`
   - Fetch/verify docs as user: `lark-cli docs +fetch --api-version v2 --as user ...`
3. Use **bot identity** for sending Feishu chat notifications/messages after the document exists.
   - Do not create collaboration docs as bot by default.
   - Do not use a bot-created doc as a fallback unless the user explicitly approves the identity change.
4. Check user auth first:

```bash
lark-cli auth status
```

5. If user identity is expired, blocked, or unavailable, stop before doc creation and report the exact auth/keychain boundary. Do not silently fall back to bot-created docs.
6. Prefer creating a focused child doc for each substantial topic.
7. Add the child doc link back to the local main document if the local convention says to do so.
8. For substantial reports, do not dump plain Markdown into Feishu. Use the current `lark-cli` embedded `lark-doc` skills first:
   - `lark-cli skills read lark-doc references/lark-doc-create.md`
   - `lark-cli skills read lark-doc references/lark-doc-xml.md`
   - `lark-cli skills read lark-doc references/style/lark-doc-style.md`
   - for updates: `lark-cli skills read lark-doc references/lark-doc-update.md`
9. Prefer XML (`--doc-format xml`) for authored Feishu docs unless the user explicitly asks to import Markdown.
   - Use chapters (`h1/h2`), callouts/highlight blocks, tables, grids, and diagrams/whiteboards when they help readability.
   - Important mechanism reports should include at least one flow diagram when the process has multiple states or components.
   - If a diagram block returns warnings/degradation, do not treat the doc as final; fix the diagram and republish.
10. Fetch the doc back after create/update and verify:
   - title is correct
   - body contains intended structure
   - rich blocks/diagrams did not degrade
   - local main doc contains the child link when relevant
11. If fetch/update/create hits missing user scopes, use the Common skill `lark-cli-permission-authorization` and generate a real `https://accounts.feishu.cn/oauth/v1/device/verify?...` link via `lark-cli auth login --scope ... --no-wait --json`; do not send developer-console `open.feishu.cn/app/.../auth` URLs as user-confirmable links.
12. Record final links in the active project `memory.md` and `progress.md`; do not add private document URLs back into shared/public skills.

## Known CLI Compatibility Note

Installed `lark-cli` versions can differ. Check `lark-cli docs +create --help` when a command fails.

Observed forms across machines:

```bash
# Some installed versions expose --markdown:
lark-cli docs +create --api-version v2 --as user --title 'Title' --markdown @file.md

# Older/other observed versions accepted --content:
lark-cli docs +create --api-version v2 --as user --title 'Title' --content @file.md
lark-cli docs +update --api-version v2 --as user --doc '<doc-url>' --command append --content @file.md
lark-cli docs +fetch --api-version v2 --as user --doc '<doc-url>' --format pretty
```

Use the form supported by the installed binary; prefer the help output for flags, but trust validation errors from the actual command over stale notes.

### Hermes tool environment vs user's global `lark-cli`

Inside a Hermes tool process, `lark-cli` can auto-detect an Agent workspace and use a Hermes-specific config path rather than the user's normal shell/global config path. Do not confuse these. When the user explicitly refers to their global/local `lark-cli`, first verify with:

```bash
which lark-cli
lark-cli config show
```

If Hermes workspace auto-detection is getting in the way and the task is to use the user's global/local CLI, run `lark-cli` under a minimal environment tailored to the target machine instead of guessing config paths.

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
