# Zhihu Login Card And Product Draft Acceptance

Use this reference when a ChatPost Zhihu task needs a real Feishu/Lark login handoff followed by exactly one draft creation.

## Layering recap

- ChatUp provides install/setup substrate: Node, Playwright, Chrome/Chromium, and browser script runtime.
- ChatBrowser owns browser Profile metadata and path/CDP/session registry.
- ChatPost orchestrates platform profile -> login state -> draft task -> receipt.

Keep non-Zhihu platform acceptance in a separate platform-specific skill or reference.

## Live login card sequence

1. Confirm the profile registry and runner config resolve the intended logical profile, e.g. `test` or `product`.
2. Confirm no stale owned CDP/browser process is occupying the configured port. If an owned process was killed and left a browser open, close it through its captured CDP `Browser.close` path rather than using unscoped process killing.
3. Start the login command as a live process:

   ```bash
   chatpost zhihu login PROFILE --timeout 900 --output json -I
   ```

4. Read the first JSON line:
   - `event=already_logged_in` / `status=LOGGED_IN`: do not send a login card; proceed to status/draft verification.
   - `event=login_url` / `status=LOGIN_REQUIRED`: send a Feishu/Lark card immediately, while the process remains alive.
5. The card should contain a URL button for the page-owned login URL. The button is navigation only; it is not a callback.
6. If the user needs the agent to react to a click, add callback buttons such as `我已授权` and `取消`, then run `status` after the callback.
7. Wait for the same login command to emit `event=logged_in` / `status=LOGGED_IN`, or verify with a follow-up `status` command.

## QR/link handling

- Prefer URL-button handoff for Zhihu page-owned `login_url`.
- If a platform produces a QR image artifact, send the image only as a live handoff artifact backed by the still-running browser/process.
- Redact tokenized login URLs, QR payloads, decoded QR internals, data URLs, base64, cookies, local/session storage, browser endpoints, and account identifiers from chat summaries, progress logs, PR bodies, docs, receipts, and shared skills.
- `feishu_card`/Lark card success only proves card delivery. It does not prove login.
- If a process is killed, times out, or its owned browser closes, the previous card/URL/QR is expired. Regenerate a fresh live handoff rather than resending the old one.

## One-shot draft acceptance

After login is proven:

1. Prepare the source Markdown with a unique non-secret marker.
2. Run dry-run first:

   ```bash
   chatpost zhihu draft PROFILE SOURCE --dry-run --output json -I
   ```

   Expected: `status=DRY_RUN_OK`. This must not start a browser or write externally.
3. For the real write, run exactly one create command with a receipt:

   ```bash
   chatpost zhihu draft PROFILE SOURCE --receipt RECEIPT.json --output json -I
   ```

4. Treat success as valid only when output/receipt contain `status=DRAFT_CREATED`, a strict locator such as draft id + review/edit URL, and closed cleanup statuses.
5. Verify the receipt mode is `0600`.
6. If the write path starts and the result is ambiguous, do not automatically retry. First read back the draft box/editor by title, marker, time, or source digest, then ask the user before another write.

## Evidence to record

Record in project progress/reports:

- logical profile and platform, not raw account details;
- login event sequence: `LOGIN_REQUIRED` -> `LOGGED_IN` or `already_logged_in`;
- card delivery success without raw URL;
- dry-run status;
- real create status;
- receipt mode and cleanup statuses;
- whether locator fields were present, without exposing private/account-identifying URLs unless the user explicitly asks.

Do not record:

- raw `login_url`;
- QR payload/data URL/base64;
- account name/profile URL;
- Feishu message IDs unless the report is private operational evidence;
- tokens, cookies, localStorage, IndexedDB, session values, SMS codes, API keys, browser WebSocket URLs, or loopback tokens.
