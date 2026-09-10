# New-device email checkpoint

## Diagnose before handing off

Use the selected ChatEnv profile and the installed ChatPyPI command first. If login still ends with a generic unauthenticated error, inspect one bounded attempt's response status, URL path, title, input names/types, and visible form errors. Do not record HTML, cookies, CSRF values, passwords, TOTP codes/secrets, or session payloads.

The transition `/account/login/` → `/account/two-factor/` → `/account/confirm-login/`, with final title `Unrecognized device · PyPI`, proves password and TOTP were accepted. A client that immediately probes the account page can hide this checkpoint behind `redirected to login page`; do not ask the user to change valid credentials.

## Minimal human boundary

Use only an existing, authorized inbox integration if it can read the exact verification email. Do not collect broad mailbox credentials to solve one confirmation. If no such access exists, ask only for the confirmation link from `noreply@pypi.org`, subject `Unrecognized login to your PyPI account`. Do not ask the user to run the same failing CLI command or re-enter password/TOTP.

PyPI's confirmation handler checks that the request IP matches the original login attempt. Consume the link from the original execution host with unchanged network egress; opening it from a phone or unrelated workstation can fail with a device-details mismatch. Recheck official behavior if the provider changes. Avoid repeated login attempts: confirmation email delivery is rate-limited.

## Resume safely

Treat the one-time URL as a credential: accept only HTTPS on the exact expected PyPI hostname and confirmation path; never echo or commit its query. Keep any temporary credential state in the approved ChatArch token store, not the workspace. After approval, save the authenticated session through ChatPyPI's token-store helper, independently run `auth whoami`, and read the exact project's Publisher details before proceeding to tag/publish. Do not claim authenticated state from approval-page navigation alone.

For a user-mandated all-server flow, do not switch to another operator workstation merely because it already has an approved device. Continue the same server flow through public package verification after the checkpoint is resolved.

References: https://github.com/pypi/warehouse/blob/main/warehouse/accounts/views.py (`two_factor_and_totp_validate`, `confirm_login`); https://github.com/pypi/warehouse/blob/main/warehouse/templates/accounts/unrecognized-device.html.
