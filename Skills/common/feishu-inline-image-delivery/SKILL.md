---
name: feishu-inline-image-delivery
description: Send screenshots/images to Feishu as text-with-inline-image post messages through Hermes normal conversation delivery; verify current thread/topic readback instead of using PDF/file/Lark CLI workarounds.
version: 0.2.0
---

# Feishu Inline Image Delivery

Use this skill when a task needs to send a screenshot, prototype image, chart, or generated image into the current Feishu/Lark conversation and the user expects the image to appear inline with explanatory text.

## Acceptance rule

The accepted result is one Feishu rich/post message in the **current conversation thread/topic** containing both:

- visible explanatory text; and
- an embedded image in the same message body.

Do **not** count these as acceptance:

- sending a PDF/file fallback;
- sending a standalone image bubble after a text message;
- sending through `lark-cli im +messages-send` as the delivery path;
- sending to the parent/main chat when the user is in a thread/topic;
- including `MEDIA:/path` in the final answer without verifying platform delivery;
- saying “image sent” without readback/log evidence.

## Normal Hermes output format

For normal Hermes conversation delivery, the assistant should output ordinary text plus a local media marker:

```text
Here is the summary or explanation.

MEDIA:/absolute/path/to/image.png
```

Important details:

- Use an absolute local path that exists on the machine running Hermes.
- Do not use Markdown local image syntax such as `![x](./image.png)` for Feishu inline delivery.
- Do not pre-convert to PDF or send a file attachment unless the user explicitly asks for a fallback.
- After the Hermes Feishu inline-media fix, a single image plus non-empty text is routed through Feishu `send_image_file(..., caption=...)`, producing a single rich `post` instead of a detached image.

## Correct Feishu/Lark wire format

The platform-level inline image flow is:

1. Upload the image to Feishu IM image API with `image_type=message`.
2. Get an `image_key` such as `img_v3_...`.
3. Send a `msg_type=post` message whose content contains both text and an image element.

Canonical post payload shape:

```json
{
  "zh_cn": {
    "content": [
      [{"tag": "md", "text": "Caption or explanation"}],
      [{"tag": "img", "image_key": "img_v3_xxx"}]
    ]
  }
}
```

Lark CLI's source/skills confirm this pattern, but Lark CLI is only a reference/readback tool here. Local image paths inside Markdown such as `![x](./a.png)` are not auto-uploaded reliably; the reliable Markdown form is `![x](img_v3_xxx)` after pre-uploading.

## Hermes-specific implementation notes

Hermes' Feishu adapter supports the correct post shape when `send_image_file(..., caption=...)` is used: it uploads the image and sends a rich `post` payload with `tag=img`.

The bug class to avoid is the generic gateway `MEDIA:` path splitting text and image:

- text is sent first;
- image is sent later through `send_multiple_images()` with empty captions;
- in Feishu thread/topic contexts this can fail with `[99992402] field validation failed`, or deliver a detached image;
- if the failure is only logged, the assistant may falsely believe the image was visible.

For Feishu thread/topic delivery, preserve a real reply anchor:

- `thread_id` identifies the topic/thread;
- `reply_to_message_id` / `reply_to` must point to a real root/current message;
- a bare `thread_id` create payload may fail validation for rich post/image delivery.

## How the 2026-07-02 local acceptance was sent

The final local acceptance used the active Hermes Feishu normal final-response pipeline, not Lark CLI delivery and not a bare direct `send_image_file` call.

High-level flow:

1. Active Hermes install was switched to the fix branch and gateway was restarted/reconnected.
2. A local validation script instantiated `FeishuAdapter` with a REST client only, so it did not start a second Feishu websocket.
3. The script called `FeishuAdapter._process_message_background(...)` with a synthetic `MessageEvent` for the current Feishu thread/topic.
4. The message handler returned normal final-response text ending with `MEDIA:/absolute/path/to/image.jpg`.
5. Hermes' normal post-processing extracted the `MEDIA:` marker and sent one Feishu `msg_type=post` containing both the text and image.
6. `lark-cli im +threads-messages-list` was used only for readback verification.

Validated current-thread readback:

- current thread: `<LOCAL_FEISHU_THREAD_ID>`;
- message id: `<LOCAL_FEISHU_MESSAGE_ID>`;
- readback `msg_type`: `post`;
- readback content contained the text plus `[Image: img_v3_...]`.

## Another-machine validation checklist

On another machine, first ensure the Hermes version includes the Feishu inline-media fix, then validate in a real Feishu thread/topic.

1. Confirm the image exists locally on that machine:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('/absolute/path/to/image.png')
print('exists', p.exists(), 'bytes', p.stat().st_size if p.exists() else None)
PY
```

2. In a normal Hermes conversation, ask it to send a final answer containing text and:

```text
MEDIA:/absolute/path/to/image.png
```

3. Read back the current Feishu thread/topic. With Lark CLI, use readback only:

```bash
lark-cli im +threads-messages-list \
  --as bot \
  --thread omt_xxx \
  --page-size 50 \
  --sort desc \
  --no-reactions
```

4. Acceptance signs:

- the target message is in the same `thread_id` as the current conversation;
- `msg_type` is `post`;
- content includes the explanatory text;
- content includes `[Image: img_v3_...]` or the raw post contains `{"tag":"img","image_key":"img_v3_..."}`.

5. If the image is missing, do not claim success. Inspect Hermes logs first:

```bash
grep -i "Failed to send image\|field validation failed\|inline image delivery" <HERMES_HOME>/logs/gateway.log | tail -40
```

## Troubleshooting

- If readback does not show the marker, retry readback with `--sort desc`; default ascending pagination may return old thread messages first.
- If the message appears in the parent chat but not the thread/topic, the delivery metadata lost the thread/reply anchor.
- If a text message appears but no image appears, inspect logs for Feishu upload/send failures before retrying.
- If the output is two messages (text plus detached image), the Hermes instance is likely missing the inline-media fix or did not use the `caption` path.
- Keep secrets out of logs and reports. Redact app ids, tenant keys, tokens, and user identifiers when storing readback artifacts.
