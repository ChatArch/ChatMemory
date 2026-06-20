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

When the user wants to discuss plans, TODOs, or blueprints collaboratively:

1. Use `lark-cli` with user identity for human-facing Feishu docs.
2. Check auth first:

```bash
lark-cli auth status
```

3. If user identity is expired, re-authorize before creating/updating docs.
4. Prefer creating a focused child doc for each substantial topic.
5. Add the child doc link back to the main document.
6. Fetch the doc back after create/update and verify:
   - title is correct
   - body contains intended structure
   - main doc contains the child link when relevant
7. Record final links in the active project `memory.md` and `progress.md`.

## Known CLI Compatibility Note

Installed `lark-cli` may show `--markdown` / `--mode` in help, but this environment accepted:

```bash
lark-cli docs +create --api-version v2 --as user --title 'Title' --content @file.md
lark-cli docs +update --api-version v2 --as user --doc '<url>' --command append --content @file.md
lark-cli docs +fetch --api-version v2 --as user --doc '<url>' --format pretty
```

Use these known-good forms first unless the CLI is upgraded and behavior changes.
