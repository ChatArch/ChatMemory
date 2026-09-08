# Configurable TTS and Plan cutovers

## Scope and configuration

- Freeze the requested capability. A TTS-only task is not permission to migrate ASR, realtime, notes, titles, sidecars or the gateway.
- Separate capability, protocol, endpoint, credential, model and subscription policy. Package/Plan names are not wire protocols.
- Where installed support exists, use `CHATVOICE_TTS_API_TYPE` (`volcengine`, `openai`, `qwen`), `CHATVOICE_TTS_API_BASE`, `CHATVOICE_TTS_API_KEY`, `CHATVOICE_TTS_MODEL`, `CHATVOICE_TTS_RESOURCE_ID`, and `CHATVOICE_TTS_VOICES`.
- For Volcengine the resource ID is the actual resource selector; the model field is metadata. OpenAI-compatible and Qwen task protocols transmit their model field. Do not imply that every model from a vendor implements the same protocol.
- Partial independent configuration fails closed; never borrow text/global keys or silently switch provider/endpoint. Preserve legacy behavior only when the independent configuration is entirely unset.
- Build candidates with explicit `EnvStore.load_*` / `save_*` values. Keep credentials in ChatEnv/runtime, not the project or source repository. Compare all non-TTS keys against the original profile.

## Plan safeguards

- Read current official documentation before selecting the endpoint. Coding Plan and Agent Plan can have different capabilities and exhaustion policies.
- Volcengine Agent Plan speech uses a dedicated Plan path, `X-Api-Key` and the speech resource header, not the ordinary text-completions protocol. Consult the current speech documentation at https://www.volcengine.com/docs/82379/2516286 .
- A Plan-specific endpoint alone does not always prohibit overage billing. Treat deduction permission and overdraft/overage permission as separate controls. Where supported and authorized, enable only the requested model's Plan deduction, explicitly leave overage false, and read back both flags plus unchanged unrelated models/services.
- When no-cash operation is required, exhaustion must stop with an error; neither server-side overage nor client-side alternate-key/endpoint fallback may silently charge usage.
- Use the existing authorized control API; do not create browser login work just to inspect account toggles. Keep controls bounded and persist sanitized receipts, not credentials. Do not keep asking about cost after the user has supplied a clear no-overage policy.

## Protocol and regression checks

- HTTP status alone is not success. Validate provider envelopes, audio data, explicit terminal markers, nonempty output, content limits and total deadline.
- Volcengine NDJSON can include a successful `code=0`, `data=null`, `sentence={...}` metadata event. Skip that valid non-audio event, but retain malformed-event, unsuccessful-code and missing-terminal rejection.
- `HTTPResponse.read1()` can return empty with Content-Length bytes outstanding. Check framing completion at EOF, and test via a real stdlib HTTP parser with a fake socket rather than only response doubles.
- Raw signed-int16 PCM has no magic signature. Valid first samples may resemble JSON punctuation, MP3 sync bits or container names. Validate protocol success, size and alignment; do not reject arbitrary legal samples by prefix. Wrap PCM as the requested WAV with correct mono/sample-rate/bit-depth metadata.
- Test resource cleanup, bounded reads, header/body deadlines, redirects, invalid audio, quota errors and no-fallback behavior. Use a fresh independent review context for code, and a separate focused fixer for reproduced blockers.
- Qwen WebSocket uses its own run/continue/finish task protocol. Avoid SDK-global credential mutation when implementing independent per-call credentials; use a scoped transport and declare its direct dependency. Scope the Plan key-class guard to the appropriate protocol.

## Verification and rollout

1. Execute the actual selected-home `chatenv test -t chatvoice -I`; schema-only success is insufficient. Use synthetic text and prove that the hook loads the selected profile rather than process/default secrets.
2. Run focused RED/GREEN tests, the full suite, actual CLI trees, strict docs, wheel/sdist and package checks. For DOM tests requiring Node, use the intended supported Node runtime. An old system Node or sandbox-disabled socket wakeup is not a product regression; reproduce outside the sandbox with the same isolated test config before changing dependencies.
3. Check exact wheel/source bytes and candidate installed import provenance. Review a frozen Git tree and retain its identity through commit/deployment; unparseable or stale review is not approval.
4. Back up the existing wheel, profile, unit and SQLite with online backup. Compare all dependency versions. Use only the service's graceful supervisor and a no-dependency package install when preserving GPU runtime. Mark installation attempted before invoking the installer so partial install failures also trigger rollback.
5. Rollback restores the prior package/profile and service, not a stale database over newer writes. Never use process signals or restart unrelated services merely because a validation script failed.
6. Verify new PID/version, database, warm ASR and protected configuration. The ASR response exposes `raw_text` and `corrected_text`; persist the receipt before assertions.
7. On the real public page, select each configured test voice and exercise MP3/WAV generation, visible progress, player time advancement and download. Save input/in-progress/completed screenshots; check recorder layout and clone selection preservation without running an unrelated clone job. Record no unintended meeting writes, zero JS errors and graceful closure of the owned browser.
8. Enumerate actual screenshot/receipt filenames instead of guessing them. If vision cannot read SSH paths, transfer only the task's non-sensitive screenshots into local control-plane cache, then inspect them. Keep final remote artifacts on their execution host.

Distinguish real provider synthesis, offline protocol tests, preview UI and production UI in every handoff. Do not claim every compatible provider was live-tested when only one was called.
