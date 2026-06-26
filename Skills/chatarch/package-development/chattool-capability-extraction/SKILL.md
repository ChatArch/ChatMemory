---
name: chattool-capability-extraction
description: ChatArch workflow for extracting useful ChatTool interfaces into standalone Python packages such as ChatPyPI.
version: 0.1.0
tags:
  - ChatArch
  - ChatTool
  - extraction
  - packaging
status: draft
owner: ChatArch
source_project: ChatTool
---

# ChatTool Capability Extraction

## Purpose

Use this skill when splitting a useful ChatTool command/interface into an independent ChatArch Python package.

Initial target: extract `chattool pypi` / `chatpypi` into a standalone ChatPyPI package.

This skill is intentionally created early as a draft. Fill in concrete details as the ChatPyPI extraction is practiced and verified.

## Related skills to load

- `workspace-task-kickoff` — establish `~/Playground` and create the task record first.
- `chattool-capability-extraction` in Hermes local skills, if available — local procedure draft and candidate rubric.
- `extracting-capabilities-to-packages` — general multi-phase extraction workflow.
- `python-package-release-with-chattool-pypi` — current ChatArch package scaffold/release workflow.
- `chatgh-pr-and-ci-workflow` — ChatArch PR/CI/repository workflow through ChatGH.

## Current known extractions

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

Expected target shape:

- GitHub repo: `ChatArch/ChatPyPI` unless renamed by user.
- PyPI distribution: confirm exact name before registry operations; do not guess a hyphenated name.
- Python module: likely `chatpypi`.
- CLI: `chatpypi`.

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
2. Check whether GitHub repo and PyPI project already exist.
3. Scaffold/harden the standalone package.
4. Add minimum CLI smoke: `--help`, `--version`, and a simple non-mutating command.
5. Add CI and tag-driven publish workflow, but do not tag/publish without explicit user approval.

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

## Fill in after practice

As ChatPyPI extraction proceeds, add:

- exact command compatibility table;
- file migration map;
- dependency decisions;
- tests moved/added;
- parent cleanup checklist;
- release and rollback notes;
- pitfalls discovered during the actual split.
