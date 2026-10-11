---
name: chatgh-repo-token-setup
description: "Use when configuring ChatGH auth or token rotation. Choose live defaults or explicit repository pins."
version: 0.2.3
tags:
  - ChatArch
  - ChatGH
  - GitHub
  - credentials
---

# ChatGH Authentication And Token Lifecycle

## Choose the lifecycle first

Preserve the same credential order for GitHub API and Git transport:

**explicit token > matching repository `set-token` > current ChatEnv default**.

A selected invalid token is an authentication error, not permission to switch to a broader account. ChatEnv is reached when no matching pin exists, not by retrying an HTTP 401 with another identity.

For centralized rotation, prefer unpinned repositories and invocation-scoped ChatGH transport. Keep `set-token` as an explicit repository/account isolation choice rather than a mandatory bootstrap step. Removing a repository copy means preserving the current ChatEnv default, not deleting all GitHub credentials.

For a new Python package with no PyPI project, complete its authorized name-claim/upload preflight before creating a GitHub repository; authentication setup does not waive that release gate.

## Installed command gate

ChatGH 0.2.13 provides these real interfaces. Check the active installation before using them:

```bash
chatgh --version
chatgh --tree
chatgh --tree-brief
chatgh fetch --help
chatgh pull --help
chatgh push --help
chatgh unset-token --help
```

An older `repo sync` implementation that runs bare Git or labels its token flag reserved does not establish dynamic authentication. Refresh the installed package rather than documenting proposed commands as implemented.

## Ordinary dynamic workflow

Inside a GitHub HTTPS checkout:

```bash
chatgh fetch
chatgh pull
chatgh push --dry-run
chatgh push
```

- Without explicit targets, commands follow the current branch's configured upstream. If it is absent or ambiguous, supply the remote and branch/refspec instead of guessing.
- `pull` defaults to fast-forward-only; `--rebase` is explicit and mutually exclusive with `--ff-only`.
- `push` supports explicit `-u/--set-upstream`, `--dry-run`, and `--tags`; force syntax and automatic reset/stash are not part of this interface.
- Explicit examples: `chatgh pull origin <branch>` and `chatgh push -u origin <branch>`.
- `repo clone` and `repo sync` reuse this transport; clone does not persist a token by default. `repo clone --set-token` is opt-in pinning.
- Callable APIs are `chatgh.github.transport.fetch`, `pull`, `push`, `clone_repository`, and `unset_token`.

Each invocation resolves the selected credential afresh and supplies it only to the authenticated Git child. No global credential helper or repository token copy is required for these commands. Native `git fetch/pull/push` do not automatically gain ChatEnv authentication.

## Release an existing pin

```bash
# Remove the selected remote's local GitHub token pin.
chatgh unset-token

# Remove every token-bearing GitHub HTTPS header in THIS repository only.
chatgh unset-token --all

chatgh repo-perms --repo <owner>/<repo> --json repo,token_source,permissions
chatgh fetch
chatgh push --dry-run
```

The unset command emits safe JSON with removed keys/count and credential-presence status, never token values or masks. It is idempotent. It removes only recognized token-bearing GitHub HTTPS headers directly owned by the current repository's local config; unrelated headers, included files, other hosts, and global/system config are preserved. Linked worktrees share common Git config: deduplicate before bulk mutation.

`--all` means all matching pins in one repository, not all workspace repositories. A workspace migration requires an explicit repository manifest and per-item verification.

## Bulk migration to the live default

1. Define the authorized host/repository scope; do not transfer another machine's credential.
2. Resolve and validate the intended default in a neutral directory without printing it. Check required scopes separately from repository push capability when workflow files are involved.
3. Verify the installed dynamic entry point with real private HTTPS read and push dry-run BEFORE removing fixed copies.
4. Deduplicate Git common config across worktrees; record each configuration root, matching key names, and intended removals. Do not recursively mutate archived checkouts.
5. Back up secret-bearing config only in an approved private application state directory, with owner-only directory/file modes. Do not place raw config or headers in task reports/public repositories.
6. Unset through the importable API or real CLI. Confirm removed counts, zero in-scope residual token headers, current resolver source, and preservation of all unrelated config entries and source status.
7. Re-read every named target and aggregate persisted results programmatically. Keep native Git authentication separate from ChatGH acceptance.
8. Prove A-to-B default-profile rotation in an isolated ChatEnv test home using dummy values and actual credential-helper protocol responses; do not rotate the real token for a simulation.

A pin-consistency audit designed to require a fixed header will report missing headers in dynamic mode. That absence is intentional; do not restore copies merely to make a pin-only audit green.

## Optional fixed repository authentication

Use HTTPS and inspect the exact remote before changing it:

```bash
git remote -v
chatgh set-token
chatgh repo-perms --repo <owner>/<repo> --json repo,token_source,permissions
```

Plain `set-token` prefers an existing pin, so it does NOT refresh a stale pin from a rotated default. To intentionally pin the new default, first validate the replacement, then unset the old pin and set again. Never put a raw token in shell history, URLs, logs or examples. Inspect the writer when process-argv secrecy is required: older pin writers serialize an encoded Authorization header into `git config` argv. Dynamic transport avoids that persistent-writer surface.

Do not silently convert unsupported transports or substitute SSH to solve an HTTPS credential gap. Preserve unrelated remote/account authority.

## Implementation and verification rules

- Validate effective fetch and push destinations before resolving credentials; `pushurl`, URL rewrites and multiple destinations need explicit handling. Scope helper responses to the exact supported host/protocol/path and disallow credential redirects.
- Reject `remote.<name>.vcs` as well as custom uploadpack/receivepack before credential resolution. A canonical-looking HTTPS URL does not prevent Git from selecting a custom remote helper that inherits its environment.
- Reset additive inherited headers/helpers only in the authenticated child so a second credential cannot override the selected one. This is not permission to bypass repository-pin precedence.
- Keep local merge/rebase/checkout token-free. Network-facing hooks and submodule recursion are disabled by the scoped transport; document this boundary rather than claiming native Git parity.
- Hold Git's exclusive config lock across the entire read/parse/transform/write/atomic-replace transaction. Locking only the final write can silently lose a concurrent writer's unrelated entries. Test both foreign-lock preservation and deterministic writer interleaving.
- Run offline tests with a minimal environment, disposable application home, isolated Git config, and task-local temp paths. Avoid pytest assertions that expand token-bearing environment dictionaries.
- Treat runtime approval timeouts separately from auth failures. A stale approval-card tap resolving zero requests is not consent to a new command; use a fresh live request and do not bypass the gate.

## Acceptance boundary

Verify the real installed command/version/tree, explicit/repo/default precedence, unpin idempotence/preservation, isolated rotation, actual HTTPS reads and push dry-run, and clean source state. For an authorized release, require exact-head CI/review, merged-default-branch tag, successful OIDC upload, PyPI exact/latest/Simple convergence, clean public installation and operator-runtime provenance. Do not equate a PR or local wheel with a published working command.
