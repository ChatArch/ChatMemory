---
name: claude-code-worker-orchestration
description: "Use when an agent needs a resumable agentic subagent billed to an API key or subscription API credits: inside Claude Code use a Messages-API agent loop behind MCP tools; elsewhere claude -p --bare with session ids, resume/fork."
version: 0.2.0
reference:
  - hermes-external-agent-cli-orchestration: "Hermes 调用外部 CLI 时的 terminal/process 托管、进度监督和验收规则"
  - openai-api-worker-orchestration: "任务指定 OpenAI API key 时使用原生 Agent session 和 resume"
---

# Claude Code Worker Orchestration

这个 skill 讲的是：把 Claude Code 作为一个外部 worker（相当于 subagent）来调用，计费走 API key，并且能多轮续接（resume）。调用方负责派活和验收，worker 负责执行。

共享 skill 必须与主机无关。key 文件路径、包装脚本路径、会话登记文件等本机信息，放在 workspace 本地 skill（`skills/local/`）或任务记录里。下文用 `<key-file>`、`<workdir>`、`<session-id>` 这类占位符。

如果任务指定 OpenAI / ChatGPT 的 API key，使用 [OpenAI API Agent skill](../openai-api-worker-orchestration/SKILL.md)，它通过官方 Agents API 的 session ID 续接任务。

## 先判断调用方（最重要）

Claude Max / Ultra / Team 订阅附带的 API 额度**不覆盖 Claude Code 用量**。一次 `claude -p` 算不算 Claude Code 用量，取决于它是从哪里启动的：

| 调用方 | `claude -p` + API key 的结果 | 该用什么 |
|---|---|---|
| Claude Code 会话（桌面 App、IDE、终端里的交互式 `claude`）通过 Bash 启动 | 子进程继承 `CLAUDE_CODE_ENTRYPOINT`，被算作 Claude Code 用量。如果组织里只有订阅额度，会返回 `Credit balance is too low`（2026-11-22 从桌面 App 实测；终端交互式 `claude` 未实测，按同一机制处理） | 下一节的“Messages API 子代理”，或者用组织里自己充值的额度 |
| Codex、Hermes、cron、普通脚本、你自己终端里的命令 | 按官方说明属于额度覆盖范围 | 本 skill 的 `claude -p` worker 模板 |
| GitHub Action、IDE 插件 | 算 Claude Code 用量 | 同第一行 |

**不要**通过删除或改写 `CLAUDE_CODE_ENTRYPOINT`、`CLAUDECODE` 等变量，来让 Claude Code 里启动的进程“看起来”像外部调用。这是在向计费系统谎报来源，违反额度条款。

如果调用方本身就是 Claude Code，真正可行的办法是：要么接受这笔用量走订阅或付费额度，要么把子任务交给直接调 Messages API 的工具。

## Claude Code 里的首选：Messages API 子代理（最常用）

日常的子任务大多是 agentic 的：调研、读代码找答案、改文件、多轮追问。在 Claude Code 里要让这类子任务花 API 额度，做法是**自己写 agent loop**：调 Messages API → 执行本地工具 → 把结果交回模型 → 再调 Messages API，直到模型给出结论。因为每一步都是直接调 Messages API，所以算 API 用量，和进程是谁启动的无关。再把它包成本地 MCP server 的几个工具交给 Claude Code。2026-11-22 实测可用。

需要的组成部分：

| 部分 | 要点 |
|---|---|
| 模型 | 默认 Opus 一档（`claude-opus-5-5`），调用方可以选 Fable、Sonnet、Haiku；effort 做成参数 |
| 工具 | Anthropic 定义的 `text_editor_20250728`（view / create / str_replace / insert）；只在用户明确授权时加 `bash_20250124`；自定义的 glob、grep；服务端的 `web_search` / `web_fetch`（较新的模型用 `_20260209` 版本，Haiku 用基础版本） |
| 权限 | 分 read / write / full 三档。读限制在允许的根目录内，写限制在工作目录内；密钥类文件名一律拒绝；bash 的环境里不放 key；改文件前先备份 |
| 历史 | 只追加不修改。`response.content` 原样保存（包括 thinking 块、fallback 块，空的 thinking 块也要保留），否则续接时 preserved thinking 的检查会失败。处理 `pause_turn`（把这一轮追加进历史后再发一次）和 `max_tokens`（让它接着写） |
| 续接 | 每个任务是一个线程（一个目录：历史、进度、结果、备份），线程 id 就是续接用的 id。如果上次在执行工具时被中断，续接前要给没有结果的 `tool_use` 补上“已中断”的 `tool_result` |
| 运行 | 在独立后台进程里跑（不依赖 MCP server 是否还活着），用 SIGTERM 让它在这一轮 API 调用结束后停下 |
| 费用 | 用顶层 `cache_control` 开自动缓存，续接时便宜很多；每次运行和每天都设上限，到上限就暂停，之后可以加预算续接 |
| MCP 工具 | `agent_start`（立刻返回线程 id）、`agent_wait`（最多等 N 秒，返回状态、进度和结论）、`agent_send`（追问、纠偏、继续、加预算）、`agent_status`、`agent_stop`；在 server 的 instructions 里写明什么时候该用它 |
| 终端 | 同一个实现再配一个命令行，包括交互式 `chat`，这样订阅额度用完时也能直接和子代理对话 |

它和 Claude Code 自带的子 agent 的区别：它花的是 API 额度；线程能跨会话续接；但工具只是一个精简集合，没有 hooks、skills，也不能再开子 agent。`full` 模式下的 bash 直接在本机执行，不在沙箱里，所以派活时要给它一个范围明确的工作目录。

