# Agents Skills

`agents/` is a shared skill group for agent-created or agent-learned skills that emerge while agents work through PRD, project, archive, and review processes.

This group is intentionally lightweight for now:

- agents may add useful reusable skills here after they are observed and validated in real work;
- the content is shared across enabled workspaces through ChatMemory;
- heavy governance and polishing requirements can be added later when usage patterns stabilize.

Use `common/` for stable non-ChatArch shared skills, `chatarch/` for stable ChatArch-specific workflows, and local workspace `skills/local/` for machine-specific or private, non-shared skills.

## Skills

- [`api-capability-guide/`](api-capability-guide/SKILL.md) — explain OpenAI and Claude model, endpoint, tool and application capabilities with sources, version relationships and project verification coverage.
- [`claude-code-worker-orchestration/`](claude-code-worker-orchestration/SKILL.md) — run an agentic, resumable subagent on an API key or subscription API credits: a Messages-API agent loop behind MCP tools inside Claude Code (the common case), or `claude -p --bare` with pre-assigned session ids elsewhere.
- [`openai-api-worker-orchestration/`](openai-api-worker-orchestration/SKILL.md) — run GPT Agent sessions with an OpenAI API key, local functions or a hosted sandbox, durable session IDs, resume, and verified turn outcomes.
- `indonesia-product-classification-workbook/` — audited image-backed Excel classification for Indonesia-bound cargo, including confirmed business rules, structured review, WPS `DISPIMG` preservation, and final workbook acceptance checks.
- [`math-research-site/`](math-research-site/SKILL.md) — build a mathematical research guide with a chapter sequence, concept dependencies, and traceable links to paper pages, Lean declarations, and computed examples.
- `wecom-desktop-reading/` — read reports and documents through the macOS WeCom client using CUA, accessibility text and screenshots, with window recovery, completeness checks and privacy-safe reuse.
