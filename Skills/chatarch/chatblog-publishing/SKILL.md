---
name: chatblog-publishing
description: "Write and publish ChatBlog articles through the full ChatArch PR, preview, merge, production readback, and anti-AI-slop editorial gate."
version: 0.1.3
tags:
  - ChatArch
  - ChatBlog
  - publishing
  - writing
  - anti-ai-slop
---

# ChatBlog Publishing

Use when the user asks to write, publish, update, or turn research into a **ChatBlog** article.

## P0 delivery contract

When the user says “写 ChatBlog / 写一篇博客 / 整理成 ChatBlog”, treat a published ChatBlog URL as the default deliverable.

Default flow:

1. Create the Playground task container and keep research/progress there internally.
2. Use the official repository `ChatArch/ChatBlog` via its HTTPS origin.
3. Fetch the newest `origin/main` before editing.
4. Establish the article-specific editorial model before drafting: reader question, central thesis, what the reader should understand after reading, and the knowledge layout that makes the subject clear.
5. Write in the repository format with source-visible facts, public-safe URLs, and prose that passes the anti-AI-slop editorial gate below.
6. Open or update the PR.
7. Wait for CI and public Preview.
8. Verify the Preview URL over HTTP/browser readback.
9. Merge when checks are green and the content is ready.
10. Wait for production deploy and read back the final public URL.
11. Reply with bare clickable URLs: final production URL first when merged, then PR URL and Preview URL when useful.

Chat-facing delivery uses PR, Preview, and production URLs. Build success alone is not content readiness; a technically valid article that reads like generic AI slop is not ready to publish.

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

## Editorial model and anti-AI-slop gate

ChatBlog should not add another generic, padded AI article to the internet. The article must teach something specific: mechanism, practice path, evidence, trade-offs, failure boundary, and a reader-relevant conclusion.

### Before drafting

Write an internal expression map for the article before producing prose:

- **Reader question**: what concrete question brought the reader here?
- **Central thesis**: what is the article actually saying, in one direct sentence?
- **Knowledge layout**: what order makes the object easier to understand: mechanism first, cases first, architecture first, or practice path first?
- **Evidence model**: which claims need official docs, source code, release notes, issue/PR links, screenshots, or live readback?
- **Voice boundary**: should the piece be neutral technical explanation, opinionated analysis, practical field note, or product/tutorial writing?

Do not start from a generic blog skeleton. Recent ChatBlog posts can be inspected for repository format, evidence density, diagrams, and URL conventions, but do not copy warmed-up formulas or rhetorical openings from older posts.

### While writing

- Preserve information, not the AI draft's shape. Reorganize freely when that helps the reader, but do not invent facts, numbers, dates, names, citations, screenshots, benchmark results, or user stories.
- Make every section earn its place. If a paragraph could move unchanged to another project, company, product, or topic, cut it or replace it with a subject-specific fact, mechanism, consequence, or judgment.
- Lead with the point when setup adds nothing. Keep context, personal aside, or uncertainty only when it creates real context, tension, or author voice.
- Use concrete nouns and direct verbs. Prefer “the route streams SSE errors as HTTP 200 events” over “the solution significantly improves robustness”.
- Repeat the clearest term instead of cycling synonyms for style.
- Use active voice with real actors when possible.
- Preserve useful edge, uncertainty, or blunt judgment when the article is analysis/opinion. For reference docs and technical tutorials, plain neutral prose is already a human voice.
- Explain projects as evidence or case studies, not as a README feature dump or table of contents.
- End on the last concrete takeaway, limitation, or next action, not on a fake-profound slogan.

### Slop patterns that block content readiness

Treat these as content blockers before PR/Preview, not as optional polishing:

