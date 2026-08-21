# ChatMemory Agents

This repository is shared ChatArch knowledge memory. Treat every tracked file, commit title, commit body, PR title, PR body, review comment, and changelog entry as public-facing unless the user explicitly says otherwise.

## Privacy Boundary

- Do not write concrete server aliases, usernames, home directories, private workspace paths, chat ids, thread ids, internal hostnames, private proxy helper paths, tokens, cookies, API keys, passwords, or account-specific URLs into shared skills or public repo notes.
- Use placeholders such as `<workspace>`, `<user>`, `<worker-host>`, `<machine-branch>`, `<proxy-helper>`, `<node-bin-dir>`, and `<chat-id>`.
- Keep concrete machine values only in workspace-local non-shared skills, private project run JSON, or user-provided local config files that are not committed to this repo.
- When cleaning already-committed environment-specific details, do not repeat those details in the new commit message, PR title/body, review comment, report, or public diff summary.
- Before opening a PR, scan the staged diff and PR text for private names/paths. If the cleanup itself would reprint sensitive removed lines in a public review UI, use an approved redaction/diff-suppression path rather than quoting them.

## Skill Writing

- Shared skills should describe reusable procedures, trigger conditions, validation gates, and placeholder-based command templates.
- Machine-specific instructions belong in that machine's workspace-local `skills/local/` copy, not in shared `Skills/common`, `Skills/chatarch`, or template files.
- If a workflow requires a host-specific executable path or proxy setup, write `<agent-command>`, `<node-bin-dir>`, or `<proxy-helper-if-needed>` in the shared skill and record concrete values in the active task/project notes only.
