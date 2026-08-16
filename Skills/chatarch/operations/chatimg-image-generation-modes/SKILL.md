---
name: chatimg-image-generation-modes
description: Generate images with ChatImg through either API-key OpenAI-compatible routing or OAuth/access-token routing, with proxy and redaction rules.
version: 0.1.0
reference:
  - crs-service-operations: "Understand CRS API-key routing, permission errors, and redaction boundaries when using OpenAI-compatible media endpoints"
---

# ChatImg Image Generation Modes

Use this skill when generating images with ChatImg/ChatImage for ChatArch tasks, especially covers, illustrations, or website-card artwork.

There are two supported modes. Choose deliberately and verify the real output file instead of only checking that a command started.

## Mode 1 — API key / OpenAI-compatible route

This mode is equivalent to the official OpenAI API-key shape, but the base URL may point to an OpenAI-compatible relay or CRS deployment.

Required profile values:

- `OPENAI_API_BASE=<openai-compatible-v1-base>`
- `OPENAI_API_KEY=<secret>`
- optional `OPENAI_IMAGE_MODEL=<image-model-or-preset>`

Command pattern:

```bash
chatimg openai generate \
  '<prompt>' \
  --model gpt-image-2 \
  --quality medium \
  --size 1536x1024 \
  --timeout 240 \
  --output <output.png> \
  -I
```

If the base URL points to the official OpenAI endpoint from a restricted server network, enable the server's approved proxy first. If the base URL is already an approved relay/proxy endpoint, do not add a second guessed proxy. Do not write real CRS/relay URLs into shared skills or public reports; use placeholders such as `<openai-compatible-v1-base>`.

Safe preflight shape:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('<chatenv-openai-profile-env>')
vals = {}
for line in p.read_text(errors='replace').splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")
print('OPENAI_API_BASE_set=' + str(bool(vals.get('OPENAI_API_BASE'))))
print('OPENAI_API_KEY_set=' + str(bool(vals.get('OPENAI_API_KEY'))))
print('OPENAI_IMAGE_MODEL=' + vals.get('OPENAI_IMAGE_MODEL', '<unset>'))
PY
```

Never print the key. Avoid printing a private relay URL when writing reusable/shared documentation.

## Mode 2 — OAuth / access-token route

This mode uses ChatEnv's OpenAI profile/token-store lifecycle and the ChatImg Codex/OAuth bridge.

Command pattern:

```bash
chatimg codex auth-status --profile <profile>
chatimg codex generate \
  '<prompt>' \
  --profile <profile> \
  --image-model gpt-image-2-medium \
  --aspect-ratio 16:9 \
  --timeout 240 \
  --output <output.png>
```

If this mode calls official OpenAI endpoints from a server that cannot reach them directly, enable the approved proxy before generation. If the profile is configured to use a proxy OAuth/base URL, rely on that configured path instead of inventing a new one.

Access tokens, refresh tokens, auth JSON, cookies, and account identifiers are secrets. Report only booleans, expiry status, profile name, command exit code, output path, dimensions, and file hash.

## Cover-image workflow

For service cards or report covers:

1. Inspect the target card/page style first. Do not blindly reuse a uniform template.
2. Write a prompt with:
   - the service title;
   - one short visible summary line;
   - desired mood/composition;
   - explicit instruction to avoid real URLs, account names, tokens, and secrets.
3. Generate a larger source image with ChatImg.
4. Crop/resize to the target ratio. For ChatGlance website-service cards, use `16:7` and `1280x560`.
5. Verify the final image visually enough to catch unreadable text, wrong service name, logo hallucinations, or secret-like strings.
6. Publish to the managed image/share host only after verification.
7. Verify the public image URL with an HTTP HEAD/GET and record only safe metadata: URL, dimensions, size, and hash.

Python crop helper:

```python
from PIL import Image
from pathlib import Path
src = Path('<source.png>')
out = Path('<cover.png>')
im = Image.open(src).convert('RGB')
w, h = im.size
ratio = 16 / 7
if w / h > ratio:
    new_w = int(h * ratio)
    left = (w - new_w) // 2
    box = (left, 0, left + new_w, h)
else:
    new_h = int(w / ratio)
    top = (h - new_h) // 2
    box = (0, top, w, top + new_h)
im.crop(box).resize((1280, 560), Image.Resampling.LANCZOS).save(out, quality=94)
```

## Failure modes

- `404` on `/images/generations`: the relay does not expose Images API compatibility; switch to a supported route or OAuth mode after confirming scope.
- `401` / `403`: key is invalid, rotated, or lacks permission; do not retry with leaked values in logs.
- Network timeout on official endpoints from a server: use the approved proxy path.
- Good HTTP response but bad image: regenerate with a more concrete prompt or use a local deterministic SVG fallback, clearly labeled as fallback.

## Redaction rules

- Shared skills must not contain real CRS/relay base URLs, API keys, access tokens, refresh tokens, auth JSON paths with user-specific account IDs, cookies, or passwords.
- Task reports may include safe public artifact URLs and hashes, but not secret-bearing profile dumps.
- When using `chatenv cat`, sanitize before saving: fully replace API-key/token lines and avoid copying private relay URLs into shared docs.
