---
name: chattool-capability-extraction
description: ChatArch workflow for extracting useful ChatTool interfaces into standalone Python packages such as ChatPyPI.
version: 0.1.0
tags:
  - ChatArch
  - ChatTool
  - extraction
  - packaging
status: maintained
reference:
  - python-package-release-with-chattool-pypi: "新 standalone Python package bootstrap/release 流程"
  - chatgh-pr-and-ci-workflow: "standalone/parent PR、CI 与 review flow"
---

# ChatTool Capability Extraction

## Purpose

Use this skill when splitting a useful ChatTool command/interface into an independent ChatArch Python package.

This was first practiced on `chattool pypi` -> standalone `ChatPyPI` / `chatpypi`. Current ChatPyPI package-operation docs should use the explicit 0.2.3+ command tree (`chatpypi pkg init/build/check/probe/upload` and `chatpypi publisher detail/add-github/pending-*`), not old parent `chattool pypi` snippets or root shortcuts except when documenting backward compatibility.

## Current known extractions

- PyPI/package release surface: `ChatPyPI` / `chatpypi` owns package scaffold/build/check/probe/upload plus PyPI account/session/project/publisher operations. Current release baseline is `ChatPyPI>=0.2.3,<0.3.0` for direct Publisher management (`publisher detail`, `publisher add-github`, and scoped `pending-*`).
- GitHub helper surface: ChatTool GitHub functionality has been extracted to `ChatGH` / `chatgh`.
- Setup/bootstrap surface: ChatTool setup functionality has been extracted to `ChatUp` / `chatup`; `chattool setup` is no longer a ChatTool command in ChatTool 7.1.0.
- DNS surface: `ChatDNS` / `chatdns` owns DNS record management, DDNS, IP detection, provider clients, and DNS-01 certificate automation (`chatdns cert`) after the 2026-06 extraction plus `0.1.1` cert follow-up; DNS MCP remains a separate boundary unless explicitly scoped in.

## Candidate selection rubric

A ChatTool capability is a good extraction candidate when:

1. The command has a clear product/domain boundary.
2. It already has, or naturally deserves, a first-level CLI binary.
3. Source code is concentrated in one module tree such as `src/chattool/tools/<name>/`.
4. Tests are already grouped under `tests/cli-tests/<name>/` and/or `tests/mock-cli-tests/<name>/`.
5. Config/env ownership can be delegated to canonical ChatArch packages such as ChatEnv.
6. Interactive CLI behavior can reuse ChatStyle rather than copying ChatTool internals.
7. ChatTool can remove the embedded logic or depend on the new package without breaking unrelated commands.

## First concrete target: ChatPyPI

Known source surface in ChatTool:

- CLI group: `chattool pypi`
- Shortcut CLI: `chatpypi`
- Source tree: `src/chattool/tools/pypi/`
- Main functions: scaffold/build/check/probe/upload Python packages
- Test families:
  - `tests/mock-cli-tests/pypi/`
  - `tests/cli-tests/pypi/`
  - `tests/mock-cli-tests/client/test_chatpypi_shortcut_basic.*`

Expected/current target shape:

- GitHub repo: `ChatArch/ChatPyPI`.
- PyPI distribution: `ChatPyPI`.
- Python module: `chatpypi`.
- CLI: `chatpypi`.
- Current command tree for package operations: `chatpypi pkg init/build/check/probe/upload`; root commands remain compatibility shortcuts only.
- Current Publisher tree: `chatpypi publisher detail/add-github/list/pending-list/pending-add/pending-remove`; existing-project Publisher writes use active `add-github`, not pending.

## DNS / operational capability extraction notes

When extracting `chattool dns` or similarly operational capabilities, add an explicit boundary pass before package creation:

1. **Name / ownership check**
   - Check PyPI and workspace history for exact and normalized names before assuming `Chat<Command>` is available.
   - For DNS, `ChatDNS` / `chatdns` may already exist, and `ChatNet` may already be an adjacent ChatArch package. Decide whether DNS becomes a new package, a `ChatNet` module, or another confirmed name.
2. **Read vs write safety**
   - Early inventory may run help commands and mocked/offline tests.
   - DNS record creation/update/delete, DDNS, and certificate issuance are live external side effects; do not run them without explicit domain/provider approval.
3. **Cross-module command attachments**
   - `chattool dns cert` is exposed under DNS but may be implemented in `tools/cert`. Decide whether cert belongs in the new DNS package, remains parent-owned, or becomes a separate package.
   - If DNS-01/cert is explicitly moved into ChatDNS, add extra safety gates: validate certificate domains before filesystem use; resolve generated key/cert paths under `cert_dir`; delete only the exact `_acme-challenge` TXT value created by the current challenge; make certbot cleanup refuse broad deletion when `CERTBOT_VALIDATION` is absent; fail hook/auth flows when DNS record creation returns `None`/`False`; and verify wildcard/public-suffix zone handling.
   - If certificate code remains parent-owned but still needs DNS provider clients, rewire it to import from the standalone DNS package (for example `from chatdns import create_dns_client, DNSClientType`) instead of keeping a parent `tools.dns` shim.
   - Remove or retarget MCP catalog entries whose implementation moved or is out of scope. For a DNS-only first release, do not assume DNS MCP is included; explicitly decide whether MCP is supported now or deferred, and remove parent-only `dns_cert_apply` until certificate ownership is settled.
   - If parent MCP `info`/catalog is explicitly in scope while implementation moved to an optional standalone package, dynamically hide moved tools unless the standalone module is importable. Test both installs: `chattool[mcp]` without the new package must not advertise moved tools; `chattool[mcp,<capability>]` must register and advertise them. If MCP is not an actively supported surface for the extraction, mark it out of scope and remove stale parent DNS/MCP advertisements instead of spending the parent PR on broader MCP catalog cleanup.
