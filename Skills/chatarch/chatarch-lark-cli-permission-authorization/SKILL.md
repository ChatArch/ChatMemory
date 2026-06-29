---
name: chatarch-lark-cli-permission-authorization
version: 0.1.0
description: ChatArch-specific pointer for lark-cli permission authorization. Use the Common lark-cli-permission-authorization skill for the canonical flow.
---

# ChatArch Lark CLI Permission Authorization

This ChatArch-series skill exists so ChatArch tasks can find the permission workflow quickly.

Canonical procedure lives in the Common skill:

```text
core/ChatMemory/Skills/common/lark-cli-permission-authorization/SKILL.md
```

## When To Use

Use this when a ChatArch task involves:

- creating or verifying Feishu/Lark docs with `lark-cli`
- missing scopes such as `docx:document`, `docx:document:create`, `docx:document:readonly`, or `docx:document:write_only`
- switching from bot-only setup to user authorization
- generating the correct user-facing permission link

## Critical Rules

- For user scopes, generate the link with `lark-cli auth login --scope ... --no-wait --json`.
- The correct user-facing link normally starts with `https://accounts.feishu.cn/oauth/v1/device/verify?`.
- Do not send `open.feishu.cn/app/.../auth?...` developer-console URLs as if they were user-confirmable verify links.
- Generate a QR code with `lark-cli auth qrcode` and show it to the user.
- After the user confirms authorization, complete the flow yourself with `lark-cli auth login --device-code <device_code>`.
- Send URLs raw, without backticks/code formatting.

## Typical ChatArch Doc Flow

1. Read Common `lark-cli-permission-authorization`.
2. Read Common `feishu-collaboration-documents`.
3. Read embedded `lark-doc` skills before writing XML docs.
4. Create/update the doc as user.
5. Fetch the doc back and verify structure/rich blocks.
6. Record final links in the active Playground project.
