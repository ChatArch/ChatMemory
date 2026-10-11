---
name: chatgh-repo-token-setup
description: "Use when updating or clearing ChatGH repo tokens. Keep set/unset symmetric and support file batches."
version: 0.2.4
---

# ChatGH Token Updates And Cleanup

## Core contract

Treat these as configuration operations, not an identity-binding or credential-lifecycle product:

- `set-token` writes or updates one repository Git HTTPS token configuration item.
- `unset-token` simply undoes that configuration: use the same origin-first GitHub remote selector and delete the same exact key.
- Unset must not inspect/decode/validate token contents, resolve a default credential, restore history, or clean other keys/remotes/repositories. An absent item is an idempotent success.
- Keep other requested commands unchanged when correcting unset. Distinguish fixing a command's implementation from restoring an earlier bulk operation; never restore credentials to other repositories based on the word “revert” alone.

Consumer token precedence remains explicit value > matching repository configuration > current typed GitHub configuration. Do not switch identities automatically after HTTP 401.

## Installed command gate

ChatGH 0.2.14 provides the verified update/cleanup and batch interfaces. Read the real installed tree/help before use:

```bash
chatgh --version
chatgh --tree
chatgh --tree-brief
chatgh set-token --help
chatgh unset-token --help
```

Unset has no broad `--all` mode. Do not teach the removed 0.2.13 expansion or advertise a future interface as installed.

## Refresh and clear repository configuration

Inside the target checkout:

```bash
chatgh set-token --from-config --dry-run --json-output
chatgh set-token --from-config --json-output
chatgh unset-token
```

`--from-config` reads the current typed GitHub configuration instead of reusing an old repository value. It is mutually exclusive with `--token`. Existing interactive and explicit-token behavior remains available without this flag. Avoid raw token values in argv, history, URLs, logs and examples.

Set and unset must select the same target even when the branch upstream differs from origin. Clearing expired, malformed or empty values is an exact-key operation; do not make content recognition a prerequisite. Global/system/included configuration and unrelated repository fields are outside unset's scope.

## Explicit JSON/YAML repository maintenance file

Store paths and optional expected repository assertions, never token values:

```json
{
  "version": 1,
  "repositories": [
    {"path": "./repo-one", "repo": "example/repo-one"},
    {"path": "./repo-two"}
  ]
}
```

Relative paths resolve from the manifest directory. JSON and safe YAML are supported. Keep machine-specific manifests in private application state, not a public source repository.

```bash
chatgh set-token --from-config --file repositories.json --dry-run --json-output
chatgh set-token --from-config --file repositories.json --json-output
chatgh set-token --from-config --file repositories.yaml --json-output
```

Batch mode requires an explicit source (`--from-config` or `--token`) and cannot combine `--file` with `--save-env`. Preflight every path/schema/repository assertion before reading a credential or writing anything. Deduplicate shared Git config plus exact key across worktrees. Preserve a nonzero result for partial write/readback failures and report requested/unique/skipped/configured/failed counts from persisted results.

Creating a maintenance file does not authorize applying it. When the user asks only for tracking or implementation, keep real repositories unchanged and use dry-run; verify all affected configs remain unchanged. A file based on an earlier audit is a maintenance target list, not evidence that those repositories are currently configured.

## Safe Git configuration writes

- Preserve native Git semantics for case-insensitive section/option names and case-sensitive URL subsections; updating a key must replace all case variants/old values of that exact key.
- Preserve valid valueless booleans, quoted comment characters, escapes, multivalues and include references. Do not assume a Python config parser is lossless: verify the minimum dependency version, not only the newest wheel resolver.
- Acquire Git's config lock with atomic exclusive creation before reading the snapshot. Never use existence-check then ordinary open, and never remove a foreign lock.
- Keep secrets out of child-process argv and errors. Native Git may process a private config copy with a nonsensitive temporary value, followed by the actual value written only in memory/private owned lock; do not introduce a persistent helper or unrelated auth state.
- Verify descriptor/inode ownership for writes and cleanup, use private permissions before secret writes, flush/fsync, and atomically replace. Holding only the final write lock can discard a concurrent writer's unrelated fields.
- Tightening permissions does not revoke or retroactively protect an already exposed old credential. Backups containing raw configuration belong only in an approved owner-private state directory.

## Verification and release boundary

Use minimal child environments, isolated typed profiles and dummy values for tests. Do not expose production provider keys to pytest dictionary assertions. Require regressions for same set/unset target, content-independent exact deletion, from-config overriding old values, JSON/YAML preflight, duplicate/shared config, dry-run, partial failures, unrelated syntax preservation and racing foreign locks.

Test source and installed artifacts separately. Verify actual version/tree/help, installed set→unset and file batches in isolated fixtures, a real maintenance-file dry-run, and unchanged real repository configurations unless an apply was expressly authorized. Native Git does not automatically read ChatEnv; unset removes the repository override so Git can use its usual remaining credentials, rather than configuring a new global helper.

For an authorized release require exact-head review/CI, merged-default-branch tag, successful OIDC upload, PyPI exact/latest/Simple convergence, clean public installation and operator-runtime provenance. Preserve existing public versions/tags when issuing a forward correction.

## Related boundaries

- Use ChatEnv typed configuration rather than inventing another token file/store.
- For new package name claims, follow the package-release gate before creating its remote repository; token maintenance does not waive it.
- Inspect HTTPS remotes before changes; do not substitute SSH, copy another machine's credential, or overwrite unrelated account authority to solve a local mismatch.
- A tool-approval timeout is not an auth failure or consent. Expired card taps resolving zero requests require a fresh live approval, not a blind retry or policy bypass.
