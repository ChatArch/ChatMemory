---
name: hermes-feishu-card-interactions
description: "Use Hermes' internal feishu_card tool to send Feishu interactive cards, wait for button clicks, and read the managed callback result."
version: 0.1.3
---

# Hermes Feishu Card Interactions

Use this shared skill when the user wants a Feishu interactive card sent from the current Hermes conversation and expects the agent to continue after the user clicks a button.

This skill documents the Hermes internal `feishu_card` tool flow. Keep it focused on that tool path.

## Core Model

- `feishu_card` is an internal Hermes tool for creating, previewing, sending, and waiting on Feishu interactive cards.
- Use `action: "request_interaction"` when the agent must wait for a user click and then continue reasoning with the callback result.
- Use `action: "send"` only when no callback is needed.
- In a gateway session, omit `chat_id` and `thread_id` by default so the card is delivered to the current conversation and topic.
- `request_id` should be unique enough for the current interaction, for example `guess-number-20260710-01`.

## Strict Input Contract

Top-level tool call:

- `action` is required. For click-and-continue cards use `"request_interaction"`; for fire-and-forget cards use `"send"`; for checking the supported DSL use `"schema"`.
- `card` is required for `request_interaction` and `send` unless using a specialized authorization action.
- `request_id` is strongly recommended for `request_interaction` so the callback can be correlated with the prompt.
- `chat_id`, `thread_id`, and `reply_to` are optional routing fields. In the current conversation, usually omit them and let Hermes preserve the active chat/topic.

Card object:

- `header` is optional; supported fields are `title` and `color`.
- `elements` is the main body and must be an array.
- Supported element `type` values in the high-level DSL are `markdown`, `divider`, `image`, `actions`, and `note`.
- `markdown` and `note` elements use `content` as plain text or markdown-ish text. Prefer separate elements for separate rows; avoid GitHub-style markdown tables because Feishu card rendering is not consistent for tables.
- If content comes from JSON/model text, use real newlines when possible. Hermes also normalizes common literal escapes like `\\n` and `\\r\\n` before rendering.
- `image` requires `image_key` or `img_key` from an uploaded Feishu image; do not pass arbitrary file tokens or URLs as image keys.
- `divider` has no required content.
- `actions` must include `buttons`; valid `layout` values are `row` and `equal`.
- `raw_feishu` exists as an escape hatch for advanced cards, but prefer the high-level DSL for normal agent interactions.

Button object inside `actions.buttons`:

- Supported button fields are `text`, `style`, `action`, `url`, and `payload`.
- For callbacks, include `action` as the stable choice ID, for example `guess_23`.
- `payload` must be a small JSON object containing only non-secret machine-readable values that the agent needs after the click.
- Use `url` only for navigation-style buttons; use `action` plus `payload` for answer/approval/selection buttons.
- For link cards that should wait for feedback, mark URL-only/navigation buttons as non-terminal with `payload: {"terminal":"false"}` and include separate terminal buttons such as `我已打开` and `取消`.
- Do not put hidden answers, private tokens, or long state blobs into the visible card or button payload.

Callback contract:

- Hermes rewrites each button into a managed card response callback.
- After the user clicks, the `feishu_card` tool call returns to the model; there is no separate polling loop in the agent.
- The returned object includes `request_id`, `choice`, `payload`, `message_id`, and `thread_id`.
- The button's `action` becomes the returned `choice` and is also available as `payload.choice`.
- Key-values from the original button `payload` are merged into the returned `payload`.
- Hermes may add managed fields such as `button_text`, `request_id`, and `session_key`; treat `session_key` as internal and do not persist or print it.

## Common Card Types

Use these patterns instead of inventing a raw Feishu card shape unless the user explicitly needs advanced layout.

### 1. Information / Announcement Card

Use `action: "send"` when no click result is needed.