- **Importance inflation**: “pivotal”, “testament”, “vital role”, “evolving landscape”, “underscores significance”, “marks a shift”. State the fact that matters.
- **Promotional padding**: “robust”, “cutting-edge”, “seamless”, “empower”, “streamline”, “showcase”, “game changer”. Replace with mechanism, result, or delete.
- **Superficial analysis**: trailing clauses such as “highlighting”, “underscoring”, “reflecting”, “showcasing”. Explain the actual cause/effect or cut the clause.
- **Vague attribution**: “experts agree”, “studies show”, “industry reports suggest”, “widely regarded”. Name the source or mark the gap instead of smoothing it over.
- **Binary contrast shells**: “不是 X，而是 Y”, “not just X but Y”, “the question is not X, it is Y”. State Y directly unless the contrast itself is the evidence.
- **Throat-clearing and signposting**: “let’s dive in”, “值得注意的是”, “下面我们来”, “in this article”, “as you can see”, “the key point is”. Start with the point.
- **Faux-insight setups**: “what nobody tells you”, “the part everyone misses”, “真正重要的是”, “本质上”. Make the claim stand without the performance.
- **Colon reveals and lecture shells**: “The best part: it learns.” / “这个问题很简单：”. Use normal sentences except for real lists, labels, or quotes.
- **Robotic rhythm**: identical paragraph shapes, forced rule-of-three lists, stacked punchy fragments, headers over tiny sections, or every bullet starting with a bold label.
- **Synonym cycling**: rotating “agent / assistant / tool / system” when one clear term is correct.
- **Formatting slop**: decorative emoji headings, unnecessary bold emphasis, title-case headings where sentence case fits, bullets where prose would read better, and decorative em dashes used as a rhythm crutch.
- **Generic endings**: “in conclusion”, “the future is bright”, “exciting times ahead”, aphoristic mic-drop lines, or final paragraphs that merely recap the article.

### Final anti-slop review before build, PR, or merge

Run this review internally on the final article text before treating it as content-ready:

1. Read the whole article as a skeptical reader, not as its author.
2. Quote any suspect line and name the pattern; do not claim “AI wrote this”. The evidence is the named pattern and the line itself.
3. Ask:
   - What makes this still sound obviously AI-generated?
   - Did the rewrite add any fact, number, quote, date, source, or judgment not supported by the source material?
   - Which sentences fail the portability test?
   - Would the author/user recognize this as their intended voice and stance?
4. Fix structure first, evidence second, voice third, surface wording last. Do not treat a word blacklist as a substitute for a real editorial pass.
5. If the article cannot pass this gate without new facts, pause and gather sources instead of inventing specificity.

## Safety and evidence

- Use public-safe sources and URLs in the article and final reply.
- Prefer official docs, source, release pages, issue/PR URLs, and reproducible URL readback evidence.
- Keep PR/Preview/production status distinct: PR Preview URL for review, production URL for the merged article.
- Record PR URL, Preview URL, production URL, verification commands, and any anti-slop rewrite decision in the task `progress.md`.
- Do not expose API keys, proxy credentials, GitHub tokens, private URLs, Feishu IDs, local machine paths, or unreleased internal details in the article.

## Completion checklist

- [ ] Official `ChatArch/ChatBlog` repo was used.
- [ ] Branch/PR created or updated.
- [ ] Article-specific expression map exists in the task notes or draft plan.
- [ ] Claims are backed by public-safe sources or explicitly marked as gaps.
- [ ] The article explains mechanisms, practice path, evidence, trade-offs, and failure boundaries where relevant.
- [ ] The anti-AI-slop gate was run after drafting; structural and evidence problems were fixed before surface wording.
- [ ] The article avoids portable filler, inflated importance claims, vague attribution, fake insight setups, robotic rhythm, and generic endings.
- [ ] Public Preview URL verified.
- [ ] PR merged after green checks and content-ready review.
- [ ] Production URL verified.
- [ ] Final response includes bare clickable PR/Preview/production URLs, with production URL first after merge.

## Attribution

The anti-AI-slop editorial gate distills operating lessons from two MIT-licensed public writing skills, adapted for ChatBlog's public technical publishing workflow rather than copied wholesale:

- `blader/humanizer`: https://github.com/blader/humanizer
- `petergyang/no-ai-slop`: https://github.com/petergyang/no-ai-slop
