# Conservative workspace hygiene review

Use this reference when a user asks to inspect workspace pollution and collect temporary files into date-grouped Trash.

## Review before moving

- Treat each workspace's governing rules as authoritative. A cleanup request is not an implicit template migration.
- Enumerate bounded outer roots and topic/task entry layers. A dated item without anchors is an orphan item, not permission to recursively enumerate its assets as tasks.
- Separate control/link metadata, valid task-specific role extensions, credentials/runtime inputs, historical evidence, raw captures, regenerable caches, and unknown ownership. A nonstandard name is not proof of waste.
- Stop at Git repository/worktree roots and symlink boundaries. Inspect source and shared-library containers at entry level only.
- Compare duplicate originals by content bytes or a content hash; use metadata-aware safety fingerprints only for unchanged-source checks.
- Rehome useful files under the existing owner's reports/scripts/playground/reference. Preserve user originals and source/workflow pairs. Keep useful unknown-owner material in a provenance-labelled holding area rather than treating it as disposable.
- Leave secrets in their existing owner-managed stores. Knowledge synchronization transports reviewed repository objects, never credentials, authentication configuration or runtime databases.

## Exact and recoverable moves

- Build an explicit reviewed source/destination/reason plan. Never feed raw scanner findings directly to a move loop.
- Require dry-run, bounded tree hashing, unchanged-source checks, no overwrite, no cross-volume copy/delete fallback, a persistent journal, and independent destination readback.
- Use nearest `.trash/YYYY-MM-DD/<batch>/` for confirmed residual files and preserve the original paths in a manifest.
- Test workspace and project-local Trash separately, source/destination Git boundaries, symlink ancestors, secrets, conflicts, concurrent edits, quiet-period gates, existing Trash exclusion, and refusal to move an entire task as a cleanup file.
- Keep whole-project archive/discard decisions separate from file hygiene. Never purge existing Trash during routine collection.
- Update actual owners' progress and current input references without rewriting historical facts.

## Multiple workspaces and knowledge boundaries

- Resolve candidate hosts and roles from the private inventory, not only an SSH registry. Confirm the per-account roster before enrollment; physical hosts, aliases and users' workspaces are different identities.
- Use separate allowlists for public procedural knowledge and private environment facts. An excluded private target may still receive the public library; preserve its existing private data without refreshing or deleting it.
- On every selected host, perform a bounded read-only identity/rules/repository/link/outer-root preflight first. Missing governance or a checkout is a gap, not proof that the whole host lacks the mechanism.
- Preserve each machine's fixed branch and unique commits; compare exact source and destination ancestry before fast-forwarding. Keep source-repository publication and target-workspace readback as separate acceptance gates.
- Keep concrete hosts, ownership, paths, private distribution rules and synchronization receipts in the private inventory or task records. Shared procedures use placeholders only.

## Scheduling, confirmation and reporting

- Reuse one maintenance task and fixed latest artifacts rather than creating a new task/report bundle every day.
- A deterministic read-only monitor can wake a model only for new or modified structural candidates. Do not include current timestamps or routine worker-directory churn in that fingerprint.
- Verify monitor stability with actual repeated runs; read back the scheduler record after changing it. Distinguish enabled/next-run, source execution, model review, file changes and message delivery.
- Some monitor implementations persist detection before agent/delivery completion. Do not infer retry or delivery success from an unchanged hash.
- Scheduled review preserves ambiguous/active-owner files and uses a quiet period, bounded batches and exact-move readback. A fleet scan does not authorize installs, service changes, credential migration or automatic deletion.
- For roster selection, require actual selected-value feedback before changing scope. A displayed checkbox, sent card or timeout is not consent. If the first interaction wrapper cannot return a form, inspect the platform CLI's bundled skills/schema before concluding the native capability is unavailable.
- If an agent-instruction write is denied or approval times out, leave that target unchanged and report it; do not retry through another filesystem tool.
- Calculate moved roots, contained file counts and per-target outcomes from saved receipts. Structural candidates are not proof of a complete content audit or of every task's active/completed state.
