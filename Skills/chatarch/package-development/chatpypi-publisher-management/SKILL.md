---
name: chatpypi-publisher-management
description: "Manage PyPI Trusted Publishers with ChatPyPI 0.2.3+: list projects/publishers, inspect details, add GitHub active publishers, and keep pending scoped to true pre-registration cases."
version: 0.1.1
---

# ChatPyPI Publisher Management

## When To Use

Use this skill when the user asks to view, add, update, clean, or verify PyPI publishing / Trusted Publisher configuration for ChatArch packages, especially phrases like:

- "project list / publisher list"
- "publish list"
- "trusted publisher"
- "把某个项目加到 PyPI publish"
- "给 ChatArch/<Repo> 配 PyPI 发布"
- "查看 pending publisher / active publisher"

This skill covers PyPI-side publisher configuration. Pair it with `python-package-release-with-chattool-pypi` / `python-package-publishing` for release gates and with `chatgh-pr-and-ci-workflow` when repository PRs/tags/workflows are involved.

## Core Rule

For existing PyPI projects, Publisher management is **active state**, not pending. Use a working released `chatpypi` command at version 0.2.3 or newer. Prefer the installed command when it is healthy; if the shell command is shadowed or stale, use the local ChatPyPI checkout venv as the operator fallback:

```bash
BIN=$(command -v chatpypi || true)
if [ -z "$BIN" ] || ! "$BIN" --version >/dev/null 2>&1; then
  BIN="$HOME/Playground/core/ChatPyPI/.venv/bin/chatpypi"
fi
$BIN --version                    # should be 0.2.3 or newer for direct publisher writes
$BIN auth login -e RexWzh --format json
$BIN auth whoami -e RexWzh --format json
$BIN publisher detail <ProjectName> -e RexWzh --format json
$BIN publisher add-github <ProjectName> --owner ChatArch --repo <Repo> --workflow publish.yml --environment "" -e RexWzh --format json
$BIN publisher pending-list -e RexWzh --format json
```

Do not guess the GitHub owner/repository from the PyPI username or session profile. For ChatArch packages, the Trusted Publisher owner is normally `ChatArch`, not `RexWzh` and not the PyPI project name as an owner.

```text
PyPI project: ChatSage / chatsage
GitHub owner: ChatArch
GitHub repository: ChatSage
Workflow filename: publish.yml
Environment: blank / (Any), unless the existing project/workflow explicitly uses an environment
```

`RexWzh/askchat` is an existing exception, not the pattern to copy to ChatArch packages.

## Current ChatPyPI 0.2.3 Publisher Tree

```text
chatpypi publisher
├── list            # account overview: active/pending counts and project names
├── detail          # project-level active Publisher details
├── add-github      # direct active GitHub Publisher add/verify for an existing project
├── pending-list    # list true pending Publisher entries
├── pending-add     # only for explicit pre-registration / nonexistent-project pending exceptions
└── pending-remove  # remove or confirm absence of a stale pending Publisher by exact target
```

Expected active Publisher readback for ChatArch packages:

```text
active_count >= 1
pending_count == 0 unless deliberately testing a pre-registration pending case
publisher_details include:
  publisher: GitHub
  repository: ChatArch/<Repo>
  workflow: publish.yml
  environment: (Any)  # when the PyPI page environment is blank
```

## ChatArch New Project Baseline

For this user's ChatArch packages, Publisher setup normally happens **after** the PyPI project exists. If `chatpypi pkg probe <ProjectName>` / PyPI JSON says the project does not exist, the expected bootstrap is:

1. Create and upload a minimal local `0.0.1` placeholder with the controlled PyPI account.
2. Re-probe PyPI and confirm the project exists and version `0.0.1` is visible.
3. Configure/verify the active GitHub Trusted Publisher on the project with `publisher add-github`.
4. Confirm `publisher detail` shows the exact owner/repo/workflow/environment and `pending_count=0`.
5. Only then use the repository's tag-driven GitHub Actions workflow for the real feature release.

Pending publishers for nonexistent projects are supported by PyPI, but in this user's workflow they are an exception/recovery path, not the default. Do not summarize a pending publisher as “the project exists,” and do not proceed as if ownership is proven until the real PyPI project or active publisher readback is verified.

## What Counts As Pending

Use `pending-*` only when the state is genuinely pending:

1. PyPI's own pre-registration / pending Trusted Publisher feature for a project that does not exist yet;
2. QR/device/browser verification;
3. CAPTCHA, email verification, password confirmation, 2FA bootstrap, or other complex checkpoint-heavy flows;
4. stale pending cleanup after an earlier wrong path.

