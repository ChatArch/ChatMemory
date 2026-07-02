---
name: hermes-platform-development
description: Hermes 作为智能体载体的平台开发、配置、gateway、Feishu 卡片、SSH Mode 与运行验证入口。
version: 0.1.0
reference:
  - hermes-slash-command-development: "Hermes slash/gateway command、Feishu thread/card、/ssh command 开发模式"
  - hermes-ssh-target-configuration: "Hermes SSH target registry、bindings、known_hosts 与安全配置"
  - hermes-terminal-env-profile: "Hermes terminal tool 环境隔离与项目/dev profile 配置"
  - hermes-environment-notes: "Hermes 会话内运行 workspace 工具的通用环境注意事项"
  - feishu-inline-image-delivery: "Feishu/Hermes 正常消息投递路径与线程内验证经验"
---

# Hermes Platform Development

## When to use

Use this shared skill when a task touches Hermes itself as the agent platform/carrier, including:

- Hermes Agent configuration, runtime setup, gateway, model/tool/provider behavior, profiles, cron, plugins, or skills.
- Hermes source development in an isolated checkout.
- Gateway or messaging-platform behavior, especially Feishu/Lark cards, callbacks, thread/session routing, media delivery, approvals, and busy/interrupt UX.
- SSH Mode / `/ssh` / `ssh_mode` model-facing backend switching.
- Updating Hermes-related reusable procedures or organizing Hermes knowledge in shared skills.

Normalize voice/transcription variants that refer to the agent runtime to **Hermes** before writing task files, code, tests, PR text, or user-visible validation.

## Workspace boundary for this user's Playground

1. Confirm backend first with `ssh_mode.status` when SSH could matter.
2. Work in local `<WORKSPACE_ROOT>` unless the user explicitly selects an SSH target.
3. Read `<WORKSPACE_ROOT>/AGENTS.md` before creating or switching tasks.
4. Put task records under `<WORKSPACE_ROOT>/projects/hermes/<MM-DD-task>/`.
5. For Hermes source changes, do not edit the running checkout at `<HERMES_HOME>/hermes-agent` directly. Use a task-local isolated clone under the task `playground/`, or an explicitly approved isolated checkout.
6. Before editing, record source path, branch, HEAD, remote, and clean/dirty status in `progress.md`.
7. Do not push, open PRs, merge, tag, release, restart the live gateway, or write runtime config/SSH registry unless the user explicitly approves that side effect.

## Required companion knowledge

For active Hermes work, load or consult the relevant Hermes runtime skills/docs in the active Hermes profile when available:

- `hermes-agent` — authoritative Hermes CLI/config/source contributor reference; official docs are the final source of truth.
- `hermes-slash-command-development` — slash command, gateway command, Feishu thread/card, `/ssh`, and session-scoped backend command patterns.
- `test-driven-development` — production behavior changes should start with RED tests.
- Local machine-only SSH operations may have a separate `local/hermes-ssh-mode-operations` skill; do not promote machine-specific hosts, key paths, or branches into this shared skill.

## Development workflow

1. **Kickoff and isolate**
   - Confirm workspace/backend.
   - Create or reuse a Hermes task folder.
   - Clone or refresh the source copy into task-local `playground/`.
   - Use HTTPS remotes for ChatArch repos; never print tokens or raw auth headers.

2. **Map before changing shared primitives**
   - For gateway/session/terminal/file/code_execution/SSH changes, write a small task-local map or brief first.
   - Identify caches, session keys, task overrides, platform callbacks, and existing focused tests.

3. **Use TDD**
   - Write a focused failing test for each user-visible behavior.
   - Verify RED, then implement the smallest GREEN change.
   - Keep tests behavior-oriented: assert observable card values, callback resolution, preview text, backend binding, and redaction.

4. **Feishu card pattern**
   - Build cards in the Feishu adapter, not in generic gateway logic.
   - Store pending state by short id plus `session_key`, `chat_id`, and relevant safe metadata.
   - `_on_card_action_trigger()` should recognize the action value, validate operator/chat synchronously, return a resolved inline card, and schedule async resolution on the adapter loop.
   - Keep unauthorized or mismatched callbacks fail-closed before returning a success-looking card.
   - Avoid dumping raw args, secrets, private key paths, tokens, host credentials, or auth headers into card body or tool preview.

5. **SSH Mode pattern**
   - Section-scoped backend switching is keyed by durable `session_key`, not one transcript `session_id`.
   - `ssh_mode.status` and `list_targets` are read-only.
   - `ssh_mode.request_use` may switch only with a session-scoped grant; otherwise request user authorization.
   - Feishu parent chats should not silently become SSH-bound; `/ssh use <alias>` creates/binds a Thread by default, leaving parent chat local.
   - When adding model-visible authorization UI, keep grant scope explicit: allow current target, allow all targets, or deny.

6. **Verification**
   - Run focused tests for touched areas and existing SSH/gateway regressions.
   - Run `python3 -m py_compile` for changed Python files and `git diff --check`.
   - Record exact commands and real outputs in the task `progress.md`.

## Current case study: SSH Mode transparency + Feishu authorization card

A proven implementation route for the 2026-07-02 SSH Mode task:

- `agent/display.py::build_tool_preview()` can provide safe `ssh_mode` action previews such as `request_use <alias> cwd=<path>` without exposing private key paths.
- `tools/ssh_mode_tool.py` can use a per-session gateway notification queue so `request_use` waits for a card decision and then grants `allow_current`, `allow_all`, or `deny`.
- `gateway/run.py` should register/unregister that SSH grant notifier alongside the existing dangerous-command approval notifier for each agent turn.
- `gateway/platforms/feishu.py` owns the interactive SSH authorization card and callback handling.
- Focused tests live naturally in:
  - `tests/agent/test_display.py`
  - `tests/tools/test_ssh_mode_tool.py`
  - `tests/gateway/test_feishu_approval_buttons.py`
  - existing SSH runtime regressions: `tests/gateway/test_ssh_command.py`, `tests/tools/test_ssh_runtime_overrides.py`

## Pitfalls

- Do not work directly in the running Hermes install unless explicitly told to.
- Do not confuse profile-local Hermes skills under `<HERMES_HOME>/skills` with shared ChatMemory skills under `<WORKSPACE_ROOT>/core/ChatMemory/Skills`.
- Do not encode machine-specific SSH aliases, key paths, Feishu IDs, tokens, or branch names into shared skills.
- Do not let a card callback show an approved/resolved card before authorization and chat checks pass.
- Do not leave a model tool blocked on a non-interactive text fallback; if no interactive resolver is available, fail closed or return `approval_required` without blocking.
