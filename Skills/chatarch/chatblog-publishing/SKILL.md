---
name: chatblog-publishing
description: "Write and publish ChatBlog articles through the full ChatArch PR, preview, merge, and production-readback flow."
version: 0.1.0
tags:
  - ChatArch
  - ChatBlog
  - publishing
---

# ChatBlog Publishing

Use when the user asks to write, publish, update, or turn research into a **ChatBlog** article.

## P0 delivery contract

When the user says “写 ChatBlog / 写一篇博客 / 整理成 ChatBlog” and does **not** explicitly say “只要草稿 / 本地草稿 / 先别发 PR”, the deliverable is a real published ChatBlog link, not a local draft.

Default flow:

1. Create the Playground task container and keep research/progress there.
2. Use the official repository `ChatArch/ChatBlog` via its HTTPS origin.
3. Fetch the newest `origin/main` before editing.
4. Write the article in the repo format, with source-visible facts and Chinese prose unless told otherwise.
5. Open or update the PR.
6. Wait for CI and public Preview.
7. Verify the Preview URL over HTTP/browser readback.
8. If checks are green and there is no content blocker, merge without asking for an extra confirmation.
9. Wait for production deploy and read back the final public URL.
10. Reply with the PR URL, Preview URL, and final production URL; put the final link first when the article has merged.

Do **not** stop at `reports/chatblog-draft.mdx` when the user asked for ChatBlog. A task-local draft is only an intermediate artifact.

## Review surface

If the user wants iterative editing, give the PR/Preview link. The user can review the rendered page there. Do not make them inspect local files with no clickable link.

If the user explicitly asks for “只写草稿”, “不要 PR”, or “先在本地整理”, then stop at the requested draft stage and state that it is not yet a ChatBlog publication.

## Safety and evidence

- Do not publish private hostnames, credentials, Feishu/Lark private IDs, local absolute paths, or screenshots containing secrets.
- Prefer official docs, source, release pages, issue/PR links, and reproducible readback evidence.
- Keep PR/Preview/production status distinct: a PR Preview is not production, and a local draft is neither.
- Record PR, Preview, production URL, and verification commands in the task `progress.md`.

## Completion checklist

- [ ] Official `ChatArch/ChatBlog` repo was used.
- [ ] Branch/PR created or updated.
- [ ] Public Preview verified.
- [ ] PR merged after green checks unless a content blocker existed.
- [ ] Production URL verified.
- [ ] Final response includes clickable PR/Preview/production links, with no code-block wrapping.
