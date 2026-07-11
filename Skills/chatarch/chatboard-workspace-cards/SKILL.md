---
name: chatboard-workspace-cards
description: 为 ChatArch workspace 逐个 review Project 并维护中文 ChatBoard card.md；禁止用批量 ensure 代替人工/单项目 review。
version: 0.1.0
---

# ChatBoard Workspace Cards

当需要把 `~/Playground` 里的任务展示到 ChatBoard 时使用本流程。

## 核心原则

- `card.md` 是任务卡，不是机械索引；必须能帮助人快速判断任务是什么、做到哪、下一步是什么。
- 每个 Project 必须单独 review：读取该项目自己的 `PRD.md`、`progress.md` 和关键 `reports/`，再写 `card.md`。
- 可以并行使用多个 subagent，但必须遵守“一名 subagent 只 review 一个 Project”。
- 不要用 `chatboard catalog --ensure` 批量生成正式卡片；它只能作为临时扫描/调试工具，不能替代 review。
- 正式 `card.md` 默认用中文书写，方便用户和后续模型复核。
- 路径负责结构归属：`projects/`、`discussion/`、`archive/YYYY-MM-DD/`、`discard/`；frontmatter 负责语义元数据。
- 不再使用 `card.json`；不要恢复 JSON 兼容层。

## 推荐 frontmatter

```yaml
---
schema: chatboard.project_card.v1
id: projects-topic-mm-dd-name
title: 中文任务标题
area: project
stage: development
priority: 1
tags:
  - chatarch
  - chatboard
assets:
  prd: PRD.md
  progress: progress.md
  reports_dir: reports
links:
  repo: https://github.com/ChatArch/Repo
  feishu:
    - https://chatarch.feishu.cn/docx/...
---
```

字段说明：

- `id`：按 workspace 相对路径 slug 化，稳定即可。
- `title`：用中文写清任务名，不要只复制目录名。
- `area`：Project 下写 `project`；Discussion 写 `discussion`；Archive/Discard 由路径表达。
- `stage`：常用 `scaffold`、`prd`、`development`、`validation`、`complete`、`archived`、`discarded`。
- `priority`：只在确实需要突出时填写；当前活跃任务可用 `1`。
- `tags`：少而准，优先写产品/系统/能力域。
- `assets`：指向项目内稳定文档。
- `links`：只放关键外部链接；不要堆砌。

## 中文正文结构

建议使用：

```markdown
# 摘要

一句到一段说明这个任务为什么存在，以及它当前对 workspace 的意义。

## 当前状态

- 已完成什么。
- 还卡在哪里。
- 是否适合继续推进、归档或拆分。

## 下一步

1. 下一步最该做的动作。
2. 可选动作或后续增强。

## 备注

关键边界、风险、外部链接说明、review 判断依据。
```

## 逐个 review 流程

1. 选择候选 Project，优先最近几天活跃、当前讨论相关、或用户明确点名的项目。
2. 读取 `PRD.md`，确认目标、范围、非目标、完成标准。
3. 读取 `progress.md`，确认当前真实状态，不要只看 PRD 的理想状态。
4. 快速浏览 `reports/` 中最新或最关键的 1-3 个报告，确认成果和证据。
5. 判断 `stage`：
   - 只有目录/想法：`scaffold`
   - 已有 PRD 但缺少执行：`prd`
   - 正在推进：`development`
   - 已实现待验证：`validation`
   - 已完成且可归档：`complete`
6. 写中文 `card.md`，避免模板化空话。
7. 用 ChatBoard 读取验证：

```bash
cd ~/Playground/core/ChatBoard
. .venv/bin/activate
chatboard card show <card-id> --root ~/Playground
```

8. 如需开 Web：

```bash
cd ~/Playground/core/ChatBoard
. .venv/bin/activate
export CHATBOARD_WORKSPACE_ROOT=~/Playground
chatboard serve --host 127.0.0.1 --port 8000
```

## subagent 使用规则

可以一次派多个 subagent 并行，但每个 subagent 的任务必须像这样明确：

```text
只 review 这一个项目：~/Playground/projects/<path>。
读取 PRD.md、progress.md 和关键 reports。
返回或写入一个中文 card.md。
不要处理其他项目，不要批量生成。
```

父 agent 必须读回每个 subagent 生成的 `card.md`，检查：

- 是否为中文；
- 是否准确反映 progress 的当前状态；
- stage 是否合理；
- tags 是否少而准；
- 是否存在过时下一步；
- 是否把外部链接放进了正确字段。

## 禁止事项

- 禁止把 `chatboard catalog --ensure` 作为正式建卡流程。
- 禁止为大量项目生成只有标题和 TODO 的空卡。
- 禁止不读 progress 就把任务标为 complete。
- 禁止英文模板标题如 `# Summary` 混入正式中文卡片。
- 禁止把敏感 token、cookie、密码写进 `card.md`。
