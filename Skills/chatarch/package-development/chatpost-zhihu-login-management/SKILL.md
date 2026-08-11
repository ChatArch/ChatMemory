---
name: chatpost-zhihu-login-management
description: "ChatPost Zhihu login/profile/draft handoff: ChatUp/ChatBrowser boundaries, Feishu cards, QR/link handling, and one-shot draft validation."
version: 0.2.0
reference:
  - chatarch-cli-package-conventions: "Keep ChatPost CLI leaves thin, visible, and testable."
  - chatarch-mkdocs-docs-alignment: "Record real CLI outputs in MkDocs and verify Preview Docs."
  - hermes-feishu-card-interactions: "Deliver login links through Feishu cards with callback buttons where needed."
---

# ChatPost Zhihu Login Management

## When To Use

Use this skill when working on ChatPost's Zhihu account/profile login and draft foundation, especially when a task mentions:

- `chatpost zhihu login`, `chatpost zhihu status`, or `chatpost zhihu logout`
- `chatpost zhihu draft PROFILE SOURCE`
- adding or validating a Zhihu browser profile such as `test` or `product`
- proving that login is browser-level while draft creation is a separate one-shot publishing flow
- writing Quickstart/MkDocs docs with real CLI transcripts
- delivering a Zhihu login link or QR handoff through Feishu/Lark

This skill is Zhihu-only. Keep other platform login paths in their own platform-specific skills or references.

## Layering Contract

Keep the three package responsibilities separate:

```text
ChatUp      = installs/setup runtime substrate: Node, Playwright, Chrome/Chromium, browser script runtime
ChatBrowser = browser runtime/profile metadata: browser Profile registry, profile paths, CDP/session metadata
ChatPost    = publishing orchestration: platform profile -> login state -> draft/post task -> receipt
```

Rules:

1. Installing browsers, Playwright, Node, extension runtime, or system dependencies belongs to ChatUp or the browser runner layer, not ChatPost.
2. Browser Profile metadata belongs to ChatBrowser. When a ChatPost runner has `browser_profile`, resolve the physical path through an importable ChatBrowser API such as `chatbrowser.registry.profile_path(...)` instead of duplicating ownership.
3. ChatPost logical profiles are human workflow labels such as `test` and `product`. They are not accounts, cookies, tokens, installation profiles, or platform IDs.
4. Physical browser dirs may be platform-specific under the logical profile, e.g. `profiles/<logical>/zhihu`, to avoid cross-platform profile contention.
5. Internal compatibility aliases such as `zhihu-test` or `zhihu-product` may exist in registries, but the user-facing workflow should accept the logical profile (`test`, `product`) where supported.
6. A browser Profile must not be used concurrently by unrelated CLI processes. If an owned login process is killed, any handoff card/link it emitted is stale.

## Core Model

ChatPost should treat a `PROFILE` as a browser-login container plus workflow target, not as a Zhihu account id, cookie, token, or publishing runner id.

The login foundation has these responsibilities:

1. Read a registry alias/profile such as `<profile>` from `accounts.toml`.
2. Resolve browser/Profile/CDP configuration for that alias.
3. Run browser-level `status`, `login`, or `logout`.
4. Report public account identity when visible from the page (`account_name`, `account_url`) only in machine-readable private output; redact or omit it in public summaries unless the user explicitly asks.
5. Keep sensitive browser state inside the Profile; never print or export cookies, localStorage, IndexedDB, session values, tokens, SMS codes, or QR tokens.

Publishing/draft readiness belongs in draft/verify flows, not ordinary login/status.

## Expected CLI Surface

For the login/profile foundation, keep the visible tree small and real:

```text
chatpost
├── --help
├── --version
├── --tree
├── platforms [--output text|json] [-I/--no-interactive]
├── profiles [--platform zhihu] [--registry PATH] [--output text|json] [-I/--no-interactive]
└── zhihu
    ├── profiles [--registry PATH] [--output text|json] [-I/--no-interactive]
    ├── login PROFILE [--registry PATH] [--timeout INTEGER] [--output text|json] [-I/--no-interactive]
    ├── status PROFILE [--registry PATH] [--output text|json] [-I/--no-interactive]
    ├── logout PROFILE [--registry PATH] [--output text|json] [-I/--no-interactive]
    └── draft PROFILE SOURCE [--dry-run] [--receipt PATH] [--output text|json] [-I/--no-interactive]
```

