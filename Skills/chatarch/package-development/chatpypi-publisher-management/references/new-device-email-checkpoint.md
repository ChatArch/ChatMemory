# New-device email checkpoint

## Diagnose before handing off

Use the selected ChatEnv profile and the installed ChatPyPI command first. If login still ends with a generic unauthenticated error, inspect one bounded attempt's response status, URL path, title, input names/types, and visible form errors. Do not record HTML, cookies, CSRF values, passwords, TOTP codes/secrets, or session payloads.

The transition `/account/login/` → `/account/two-factor/` → `/account/confirm-login/`, with final title `Unrecognized device · PyPI`, proves password and TOTP were accepted. A client that immediately probes the account page can hide this checkpoint behind `redirected to login page`; do not ask the user to change valid credentials.

## Align network egress before another confirmation

When a user says the email link was already confirmed, first check the selected profile's actual session and network route. Do not reinterpret that statement as a request to inspect their mailbox or browser. Compare the effective proxy selection for the PyPI hostname, a bounded public egress-IP probe, and the intended confirmation route. Host identity alone is insufficient: a desktop can connect directly while a CLI loaded the workspace proxy.

PyPI recognizes the user/IP pair, not merely the machine name. If the approved direct route authenticates and the proxy route still requests confirmation, keep PyPI on the verified route. Back up the approved workspace network configuration and add a PyPI-only `no_proxy`/`NO_PROXY` exception when appropriate; do not disable the GitHub proxy or switch hosts. Verify a fresh CLI `auth whoami` and exact Publisher readback after loading only the normal persisted configuration, with no temporary override.

A CLI that exits at the email checkpoint is not necessarily waiting for a callback. Do not blame a missing wait or ask for another email until the provider's continuation/IP rules and actual route have been checked. Once the IP is confirmed, a fresh login from that same route can establish and save the CLI session.

SSH terminal binding does not by itself prove desktop-tool routing. Verify the desktop driver's host/display before any GUI use; never use a gateway-local computer tool as if it controlled the SSH host. HTTP/CLI package publishing normally requires no GUI access.

Treat proxy fields as secret-bearing even when named `host`: configured strings may embed userinfo. Strip userinfo from saved diagnostics and filter file-tool diff context before displaying edits near credential lines.

## Minimal human boundary

Use only an existing, authorized inbox integration if it can read the exact verification email. Do not collect broad mailbox credentials to solve one confirmation. If no such access exists, ask only for the confirmation link from `noreply@pypi.org`, subject `Unrecognized login to your PyPI account`. Do not ask the user to run the same failing CLI command or re-enter password/TOTP.

PyPI's confirmation handler checks that the request IP matches the original login attempt. Consume the link from the original execution host with unchanged network egress; opening it from a phone or unrelated workstation can fail with a device-details mismatch. Recheck official behavior if the provider changes. Avoid repeated login attempts: confirmation email delivery is rate-limited.

## Resume safely

Treat the one-time URL as a credential: accept only HTTPS on the exact expected PyPI hostname and confirmation path; never echo or commit its query. Keep any temporary credential state in the approved ChatArch token store, not the workspace. After approval, save the authenticated session through ChatPyPI's token-store helper, independently run `auth whoami`, and read the exact project's Publisher details before proceeding to tag/publish. Do not claim authenticated state from approval-page navigation alone.

For a user-mandated all-server flow, do not switch to another operator workstation merely because it already has an approved device. Continue the same server flow through public package verification after the checkpoint is resolved.

References: https://github.com/pypi/warehouse/blob/main/warehouse/accounts/views.py (`two_factor_and_totp_validate`, `confirm_login`); https://github.com/pypi/warehouse/blob/main/warehouse/templates/accounts/unrecognized-device.html.
