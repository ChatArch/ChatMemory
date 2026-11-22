# OpenAI API 的能力范围

资料核对日期为 2026-11-22。接入时重新核对模型、端点和关闭公告，模型列表用于记录当前项目 key 的可见 ID。

## 模型、接口和工具

`GET /v1/models` 可取得 key 可见清单。同一系列常同时出现滚动名称和日期快照，目录展示它们之间的版本关系。模型的输入形式、工具支持、推理参数、价格、上下文与生命周期需要从模型页核对。[模型目录](https://developers.openai.com/api/docs/models)

| 能力 | 主要接口 | 典型应用与边界 |
| --- | --- | --- |
| 文本、代码、推理、图像理解 | Responses；部分型号也支持 Chat Completions | 问答、编程、研究、图片问答。按型号核对输入及参数支持。 |
| 结构化数据与函数调用 | Responses 的 schema / function tools | 抽取、分类、业务流程。自定义函数由应用执行并回传结果。 |
| 图像生成与编辑 | Images generations / edits | 文章配图、产品图、参考图编辑。分别验证生成与编辑，尺寸和质量选项按型号。 |
| 音频理解与生成 | Audio speech / transcriptions；音频型号可走 Chat Completions | 朗读、转写、音频问答。分别核对音频输入输出与响应格式。 |
| 实时语音、流式转写、翻译 | Realtime / Live 的对应流程 | 对话、连续字幕、同传。WebRTC 和 WebSocket 的连接及事件协议需要分别实现。 |
| 语义向量 | Embeddings | RAG、检索、聚类与推荐。保存 embedding 型号及维度，以便维护索引。 |
| 内容分类 | Moderations | 文本或图片的分类与分数，作为应用审核流程的输入。 |
| 搜索和文件检索 | web_search / file_search 等工具 | 联网资料核对、文档问答。工具的费用、引用和存储需要随结果呈现。 |
| 非实时批处理 | Batch | 批量抽取与评测。检查整批状态，也检查每条响应的实际完成状态。 |

来源分别见 [Responses](https://developers.openai.com/api/docs/guides/text)、[工具](https://developers.openai.com/api/docs/guides/tools)、[图像](https://developers.openai.com/api/docs/guides/image-generation)、[音频](https://developers.openai.com/api/docs/guides/audio)、[Live](https://developers.openai.com/api/docs/guides/live)、[Embeddings](https://developers.openai.com/api/docs/guides/embeddings)、[Moderation](https://developers.openai.com/api/docs/guides/moderation)。

## 对话与 Agent

Responses 可以用 `previous_response_id` 关联多轮。应用选择自己维护历史时，保留完整输出及工具调用结构，并按 wire schema 序列化。长对话的历史输入仍参与计费。[对话状态](https://developers.openai.com/api/docs/guides/conversation-state)

Agents API 用持久 session 保存配置、对话与工作状态，空闲时追加输入开启新 turn，运行时追加输入会纠偏当前任务。自定义函数需要调用方处理 required_actions。OpenAI-hosted 环境可运行云端代码；本机材料通过上传或提供工具接入。Agents SDK 的循环与工具执行则由部署该 SDK 的应用承载。[Agents API](https://developers.openai.com/api/docs/guides/agents-api/quickstart) · [Agents SDK](https://openai.github.io/openai-agents-python/)

2026-11-22 的项目实践中，Agents 创建和更新拒绝了参考文档中的 `spend_control`。实现应以接口实际接受的配置为准，费用控制的验收需要查看服务端返回。持久会话、幂等提交和工具结果恢复的执行细节见对应 Agent skill。

## 生态与认证

官方 SDK 通常用 `OPENAI_API_KEY`，也可由程序显式传入 key。使用兼容客户端时，核对它发送的是 Responses、Chat Completions、Images 还是 Audio 请求，选用支持该接口的型号。Realtime 浏览器端采用后端签发的短期凭据，长期 key 保留在服务端。[快速入门](https://developers.openai.com/api/docs/quickstart) · [WebRTC](https://developers.openai.com/api/docs/guides/realtime-webrtc)

ChatGPT Pro / Business 的 API credits 需要关联到符合条件的 API organization。额度的领取、到期和扣费顺序查看组织 Billing。福利文档涵盖 Responses、Agents 及工具，Codex 的 API-key 用量另有明确排除条款。以官方当期规则和实际账单核对具体用法。[API credits](https://developers.openai.com/api/docs/guides/chatgpt-api-credits)

兼容式 TTS 模型 `gpt-4o-mini-tts`、`tts-1`、`tts-1-hd` 当前有 2027-01-06 关闭公告。迁移目标与调用流程需要一起更新，现有 `/audio/speech` 配置要结合 Realtime 的接入方式调整。[TTS 迁移说明](https://developers.openai.com/api/docs/guides/text-to-speech)