`doctor`, adapter auth, bridge/extension readiness, and platform-specific setup helpers must not leak into the visible Zhihu login tree. If draft is present, document it as a one-shot write/create leaf, not as part of login.

## Semantics

### `profiles`

- Discovery only.
- Do not start a browser.
- Do not check login.
- Do not call Wechatsync, extension bridges, publishing adapters, or token checks.
- Output registry aliases and browser-profile metadata only.

### `status PROFILE`

- Use page-visible browser state only: DOM/URL/title and same-origin public `me`/`whoami` style endpoint responses.
- Do not read or dump Cookie/localStorage/IndexedDB/session/token values.
- Return `LOGGED_IN`, `LOGGED_OUT`, or `UNKNOWN` with `check_method=browser_page`.
- If public identity is visible, include public `account_name` and `account_url` in private JSON output; redact in chat/progress/public docs unless explicitly needed.
- `UNKNOWN` must not fall back to publishing-adapter auth.

### `login PROFILE`

- Start or attach to the configured browser Profile.
- First run a short browser-page status precheck.
- If already logged in, return `event=already_logged_in` / `status=LOGGED_IN` without emitting a login URL or sending a card.
- If not logged in, open the Zhihu login page and emit the page-owned `login_url` immediately as `event=login_url` / `status=LOGIN_REQUIRED`.
- Keep the same CLI command alive until either:
  - the user authorizes and the command emits `event=logged_in` / `status=LOGGED_IN`, or
  - the command reaches its timeout and emits `event=login_timeout` / `status=LOGIN_TIMEOUT`.
- Do not run Wechatsync `auth zhihu`, adapter bridge checks, extension readiness, draft publishing, or token refresh before emitting the URL.
- If the process is interrupted/killed or the browser it owns is closed, treat its `login_url`/QR/card as expired. Regenerate a fresh live handoff; never resend the old URL.

### `logout PROFILE`

- Run browser-level status first.
- If already logged out, return a no-op status.
- If logged in, use page/browser-level logout or clear Zhihu origin state.
- Do not read token contents as part of logout.

### `draft PROFILE SOURCE`

- Run `--dry-run` first when validating a new profile or source shape. Dry-run must stay browser-free and must not create external side effects.
- Before real create, prove the same `PROFILE` is logged in through `status` or the completed login command.
- Real create is a one-shot side-effecting operation. Do not automatically retry if the result is ambiguous after the write path starts.
- Return `DRAFT_CREATED` only when the adapter/extension response contains the strict locator required by the domain, such as a draft id and complete review/edit URL.
- Write a receipt when requested. The receipt must be mode `0600`, include `source_sha256`, status, cleanup fields, and locator presence, but must not include cookies, tokens, raw QR payloads, browser endpoints, or account secrets.
- Record cleanup independently: browser, extension, and adapter should each report `CLOSED`/equivalent.

## Feishu/Lark Handoff Cards

A Feishu/Lark URL button is navigation-only. Do not assume the agent can observe that the user clicked it.

### Live login card workflow

1. Start `chatpost zhihu login PROFILE --timeout 900 --output json -I` as a live process.
2. Read the first JSON event from that exact process.
3. If it is already logged in, do not send a login card.
4. If it emits `event=login_url` / `status=LOGIN_REQUIRED`, immediately send a Feishu/Lark interactive card with a URL button pointing to that live `login_url`.
5. Keep the login process alive while the card is usable.
6. Wait for that same process to emit `LOGGED_IN`, or pair the URL button with a callback such as `我已授权` and then run `status`.
7. If the process times out, is killed, or the owned browser is closed, mark the previous card expired and regenerate a fresh handoff before asking the user to try again.

### URL and QR handling

