---
name: module-archive-hardening
description: Review completed project modules before archiving and harden the canonical package implementation. Use when Codex is asked to archive project modules, decide whether functionality belongs in a maintained package or a skill, trim redundant CLI exposure, verify docs/tests/config integration, or open follow-up tasks and PRs from archived module output.
---

# Module Archive Hardening

Use this skill when a short-lived project has already produced useful functionality and the next question is where that functionality should live permanently.

## Workflow

1. Read the workspace archive rules, the source project's `PRD.md`, `progress.md`, `reports/`, and the target package `AGENTS.md`.
2. Classify the source output:
   - `package-canonical`: the behavior should live in a maintained package or CLI.
   - `skill-candidate`: the reusable value is a workflow, checklist, or governance pattern.
   - `archive-only`: the material is historical context and should not become shared behavior.
3. For `package-canonical` work, inspect the package before editing:
   - look for redundant or low-signal CLI commands;
   - look for advanced or sensitive options shown in default help;
   - verify docs, changelog, tests, and config-provider wiring;
   - separate compatibility aliases from user-facing commands.
4. Create follow-up tasks when the source module exposes adjacent package issues. Keep those issues out of the archive move itself.
5. Archive the source project only after the maintained destination and any follow-up tasks are recorded.

## CLI Hardening Rules

- Keep ordinary help focused on the common path.
- Hide debug, diagnostic, sensitive, low-level, or very low-frequency commands from default help instead of deleting them immediately.
- Prefer a clearer public alias if an existing command name reflects implementation details rather than user intent.
- Add tests that assert both the visible help surface and the hidden compatibility path.

## Skill Boundary

- Do not turn site-specific or account-specific operations into shared ChatArch skills.
- Promote the general review or governance pattern, not the sensitive operational details.
- If the skill is still workspace-local or immature, keep it outside ChatMemory until the pattern stabilizes.

## References

- Read `references/checklist.md` when doing a full archive-to-package review.
- Read `references/scope-boundary.md` when deciding whether something should become a ChatArch skill or remain local/project-specific.
