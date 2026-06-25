---
name: chatnet-ecnu-default-visitor
description: Set or refresh ECNU default visitor accounts through ChatNet safely, including login fallback and secret redaction.
version: 0.1.0
---

# ChatNet ECNU Default Visitor

## When To Use

Use this skill when the user asks to create, set, refresh, or sync the default ECNU visitor accounts using ChatNet, especially phrases like:

- `chatnet ecnu` 访客账号
- 默认访客账号
- `set default`
- `chatnet ecnu visitor default`

## Safety Rules

- Never write real ECNU usernames, visitor account names, passwords, cookies, sessions, CSRF tokens, or long token-like values into chat, project notes, skills, reports, or reusable examples.
- It is OK to mention environment variable names such as `ECNU_USERNAME`, `ECNU_PASSWORD`, `ECNU_VISITOR_PASSWORD1`, `ECNU_VISITOR_PASSWORD2`, and `ECNU_VISITOR_REMARK`; do not include their values.
- Treat `chatnet ecnu visitor default` as a real external account operation. It may create accounts or update visitor passwords/remarks.
- If login requires SMS verification, stop and ask the user for the SMS code; do not try to bypass it.
- Use redacted logs for records. Redact account-like values, numeric IDs, cookies, tokens, passwords, and session material before writing persistent notes.

## Procedure

1. Establish the workspace first if working in `~/Playground`:
   - read `AGENTS.md`
   - read `projects/README.md`
   - create or update a small task project when this is a real operation
2. Verify ChatNet is available without exposing secrets:

   ```bash
   command -v chatnet
   chatnet --help
   chatnet ecnu visitor --help
   ```

3. Run the default visitor sync with a redaction wrapper rather than streaming raw output directly into notes:

   ```bash
   chatnet ecnu visitor default
   ```

4. If it fails with a login/session/cookie-expired error such as a redirect to the login page, refresh login first:

   ```bash
   chatnet ecnu login
   chatnet ecnu visitor default
   ```

5. If `chatnet ecnu login` reports that an SMS code is required, ask the user for the code and then run:

   ```bash
   chatnet ecnu login --sms-code '<code-from-user>'
   chatnet ecnu visitor default
   ```

6. Record only a safe summary:
   - command name
   - exit code
   - whether login refresh was needed
   - whether default visitor sync completed
   - path to a redacted log if one was written

## Recommended Redaction Targets

Before writing any command output into project notes, redact at least:

- `account=<anything>` -> `account=<ACCOUNT>`
- `username=<anything>` -> `username=<REDACTED>`
- `password`, `cookie`, `session`, `token`, `csrf`, `secret` values -> `<REDACTED>`
- long numeric IDs -> `<NUMBER>`
- long token-like strings -> `<LONG_TOKEN>`

## Verification

Successful completion is indicated by `chatnet ecnu visitor default` exiting with code `0` and reporting that the default visitor sync completed. Do not repeat the actual visitor account identifiers in the user-facing summary unless the user explicitly asks and it is safe for the channel.

## Pitfalls

- A cookie/session may expire even when the config is otherwise correct. In that case, run `chatnet ecnu login` and retry the default sync.
- `chatnet ecnu login` may use OCR-backed CAPTCHA solving and can succeed without manual CAPTCHA input; if SMS is required, user input is still needed.
- Raw command output can include visitor account identifiers and IDs. Never copy raw output into a skill.
