# Multi-profile account tracking and live package upgrades

## Separate three authorities

Treat credential profiles, tracking selection and provider ACLs as distinct resources. A configuration substrate supporting multiple named profiles does not prove a consumer actually selects more than one. Trace its effective settings, batch client factory and live scheduler before proposing a fix.

- Bind each tracked record to an explicit existing credential profile and exact provider account ID; never infer an identity from a display name or enumerate every secret profile by default.
- Keep stable references in the consumer's typed registry and credentials in their registered owner. Do not replace a shared Key for every newly monitored account when independent scoped profiles can be registered instead.
- Preserve existing read/consume scopes and policy. New monitoring credentials should grant reads only, and new automatic-use policies must start disabled.
- Keep native HTTP credential provisioning separate from routine collection. Consumer collection must not adopt Admin credentials or local upstream OAuth as a fallback.

For ChatGlance releases exposing the subscriptions namespace, verify the installed tree before using the native surface:

```bash
chatglance --tree
chatglance account-limits subscriptions list --json-output
chatglance account-limits subscriptions add <label> --crs-profile <profile> --account-id <account-id>
chatglance account-limits subscriptions add <label> --crs-profile <profile> --account-id <account-id> --execute
chatglance account-limits subscriptions disable <label> --execute
chatglance account-limits subscriptions enable <label> --execute
chatglance account-limits subscriptions remove <label> --execute
```

An explicitly selected consumer `--env-profile` edits that named profile without global activation. Provision a referenced CRS profile through its owner before registration; tracking commands must not silently rewrite its Key.

## Selection, history and migration contracts

Make an absent registry preserve legacy behavior, but an explicit empty registry authoritative. All-disabled or all-removed tracking must not revive entries from an old snapshot. Validate the entire registry, including a malformed later or disabled entry, before public-source reads, account factories or collector/ledger state writes.

Retain an immutable label-to-account binding when stopping tracking. Do not let a new account inherit an enabled policy, cached observation or uncertain ledger from a reused label. Reject a label with an orphan historical policy unless its prior identity can be proven; resetting that policy silently is not preservation. A tombstoned record may resume only its original binding. Stop stale popup/CLI paths from bypassing disabled or removed tracking.

Keep per-provider failures independent: a failed credential profile or account must publish a truthful error/partial row while healthy accounts stay visible. Last-known values are display evidence with their original observation time, never fresh permission to consume.

## Configuration ownership

Key synchronization to the effective configuration home, not one assumed runtime directory. A supported custom runtime location must share the same configuration owner as registration, first legacy migration, collection and policy/consuming controls. Reuse an existing lock primitive in a distinct configuration namespace rather than reentering a publication lock already held by refresh.

Preflight complete syntax before creating lock state; reload effective settings after ownership is acquired. Include legacy controls during the first migration instead of bypassing the lock until a new registry exists. Keep actual consumption within ownership so a successful disable cannot race a frozen old selection. Report contention as explicit no-action busy state; do not turn it into success, invalid authorization or evidence that a card was consumed. Never retry an ambiguous consuming POST.

Tests should cover a custom runtime, an orphan enabled policy, a configuration change at lock acquisition, concurrent legacy migration, full-batch zero-I/O rejection, and many accounts across multiple credential profiles.

## Preserve the real installed runtime before upgrading

Inventory installed module bytes separately from public source/version. An installed distribution may have necessary, unpublished portability or rendering repairs despite reporting the same version as PyPI. Recover their canonical source and tests, integrate only the proven compatibility delta, and review the combined candidate before replacing it with a formal release.

Use platform-owned fixture identity in cross-platform tests. Do not hard-code one developer account's UID into a simulated native service test while also checking real file ownership; repair the fixture rather than weakening the production ownership check.

Follow the user-selected order: final-head review and CI, merge/default-branch readback, merged-commit tag, actual automated upload, exact/project/Simple registry convergence and clean public install, then target installation. Back up secret-bearing profiles and package rollback material only under the original private owner. Pause/recover only the existing supervisor-owned jobs needed for the upgrade, preserve their definitions/cadence, and verify installed provenance, new serving/control PIDs and dependency compatibility.

## Keep acceptance facts independent

Verify provider read ACLs separately from upstream account health. A scoped denial is not a provider outage; a CRS `oauth_refresh_failed` response is not repaired by adding a dashboard registry entry. Preserve it visibly and report the remaining provider authorization gate without copying rotating credentials or inventing fresh quotas.

Distinguish configured, collected, published and authenticated-browser-visible records. A native partial refresh may successfully publish healthy and failed rows while exiting nonzero. Read its explicit validation/publication/restart and no-consumption receipt before deciding what happened.

If secure browser login is unavailable, retain the successful public login-gate check but leave signed-in visual/interaction acceptance open. Never replace it with a forged session, copied unrelated cookies, static-file assertions or an about:blank screenshot. A browser harness losing its page identity is an acceptance setup fault, not proof of an application regression.