4. **Parent branch sequencing**
   - Before removing parent implementation, ensure `core/ChatTool` is on a fresh branch from the updated default branch. Do not stack a new extraction on a branch still carrying a previous extraction PR.
5. **Parent dependency reconnection**
   - Move provider SDK/runtime dependencies into the standalone package.
   - Reconnect ChatTool through bounded optional extras such as `dns = ["ChatDNS>=X,<Y"]` and update `arch` only if the new package is part of the parallel ChatArch tool bundle.

## Standard extraction phases

### Phase 0 — task and isolated workspace

1. Start at `~/Playground`; read `AGENTS.md` and `projects/README.md`.
2. Create a task under the active extraction topic, for example:

```text
projects/chatup-setup-split/05-chatpypi-extraction/
  PRD.md
  progress.md
  reports/
  playground/
```

3. To avoid polluting long-lived checkouts and tracker state, clone or copy fresh working repos under the task `playground/` before exploratory migration/removal work:

```bash
git clone ~/Playground/core/ChatTool playground/ChatTool-parent-update
# Create or clone the standalone package repo/scaffold under playground/<PackageName> for the extraction spike.
```

Rules:

- Treat the task-local copy as the default scratchpad for tracker-style capability separation, especially when removing modules from a parent repo.
- Record the copy source, remote, base branch, and HEAD in `progress.md` before editing it.
- Do not modify `~/Playground/core/ChatTool` directly during early extraction practice or while its canonical checkout is already on another feature/release branch.
- After the copy proves the migration and tests, apply the reviewed delta to canonical `core/ChatTool` only on a fresh feature branch from the updated default branch.

### Phase 1 — bootstrap or prepare standalone package

1. Confirm exact names: repo, PyPI distribution, module, CLI, initial version.
2. Check whether GitHub repo and PyPI project already exist with `chatpypi pkg probe` plus GitHub repo checks.
3. For new ChatArch PyPI projects, create the real project first via a controlled `0.0.1` placeholder upload, then configure active Publisher with `chatpypi publisher add-github`; do not use pending Publisher as the default bootstrap.
4. Scaffold/harden the standalone package with `chatpypi pkg init` or an existing source tree.
5. Add minimum CLI smoke: `--help`, `--version`, and a simple non-mutating command.
6. Add CI and tag-driven publish workflow, but do not tag/publish without explicit user approval.

### Phase 2 — migrate the capability

1. Inventory ChatTool source, docs, tests, and shortcut wrappers.
2. Move implementation and tests into the standalone package.
3. Keep a preserve / retarget / delete table:
   - preserve user-facing CLI behavior;
   - retarget imports/config/docs to canonical ChatArch packages;
   - delete parent-only shims or obsolete assets.
4. Run tests, build, twine check, wheel/package-data checks, and CLI smoke.

### Phase 3 — update parent ChatTool

Only after the standalone package is working and, if needed, published:

1. Remove embedded implementation from ChatTool or replace with an intentional wrapper.
2. Remove parent-managed aliases that duplicate real standalone CLIs.
3. Update ChatTool dependencies/extras, docs, tests, CI smoke lists, and changelog.
4. Use PR flow; merge and release are separate user approval gates.

## Hard boundaries

- Do not create repositories, push branches, change visibility, configure branch protection, tag, or publish unless the user explicitly approves that concrete action.
- Do not print tokens or auth headers.
- Merge is not release.
- Keep source mutations in task-local clones until the user asks to apply them to canonical `core/` checkouts or remote repositories.

## ChatPyPI Practice Notes

- Use `chatpypi pkg ...` as the canonical package-operation tree in shared docs. Root `chatpypi init/build/check/upload/probe` commands are compatibility shortcuts and should not be the primary examples.
- Treat PyPI Publisher state as a tree with separate active and pending branches. Existing project operations are active (`publisher detail`, `publisher add-github`); only PyPI pre-registration or stale cleanup uses `pending-*`.
- After releasing an operator tool such as ChatPyPI, upgrade `/Users/rexwzh/.chatarch/venv` to the published version and run installed-command smoke without `PYTHONPATH` before updating parent skills.
- Parent ChatTool cleanup remains part of extraction done-ness unless the user scopes it out: remove duplicated implementation, update dependencies/extras/docs/tests, and only release ChatTool after the standalone package is published and clean-install verified.
