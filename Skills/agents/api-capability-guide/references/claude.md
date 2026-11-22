# Claude API 的能力与接入

以下认知在 2026-11-22 对照官方文档和官方 SDK schema 核对。模型、工具版本及产品覆盖范围应在实际接入时刷新。

## 从模型目录读能力

用 `GET /v1/models` 或 `client.models.list()` 取得当前凭据可见的模型。HTTP 默认每页 20 条，用 `after_id`、`has_more` 和 `last_id` 继续分页。默认列出 active 与 deprecated，查询历史退休型号需显式指定 lifecycle。`GET /v1/models/{id}` 可取得型号信息并解析别名。[Models API](https://platform.claude.com/docs/en/api/models/list)

优先读取 `ModelInfo` 的 `line`、`capabilities`、`lifecycle`、`max_input_tokens`、`max_tokens` 和 `retires_at`。按 `line` 分组，保留未来新增系列。`capabilities` 可核对图片、PDF、结构化输出、thinking 和工具支持。工具支持为 true 时，还要核对所用工具版本与组织设置。`server_tools.code_execution` 表示接受服务端代码工具，顶层 `code_execution` 表示代码能调用请求中的其他工具。[模型总览](https://platform.claude.com/docs/en/about-claude/models/overview) · [官方 SDK schema](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/model_info.py)

当日模型总览把 Fable 5.2、Opus 5.5、Sonnet 5.5、Haiku 5.5 列为当前主模型，输入为文本和图片，输出为文本，支持 vision 与 tool use。完整目录还包含其他系列和旧型号。向用户列举时，分别展示具体 ID、官方系列、生命周期和已验证范围。[模型总览](https://platform.claude.com/docs/en/about-claude/models/overview)

## 接口与用途

| 能力 | 调用形态 | 说明与边界 |
| --- | --- | --- |
| 文本、代码、推理 | Messages API，支持流式 | 多轮消息、system、输出长度及 effort 按具体模型支持配置。 |
| 图片理解与 PDF | Messages 的 image / document content blocks | 可按文件类型使用 base64、URL 或 Files 引用，检查模型的 image_input / pdf_input。 |
| 结构化结果 | `output_config.format` 与 strict tool schemas | 用于字段抽取和程序消费。JSON 输出与 citations 等特性的组合需查兼容表。 |
| 自己的函数 | tool_use → 执行函数 → tool_result | 本地工具由应用执行，工具结果用原调用 ID 关联。 |
| 搜索、网页获取、代码执行 | 带版本的 server tools | 服务端执行相应工具，查模型、平台、组织和工具组合的支持情况。 |
| Prompt caching | `cache_control` 与 usage 的缓存字段 | 缓存重复前缀。会话保存和缓存分别配置，核对实际命中。 |
| 批处理 | Message Batches API | 用于非实时任务，提交后查询完成状态并按 custom_id 收集逐项结果。 |
| 文件复用 | Files API | 取得 file_id 后在支持的消息或工具中引用，使用范围依文件类型和接收方能力。 |

具体请求以对应文档为准。[Messages](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) · [Vision](https://platform.claude.com/docs/en/build-with-claude/vision) · [PDF](https://platform.claude.com/docs/en/build-with-claude/pdf-support) · [结构化输出](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) · [工具](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) · [缓存](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) · [Batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing) · [Files](https://platform.claude.com/docs/en/build-with-claude/files)

需要语音、生成图片或其他服务时，可以把对应服务注册为工具，并在说明中展示实际执行该步骤的 provider、模型、凭据来源和费用。向量检索可按官方 embeddings 指南选择专用服务，该指南介绍 Voyage AI 的接入。[Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)

## 会话与 Agent 执行位置

| 形态 | 谁执行与保存什么 | 接入时要核对 |
| --- | --- | --- |
| 自建 Messages loop + MCP | 应用调用模型、执行工具并持久保存历史，可包装成宿主的 MCP 工具 | 完整保存 content blocks，处理 tool_use、pause_turn 和 max_tokens，记录工具结果及实际用量。 |
| Messages threads | API 保存可续接的消息线程 | 保留自己的完整副本。线程为 append-only，从最新 response ID 续接，每个 response ID 可续接一次，过期或其他无法续接情况按官方恢复流程处理。 |
| Claude Agent SDK | SDK 使用 Claude Code CLI，提供工具循环、双向会话、自定义 MCP 工具和 hooks | 保存 session ID，核对 cwd、resume/fork 和权限。`allowed_tools` 是自动批准列表，禁用指定工具用 `disallowed_tools`。 |
| Claude Managed Agents | 配置 agent、environment、session，服务保存事件与运行状态并执行工具 | 可选云端或自托管环境。使用该产品的 session/events 机制续接，并核对当前 beta header、预算与会话状态。 |

Messages threads 的存储、工具执行和 Managed Agents 的环境分别核对。当前 Managed Agents 文档要求 `managed-agents-2026-04-01` beta header，提供文件操作、Bash、搜索/fetch 和 MCP 工具。[Message threads](https://platform.claude.com/docs/en/build-with-claude/message-threads) · [Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) · [官方 SDK 权限说明](https://github.com/anthropics/claude-agent-sdk-python#using-tools) · [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)

## 认证、额度与生态兼容

官方 SDK 可从 `ANTHROPIC_API_KEY` 读取 key。当前直接 HTTP 认证页使用 `Authorization: Bearer <key>`，仍兼容 legacy `x-api-key`，请求还需对应的 `anthropic-version`。对可跨 workspace 的凭据，按认证文档设置 `anthropic-workspace-id`。[认证](https://platform.claude.com/docs/en/manage-claude/authentication)

订阅附带 API credits 需领取到关联的 Claude Platform organization。官方覆盖表包含 Claude API、Managed Agents、Agent SDK 和 Console Playground，Claude Code 产品与其他云平台的用量另有适用范围。关联组织的 key 与 workspace 共用余额，赠送额度先消耗，再使用已购额度，赠送额度按账单周期到期。认证成功、额度覆盖和剩余余额分别确认。[订阅 API credits](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)

一般生态优先选择 Anthropic provider 与原生 Messages 协议。官方另提供 OpenAI SDK compatibility，使用 Claude 的 base URL、key 和模型，可用于比较模型。该层的字段兼容范围需单独检查，例如 function strict 被忽略、audio/file 输入会返回 400、prompt caching 不受支持。需要 PDF、完整 thinking、缓存等能力时采用原生 SDK。[OpenAI SDK compatibility](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)