Do **not** call these pending:

- existing-project Publisher add/detail/readback;
- package probe/build/check/upload;
- PyPI JSON/simple/pip-index version checks;
- GitHub Actions publish status;
- clean install verification.

If an operation can be directly implemented, fix or use ChatPyPI instead of inventing a pending workflow.

## Safe Workflow For Existing Projects

```bash
BIN=$(command -v chatpypi || true)
if [ -z "$BIN" ] || ! "$BIN" --version >/dev/null 2>&1; then
  BIN="$HOME/Playground/core/ChatPyPI/.venv/bin/chatpypi"
fi
PROJECT=ChatECNU
OWNER=ChatArch
REPO=ChatECNU
WORKFLOW=publish.yml

$BIN auth login -e RexWzh --format json
$BIN auth whoami -e RexWzh --format json
$BIN publisher detail "$PROJECT" -e RexWzh --format json
$BIN publisher add-github "$PROJECT" --owner "$OWNER" --repo "$REPO" --workflow "$WORKFLOW" --environment "" -e RexWzh --format json
$BIN publisher pending-list -e RexWzh --format json
```

Interpretation:

- `posted=false` and `already_active_before=true` means the command found the correct active Publisher and did not mutate PyPI.
- `environment=(Any)` is the expected summary when the PyPI page environment is blank.
- `pending_count=0` is expected for normal existing-project Publisher setup.

## Safe Workflow For Stale Pending Cleanup

Only run this when a previous wrong path may have left a pending Publisher:

```bash
$BIN publisher pending-remove "$PROJECT" --owner "$OWNER" --repo "$REPO" --workflow "$WORKFLOW" --environment "" -e RexWzh --format json
```

Expected no-op shape when no stale pending exists:

```text
ok=True
removed=False
pending_count=0
```

If a matching pending exists and PyPI exposes a matching remove form, ChatPyPI 0.2.3 removes it and reads back. If not, it fails loudly rather than pretending cleanup happened.

## Safety Rules

- Never print `PYPI_SESSION_TOKEN`, cookies, CSRF token values, passwords, TOTP secrets, or API tokens.
- Use a named ChatEnv profile such as `-e RexWzh` for account-specific PyPI management.
- Before writing to PyPI, confirm the logged-in account with `auth whoami -e <profile>`.
- If `auth whoami`, `publisher detail`, or `publisher add-github` says the PyPI session is not logged in / redirected to login, refresh it with `auth login -e <profile> --format json`, then retry the same Publisher command. Session expiry is not a release blocker and must not trigger Twine/token/manual upload fallback.
- Treat adding/removing/updating Trusted Publishers as real remote mutations.
- For real ChatArch releases after the initial `0.0.1` placeholder/name-claim, active Publisher readback is a hard gate: no active Publisher readback means no tag and no publish attempt.
- Prefer blank environment for the current ChatArch baseline when existing similar projects show `(Any)`. Use `environment: pypi` only when the GitHub workflow and PyPI publisher are both explicitly configured for that environment.
- Do not assume PyPI exposes a public JSON API for publisher configuration; the practical automation path is authenticated PyPI web forms plus post-write readback through ChatPyPI.

## ChatECNU 2026-06-27 Correction

This workflow was corrected after the ChatECNU release:

- The initial attempt overused a pending Publisher for a nonexistent project.
- The correct ChatArch flow was to upload `ChatECNU==0.0.1` as a real placeholder project, then configure active `ChatArch/ChatECNU` Publisher, then publish `0.1.0` through the tag-driven GitHub Actions workflow.
- The first `v0.1.0` publish run failed with `invalid-pending-publisher: valid token, but project already exists`; after confirming account pending was gone and project active Publisher existed, rerunning the workflow succeeded.
- Final readback: `ChatECNU==0.1.0`, active Publisher `ChatArch/ChatECNU`, workflow `publish.yml`, environment `(Any)`, `pending_count=0`.

## Common Pitfalls

- Copying `RexWzh/askchat` as a pattern for ChatArch packages. It is an exception.
- Treating the PyPI username/profile as the GitHub owner.
- Assuming the overview page includes repository/workflow/environment details; use `publisher detail <project>` for project-level details.
- Treating `#errors` in old web-form experiments as failure without inspecting readback.
- Adding `environment: pypi` on the PyPI side while the GitHub workflow has no matching `environment: pypi`, or vice versa.
- Printing raw session/cookie/CSRF values during debugging.
- Keeping project-local PyPI scripts after ChatPyPI exposes the capability; prefer released `chatpypi 0.2.3+`.
