---
name: chatenv-provider-workflow
description: Add, review, or debug a ChatEnv typed-config provider. Use when a package exposes `chatenv.configs` entry points, when `chatenv cat/test/use` behavior is missing or confusing, when provider discovery fails after install, or when a config class needs a safe `test()` implementation and clearer docs.
---

# Chatenv Provider Workflow

Use this skill when a package should integrate with ChatEnv and the question is whether the provider is discoverable, testable, and understandable from the CLI.

## Workflow

1. Confirm the package publishes a `chatenv.configs` entry point in `pyproject.toml`.
2. Inspect the config class:
   - `_title`, `_aliases`, `_storage_dir`;
   - required and sensitive fields;
   - whether `test()` exists and is safe.
3. Validate the discovery boundary:
   - source checkout alone does not guarantee entry-point discovery;
   - install the package into the active environment before expecting `chatenv cat -t ...` to work.
4. Make `chatenv test -t <alias>` useful:
   - it should not raise `NotImplementedError`;
   - prefer a local, non-destructive provider/schema check by default;
   - only call live network APIs when that behavior is clearly intended.
5. Document what is local schema validation versus what is a real service connectivity test.

## Interaction Rules

- `chatenv cat` should help users see loaded config values with masking.
- `chatenv test` should prove that the provider wiring is present and usable.
- `chatenv use` and other profile selection commands should follow the interaction model instead of failing with opaque behavior when recoverable input is missing.

## Provider Test Guidance

- Safe default:
  - print provider title;
  - confirm required defaults or configured values exist;
  - avoid live credentials and avoid printing secrets;
  - return a readable success/failure message.
- Escalate to real network checks only when the provider is explicitly meant to validate remote connectivity and the command behavior is documented.

## References

- Read `references/checklist.md` for the concrete provider review sequence.
- Read `references/test-guidelines.md` when deciding whether a config provider should do local validation or a real remote health check.