```json
{
  "action": "send",
  "title": "系统通知",
  "card": {
    "header": {"title": "系统通知", "color": "blue"},
    "elements": [
      {"type": "markdown", "content": "**任务已完成**"},
      {"type": "divider"},
      {"type": "note", "content": "这类卡片只通知，不等待用户反馈。"}
    ]
  }
}
```

### 2. Status Summary Card

Avoid markdown tables. Feishu card markdown does not consistently render GitHub-style tables, and model-generated `\\n` may show literally if not normalized. Prefer one row per element.

```json
{
  "action": "send",
  "card": {
    "header": {"title": "路由验证状态", "color": "green"},
    "elements": [
      {"type": "markdown", "content": "**当前会话 chat/thread**：已读取"},
      {"type": "markdown", "content": "**om_ reply anchor**：已使用"},
      {"type": "markdown", "content": "**Feishu interactive card**：已发送"},
      {"type": "markdown", "content": "**Python SDK reply path**：已对齐"}
    ]
  }
}
```

### 3. Link Card With Feedback

A URL button opens a page; it should not be the only terminal action if the agent must know what happened. Pair it with `我已打开` / `取消` buttons and use `request_interaction`.

```json
{
  "action": "request_interaction",
  "request_id": "link-card-001",
  "card": {
    "header": {"title": "打开链接并反馈", "color": "turquoise"},
    "elements": [
      {"type": "markdown", "content": "请先打开链接，完成后回到这里反馈。"},
      {
        "type": "actions",
        "layout": "row",
        "buttons": [
          {
            "text": "打开链接",
            "style": "primary",
            "action": "open_link",
            "url": "https://example.com/verify",
            "payload": {"terminal": "false", "target": "verify_page"}
          },
          {
            "text": "我已打开",
            "style": "primary",
            "action": "opened_link",
            "payload": {"result": "opened", "target": "verify_page"}
          },
          {
            "text": "取消",
            "style": "danger",
            "action": "cancel_link",
            "payload": {"result": "cancelled", "target": "verify_page"}
          }
        ]
      }
    ]
  }
}
```

### 4. Authorization Card

For a simple verification/permission URL, prefer `request_authorization`. It renders an open-link button and terminal buttons so the agent can continue after the user clicks.

```json
{
  "action": "request_authorization",
  "title": "需要授权",
  "body": "请点击授权按钮完成权限确认。完成后回到对话里点击“我已完成授权”；如果不授权，请点击“取消”。",
  "verification_url": "https://accounts.feishu.cn/oauth/v1/device/verify?...",
  "flow_id": "auth-flow-001"
}
```

## Example: Guess Number Card

1. Optionally inspect the supported DSL:

   ```json
   {"action":"schema"}
   ```

2. Send an interactive card and wait for the click:

   ```json
   {
     "action": "request_interaction",
     "request_id": "guess-number-001",
     "card": {
       "header": {
         "title": "猜数字小游戏",
         "color": "turquoise"
       },
       "elements": [
         {
           "type": "markdown",
           "content": "我已经在心里想好了一个数字。\n\n下面三个选项里，有一个就是它。你猜是哪一个？"
         },
         {"type": "divider"},
         {
           "type": "actions",
           "layout": "equal",
           "buttons": [
             {
               "text": "7",
               "style": "default",
               "action": "guess_7",
               "payload": {"number": "7"}
             },
             {
               "text": "23",
               "style": "default",
               "action": "guess_23",
               "payload": {"number": "23"}
             },
             {
               "text": "41",
               "style": "default",
               "action": "guess_41",
               "payload": {"number": "41"}
             }
           ]
         },
         {
           "type": "note",
           "content": "选一个按钮，我来告诉你猜对没有。"
         }
       ]
     }
   }
   ```

3. Read the returned result from the tool call:

   ```json
   {
     "success": true,
     "request_id": "guess-number-001",
     "choice": "guess_41",
     "payload": {
       "button_text": "41",
       "choice": "guess_41",
       "number": "41",
       "request_id": "guess-number-001",
       "session_key": "[managed-by-hermes]"
     },
     "message_id": "om_...",
     "thread_id": "omt_..."
   }
   ```

