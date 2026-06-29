---
name: feishu-collaboration-local-conventions
description: Local/private placeholders for this machine's Feishu collaboration document and group conventions. Fill per deployment; do not publish concrete tenant links in shared skills.
version: 0.1.0
---

# Feishu Collaboration Local Conventions

This local skill is the place for machine-, tenant-, or team-specific Feishu/Lark links and chat conventions. Keep the public `feishu-collaboration-documents` skill generic.

## Fill These Per Machine

Replace the placeholder values below after confirming the local workspace convention with the user.

- Main collaboration document URL: `https://example.feishu.cn/docx/LOCAL_MAIN_DOC_TOKEN`
- Main document title: `<LOCAL_MAIN_DOC_TITLE>`
- Section for child task links: `<LOCAL_TASK_LINK_SECTION>`
- Section for daily brainstorm logs: `<LOCAL_BRAINSTORM_SECTION>`
- Notification chat name or ID: `<LOCAL_CHAT_NAME_OR_OC_ID>`
- Preferred app/profile for doc operations: `<LOCAL_LARK_CLI_PROFILE>`
- Preferred app/profile for message mentions: `<LOCAL_HERMES_OR_BOT_PROFILE>`

## Local Bot ID Lookup Notes

Use `lark-cli` to discover current group bot IDs rather than blind `@` tests:

```bash
lark-cli doctor
lark-cli profile list
lark-cli im +chat-list --as user --sort active_time --page-size 20 --format json
lark-cli im chat.members bots --as user --chat-id '<oc_chat_id>' --format json
```

Remember that Feishu/Lark `ou_*` IDs are app-scoped. Store mappings with the app/profile that produced them. Example placeholder:

```text
<APP_OR_PROFILE_NAME> / <CHAT_NAME>:
- <BOT_DISPLAY_NAME>: ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

If this machine has a known Hermes mention mapping, record it here rather than in the public skill.
