---
name: chatpost-zhihu-login-management
description: "ChatPost Zhihu account login/profile management: browser-level status/login/logout, real CLI transcripts, and Feishu handoff cards."
version: 0.1.0
reference:
  - chatarch-cli-package-conventions: "Keep ChatPost CLI leaves thin, visible, and testable."
  - chatarch-mkdocs-docs-alignment: "Record real CLI outputs in MkDocs and verify Preview Docs."
  - hermes-feishu-card-interactions: "Deliver login links through Feishu cards with callback buttons where needed."
---

# ChatPost Zhihu Login Management

## When To Use

Use this skill when working on ChatPost's Zhihu account/profile login foundation, especially when a task mentions:

- `chatpost zhihu login`, `chatpost zhihu status`, or `chatpost zhihu logout`
- adding or validating a Zhihu browser profile
- proving that login is pure browser-level and not tied to a publishing adapter
- writing Quickstart/MkDocs docs with real CLI transcripts
- delivering a Zhihu login link through Feishu/Lark

## Core Model

ChatPost should treat a `PROFILE` as a browser-login container, not as a Zhihu account id, cookie, token, or publishing runner id.

The login foundation has these responsibilities:

1. Read a registry alias such as `<profile>` from `accounts.toml`.
2. Resolve browser/Profile/CDP configuration for that alias.
3. Run browser-level `status`, `login`, or `logout`.
4. Report public account identity when visible from the page (`account_name`, `account_url`).
5. Keep sensitive browser state inside the Profile; never print or export cookies, localStorage, IndexedDB, session values, tokens, SMS codes, or QR tokens.

Publishing/draft readiness belongs in publish/draft/verify flows, not ordinary login/status.

## Expected CLI Surface

For the login-only foundation, the visible tree should stay small and real:

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
    └── logout PROFILE [--registry PATH] [--output text|json] [-I/--no-interactive]
```

`draft`, `verify`, `doctor`, adapter auth, bridge/extension readiness, QR artifact helpers, and publishing tools must not leak into this visible login-only tree.

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
- If public identity is visible, include public `account_name` and `account_url`.
- `UNKNOWN` must not fall back to publishing-adapter auth.

### `login PROFILE`

- Start or attach to the configured browser Profile.
- First run a short browser-page status precheck.
- If already logged in, return `event=already_logged_in` / `status=LOGGED_IN` without emitting a login URL.
- If not logged in, open the Zhihu login page and emit the page-owned `login_url` immediately as `event=login_url` / `status=LOGIN_REQUIRED`.
- Keep the same CLI command alive until either:
  - the user authorizes and the command emits `event=logged_in` / `status=LOGGED_IN`, or
  - the command reaches its timeout and emits `event=login_timeout` / `status=LOGIN_TIMEOUT`.
- Do not run Wechatsync `auth zhihu`, adapter bridge checks, extension readiness, draft publishing, or token refresh before emitting the URL.

### `logout PROFILE`

- Run browser-level status first.
- If already logged out, return a no-op status.
- If logged in, use page/browser-level logout or clear Zhihu origin state.
- Do not read token contents as part of logout.

## Feishu/Lark Handoff Cards

A Feishu/Lark URL button is navigation-only. Do not assume the agent can observe that the user clicked it.

Use one of these patterns:

### Two-button pattern

- `打开登录链接` — URL button; opens the page but does not callback.
- `取消` — callback button; tells the agent to stop the flow.

Completion is detected only by the running CLI emitting `LOGGED_IN`, or by a follow-up `chatpost zhihu status PROFILE` command.

### Three-button pattern

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

## Verification Workflow

For a real profile login validation:

1. Run `chatpost zhihu status PROFILE --registry PATH --output json -I`.
2. Run `chatpost zhihu login PROFILE --registry PATH --timeout 900 --output json -I` and keep it alive.
3. Deliver the emitted `login_url` immediately to the user.
4. Wait for the same command to emit `LOGGED_IN`, or ask the user to click a separate callback button and then run `status`.
5. Run `status` again to prove the persisted Profile is logged in.
6. Save the command, exit code, stdout, and stderr to the project report and MkDocs Quickstart. Redact tokenized live login URLs and any credentials.
7. Run docs/tests/MkDocs, commit, push, and read back Preview Docs.

A successful run-through must include both:

- `login` stdout containing `LOGIN_REQUIRED` followed by `LOGGED_IN`; and
- a separate `status` command returning `LOGGED_IN` for the same profile.

## Regression Checks

Tests/docs should prove:

- `status/login/logout` do not require `WECHATSYNC_TOKEN`, extension dirs, bridge ports, or publishing-adapter auth.
- `profiles` commands do not launch a browser.
- `login` returns `already_logged_in` for an existing logged-in Profile.
- `login` emits the page-owned URL before waiting for manual auth.
- live documentation shows real command transcripts, not prose-only success claims.
- public docs omit or redact tokenized live login URLs.
