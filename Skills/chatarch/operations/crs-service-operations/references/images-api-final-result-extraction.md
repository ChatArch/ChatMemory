# Images bridge: final results versus partial previews

Use when a standard Images client receives `502 no image produced by upstream`, but the same caller key can generate through Responses image tooling.

## Read-only diagnosis

1. Pin the actual running process CWD, source revision, clean/dirty state, and relevant source-file hash. Compare upstream and the maintained fork separately; a newer local helper is not proof of deployed behavior.
2. Trace client Images payload -> carrier-model selection -> upstream Responses tool payload -> SSE consumer -> Images JSON. Check whether configured host-model settings are actually read by that source version.
3. Compare final image bytes in `response.output_item.done.item.result` with `response.completed.response.output[]`. A successful terminal response can have an empty output list while the image is present in the earlier output-item event.
4. Trace `partial_image_b64` independently. A consumer that only reads previews can return 502 for a valid final-only stream or return a preview as the final image. A request builder that does not request previews must not depend on them.
5. Execute the unchanged stream-consumer block offline with network/account/usage dependencies stubbed. Use a saved real SSE plus explicitly named derived fixtures: remove only the preview event, or retain only a preview without terminal success. Label these as offline fixtures, never new provider responses.
6. Compare selected bytes by hash with the known final image. A preview can be larger than the final image, so recursive extraction plus longest-base64 selection is still wrong.

## Correctness contract

- Collect completed `image_generation_call` results from output-item and terminal-output locations; deduplicate by item identity.
- Keep previews separate. Final-item status/identity outranks size or event order.
- Require terminal `response.completed` success; reject error/failed/incomplete or truncated streams even after an image item.
- Parse complete SSE frames, joining multiple `data:` lines and dispatching only at a blank-line boundary. A complete-looking JSON terminal object is not a complete SSE event when EOF arrives before that boundary; reject pending data at EOF, including a trailing incomplete frame after an earlier successful terminal event.
- Test final-only, completed-output, preview+final, preview-only, truncation, late error/failure/incomplete, multiline frames, and unterminated terminal/trailing frames.
- Verify extracted PNG bytes/signature/dimensions; do not equate HTTP 200 with the final artifact.

## Attribution and upstream feedback

A working Responses request with a different carrier model or payload is not a controlled same-payload A/B test. Without the failed Images request's internal SSE, do not claim that its upstream generation definitely completed. State the consumer defect proven by replay separately from the original incident's remaining uncertainty.

Search existing issues and PRs for the exact error, endpoint, event names, and final-result fields. A merged endpoint feature PR is not a fix for a later result-extraction bug. Draft a narrow report against the source that actually contains the defect, with pinned source links, reproduction fixtures, expected/actual results, and evidence limits. Exclude deployment URLs, credentials, account identifiers, private paths, and raw SSE. Production remediation and upstream issue publication are separate authorization scopes.
