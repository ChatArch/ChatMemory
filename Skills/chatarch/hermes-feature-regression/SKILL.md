---
name: hermes-feature-regression
description: "ChatArch Playground internal-release guarantee for Hermes: inventory ChatArch-owned Hermes features and verify each feature on every merge, upstream sync, PR review, or live rollout."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [local, hermes, chatarch, regression, merge, gateway]
    related_skills: [hermes-platform-development]
---

# ChatArch Hermes Feature Regression Checklist

## When to use

Use this Playground skill whenever work touches ChatArch's Hermes fork or the live Hermes gateway, especially:

- Merging or syncing official/upstream Hermes into `ChatArch/hermes-agent`.
- Reviewing, merging, or rolling out a Hermes PR.
- Changing gateway routing, slash commands, Feishu/Lark behavior, SSH Mode, terminal/file tools, compression, model/provider selection, or packaging.
- Updating the live checkout on an approved `<HERMES_SERVER>` or restarting its `hermes-gateway.service`.

This is a ChatArch internal-version feature guarantee. It is feature-regression focused: each ChatArch-owned Hermes feature below must be checked by code path and by a real user-facing entrypoint when available. Compile-only validation is not enough.

## Current ChatArch Hermes feature inventory

Treat this list as the must-preserve inventory for every merge. If a feature is intentionally removed or delegated to upstream, record that decision explicitly in the PR/task report.

### Gateway command surfaces

- `/thread` and `/t`: Feishu/Lark thread creation, section routing, prompt handoff, and typed `/t <prompt>` entrypoint.
- `/template` and `/tpl`: template listing/launching and thread/session creation behavior.
- `/ssh`: section-level SSH binding UX, list/status/test/use/off flows, cwd handoff, and thread-aware behavior.
- `/interrupt`: active-agent interruption and no-active-agent fallback where `/interrupt <prompt>` becomes a normal user turn.
- Active-session command bypass: command messages such as `/t`, `/thread`, `/tpl`, `/template`, `/ssh`, `/interrupt`, and other registered bypass commands must not be swallowed or queued as plain text while an agent is running.

### ChatArch custom seam package

- `chatarch_custom/`: owned extension package for ChatArch-local metadata/helpers.
- `chatarch_custom.gateway.local_features`: command definitions, aliases, active-session bypass names, and gateway handler mapping for ChatArch local gateway features.
- `CHATARCH_LOCAL_SEAM` comments: required markers in official-heavy files where behavior cannot yet be fully moved out.
- Packaging discovery: `pyproject.toml` must include `chatarch_custom` and `chatarch_custom.*` so installed wheels do not miss local feature code.

### Feishu/Lark behavior

- Structured card replies: `CardReply` must reach platform card delivery where supported, with text fallback only when card delivery is unavailable or fails.
- Feishu interactive cards and approval buttons: button payloads/callbacks must continue to route to the correct session and thread.
- SSH authorization cards: `ssh_mode.request_use` must trigger the real gateway/Feishu SSH grant card in no-yolo + Feishu thread contexts; fallback `/ssh yolo on ...` text is only acceptable when the gateway callback or platform card support is unavailable.
- Thread metadata preservation: `SendResult.thread_id` and Feishu/Lark thread/topic metadata must survive sends and be reused by follow-up messages.
- Reply metadata: Feishu `reply_to_message_id` and thread reply context must not be dropped.
- Inline media delivery: images/files emitted from agent responses must preserve thread/topic semantics and not detach from the active Feishu thread.
- Final-message ordering: thread seed/final delivery behavior must stay deterministic.

### SSH Mode and remote tool backend

- `ssh_mode` tool exposure: available in the default/terminal toolsets where expected.
- `ssh_mode.request_use`: respects yolo grants, prompts via authorization card when needed, and never silently switches targets without the correct grant.
- `ssh_mode.request_local`: returns to local backend without clearing user-created sticky bindings incorrectly.
- Control-plane boundaries: model-created grants/bindings and user-created `/ssh` bindings must remain separate.
- Terminal backend isolation: terminal session keys must include SSH target and task environment overrides; sessions must not leak across targets or tasks.
- File tools over SSH: remote/backend paths must stay remote paths, not local display paths.
- Code execution / terminal / file tool behavior must preserve normal login identity and must not invent keys or escalate privileges.

### Compression and context rescue

- `/compress-local`, `/compact-local`, and `/rescue-compress` when present: local deterministic rescue compression that does not call an LLM or auxiliary compression model.
- Normal `/compress` and automatic compression must remain unchanged unless the PR explicitly targets them.
- Compression persistence: archive/session rotation/in-place persistence must preserve the original transcript and compacted context.
- Plugin compressor safety: local fallback must fail closed when a compressor does not explicitly support `local_fallback_only`.

### Provider/model/runtime features

- Provider/model fallback paths must not lose auth/config error reporting.
- Model catalog fallback behavior must distinguish remote curated manifest fallback from in-repo static snapshot fallback.
- `max` / `ultra` reasoning effort is an official/shared feature, not ChatArch-only, but local UI/tests must not regress its availability if the base branch already contains it.

### Runtime, credentials, and rollout behavior

