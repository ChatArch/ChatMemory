# Module Archive Hardening Checklist

## Source Project

- Confirm the module's goal, current state, and done criteria from `PRD.md` and `progress.md`.
- List what the project actually produced: commands, scripts, reports, helpers, config conventions, release logic.
- Decide whether each output is `package-canonical`, `skill-candidate`, or `archive-only`.

## Package Review

- Check the target package's CLI help and identify commands or options that are debug-only, sensitive, low-level, or rarely used.
- Prefer hiding advanced commands over removing them outright when compatibility matters.
- Add a clearer public alias when the current command name reflects internal implementation rather than user intent.
- Verify docs, changelog, and tests cover the behavior users will actually see.
- Verify config discovery and packaging boundaries if the package integrates with ChatEnv.

## Follow-up

- Open separate tasks for adjacent package issues instead of mixing them into the archive move.
- Record the canonical package path in the archive note before moving the source project.
- Archive only after the maintained destination and any follow-up tasks are named explicitly.
