---
name: feishu-inline-image-delivery
description: Use when sending screenshots or generated images to Feishu, including files created on an active Hermes SSH target.
version: 0.3.1
reference:
  - hermes-platform-development: "Hermes gateway, Feishu delivery, deployment, and runtime verification boundaries"
  - hermes-ssh-target-configuration: "SSH registry aliases and session-bound target configuration"
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
- including `MEDIA:/path`, `MEDIA:ssh://...`, or `[media attachment]` in the final answer without verifying platform delivery;
- saying “image sent” without readback/log evidence.

## MEDIA marker quick reference

`MEDIA:` is a Hermes outbound directive, not Feishu/Lark syntax. It must be normal final-response text, outside code blocks/JSON/quotes, so Hermes can consume it before Feishu delivery.

Correct SSH image delivery:

```text
Caption or short explanation.

MEDIA:ssh://<current-target-alias>/absolute/remote/path/to/image.png
```

Correct gateway-local delivery:

```text
Caption or short explanation.

MEDIA:file:///absolute/gateway/path/to/image.png
```

Display-only / not delivery:

````text
```text
MEDIA:ssh://<current-target-alias>/absolute/remote/path/to/image.png
```
````

Failure and success signals:

- If the user sees literal `MEDIA:...` or `[media attachment]`, the directive was not consumed. Do not claim success.
- Success means the user sees the image, or readback shows `msg_type=post` plus `img_v3_...` / `tag=img`.
- Do not use `cronjob` as an immediate Feishu media sender; cron delivery does not run the same SSH URI materialization step as normal assistant final delivery.

## Normal Hermes output format

For normal Hermes conversation delivery, output ordinary explanatory text plus one explicit `MEDIA:` resource directive.

Gateway-local file, canonical form:

```text
Here is the summary or explanation.

MEDIA:file:///absolute/path/to/image.png
```

File created on the current SSH target:

```text
Here is the summary or explanation.

MEDIA:ssh://<current-target-alias>/absolute/remote/path/to/image.png
```

`MEDIA:/absolute/path/to/image.png` remains a compatibility form. Prefer the typed URI forms because they state which filesystem owns the path.

Important details:

- Get `<current-target-alias>` from `ssh_mode.status` or `/ssh status`. Use the exact Hermes registry alias, not a guessed hostname, IP address, or another configured target.
- `file:///...` means a file on the gateway host. It must not be used for a path that exists only on the SSH target.
- `ssh://<alias>/...` means a file on the currently bound SSH target. The alias must match the current section/thread binding or delivery fails closed.
- Use an absolute path. Percent-encode spaces and other URI-sensitive characters, for example `page%20one.png`.
- Keep the SSH binding active through the final response. The gateway materializes the remote bytes into its local delivery cache before the Feishu adapter runs.
- Do not manually `scp` the image back, generate a local stand-in, or use Lark CLI for delivery. Those paths bypass the capability being validated.
- Do not use Markdown local image syntax such as `![x](./image.png)` for Feishu inline delivery.
- Do not pre-convert to PDF or send a file attachment unless the user explicitly asks for a fallback.
- A single image plus non-empty text is routed through Feishu `send_image_file(..., caption=...)`, producing a single rich `post` instead of a detached image.

## SSH Mode remote-image workflow

1. Confirm the current binding with `ssh_mode.status`; if switching is needed, use the authorized `ssh_mode.request_use` / YOLO flow or ask the user to run `/ssh use <alias>`.
2. Generate the image on the SSH target using terminal, browser, screenshot, plotting, or another remote execution tool.
3. Verify the remote file exists, is a regular file, and has a non-zero size. Do not read or expose unrelated sensitive paths.
4. Return normal explanatory text followed by `MEDIA:ssh://<current-target-alias>/absolute/remote/path.png` while the binding is still active.
5. Hermes verifies the current alias, canonical remote path, sensitive-path policy, regular-file metadata, size/count/deadline limits, and transfer consistency before atomically staging the file in the gateway cache.
6. The Feishu adapter receives only the gateway-local staged path and sends the text plus image in the current thread/topic.
7. Treat user confirmation or Feishu readback in the current thread/topic as acceptance. Do not claim success from the model response alone.