派活方的规则和后文一样：任务说明要自包含；结论只是子代理的自述，汇报完成前要自己核对；把线程 id 记进 `progress.md`。

## 认证：强制只用 API key

用 `--bare`。在 bare 模式下，Anthropic 认证只认 `ANTHROPIC_API_KEY` 或 `--settings` 里的 `apiKeyHelper`，不会读 OAuth 和钥匙串，所以 key 缺失时会直接报错，不会悄悄退回订阅登录。

推荐用 `apiKeyHelper` 而不是环境变量，因为这样 key 不进 worker 的环境，worker 里执行的 Bash 命令拿不到它：

```bash
HELPER="sed -E 's/^(export +)?ANTHROPIC_API_KEY=//' <key-file>"
claude -p --bare --settings "{\"apiKeyHelper\": \"$HELPER\"}" ...
```

启动时把 `ANTHROPIC_API_KEY` 和 `ANTHROPIC_AUTH_TOKEN` 从子进程环境里删掉。不要把 key 写进 prompt、日志或 shell rc 文件；不要打印 key 文件。

`--bare` 也会跳过 hooks、auto-memory 和 CLAUDE.md 自动发现。需要的上下文要显式传入：
- `--add-dir <workdir>`：加载该目录的 CLAUDE.md / AGENTS.md 规则
- `--append-system-prompt-file <file>`：追加系统提示
- `--mcp-config <json>`：给 worker 配 MCP server

## 会话与 resume

**resume 要不要指定 id？** `--continue` 不用 id，但它取的是“当前目录里最近的一个会话”。只要同一目录里还跑过别的会话（另一个 worker、一次 fork，或者你自己手动跑的 `claude`），它就会接错。实测：fork 之后执行 `--continue`，接上的是 fork 出来的会话，而不是原会话。所以：

1. **新会话时预先分配 id**：`--session-id "$(uuidgen | tr A-Z a-z)"`。在启动之前就把 id 记进 `progress.md` 或登记文件，这样即使进程崩溃或超时，也能找回这个会话。
2. **续接用 `--resume <session-id>`**：id 不变，历史接在同一个 transcript 后面，存放位置是 `~/.claude/projects/<cwd-slug>/<session-id>.jsonl`。
3. **换个做法试用 `--resume <session-id> --fork-session`**：复制已有历史开一个新 id，原会话不动。新 id 从输出 JSON 的 `session_id` 里读。
4. **只跑一次、不再续接**：用 `--no-session-persistence`。
5. **工作目录**：续接时用和第一次相同的 `<workdir>`。在 2.1.323 版本里，换目录 resume 仍然能找到会话，但工具会在新目录里运行，容易改错地方。
6. `-n/--name` 起的名字也能用来 `--resume <name>`，但名字可能重复，自动化场景里优先用 id。

`--output-format json` 输出的结果里要读这些字段：`session_id`、`is_error`、`result`、`total_cost_usd`、`terminal_reason`。认证失败或额度不足也会以 `is_error: true` 返回，所以一定要检查 `is_error`，不要只看进程退出码。

## 命令模板

```bash
SID=$(uuidgen | tr A-Z a-z)              # 先记下 SID
HELPER="sed -E 's/^(export +)?ANTHROPIC_API_KEY=//' <key-file>"
cd <workdir>
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN \
  claude -p --bare --settings "{\"apiKeyHelper\": \"$HELPER\"}" \
  --add-dir "$PWD" --output-format json \
  --model claude-sonnet-5-5 --max-budget-usd 1 --max-turns 30 \
  --permission-mode acceptEdits --allowedTools "Read,Grep,Glob,Edit,Bash" \
  --session-id "$SID" "<自包含的任务说明>" < /dev/null

# 追问或纠偏：同一个 SID
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN \
  claude -p --bare --settings "{\"apiKeyHelper\": \"$HELPER\"}" \
  --add-dir "$PWD" --output-format json --max-budget-usd 1 \
  --resume "$SID" "<追问>" < /dev/null
```

`< /dev/null` 不是可有可无：没有它，非终端环境里的 `claude -p` 会先等 3 秒看有没有管道输入。

权限模式：只读调研用 `--permission-mode plan`；需要改文件用 `acceptEdits`，并配合 `--allowedTools` 收窄工具范围。只有在没有网络的沙箱里才用 `bypassPermissions`。

预算：每次调用都加 `--max-budget-usd`；长任务再加 `--max-turns`。

## 派活与验收

- prompt 要自包含：仓库或目录、范围、禁止做的事、验收标准、最后要汇报什么。
- 多个 worker 并行时，每个 worker 用独立的 worktree 和 session id，不要让两个 worker 同时改同一个 checkout。
- worker 的输出只是它的自述。汇报成功之前，调用方要自己核对：`git status`、`git diff`、测试结果，或者它声称生成的文件。
- 把 session id、workdir、prompt 路径、每次花费记进任务的 `progress.md`。下一轮用 id 续接，不要开新会话重做，避免重复产生副作用。

## 常见坑

- 在 Claude Code 里启动 `claude -p`，期望花订阅附带的 API 额度：会被拒（`Credit balance is too low`），见第一节。
- 没加 `--bare`，key 又刚好缺失：会悄悄退回订阅登录，用掉订阅额度。
- 依赖 `--continue`：同一目录里有多个会话时会接错。
- 只看退出码：额度或认证错误会在 JSON 里以 `is_error` 返回。
- 把 `ANTHROPIC_API_KEY` 写进全局 shell 配置：交互式 Claude Code 也会改用这个 key，然后报额度不足。