4. Continue in the same turn using the callback data. For the game example, compare `payload.number` with the answer held in the agent's own state, then reply with whether the guess was correct.

## Example: Authorization Card

Use this when the user needs to open a verification URL or permission grant URL and the current Hermes environment has the `feishu_card` tool available.

Prefer the specialized authorization action for a simple authorize/cancel card:

```json
{
  "action": "request_authorization",
  "title": "需要授权",
  "body": "请点击授权按钮完成权限确认。完成后回到对话里告诉我已完成。",
  "verification_url": "https://accounts.feishu.cn/oauth/v1/device/verify?...",
  "flow_id": "auth-flow-20260710-01"
}
```

Notes:

- `verification_url` must be the exact user-facing URL that the user should open.
- `flow_id` should identify this one authorization attempt; do not use secrets or long-lived tokens as the flow ID.
- The card normally renders an open-link button plus terminal buttons such as `我已完成授权` and `取消`; the terminal button is what returns feedback to the agent.
- A card click is not proof that the downstream authorization succeeded. After the user completes the browser-side flow, verify the authorization through the original workflow's completion/check step.
- If the user clicks cancel or says they did not approve, stop the privileged action and explain what remains blocked.

Use the generic `request_interaction` path only when the authorization card needs custom buttons or extra structured choices.

## How Feedback Reaches The Agent

The agent gets the user's click as the return value of the same `request_interaction` tool call that sent the card.

For example, if the user clicks the `41` button, the tool returns a structured result similar to:

```json
{
  "success": true,
  "request_id": "guess-number-001",
  "choice": "guess_41",
  "payload": {
    "button_text": "41",
    "choice": "guess_41",
    "number": "41",
    "request_id": "guess-number-001",
    "session_key": "[managed-by-hermes]"
  },
  "message_id": "om_...",
  "thread_id": "omt_..."
}
```

Then the agent should:

1. Check `success` is true.
2. Use `choice` for the clicked button identity.
3. Use semantic fields from `payload`, such as `payload.number`, for task logic.
4. Ignore `session_key` except to know Hermes managed the interaction.
5. Continue the conversation normally with the result.

## Button DSL Notes

- The action element must use `type: "actions"` and a `buttons` array.
- Each button should include `text`, `style`, `action`, and optional `payload`.
- `payload` is returned to the agent after the click; use it for stable machine-readable values such as `number`, `choice_id`, or `task_id`.
- Keep payloads small. Do not put secrets, private tokens, or hidden answers into button payloads.
- `session_key` is inserted and managed by Hermes; never create, edit, persist, or echo it.

## Fair Hidden-Answer Cards

For games or quizzes where one option is secretly correct:

- Keep all button styles visually neutral unless highlighting is intentionally part of the UX.
- Do not reveal the answer through button color, order, wording, notes, or visible metadata.
- Store the correct answer in the agent's local reasoning state, not in the card payload.
- Return only the selected value in each button payload, then compare it after the callback.

## Common Pitfalls

- If the tool says `request_interaction requires at least one action button`, check that the action element uses `buttons`, not another key.
- `request_interaction` waits for one managed response; do not add a separate polling loop for the same click.
- `send` does not give the agent a click result. Use `request_interaction` when the next answer depends on the click.
- Do not copy private `message_id`, `thread_id`, or `session_key` values into reusable skills or public reports.
- If a card is meant to stay in the current Feishu topic, avoid manually setting destination fields unless the user asked for a different target.
- Do not rely on markdown tables for status cards; use one markdown element per row plus dividers/notes.
- For link/authorization cards, URL buttons are navigation only. Include a terminal button for `completed/opened/cancelled` so `request_interaction` can return a result.

## Verification Checklist

- The card appears in the current Feishu conversation.
- Clicking one button returns `success: true` from `request_interaction`.
- The returned `payload` contains the expected semantic field, such as `number`.
- The agent's follow-up answer uses the callback result instead of guessing from chat text.
