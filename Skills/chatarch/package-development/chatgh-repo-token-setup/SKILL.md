---
name: chatgh-repo-token-setup
description: Configure repo-local HTTPS token auth for ChatArch repositories immediately after repo creation or first checkout so git fetch/push works without SSH.
version: 0.1.0
tags:
  - ChatArch
  - ChatGH
  - GitHub
  - repository
  - credentials
reference:
  - package-development: "主题索引；用于定位 ChatArch package/repo workflow 相关 skill"
  - python-package-release-with-chattool-pypi: "新建 ChatArch Python 包时会调用本 repo auth 流程"
  - chatgh-pr-and-ci-workflow: "PR/CI 检查中区分 GitHub API auth 与 git transport auth"

---

# ChatGH Repo Token Setup

## Purpose

Use this skill when a ChatArch / Chat-series repository is newly created, first checked out, or newly initialized locally and needs to push/fetch over HTTPS.

This is not a PR/CI skill. `chatgh pr`, `chatgh repo-perms`, and other GitHub API commands can use a token from ChatEnv directly. `chatgh set-token` exists for a different reason: **configure the local git repository so HTTPS `git push` / `git fetch` can authenticate without SSH and without putting a token in the remote URL.**

## Core rule

For ChatArch / Chat-series repositories:

- Use HTTPS remotes.
- Configure repo-local token auth with `chatgh set-token` at repository creation / first local checkout time.
- Do not switch to SSH clone/push as a workaround for missing HTTPS credentials.
- Do not put tokens in remote URLs.
- Do not print tokens, `.git/config` extraHeader values, or decoded Authorization headers.

## When to run

Run this immediately after any of these:

1. `chatgh repo create ...` creates a new remote repo.
2. A local package/repo scaffold is initialized and `origin` is set for the first time.
3. A repo is cloned/checked out on a new machine and needs HTTPS push.
4. `git push` / `git fetch` over HTTPS fails with an auth error even though ChatGH API commands work.

## Standard setup

From the local repository root:

```bash
cd ~/Playground/core/<RepoName>

git remote add origin https://github.com/ChatArch/<RepoName>.git 2>/dev/null || \
  git remote set-url origin https://github.com/ChatArch/<RepoName>.git
git remote set-url --push origin https://github.com/ChatArch/<RepoName>.git

# Prefer the password-style interactive prompt; avoid putting a real PAT in shell history or process listings.
chatgh set-token
```

If using the existing ChatGH/ChatEnv token path programmatically, never print the token. Pipe/pass it directly to `chatgh set-token` only through a non-logging helper and redact command output if needed; do not show the raw command with the token value.

## Verification

Verify capability, not credential content:

```bash
chatgh repo-perms --repo ChatArch/<RepoName> --json-output
git push --dry-run origin <branch-or-tag>
git remote -v
```

Expected:

- `repo-perms` token source should be `repo git config` after setup.
- `permissions.push` should be true for write tasks.
- `git remote -v` should show HTTPS fetch and push URLs.
- dry-run push should succeed or report `Everything up-to-date`.

## Important distinction

ChatGH API commands and git transport auth are different surfaces:

- `chatgh pr ...`, `chatgh repo ...`, `chatgh run ...`, and `chatgh repo-perms ...` use GitHub API tokens.
- `git push` and `git fetch` over HTTPS use git's repo-local credential config.
- A valid ChatEnv token can make `chatgh repo-perms` pass while HTTPS `git push` still fails until `chatgh set-token` writes the repo-local git config.

## Do not use SSH for ChatArch repo workflow

SSH can expose broader machine-level authority and is less portable across the user's machines. The expected ChatArch workflow is HTTPS + repo-local token auth.

If a repo currently has SSH remotes from older work, convert them:

```bash
git remote set-url origin https://github.com/ChatArch/<RepoName>.git
git remote set-url --push origin https://github.com/ChatArch/<RepoName>.git
chatgh set-token
```

Then verify with `repo-perms` and HTTPS dry-run push.

## Related workflows

- Use this skill from package/repo creation workflows such as `python-package-release-with-chattool-pypi`.
- PR/CI workflows may reference this skill when git transport auth is missing, but `set-token` itself belongs to repository setup, not PR readiness.