- Prefer a card URL button for Zhihu page-owned `login_url` handoff.
- If the CLI or page also produces a QR image artifact, send the image as media/attachment or card image only while the backing browser/process is still live.
- Do not paste tokenized `login_url`, QR payload, data URL, base64, or decoded QR internals into chat, docs, progress, PR bodies, receipts, or shared skills. In logs/summaries use `[URL_REDACTED]` or say only that a live URL/QR was delivered.
- In Feishu, report card delivery only after the card tool/API returns success with message/thread identifiers. Card-send success proves delivery, not login.
- When the user says “再发” / “重发” / “login card 呢?”, generate a fresh live card unless the current process is definitely still alive and the user explicitly asked to duplicate the same link.

Use one of these interaction patterns:

#### Two-button pattern

- `打开登录链接` — URL button; opens the page but does not callback.
- `取消` — callback button; tells the agent to stop the flow.

Completion is detected only by the running CLI emitting `LOGGED_IN`, or by a follow-up `chatpost zhihu status PROFILE` command.

#### Three-button pattern

- `打开登录链接` — URL button; opens the page.
- `我已授权` / `我已打开` — callback button; tells the agent to run `status` immediately.
- `取消` — callback button; tells the agent to stop the flow.

Use the three-button pattern when the user expects the agent to react to their explicit card action. The URL click itself still is not the callback.

### Do Not

- Do not close the browser/page immediately after sending the link.
- Do not treat card-send success as login success.
- Do not treat URL-button navigation as a callback.
- Do not reuse expired QR/login links.
- Do not publish tokenized live login URLs to public docs or shared skills.
- Do not route Zhihu login through another platform's QR or login flow.

## Verification Workflow

For a real profile login validation:

1. Run `chatpost zhihu status PROFILE --registry PATH --output json -I`.
2. Run `chatpost zhihu login PROFILE --registry PATH --timeout 900 --output json -I` and keep it alive.
3. Deliver the emitted `login_url` immediately to the user via a Feishu/Lark card; redact it in summaries.
4. Wait for the same command to emit `LOGGED_IN`, or ask the user to click a separate callback button and then run `status`.
5. Run `status` again to prove the persisted Profile is logged in.
6. For draft acceptance, run `chatpost zhihu draft PROFILE SOURCE --dry-run --output json -I` first.
7. If dry-run is clean and the user requested a real draft, run exactly one real `draft` command with `--receipt PATH`.
8. Verify receipt mode `0600`, `status=DRAFT_CREATED`, locator presence, and cleanup statuses. Do not expose the locator if it is private or account-identifying.
9. Save the command shapes, exit codes, redacted stdout/stderr summaries, and acceptance evidence to the project report/MkDocs Quickstart. Redact tokenized live login URLs and credentials.
10. Run docs/tests/MkDocs, commit, push, and read back Preview Docs/CI when the repository task requires it.

A successful login run-through must include both:

- `login` stdout containing `LOGIN_REQUIRED` followed by `LOGGED_IN`; and
- a separate `status` command returning `LOGGED_IN` for the same profile.

A successful draft run-through must include:

- dry-run returning `DRY_RUN_OK`;
- real create returning `DRAFT_CREATED` exactly once;
- receipt mode `0600`;
- cleanup statuses closed; and
- no automatic retry after ambiguous write-path failure.

## Regression Checks

Tests/docs should prove:

- `status/login/logout` do not require `WECHATSYNC_TOKEN`, extension dirs, bridge ports, or publishing-adapter auth.
- `profiles` commands do not launch a browser.
- `login` returns `already_logged_in` for an existing logged-in Profile.
- `login` emits the page-owned URL before waiting for manual auth.
- `draft --dry-run` does not start a browser or create a draft.
- real `draft` records strict success/unknown status and writes a `0600` receipt.
- live documentation shows real command transcripts, not prose-only success claims.
- public docs omit or redact tokenized live login URLs, QR payloads, account names, account URLs, cookies, and tokens.
- the Zhihu skill and docs do not include other-platform login instructions.

## References

- `references/zhihu-login-card-and-product-draft.md` — reusable login-card, expired-handoff, and one-shot product draft acceptance lessons.