- GitHub operations on an approved SSH target must use that target's configured ChatGH venv, for example `<REMOTE_CHATGH_BIN>`; a bare shell `PATH` check is not sufficient.
- GitHub/proxy credentials and provider tokens must never be printed. Compare token alignment by existence, validity, permission summary, expiration header, or private hash equality only.
- Live checkout update and gateway process restart are separate rollout steps. A repo fast-forward is not complete until the new gateway PID/start time and reconnect logs are verified.

## Mandatory per-merge checklist

For every merge, upstream sync, PR review, or live rollout:

1. Start from a clean baseline or isolated worktree. Do not patch-stack on a broken live checkout.
2. Record base branch, source branch, `HEAD`, `origin/main`, dirty status, and target machine in the task `progress.md`.
3. Build a visible feature checklist from the inventory above. Each item must be marked `preserved`, `changed intentionally`, `not present on this base`, or `broken/blocking`.
4. For every conflicted or touched gateway/tool/platform/runtime file, map each hunk to the feature it owns. Do not resolve high-risk files by whole-file `ours`/`theirs`.
5. For every high-risk feature, verify the real user entrypoint, not only the internal handler. Examples: `/t 你好` through `GatewayRunner._handle_message()`, `/tpl list`, `/ssh list`, `ssh_mode.request_use`, Feishu card callback, and inline media delivery.
6. If a regression is found in a basic feature such as `/t`, `/ssh`, `ssh_mode.request_use`, Feishu cards, or local compression rescue, stop merging. Fix in the branch or revert/isolate the bad merge before continuing.
7. Merge only after required CI is green or after the user explicitly accepts a documented risk.
8. Roll out live code only after local/CI checks pass. Verify live checkout separately from gateway restart.
9. Report final state with PR URL, merge commit, live `HEAD`, test counts, skipped/warning rationale, gateway PID/start time, and any unresolved risks.

## Suggested focused validation matrix

Run the smallest matrix that covers touched features, then expand when high-risk files changed.

### Always run for gateway/command changes

```bash
python -m compileall -q chatarch_custom hermes_cli gateway tools agent run_agent.py
python -m pytest \
  tests/gateway/test_chatarch_custom_entrypoints.py \
  tests/gateway/test_thread_command.py \
  tests/gateway/test_template_command.py \
  tests/gateway/test_ssh_command.py \
  tests/gateway/test_command_bypass_active_session.py \
  tests/gateway/test_interrupt_command.py \
  -q
```

### Feishu/Lark changes

```bash
python -m pytest \
  tests/gateway/test_feishu.py \
  tests/gateway/test_feishu_card_capability.py \
  tests/plugins/test_feishu_card_plugin_tool.py \
  tests/gateway/test_feishu_approval_buttons.py \
  tests/gateway/test_feishu_inline_media_delivery.py \
  tests/gateway/test_feishu_thread_seed_final.py \
  -q
```

### SSH/tool backend changes

```bash
python -m pytest \
  tests/tools/test_ssh_mode_tool.py \
  tests/tools/test_ssh_environment.py \
  tests/tools/test_ssh_mode_control_plane_boundaries.py \
  tests/tools/test_ssh_runtime_overrides.py \
  tests/tools/test_file_tools_ssh_backend_paths.py \
  tests/tools/test_terminal_session_isolation.py \
  -q
```

### Compression changes

```bash
python -m pytest \
  tests/agent/test_context_compressor.py \
  tests/gateway/test_compress_command.py \
  tests/cli/test_compress_flags.py \
  tests/agent/test_compression_concurrent_fork.py \
  tests/run_agent/test_compression_persistence.py \
  -q
```

### Packaging/model changes

```bash
python -m pytest tests/test_packaging_metadata.py tests/hermes_cli/test_models.py -q
```

## Report template

Use this shape in PR bodies or task `progress.md`:

```markdown
## ChatArch Hermes feature regression checklist

- Base: `<branch/SHA>`
- Head: `<branch/SHA>`
- Target machine: `<approved-host/path>`
- Live checkout updated: yes/no, `<SHA>`
- Gateway restarted: yes/no, PID/start time

### Feature inventory status

- `/t` / `/thread`: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- `/template` / `/tpl`: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- `/ssh`: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- `ssh_mode.request_use` card grant: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- Feishu cards/thread/media: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- Active-session bypass: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- `/interrupt`: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- `/compress-local`: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- SSH/file/terminal backend isolation: preserved | changed | not present | broken — evidence: `<test/entrypoint>`
- Packaging/custom seams: preserved | changed | not present | broken — evidence: `<test/entrypoint>`

### Validation

- `git diff --check`: pass/fail
- compileall repo venv: pass/fail
- compileall service venv: pass/fail
- pytest matrix: `<counts>`
- CI: pass/fail/pending
- Risks/skips: `<explicit rationale>`
```

## Pitfalls

- Handler tests are not enough for slash commands. Add or run real typed-entrypoint tests through `GatewayRunner._handle_message()` or the platform adapter boundary.
- Do not confuse an SSH target's bare shell environment with its Hermes/ChatGH venv. Verify the actual venv path before declaring credentials missing.
- Do not claim a live rollout is complete after `git pull`; the running gateway must load the new code and show a new PID/start time.
- Do not print tokens, proxy credentials, Feishu tickets/access keys, or provider keys. Use `[REDACTED]` in logs and summaries.
- If official upstream introduces a competing implementation, understand and merge the behavior; do not blindly prefer local or upstream whole files.
