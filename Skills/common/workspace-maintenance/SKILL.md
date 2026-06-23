---
name: workspace-maintenance
description: Maintain the outer workspace structure. Use for project cleanup, archive review, root protocol alignment, and moving files into the proper workspace-level locations.
version: 0.2.2
---

# Workspace Maintenance

Use this skill when maintaining the outer workspace rather than editing a source repository.

- keep active work under `projects/` and archive inactive work into `archive/YYYY-MM-DD/`
- update `ARCHIVE.md` when projects are archived or restored
- keep workspace-level scripts under `scripts/`
- prefer moving files into the nearest `.trash/` instead of deleting them directly
- keep root protocol files (`AGENTS.md`, `ARCHIVE.md`, `TODO.md`) aligned with the real workspace structure
