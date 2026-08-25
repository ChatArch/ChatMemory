---
name: workspace-task-kickoff
description: 为 Playground 中稍复杂的调研、分析、实现、评审、报告或外部交付建立规范 Project。用户说“开任务”“调研一下”“做完整分析/报告”“写飞书文档”或任务明显需要多步骤、素材、验证和持续记录时，在实质工作前触发。
version: 1.0.0
---

# Workspace Task Kickoff

## 核心规则

在工作区中，稍复杂的任务必须先有 Project，再开始实质调研、实现或外部交付。聊天不是任务记录，任务结束后补目录也不算遵循规范。

以下情况默认触发，不必等用户逐字说“开 Project”：

- 用户明确说“开任务”“建一个任务”“继续这个任务”；
- 要求调研一个技术、模型、产品、仓库或生态，并形成分析结论；
- 要求完整报告、对比报告、设计文档、飞书文档或带截图/素材的交付物；
- 任务包含三个以上步骤，或涉及源码、素材、测试、验证、外部链接与后续维护；
- 当前工作需要在多个会话间延续，或结论未来需要被再次查找。

只有明确的一次性小问题、简单命令查询、无需持久产物的简短问答可以保持 chat-only。不能因为用户没说“开任务”就把复杂调研留在聊天里。

## 启动顺序

1. 确认当前执行环境和工作区根目录。
2. 读取工作区 `AGENTS.md` 和它指向的项目规范。
3. 确认是否已有匹配 Project；有则复用，没有则按工作区命名规范创建。
4. 创建最低限度控制文件：
   - `PRD.md`：目标、范围、约束、交付物、完成标准；
   - `progress.md`：当前状态、已完成动作、下一步；
   - `links.md`：外部产物、在线文档、PR、报告等链接索引；
   - `.trash/`：需要清理时采用 move-first；
   - `reports/`、`scripts/`、`playground/`、`reference/` 按任务实际需要创建。
5. 把当前用户目标和硬边界写入 PRD，再开始调研、克隆、编码、生成素材或创建在线文档。
6. 每完成一项实质动作立即更新 `progress.md`，不要全部拖到会话结束。

## 共享环境入口

- Playground 根目录 `.env` 是工作区级共享环境入口，适合记录 Universe RC、代理启用函数、服务入口键名等跨 Project 复用约定。
- 需要 GitHub、X、外网 API、服务账号或机器环境信息时，先确认 `.env` 中是否已有对应键名、函数或占位约定，再决定如何启用环境；不要猜测机器私有路径或手写固定代理地址。
- 读取 `.env` 必须脱敏：可以确认变量/函数是否存在、用途是什么；不要把 token、cookie、password、proxy URL、API key、Authorization header、具体账号路径等值写入 PRD、progress、reports、日志或回复。

## Playground 默认结构

当工作区规范采用 `projects/` 时：

```text
<WORKSPACE_ROOT>/projects/MM-DD-<task-name>/
  PRD.md
  progress.md
  links.md
  .trash/
  reports/
  playground/
  reference/
```

报告和飞书源稿进入 `reports/`，截图与图表进入 `reports/assets/`，原始采集与实验输出进入 `playground/` 或 `reference/`。不要把任务文件散落在工作区根目录、用户主目录或 `/tmp`。

## 调研与飞书交付

调研型 Project 至少记录：

- 调研对象、问题和时间范围；
- 第一方、System Card、API 文档和外部评测等来源层级；
- 原始资料与图片来源；
- 分析报告源文件；
- 外部交付链接与验证结果。

创建飞书文档或其他外部产物时：

- 先在 Project 内完成报告源和素材整理；
- 把在线链接写入 `progress.md`、Project 根目录 `links.md` 和 `reports/links.md`；
- 按工作区协作规范回链主文档；
- 回读验证在线内容后才能宣布完成。

## 恢复规则

如果调研或实现已经开始，但 Project 不完整：

1. 立即停止继续扩展；
2. 确认正确工作区和 Project 路径；
3. 补齐 PRD、progress 和必要目录；
4. 把已经获得的来源、结论、素材和临时文件迁入 Project；
5. 在 `progress.md` 记录恢复动作，然后从 Project 中继续。

## 验证

开始实质工作前确认：

- Project 路径位于正确工作区；
- `PRD.md`、`progress.md` 和 `links.md` 已存在；
- PRD 反映用户当前目标与边界；
- 报告、素材、实验和外部链接都有明确落点；
- 后续动作不再依赖聊天历史作为唯一事实源。
