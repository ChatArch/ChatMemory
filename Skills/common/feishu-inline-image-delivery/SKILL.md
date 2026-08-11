---
name: feishu-inline-image-delivery
description: Use when sending screenshots or generated images to Feishu, including files created on an active Hermes SSH target.
version: 0.3.2
reference:
  - hermes-platform-development: "Hermes gateway, Feishu delivery, deployment, and runtime verification boundaries"
  - hermes-ssh-target-configuration: "SSH registry aliases and session-bound target configuration"
---

# Feishu Inline Image Delivery

Use when the user expects an image to appear inline in the current Feishu/Lark conversation or thread. Keep this simple: produce the image, verify the file exists, then send normal text plus one `MEDIA:` directive in the final response.

## Core contract

Accepted delivery means the current Feishu thread/topic contains the image inline. Acceptance evidence is either user confirmation or readback showing `msg_type=post` plus `tag=img` / `img_v3_...`.

Not accepted:

- the user sees literal `MEDIA:...` or `[media attachment]`;
- only a local/remote path is listed;
- text and image go to the wrong parent chat/thread;
- a file/PDF fallback is sent without the user asking for one;
- the assistant says it sent an image without readback or user-visible image evidence.

## The normal way to send one image

Gateway-local file:

```text
Short caption or explanation.

MEDIA:file:///absolute/gateway/path/to/image.png
```

File created on the active SSH target:

```text
Short caption or explanation.

MEDIA:ssh://<current-target-alias>/absolute/remote/path/to/image.png
```

Media-only is also valid when the user asked for only the image:

```text
MEDIA:ssh://<current-target-alias>/absolute/remote/path/to/image.png
```

Rules:

1. Use the exact current SSH alias from Hermes SSH Mode; do not guess hostnames or switch to `file://` for a remote-only path.
2. The path must be absolute and the file must exist with non-zero size before the final response.
3. Keep user-clickable URLs as plain text or normal Markdown links. A common valid shape is a bare URL line followed by a `MEDIA:ssh://...` line; the URL remains visible/clickable, and only the `MEDIA:` line is consumed.
4. Do not wrap user-clickable URLs in backticks, fenced code blocks, JSON snippets, table code cells, or angle brackets.
5. Do not use Markdown image syntax like `![x](./image.png)` for local files.
6. Do not use `cronjob` as an immediate image sender.

## Parser behavior to rely on

Hermes treats `MEDIA:` as an internal outbound directive, not as Feishu text.

Expected pipeline:

1. `MEDIA:ssh://<alias>/...` is verified against the current session binding.
2. Hermes copies only that artifact into a bounded gateway-local cache.
3. The marker is rewritten to a local `MEDIA:/...` path.
4. `extract_media()` consumes the marker and removes it from user-visible text.
5. Feishu uploads the file and sends an inline image message, using `send_image_file(..., caption=...)` for a single image. Empty caption/media-only should still use the direct single-image path.

Display-only examples must stay examples and must not trigger upload:

````text
```text
MEDIA:ssh://<alias>/path/image.png
```

> MEDIA:ssh://<alias>/path/image.png

{"example":"MEDIA:ssh://<alias>/path/image.png"}
````

## Failure handling

If a media resource cannot be materialized, Hermes should fail closed: remove the raw directive from visible text and report a generic attachment failure instead of leaking `MEDIA:ssh://...`.

When an image did not arrive:

1. Do not repeat the same `MEDIA:` line as proof.
2. Check whether the final output path exists on the owning machine.
3. Check the current SSH alias/session binding if using `MEDIA:ssh://...`.
4. Inspect/read back the current Feishu thread. Success requires inline image evidence (`img_v3_...` / `tag=img`).
5. If readback lacks the image, inspect Hermes/Feishu send logs for materialization, upload, reply-anchor, or thread metadata errors before retrying.

## Short-lived QR/login images

For expiring QR codes, delivery is the active blocker:

1. Prepare output path and thread context before generating the QR.
2. Generate the QR at the last responsible moment and keep the source browser/page alive.
3. Send the fresh image immediately with the normal `MEDIA:ssh://...` or `MEDIA:file://...` form.
4. Verify quickly by readback or user confirmation, then stop and wait for scan/login confirmation.
5. If it expires or did not arrive, regenerate a fresh QR and send a new image; do not reuse old PNGs, old image keys, or old tokenized links.

## Minimal verification checklist

Before claiming success:

- file exists on the correct owner machine;
- the final response uses a parser-visible `MEDIA:` line, not code/quote/JSON;
- raw `MEDIA:` / `[media attachment]` is not visible to the user;
- readback/user confirmation shows inline image in the current thread/topic.

Relevant implementation tests in Hermes:

- `tests/gateway/test_media_resource_delivery_safety.py` covers URL+MEDIA, media-only SSH resources, fail-closed unresolved resources, protected examples, and streamed delivery materialization.
- `tests/gateway/test_feishu_inline_media_delivery.py` covers Feishu single-image dispatch, including media-only.
- `tests/gateway/test_background_command.py` covers background task SSH media materialization before extraction.

## References

- `references/media-marker-visible-vs-consumed.md` — distinguish consumed media delivery from visible marker text.
- `references/2026-08-url-plus-ssh-media-content-contract.md` — URL plus `MEDIA:ssh://...` contract.
- `references/2026-08-hermes-media-resource-runtime-rollout.md` — runtime rollout and restart boundary.
- `references/media-parser-paths-and-cron-boundary.md` — normal final vs protected examples vs cron boundary.
- `references/short-lived-qr-delivery.md` — expiring QR handoff rules.
- `scripts/validate_feishu_inline_media.py` — optional explicit validation script for authorized contexts.