If materialization fails, Hermes removes the unusable directive and emits a generic attachment warning without exposing the remote path. Check the current alias, remote file existence/size, and gateway logs before retrying.

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

## Historical validation note

The validated local acceptance used the normal Hermes final-response pipeline: handler returns text plus `MEDIA:/absolute/path.jpg`; Hermes extracts the marker; Feishu readback shows the current thread, `msg_type=post`, explanatory text, and `[Image: img_v3_...]`. `lark-cli` was readback only, not delivery.

## Another-machine validation checklist

On another machine, first ensure the Hermes version includes both the Feishu inline-media fix and SSH remote-media materialization, then validate in a real Feishu thread/topic.

1. Identify the resource owner and confirm the image exists there. For local mode, inspect the gateway-local path. For SSH Mode, inspect the path through the active SSH backend without copying it locally:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('/absolute/path/to/image.png')
print('exists', p.exists(), 'bytes', p.stat().st_size if p.exists() else None)
PY
```

2. In a normal Hermes conversation, use the matching typed resource directive:

```text
MEDIA:file:///absolute/gateway/path/to/image.png
```

or, while bound to the target:

```text
MEDIA:ssh://<current-target-alias>/absolute/remote/path/to/image.png
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

## Short-lived QR and login images

Authentication QR codes are live handoffs, not ordinary screenshots.

1. Confirm the SSH binding and remote output path first.
2. Generate the QR at the last responsible moment and keep the source browser/page alive.
3. Send exactly one normal Hermes response with explanatory text and a typed `MEDIA:ssh://<current-target-alias>/absolute/path.png` marker.
4. Do not route login QR delivery through unrelated public file sharing services, Markdown local-image syntax, or hand-written Feishu/Lark API calls unless the user explicitly asks for a separate fallback. Those paths bypass the Hermes inline-media capability being validated.
5. After sending, verify by current-thread readback or explicit user confirmation before claiming success.
6. If the user reports expiry or missing image, regenerate a fresh QR and repeat the Hermes image path; do not merely resend a cached PNG or an old image key.

## Troubleshooting

- If the user sees the literal `MEDIA:ssh://...` text, Hermes did not consume the media directive. Treat this as a gateway final-response post-processing / SSH artifact materialization / Feishu inline-send failure, not as a successful image send.
- If readback does not show the marker, retry readback with `--sort desc`; default ascending pagination may return old thread messages first.
- If the message appears in the parent chat but not the thread/topic, the delivery metadata lost the thread/reply anchor.
- If a text message appears but no image appears, inspect logs for Feishu upload/send failures before retrying.
- If SSH delivery reports a materialization failure, verify that the URI alias exactly matches the active binding and that the file exists on that target. Do not switch to `file://` for a remote-only path.
- If the output is two messages (text plus detached image), the Hermes instance is likely missing the inline-media fix or did not use the `caption` path.
- Keep secrets out of logs and reports. Redact app ids, tenant keys, tokens, and user identifiers when storing readback artifacts.

## Critical text report formatting

For Feishu release reports or validation summaries where exact dependency/version text matters, avoid using multiple fenced Markdown code blocks for core evidence. Prefer short paragraphs, bullet lists, inline code, and bare links.

Known risky patterns include dependency constraints with angle brackets, such as `package>=0.2.2,<0.3.0`, when they appear inside complex code blocks or mixed Markdown structures. Feishu may accept the post while rendering drops nearby text, so this may not surface as a send error.

For critical reports, verify readback or user confirmation when possible. If rendered output is missing core lines, resend using simpler plain-text bullets and compare three layers: assistant final text, the outbound/API-stored payload, and client-visible rendering.

Treat repeated missing or swallowed text as a delivery/rendering bug rather than a formatting annoyance. Reproduce with the smallest offending text in the current thread, then read it back through Feishu OpenAPI or Lark CLI. Use Lark CLI for readback only, never as a replacement delivery path.

## Included validation script

- `scripts/validate_feishu_inline_media.py` exercises the Hermes FeishuAdapter normal text-plus-`MEDIA:` pipeline without starting a second websocket. Use it only in an explicitly authorized validation context and keep identifiers and credentials out of stored output.
