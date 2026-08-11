# ChatCRS runtime token store

Use this reference when preserving the CRS Admin token-store behavior and release verification lessons from ChatCRS 0.2.4.

## Problem

CRS Admin sessions are login-derived runtime state. Storing a stale Admin session token as a stable env value causes local Admin commands to fail with 401 even when the CRS service and Admin username/password are valid.

## Correct layering

```text
~/.chatarch/envs/CRS/<profile>.env      # stable profile values
~/.chatarch/tokens/CRS/<profile>.json   # dynamic Admin session token state
```

Stable profile values include base URL, username/password entry, and caller API-key references when needed. Runtime token files include structured metadata such as profile, base URL, base-url hash, token type, expiry, created/updated timestamps, and source. They are machine-maintained JSON, not human-edited `.env` files.

## Required behavior

- Runtime token directory and service subdirectory use private permissions.
- Token file uses `0600`.
- Loading a token validates profile and base URL target.
- Expired or target-mismatched tokens are ignored.
- CLI output never prints the token.
- Admin request priority is explicit token > runtime token file > legacy env token > username/password login.
- On Admin 401, login once with stable credentials, save the new token file, retry once, then fail redacted if the retry also fails.
- Token clearing requires an explicit execute flag.

## Verification checklist

Use the installed command surface, not only a source checkout:

```bash
chatcrs --version
chatcrs health --base-url <crs-base-url> --json-output
chatcrs admin token refresh --profile <profile> --json-output
chatcrs admin token status --profile <profile> --json-output
chatcrs admin accounts usage --profile <profile> --json-output
chatcrs admin keys list --profile <profile> --json-output
```

Safe readback fields:

- `version`
- `health_ok`
- `token_refresh_ok`
- `token_saved`
- `token_present`
- `expired`
- `base_url_match`
- `token_file_mode`
- `accounts_usage_count`
- `keys_count`

Do not include real base URLs, usernames, account names, tokens, API keys, cookies, or provider secrets in shared skill artifacts.

## Release pitfall

Local validation on a newer Python can miss CI failures on Python 3.10. Run a Python 3.10 task-local venv or otherwise match CI's oldest supported version. Avoid Python 3.11+ stdlib APIs such as `datetime.UTC`; use `datetime.timezone.utc`.
