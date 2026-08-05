# Hermes Runtime Initialization Baseline

Use this reference when provisioning a new Hermes machine, changing the primary model/provider, or fixing context compression that triggers too early, times out, or loops.

## Safety boundary

- Treat `config.yaml`, `.env`, credentials, state databases, and session transcripts as protected runtime assets.
- Persist YAML scalars with `hermes config set <key> <value>`.
- For model IDs containing dots or nested provider model maps, use `hermes_cli.config.load_config()` and `save_config()` rather than a dotted CLI path that could split the model ID.
- Never copy credentials, private endpoints, machine paths, session IDs, or chat IDs into a shared skill or report.
- Record previous scalar values as a rollback manifest before changing them.
- Do not delete a transcript, clear a compression lock, edit state DB rows, or restart a gateway unless that side effect is explicitly approved.

## 1. Inventory before configuration

Collect a redacted inventory:

```bash
hermes --version
hermes config show
```

Using a read-only config loader, record only:

- `model.provider`
- `model.default`
- matching custom-provider name and `api_mode`
- `agent.reasoning_effort`
- configured model context length
- `compression.threshold`
- `compression.target_ratio`
- `compression.hygiene_hard_message_limit`
- `compression.hygiene_timeout_seconds`
- `compression.hygiene_total_ceiling_seconds`
- `compression.hygiene_failure_cooldown_seconds`
- `auxiliary.compression.model`
- `auxiliary.compression.timeout`

Do not print API keys or concrete private endpoint URLs.

## 2. Verify model context instead of copying a number

A model label, picker catalog, or upstream maximum is not evidence that the configured endpoint exposes the same context window. Custom relays may enforce a smaller limit.

1. Confirm the exact API mode used by Hermes (`chat_completions`, `responses`, `codex_responses`, or another supported transport).
2. Run a minimal real request through that route.
3. Inspect provider-reported prompt usage and the largest request known to succeed.
4. Treat provider context-overflow errors as authoritative for that route.
5. Configure the model's context length to the verified route limit, including a safety margin; do not claim a 1M window when the endpoint rejects assembled requests around 400K-500K.
6. Keep `compression.threshold * context_length` below the provider's practical overflow point.

For model IDs containing dots, update a verified provider entry through the Hermes helper:

```bash
<HERMES_PYTHON> - <<'PY'
from hermes_cli.config import load_config, save_config

cfg = load_config()
# Locate the provider by its configured name; do not assume index 0.
provider = next(
    item for item in cfg.get("custom_providers", [])
    if item.get("name") == "<PROVIDER_NAME>"
)
provider.setdefault("models", {}).setdefault("<MODEL_ID>", {})["context_length"] = <VERIFIED_TOKENS>
save_config(cfg)
PY
```

Re-read the parsed provider/model map after saving.

## 3. Understand the compression timers

These settings govern different boundaries:

- `auxiliary.compression.timeout`: inner hard deadline for the model request that generates a summary.
- `compression.hygiene_timeout_seconds`:
  - on older fixed-wait code, the total time the gateway waits for hygiene;
  - on activity-aware code, the allowed inactivity interval while no compression progress is observed.
- `compression.hygiene_total_ceiling_seconds`: finite total wall-clock ceiling on activity-aware code.
- `compression.hygiene_hard_message_limit`: row-count safety valve independent of token usage. A very low value causes tool-heavy sessions to compress even when token usage is modest.
- `compression.hygiene_failure_cooldown_seconds`: retry suppression after a real failure.

The outer gateway wait must not expire before the inner auxiliary request can finish and clean up. A timeout that returns while an executor worker continues can leave the worker holding the session compression lease and make later turns fail or defer.

## 4. Baseline templates

These are starting points, not universal provider claims.

### Older fixed-wait gateway

Use when the installed gateway wraps hygiene in one fixed wait and does not support a total-ceiling setting:

```yaml
compression:
  hygiene_hard_message_limit: 5000
  hygiene_timeout_seconds: 660
  hygiene_failure_cooldown_seconds: 1800
auxiliary:
  compression:
    timeout: 600
```

The outer 660-second wait gives a 600-second auxiliary deadline time to return and clean up while remaining finite.

### Activity-aware gateway with streaming progress

Use only after confirming that the auxiliary endpoint emits progress before completion:

```yaml
compression:
  hygiene_hard_message_limit: 5000
  hygiene_timeout_seconds: 120
  hygiene_total_ceiling_seconds: 660
  hygiene_failure_cooldown_seconds: 1800
auxiliary:
  compression:
    timeout: 600
```

If the endpoint emits no observable progress until the final summary, an inactivity budget of 120 seconds will still fail early. In that case use an inactivity budget longer than the inner request deadline (for example 660 seconds) while keeping a finite total ceiling.

Do not reduce `hygiene_hard_message_limit` to a few hundred merely to force proactive compression. Tool and reasoning records can cross that count quickly, creating a compression storm far below the token threshold.

## 5. Persist through Hermes

For scalar settings:

```bash
hermes config set compression.hygiene_hard_message_limit 5000
hermes config set compression.hygiene_timeout_seconds 660
hermes config set compression.hygiene_failure_cooldown_seconds 1800
hermes config set auxiliary.compression.timeout 600
```

Only set `compression.hygiene_total_ceiling_seconds` after confirming that the installed source supports activity-aware hygiene.

## 6. Verification

1. Re-read effective values using `hermes_cli.config.load_config()` without exposing secrets.
2. Confirm the resolved auxiliary compression timeout.
3. Verify the configured context length maps to the intended provider/model.
4. If rollout is approved, restart through the owning supervisor or official Hermes command.
5. Verify a new PID/start time and successful gateway reconnect.
6. Send one ordinary turn and confirm a substantive response.
7. For a controlled compression test, confirm logs show a committed summary/compaction rather than only a lifecycle status message.
8. Confirm the session compression lock is released after success or failure.
9. Record exact old/new values and test evidence in the active Playground project.

## 7. Misleading status warning

A user-visible status such as `Context compaction complete` is not sufficient proof of success. Some implementations close the progress lifecycle with the same terminal message after lock contention, cancellation, or an aborted summary. Verify the storage/log commit result and transcript reduction.

## 8. Rollback

Rollback uses the same supported configuration surface. Restore the recorded scalar values with `hermes config set`, re-read them, and restart only if needed and authorized. Do not restore by copying an entire stale `config.yaml`, because that can overwrite newer credentials, provider definitions, or unrelated settings.
