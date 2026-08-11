---
name: chatboard-card-writing
description: Reviewer/board-maintenance guidance for writing card.md files for ChatArch Discussion items and optional Project board metadata. Use after the item exists; review PRD/progress/reports/Items and write a concise Chinese card for classification, indexing, or board use.
version: 0.1.0
reference:
  - workspace-structure-alignment: "baseline Project/Discussion item protocol; Discussion items include card.md"
---

# ChatBoard Card Writing

Use this skill when maintaining `card.md` metadata for an existing ChatArch workspace item.

Do not use this skill as the primary task execution workflow. Project authors should focus on `PRD.md`, `progress.md`, `reports/`, `scripts/`, and `playground/`. Discussion authors also maintain `card.md` because a Discussion is a classification/absorption node: its card explains the topic, why items are grouped there, and how `Items/` should be handled.

## Core Rules

- Treat `card.md` as required for Discussion items and optional reviewer-generated board metadata for Project items.
- For Project items, start from an existing Project with its baseline materials (`PRD.md`, `progress.md`, `reports/`, etc.), then write a card only during a reviewer, Discussion review, scheduled board-maintenance, or explicit board refresh pass.
- Create or update `card.md` directly as Markdown when needed; use a local card helper/CLI only if it is already available.
- Review the item before writing: read `PRD.md`, current `progress.md`, key files under `reports/`, and `Items/` when present.
- Default to Chinese for title, summary, current status, and next action unless the project itself is clearly English-only.
- Do not batch-generate final cards blindly. Bulk template creation is acceptable only as a temporary initialization step; final cards require per-item review.
- Do not change task lifecycle placement while writing a card. Moving to `discussion/`, `archive/`, or `.trash/` is a separate explicit action.

## When To Create Or Update

Create or update `card.md` when:

- creating or maintaining a Discussion item;
- a Discussion's absorbed `Items/` change or need clearer classification;
- the user asks to refresh board/card metadata;
- a scheduled card-maintenance job detects stale or missing card metadata;
- a Discussion item finishes and its `Items/` have been handled/cleared;
- a Project item should appear clearly in board/indexing views or has a changed status.

Skip card work when:

- the user is asking to execute the task itself;
- the task is still being drafted and `PRD.md` is not stable;
- you have not read enough task context to summarize honestly;
- the item is a transient scratch directory rather than a Project/Discussion item.

## Recommended Workflow

1. Identify the workspace item path.
2. If there is no `card.md`, create it directly as Markdown. If a local ChatBoard helper is already available, this command can initialize the file, but do not install/clone ChatBoard just for this step:

```bash
chatboard card ensure <project-or-discussion-path> --root <workspace-root>
```

3. Read the core task files:

```text
PRD.md
progress.md
reports/
```

4. Write or update the card with human-readable Chinese content.
5. Keep metadata concise and stable; avoid copying whole PRDs or reports into the card.
6. Verify that ChatBoard can still read the item if the local service or CLI is available.

## Suggested Content

A useful card should answer:

- 这是什么任务 / Discussion？
- 当前状态是什么？
- 最近完成了什么？
- 下一步是什么？
- 有哪些关键 tags / links / assets？

Keep the body short. The full task history belongs in `progress.md`; detailed analysis belongs in `reports/`.

## Frontmatter Guidance

ChatBoard recognizes `card.md` through simple YAML frontmatter followed by a short Markdown body. Keep these fields stable:

```yaml
---
schema: chatboard.project_card.v1
id: discussion-07-07-example
title: 示例 Discussion 标题
area: discussion
stage: review
tags:
  - chatarch
  - discussion
assets:
  prd: PRD.md
  progress: progress.md
  reports_dir: reports
---

# Summary

用 1-3 句话说明这个 Discussion 在消化什么、为什么把这些 Items 放在一起、当前判断是什么。
```

Recognition checklist:

- Put the file at the item root: `discussion/MM-DD-<topic>/card.md` or `projects/.../MM-DD-<project>/card.md`.
- Use `schema: chatboard.project_card.v1` unless the current ChatBoard code has changed.
- Use `area: discussion` for Discussion items; use `area: project` for Project items. The path is still the source of truth for lifecycle placement.
- Use a known `stage` such as `review`, `decision`, `postprocess`, `development`, `validation`, `complete`, `paused`, or `blocked`.
- Keep `assets.prd`, `assets.progress`, and `assets.reports_dir` relative to the item root.
- Put the human-readable summary in the Markdown body; do not hide the real summary only in tags.

## Discussion Items

Creating a Discussion means reviewing related projects/items, not just creating an empty folder.

Recommended Discussion review flow:

1. List the candidate related items that should be digested together.
2. For each related item without `card.md`, browse its `PRD.md`, `progress.md`, reports, and important files, then write a concise item card first.
3. For each related item with `card.md`, read the card first, then inspect the project files only as needed to verify status and context.
4. Create or update the Discussion's own `card.md` to explain the topic, absorption goal, item groups, current judgment, and next action.
5. Move or link absorbed items under `Items/` only after review confirms they belong together.

A Discussion item is still project-like, with an optional `Items/` directory while it is digesting other items.

When a Discussion completes:

- handle and clear `Items/` as appropriate;
- record the result in `progress.md` or a report;
- update `card.md` summary/status only after the task record has been updated;
- do not recursively put the Discussion into another Discussion unless the user explicitly asks for a meta-discussion.

## Pitfalls

- Do not treat `card.md` as a substitute for `PRD.md` or `progress.md`.
- Do not write cards from filenames only when PRD/progress/reports exist.
- Do not create polished cards for every old directory without review.
- Do not expose secrets, private tokens, raw credentials, or sensitive IDs in card body or links.
- Do not let card metadata override path truth: lifecycle area should primarily come from the directory path.
