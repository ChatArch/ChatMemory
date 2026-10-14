# Authenticated service onboarding contract

Use this reference when a reusable Python package provides login, account APIs and optional browser templates to other host applications.

## Product boundary

- Separate one shared HTTP contract from one centralized identity service. Same-origin router mounting is not cross-site SSO, shared Cookie state or a generic external-provider CRUD adapter.
- Keep credential backend, managed-account lifecycle, session store and frontend presentation independently selectable. An authentication callback does not imply account-create/update/delete support.
- Have HTTP, CLI and Python adapters call the same domain policy rather than duplicating account, CSRF or authorization logic in a template or client.

## Discoverability and navigation

- Build a read-only operation directory from actual registered methods and paths. Advertise backend capabilities and available pages truthfully; headless mode must not expose nonexistent default HTML or assets.
- Separate a stable discovery-format version from the actual installed package version. Do not hardcode a release version into an HTTP handler that will survive later releases.
- Derive URLs from the configured prefix and trusted application mount metadata, never arbitrary forwarded headers. Apply Host validation and no-store; the discovery response must contain no credentials, actor directory, session/CSRF values or storage paths.
- Document request fields, object-level policy, response and error semantics explicitly. A route catalog is not a complete OpenAPI request/response schema.
- Resolve menu identity and links from the live server session. A stale role, password or enabled-state change must not retain old management navigation; underlying API authorization remains the real boundary.
- Keep the host HTML containing identity non-share-cacheable. Let the host choose gear, ordinary links, a template override or trusted renderer without making frontend choice alter account policy.

## Factory and template lifetime

- Use an explicit app/router factory with validated origin and instance; do not create production accounts, install software or start a listener during import.
- Close resources created by the factory, but leave injected/shared service objects caller-owned. Document this distinction and prove one application's shutdown does not destroy another consumer's service.
- Keep production HTTPS defaults. Allow HTTP only as an explicit, validated loopback convenience; never infer production trust from request headers.
- Bootstrap the first privileged account through a trusted explicit setup path with an environment-variable name or secure input, not a password in argv or a production default.
- Make a menu an optional reusable fragment with scoped CSS and native keyboard/touch semantics. Do not emit a fake settings control when headless mode provides no page links, or leave duplicate old/new navigation in default pages.

## Acceptance from a published artifact

- Run a complete new-host example against a wheel outside the checkout, then against a fresh exact-name public install. Read module/distribution provenance, pip check and actual CLI trees; compare measured package bytes when carrying forward identical-artifact review evidence.
- Use separate browser contexts for ordinary/admin/owner identities. Exercise native login, menu navigation, a real management write with readback, denied elevation, self-profile/password changes and session invalidation.
- Verify gear, links and a custom host entry against the same protected API, including explicit mounted prefixes and JSON-only mode.
- Inspect desktop, intermediate and mobile screenshots. Test popup bounds against its owning button/content column as well as document overflow: a page can fit the viewport while its menu protrudes outside its card.
- For no-JavaScript credential safety, check the disabled fieldset attribute and the actual child input's disabled behavior. A driver's disabled predicate on the fieldset itself may not represent the inherited native input state.
- Preserve CSP and original permission checks during acceptance. Close the owned browser normally and request graceful app shutdown; prove the listener and app thread exited before claiming cleanup.

Keep legacy-provider migrations, shared identity centers and deployment of existing consumers as separately authorized work. A released provider or a synthetic demonstration is not evidence that a production consumer has switched.
