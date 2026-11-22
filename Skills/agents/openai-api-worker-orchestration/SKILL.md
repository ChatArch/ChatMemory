---
name: openai-api-worker-orchestration
description: 用 OpenAI API key 或 ChatGPT 订阅附带的 API credits 派发 agentic 子任务，配置本地函数或云端 sandbox，并以同一个 Agents API session ID 续接、恢复和验收。适用于从 Claude Code、Codex、Hermes 或脚本调用可持久化的 GPT Agent。
---

# OpenAI API Agent

默认用官方 Agents API 的持久会话。创建一次，保存返回的 session ID；之后把追问发到同一个会话。API key 从调用进程的环境或本机配置读取，留在运行器中。任务说明写清工作目录、允许的操作和验收方式。可运行的包装器与本机密钥位置由 workspace-local skill 提供。

## 运行与 resume

| 操作 | 接口与判定 |
| --- | --- |
| 开始 | `POST /v1/agents/sessions`，传 `agent`、`environment`、`input`。保存返回的 `id`。即使 `stream=false`，任务仍异步执行。 |
| 等待 | 读取 session 的 `required_actions` 并处理工具请求，或订阅事件流。结合 root turn 的完成、失败或取消状态取结果。 |
| 追问 | `POST /v1/agents/sessions/{id}/events`，事件为 `agent.session.input.message`。空闲时开启新 turn，运行中会纠偏当前 turn。 |
| 重新接管 | 新进程读取原 session ID、工作目录与未提交的工具结果，继续查状态或提交输入。会话的对话状态由 API 保存。 |
| 取消 | 向同一 events 接口发送 `agent.session.input.cancel`，再查最终状态。 |

Agents 请求需要 `OpenAI-Beta: agents=v1`；key 要有 `api.agents.read`、`api.agents.write`、`api.responses.write`。开始前可先列模型及会话以检查认证。普通 Responses 调用也可以用 `previous_response_id` 关联上下文，采用它做 Agent 时需由调用方执行工具循环。根据任务选用已可用的接口。[官方 Agent 入门](https://developers.openai.com/api/docs/guides/agents-api/quickstart) · [会话续接](https://developers.openai.com/api/docs/guides/agents-api/sessions)

## 工具与执行位置

`environment.type=none` 适合保留本机目录的任务。在 `agent.tools` 定义函数和 JSON Schema，由运行器读取待处理的 `function_call`，执行后发送 `agent.session.input.tool_result`，带原 `turn_id`、`call_id` 和结果。读取待处理动作时以 `required_actions` 为准。本机包装器可暴露受工作目录约束的读写工具。

`environment.type=openai_hosted` 让 Agent 在云端 sandbox 运行代码和操作环境文件。需要本机材料时，显式上传或提供对应工具。把项目规则和必要上下文写入任务或配置中的 instructions。[函数工具](https://developers.openai.com/api/docs/guides/agents-api/tools/functions) · [托管环境](https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted)

## 恢复与验收

- 每条逻辑输入保存一个 idempotency key，重试复用原 key。创建请求也保存请求 ID；连接中断后先找原会话和请求记录。
- 按 session、turn、call ID 保存工具执行结果，再送回 API。若工具可能已产生副作用但没有保存结果，先检查实际文件或外部状态，再决定如何恢复。
- 把 session ID、工作目录、用量和结果位置记进任务的 `progress.md`。运行器在本机用锁避免两个进程重复处理同一工具请求。
- 验收看 root turn 的 `completed` 与实际输出。抽查工具结果、文件 diff 和适用测试。仅 session 空闲不足以判断成功。
- 验证 resume 时，第一轮让 Agent 读取一个临时标记，关闭调用进程，第二轮用原 ID 根据记忆写出该标记。检查同一 session 有两个已完成 root turns，第二轮的写入与输入相符。

## 额度与接口差异

ChatGPT Pro / Business 的 API credits 需领取到关联的 API organization，key 应属于该组织。文档将 Responses、Agents 及其工具费用列入覆盖范围，实际领取情况、剩余余额与到期日看 Billing。赠送额度用完后，有已购余额的组织会继续消耗已购额度。[官方额度规则](https://developers.openai.com/api/docs/guides/chatgpt-api-credits)

2026-11-22 实测 Agents API 可新建会话，但创建及更新均拒绝文档中的 `spend_control` 参数。使用前核对当前接口，只有服务支持时才把它当会话费用上限。已传入费用上限而失败的请求，应原样报错。Responses 的 `max_output_tokens` 可限制单次生成长度。每轮记录 API 实际 usage，账单以组织 Usage 为准。
