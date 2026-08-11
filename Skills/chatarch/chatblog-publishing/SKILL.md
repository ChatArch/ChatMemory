---
name: chatblog-publishing
description: "Write and publish ChatBlog articles through the full ChatArch PR, preview, merge, and production-URL readback flow."
version: 0.1.2
tags:
  - ChatArch
  - ChatBlog
  - publishing
---

# ChatBlog Publishing

Use when the user asks to write, publish, update, or turn research into a **ChatBlog** article.

## P0 delivery contract

When the user says “写 ChatBlog / 写一篇博客 / 整理成 ChatBlog”, treat a published ChatBlog URL as the default deliverable.

Default flow:

1. Create the Playground task container and keep research/progress there internally.
2. Use the official repository `ChatArch/ChatBlog` via its HTTPS origin.
3. Fetch the newest `origin/main` before editing.
4. Write the article in the repo format, with source-visible facts and Chinese prose according to the request.
5. Open or update the PR.
6. Wait for CI and public Preview.
7. Verify the Preview URL over HTTP/browser readback.
8. Merge when checks are green and the content is ready.
9. Wait for production deploy and read back the final public URL.
10. Reply with bare clickable URLs: final production URL first when merged, then PR URL and Preview URL when useful.

Chat-facing delivery uses PR, Preview, and production URLs.

## URL output contract

When the user asks for “地址 / 链接 / URL”, they mean a URL they can open from Feishu/chat.

- Give complete bare clickable URLs directly.
- Put the production article URL first after merge.
- Include the PR URL and Preview URL during review or as supporting evidence.
- Keep internal workspace details in task records.
- Report each stage by its public URL once available.

## Delivery modes

- **Publication mode**: default for ChatBlog writing and research-to-article tasks; complete PR, Preview, merge, production deploy, and production URL readback.
- **Review mode**: when the user asks for PR review, provide the PR Review/Preview URL and continue from that review surface.
- **Draft mode**: when the user asks for a draft-only artifact, state the current artifact stage clearly and continue to publication when asked.

## Safety and evidence

- Use public-safe sources and URLs in the article and final reply.
- Prefer official docs, source, release pages, issue/PR URLs, and reproducible URL readback evidence.
- Keep PR/Preview/production status distinct: PR Preview URL for review, production URL for the merged article.
- Record PR URL, Preview URL, production URL, and verification commands in the task `progress.md`.

## Completion checklist

- [ ] Official `ChatArch/ChatBlog` repo was used.
- [ ] Branch/PR created or updated.
- [ ] Public Preview URL verified.
- [ ] PR merged after green checks and content-ready review.
- [ ] Production URL verified.
- [ ] Final response includes bare clickable PR/Preview/production URLs, with production URL first after merge.
