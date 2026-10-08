---
name: chatpypi-tool-service-operations
description: Use when serving or calling ChatPyPI REST/MCP tools. Configure local/service mode, account bindings, and artifact-only uploads.
version: 0.1.0
reference:
  - chatpypi-publisher-management: "Apply PyPI Publisher ownership and mutation rules when invoking the Publisher tools."
---

# ChatPyPI Tool Service Operations

Use ChatPyPI 0.2.14 or newer for its headless REST/MCP service and local/service CLI modes. This skill covers operating and consuming those tools, not package registration orchestration or release management.

## Verify the installed surface

```bash
chatpypi --version
chatpypi --tree
chatpypi serve --help
```

Install `ChatPyPI[service]` into the approved ChatArch runtime. Verify that imports resolve to the intended installed package, not an older editable checkout. Do not treat a pre-feature public version or a candidate wheel as proof the feature is released.

## Choose local or service execution

```bash
chatenv set CHATPYPI_MODE=local -I
chatenv set CHATPYPI_BASE_URL=https://tools.example.test -I
chatenv set CHATPYPI_AUTH_PROFILE=tool-client -I
chatpypi --mode local pkg probe ChatPyPI
chatpypi --mode service pkg probe ChatPyPI
```

- One selector: `--mode local|service`; default comes from `CHATPYPI_MODE`, normally `local`.
- Precedence: explicit CLI option → process environment → active ChatEnv profile → default. Fields extend the existing `pypi` type / `PyPI` namespace.
- `--base-url` overrides the configured service root; do not store a per-operation endpoint.
- `--auth-profile` selects `TokenStore().read("ChatAuth", profile)` and its `values.access_token`. `CHATPYPI_ACCESS_TOKEN` is optional explicit bootstrap, not a PyPI credential.
- Scaffold/build/check, mirrors, local profiles/config and PyPI login/session commands remain local by declared policy. Remote errors never fall back to local execution.
- Remote probe requires a concrete package name. If the CLI omits it, resolve metadata on the client before the request; never infer from server CWD.

## Serve an authenticated backend

Configure an existing issuer/JWKS and a server-owned PyPI account profile:

```bash
chatenv set CHATPYPI_AUTH_ISSUER=https://auth.example.test -I
chatenv set CHATPYPI_AUTH_AUDIENCE=chatpypi-service -I
chatenv set CHATPYPI_AUTH_JWKS_URL=https://auth.example.test/jwks -I
chatenv set CHATPYPI_AUTH_SCOPE=chatpypi:invoke -I
chatpypi --mode local serve --host 127.0.0.1 --port 8765 \
  --profile-binding tool-client=pypi-account
```

- Map authenticated subject/client IDs to existing server profiles with repeated `--profile-binding`; callers cannot override this mapping.
- HTTP requires RS256/JWKS signature, issuer, audience, time and scope validation. Missing configuration refuses startup; missing/invalid access gets 401 and unbound identity gets 403.
- Keep actual PyPI session/upload credentials only on the backend. `CHATPYPI_ACCESS_TOKEN` must contain a ChatAuth access token, never a PyPI key.
- Bind loopback by default. For an explicitly authorized network deployment, set actual client-facing Host values with repeated `--allowed-host`; wildcard bind addresses are not trusted Host names. Resource clients require HTTPS except loopback.
- Stdio is a trusted local process boundary, not network Bearer auth; use `serve --transport stdio --profile-binding tool-client=pypi-account` with exactly one bound account. Do not bridge it anonymously.
- Use the normal target-host supervisor for persistent serving; do not leave production service lifecycle attached to an agent background command. Service deployment, ingress and account provisioning remain separately scoped operations.

## Discover and call the tools

Read `references/interfaces-and-client-usage.md` for the REST tree, request/result schema, MCP client and upload contract. Discover the live catalog with authenticated `GET /api/tools`; do not infer planned CLI entries are available tools.

HTTP and MCP use the same implemented catalog with aliases deduplicated. Queries accept GET parameters and POST JSON; writes accept POST only. Responses contain `tool`, `exit_code`, `stdout` and `stderr`. HTTP success is transport success: inspect the tool exit code too.

## Acceptance and boundaries

1. Test anonymous/invalid-token 401, unbound identity403, unexpected profile/path input422 and protected catalog readback.
2. Compare local and service CLI output/exit for the same controlled operation. An occupied-name probe can correctly return nonzero; do not call that a transport failure.
3. Exercise actual MCP initialize/list/call over the advertised transport, not only direct Python tool calls.
4. Validate real publishing only when separately authorized. Prefer synthetic/mocked upload evidence otherwise; report that distinction.
5. Keep secrets, tokens, private paths and host identities out of output and public artifacts. Close temporary proof listeners through normal lifecycle and verify their ports close.

ChatPyPI does not issue ChatAuth tokens or implement automatic remote refresh. Use the existing authorization flow to renew runtime state; do not fabricate an issuer or pretend the resource package supplies `/oauth/token`. The service invokes one tool per request: no jobs/plans/queues, repo creation, Pages provisioning or composite registration workflow.

User-facing guide: https://arch.gh.wzhecnu.cn/ChatPyPI/tool-service/
