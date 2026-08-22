---
name: chatvoice-speakr-operations
description: Operate ChatVoice/Speakr voice-workspace releases with ChatEnv, Token Plan, and browser visual acceptance gates.
version: 0.1.0
---

# ChatVoice / Speakr Operations

Use this skill when operating or developing a ChatVoice-backed Speakr/VoiceNote web service: meeting recording, meeting notes, voice studio, system text-to-speech, or one-shot voice cloning.

This shared skill is host-neutral. Keep concrete server aliases, usernames, private paths, ports, tokens, cookies, and account URLs in workspace-local notes or task progress, not in this shared file.

## P0 boundaries

1. **ChatEnv is canonical.** Production configuration must live in the typed ChatEnv profile for the service, e.g. `~/.chatarch/envs/ChatVoice/.env`. Do not create a parallel dotenv pointer such as `QWEN_TOKEN_PLAN_ENV_FILE`, and do not create a differently-cased storage namespace such as `Chatvoice`.
2. **OpenAI-compatible model fields only.** Model-provider config uses `OPENAI_API_BASE`, `OPENAI_API_KEY`, and `OPENAI_API_MODEL`. Provider-specific variables are not the product-facing or deployment-facing interface.
3. **Token Plan guard.** If the deployment is expected to use a Token Plan key, the system-voice path must require an `sk-sp...` `OPENAI_API_KEY` and reject ordinary usage-billed `sk-...` keys with a clear 503 before calling upstream. Never print full keys, key fragments, hashes, or derived identifiers.
4. **No silent UI no-ops.** A disabled or blocked button must show a visible reason: login missing, reference audio missing, consent missing, sidecar offline, Token Plan missing, or text missing.
5. **Visual acceptance includes all primary buttons.** Do not validate only the API or only one panel. Check both the meeting recorder page and the voice studio. If a screenshot/user report shows a clipped button, verify actual browser geometry after the fix.

## Voice Studio product rules

- System voices and the cloned voice live in one `选择音色` / voice-card list and share one text box and one generate button.
- The cloned voice flow is one-shot unless the product explicitly adds saved voice profiles later: reference audio + text -> temporary generated audio. Do not persist generated-audio history by default.
- The meeting recorder does not save or download raw recording audio; it saves text/summary state only according to product mode.
- The reference-audio row must remain responsive. A known regression is a fixed-width grid where the `录参考音` button overflows underneath the right `试听结果` panel. Prefer flexible `minmax()` columns and a static contract that forbids the old fixed-width grid.

## Runtime implementation checklist

- Register and test a typed ChatEnv provider with canonical storage name `ChatVoice`.
- Runtime startup scripts should export process environment from `EnvStore(...).load_active(ChatVoiceConfig)` / `ChatVoiceConfig.load_from_sources(...)`, then run the packaged service command. Startup scripts should not embed secrets or point to a second provider-specific env file.
- `/api/status` should expose only safe booleans and redacted metadata: storage namespace, base host/path, Token Plan key present/valid, configured sidecar URL boolean, and selected model name. It must not expose raw keys or hashes.
- System TTS should return 503 for missing/non-Token-Plan model key and should pass through `HTTPException` instead of wrapping it as 500/502.
- Keep direct legacy voice-enrollment routes out of the product path unless explicitly reintroduced; one-shot cloning should go through the local sidecar API such as `/api/voice-clone/*`.
- CLI tree support should come from ChatStyle (`add_tree_option`) and be verified with the real installed `chatvoice --tree-brief`.

## Release / deployment gates

Before publishing a ChatVoice release:

1. `git status --short --branch` and understand any dirty files.
2. Run targeted tests for config, web API, static UI contracts, and CLI tree.
3. Run full gates: pytest, compileall, `git diff --check`, docs build strict, wheel/sdist build, and `twine check`.
4. Clean-install the published or candidate package in an isolated venv and run `chatvoice --version` plus `chatvoice --tree-brief`.
5. Deploy using the service's graceful supervisor/tmux/systemd helper; do not use `kill` / `kill -9` for normal restarts.
6. Public readback: heartbeat, status, voice-clone sidecar status, system `/api/tts` real audio generation when Token Plan is configured, and one-shot voice-clone flow when relevant.
7. Browser visual acceptance without annotation overlays:
   - meeting recorder start/finish controls visible and hit-testable;
   - voice studio cards visible in one list;
   - default text present if product expects immediate debugging;
   - `录参考音` / reference-audio controls visible and not covered by the right result panel;
   - console has no JS errors.
8. Add or update docs with the acceptance result and screenshot asset when the UI changed.

## Geometry check pattern for clipped buttons

For a suspected overlap, verify with the browser DOM rather than visual impression alone:

```js
(() => {
  const btn = document.querySelector('#record-clone-reference');
  const result = document.querySelector('.studio-result');
  const r = btn.getBoundingClientRect();
  const rr = result.getBoundingClientRect();
  const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return {
    hitId: hit && hit.id,
    rightGap: rr.left - r.right,
    overflowX: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
  };
})();
```

Pass criteria: `hitId` is the target button id, `rightGap > 0`, and `overflowX === 0`.

## Documentation updates

Update public docs and README-like surfaces when behavior changes:

- user guide for voice cloning / voice studio;
- deployment docs for ChatEnv and Token Plan model fields;
- changelog;
- screenshot asset references for visible UI fixes.

All doc and PR text in shared/public repos must remain host-neutral and secret-free.
