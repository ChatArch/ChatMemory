# Common Skills

跨项目通用共享 skills。这里放不绑定单一 ChatArch package、但会被多个项目/机器人/工作区反复使用的流程。

## Skills

### Hermes / agent platform

- `hermes-platform-development/` — Hermes 作为智能体载体的平台开发、配置、gateway、Feishu 卡片、SSH Mode 等总入口与关联。
- `hermes-slash-command-development/` — Hermes slash/gateway command、Feishu thread/card、`/ssh` command 开发流程。
- `hermes-ssh-target-configuration/` — Hermes SSH target registry、bindings、known_hosts 与安全配置。
- `hermes-terminal-env-profile/` — Hermes terminal tool 子进程环境 profile 配置与隔离。
- `hermes-environment-notes/` — Hermes 会话内运行 workspace 工具的环境注意事项。
- `hermes-lark-cli-binding/` — Lark CLI 与 Hermes Feishu/Lark app 绑定。

### Feishu / Lark collaboration

- `feishu-collaboration-documents/` — Feishu 协作文档和人机协作主文档流程。
- `feishu-document-writing/` — 飞书分析报告的信息设计、截图/图表、来源引用与发布后质量验证。
- `feishu-inline-image-delivery/` — Hermes 正常会话路径里发送/验证 Feishu inline image。
- `lark-cli-permission-authorization/` — lark-cli 权限申请、授权和 completion 流程。

### Workspace

- `workspace-task-kickoff/` — 稍复杂的调研、报告、设计、实现和外部交付在实质工作前创建规范 Project。
- `workspace-maintenance/` — outer workspace 结构维护、Project/Discussion item 生命周期、Discard/Archive 路由、文件移动与协议对齐。
- `workspace-structure-alignment/` — 将旧机器/旧 workspace 对齐到最新 `chatup workspace` 模板、ChatMemory shared skill 布局、Project/Discussion item 协议和项目 Markdown 规范。
