---
name: crs-service-operations
description: Use when operating CRS / Claude Relay Service and ChatCRS HTTP-first management workflows.
version: 0.1.0
---

# CRS Service Operations

Use this skill when the task touches CRS / Claude Relay Service, ChatCRS, CRS Admin/API keys, CRS account state, or CRS-related ChatArch package release/verification.

## Boundaries

- Prefer HTTP/Admin/API-key operations through ChatCRS or direct CRS HTTP endpoints. Do not fill missing ordinary management capability with SSH, direct Redis writes, local app scripts, or browser cookies.
- Keep host lifecycle operations separate from HTTP management. Process, Redis, Nginx, filesystem, and `127.0.0.1` checks require the service host or an explicit tunnel; ChatCRS HTTP commands can run from the local control plane when the public base URL and profile credentials are valid.
- Redact CRS API keys, Admin session tokens, provider tokens, cookies, passwords, JWT/encryption keys, Redis credentials, and connection strings. Reports may include safe fields such as status, counts, file modes, base-url match booleans, and package versions.
- Shared skills must use placeholders such as `<crs-base-url>`, `<profile>`, `<account-id>`, and `<api-key-name>`. Concrete production URLs, usernames, account names, hostnames, and machine paths belong in task reports or machine-local skills only.

## CRS Admin auth model

Upstream-style CRS Admin auth is username/password plus a login-derived session token:

1. `POST /web/auth/login` validates the Admin username/password.
2. CRS returns a bearer session token with an expiry.
3. Admin API requests use `Authorization: Bearer <admin-session-token>`.
4. There is no durable fixed Admin bearer-token or refresh-token contract for ChatCRS to rely on.

Keep these separate:

- Admin session token: short-lived management token for `/admin/*`.
- CRS caller API key: client key for `/openai/*` and key-info/model requests.
- Provider/OAuth token: upstream model-provider credential owned by an account record.

## ChatCRS profile and token-store pattern

Stable profile values stay in ChatEnv:

```text
~/.chatarch/envs/CRS/<profile>.env
```

Dynamic Admin session tokens belong in the parallel runtime token store:

```text
~/.chatarch/tokens/CRS/<profile>.json
```

Expected behavior for ChatCRS 0.2.4+:

1. Explicit `--admin-token` / explicit token wins.
2. Otherwise use a valid runtime token file matching the current base URL.
3. Legacy `CRS_ACCESS_TOKEN` is only a fallback.
4. If no valid token exists, login with stable username/password and save the runtime token file.
5. If an Admin request returns 401 and stable credentials are available, login once, update the token file, and retry the original request once.
6. Token commands must never print token values; `clear` should require an explicit execute flag.

Useful commands:

```bash
chatcrs health --base-url <crs-base-url> --json-output
chatcrs admin login --profile <profile> --save-token --json-output
chatcrs admin token status --profile <profile> --json-output
chatcrs admin token refresh --profile <profile> --json-output
chatcrs admin token clear --profile <profile> --execute --json-output
chatcrs admin accounts usage --profile <profile> --json-output
chatcrs admin keys list --profile <profile> --json-output
```

`chatcrs health` may not accept `--profile`; use an explicit `--base-url` when validating public reachability.

## Local实操 verification

When the user asks whether ChatCRS really works, verify the installed command the user will run, not only editable source code:

```bash
chatcrs --version
chatcrs health --base-url <crs-base-url> --json-output
chatcrs admin token refresh --profile <profile> --json-output
chatcrs admin token status --profile <profile> --json-output
chatcrs admin accounts usage --profile <profile> --json-output
chatcrs admin keys list --profile <profile> --json-output
```

Report only redacted/safe evidence:

- command path and package version;
- health `ok`/status;
- token refresh `ok` and `token_saved`;
- token present, expired false, base URL matches, token-file permission mode such as `0600`;
- account/key counts;
- Git/PyPI/tag identifiers only when release verification is in scope.

## Account-state and routing checks

If the user asks for current account state, answer the account objective first. A CRS `/health=200` does not prove account routing.

Preferred read-only report shape:

- accounts by platform/provider;
- active/schedulable/shared/dedicated status;
- rate-limit and reset-window state, distinguishing current limits from stale flags;
- direct API-key bindings and their routing consequence;
- temporary-unavailable/cooldown overlays when visible through authorized read-only surfaces.

Do not create temporary keys, reset account status, refresh provider tokens, clear limits, or mutate Redis unless the user explicitly authorizes that practice step.

## Release and package verification

For ChatCRS package releases:

1. Run tests on the oldest supported Python used by CI, not only the operator's newest Python.
2. Run docs/build/twine gates.
3. Open a PR and wait for PR CI.
4. Squash merge only after the user authorizes merge/release or the refresh/release workflow explicitly includes it.
5. Tag the merged default-branch commit; do not tag the feature branch.
6. Wait for tag-triggered PyPI Trusted Publishing.
7. Verify PyPI JSON/simple index, clean install from official PyPI, installed `chatcrs --version`, and a live redacted ChatCRS profile smoke when credentials are available.

Avoid Python-version drift: for Python 3.10 compatibility use `datetime.timezone.utc` rather than Python 3.11+ conveniences such as `datetime.UTC`.

## References

- `references/chatcrs-runtime-token-store.md`
