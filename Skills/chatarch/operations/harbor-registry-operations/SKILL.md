---
name: harbor-registry-operations
description: Use when operating Harbor registries and official CLI.
version: 0.1.1
---

# Harbor Registry Operations

## Boundaries and tool choice

Use the official Harbor service, official `goharbor/harbor-cli` for management, and Docker/other OCI clients for image transport. A REST API is not the same thing as a management CLI. Before proposing a custom wrapper, check the official CLI's registered help, maintained release, authentication, required operations and compatibility against the deployed service. Prefer the existing CLI when verified; document gaps before considering another package.

For ChatArch onboarding, follow the ingress catalog's canonical `SITES.md` shared account/email/password on every application host unless the user declares an exception. Provision only those fields privately, without another cross-host reuse question. Keep unrelated account databases, tokens and personal profiles out of the transfer. Deploy the service and verify its real workflow before catalog/homepage registration or tool-development work.

## Deployment and exposure

- Inspect the named host's resources, existing Harbor/registry containers, persistent mounts, compose labels, occupied ports, historical projects and exact ingress name first. Preserve existing registries and data; a cached image or vhost is not a running Harbor.
- Pin an official release and verify the downloaded asset against the publisher's digest. Use the verified installer templates and image tags, with all persistent state under the resolved service runtime in `CHATARCH_HOME`.
- Review preparation mounts and privilege requirements. Restrict preparation to the service's runtime where possible. Audit the generated Compose file before starting it: loopback bindings, persistent paths, explicit restart policy and bounded resources. Never run an installer `down -v` against an established deployment merely to validate it.
- Route through the established local/public entry. Reuse valid shared certificates and bridges, with verified upstream Host/SNI/CA. Trust forwarding metadata only from the proven ingress peer; DNS destination and the peer's chosen outbound address need not be identical.
- Back up one affected vhost, validate Nginx, reload gracefully and read back the real endpoint. A brief bounded readback retry can cover asynchronous worker replacement; do not weaken TLS or skip the syntax gate.
- When a shared local entry moves, verify the exact existing DNS owner, current DDNS/host identity, target route and old value before updating it. Preserve record identity/TTL and unrelated records, read back provider and authoritative DNS, and record any operator hosts snapshot explicitly. Do not hide a browser resolver override as ordinary DNS success.

## Identity and session acceptance

Use native Harbor authentication. Create the declared shared human identity, verify it through `/api/v2.0/users/current`, close unrestricted signup where required, and create an intentional private project. After a sysadmin update, read back the actual `sysadmin_flag`; HTTP success alone can conceal an ignored payload field.

Exercise the real browser login, authenticated project view and logout. Inspect the actual `sid` session cookie, not only the CSRF cookie, and require Secure/HttpOnly on HTTPS. If external TLS terminates before Harbor's HTTP proxy, preserve origin metadata and apply a narrowly targeted cookie transport override in the Harbor-owned proxy where needed. Validate and reload that proxy, repeat the complete flow, and retain the override in the deployment recipe after future preparation. Authentication stays in Harbor.

## Official CLI configuration and verified command surface

Install a checksum-verified official binary under the service runtime. Pass `--config <private-config>` explicitly rather than allowing credentials to fall into an unrelated default directory. A thin command entry may only supply this path; it does not justify a new wrapper repository. Keep config mode `0600` and its parent private.

```bash
harbor --config <private-config> login <https-origin> --username <shared-user>
harbor --config <private-config> version
harbor --config <private-config> health
harbor --config <private-config> --output-format json project list --name <project>
harbor --config <private-config> --output-format json repo list <project>
harbor --config <private-config> --output-format json artifact list <project>/<repository>
```

Read the installed command's help before automation. Prefer interactive password input or an already-initialized private context, never a password flag or raw credential output. Verify whether that release's `--password-stdin` really supports non-TTY input; if it requires a TTY, initialize through a bounded owned non-echoing terminal and verify the resulting context. Do not claim generic unattended login support from the flag name alone.

Normalize JSON deliberately: some commands return an array while others wrap results in `Payload` and expose `XTotalCount`. Paginate and reconcile totals before reporting an all-items result. Read-only command compatibility does not prove every administrative write, scanner or replication feature is supported.

## Client/server and API boundary

Run the official CLI wherever a supported client can reach the configured HTTPS Harbor origin; the client is not required to share the service host and does not need SSH or the server Docker daemon. Keep management REST `/api/v2.0/`, the Swagger API Explorer, and Registry data-plane `/v2/` distinct. Read back authenticated identity and a real list before claiming remote access. Preserve server/runtime migration as a separate operation.

For complete capability checks, build the visible command tree recursively from real installed help and reconcile node coverage; do not invent a `--tree` option or drop longest Cobra command names because their description padding is only one space. See [official CLI and API contract](references/official-cli-api.md) for the versioned tree, platform/placement boundary, API examples and verified automation limits.

## Registry acceptance and CI

Perform an authenticated real push and pull with a tiny task-owned image in a private project. Compare pulled image identity and artifact digest with the Harbor API, check anonymous private-manifest rejection, and clear the test Docker authentication. `/v2/` returning a HTTPS Bearer challenge with the correct token realm is normal; a landing page or healthy GET alone is insufficient.

For CI, prefer project-scoped Robot Accounts with the minimum required rights rather than the shared website administrator. Create/rotate credentials only within the authorized scope, keep them in a secret provider, and use Docker's password-stdin without shell tracing. Distinguish Docker's stdin behavior from the management CLI's implementation. Do not enable insecure registries or skip TLS to make tests pass.

After the service gate, register the accepted public URL in the canonical catalog and common homepage, use the built-in SVG cover unless custom artwork is requested, and attach the existing service monitoring. Regenerate through the live dashboard's native pipeline, respecting its refresh lock, then verify generated counts, health, actual homepage/card links and user-visible navigation. A written inventory is not a loaded card.

## Sources

- https://github.com/goharbor/harbor
- https://github.com/goharbor/harbor-cli
- https://goharbor.io/docs/
