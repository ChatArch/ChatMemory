# ChatUp / ChatTea Documentation Alignment Session

Use this as a compact reference for ChatArch CLI package docs when the user asks for ChatTea-style alignment.

## User Corrections Captured

- Links in user-facing reports should be plain URLs, not wrapped in code ticks.
- CLI trees should be annotated like ChatTea docs: each command or command group needs a short `#` explanation.
- Formal package docs must not read like a linear setup essay or PR narrative.
- Docs should align structurally with ChatTea: scenario selection, docs-column organization, CLI/help entry points, and a separate CLI capability map when the command surface is non-trivial.
- Visual column layout is not enough by itself; the information architecture must be non-linear and task-oriented.

## ChatTea Structure To Reuse

ChatTea's mature docs provide a reusable structure for ChatArch CLI packages:

- README starts with a compact product summary and a `按场景选择文档` table.
- `docs/index.md` starts with scenario-based document selection.
- Docs home includes `文档栏目组织` so readers understand the map before detailed procedures.
- CLI docs include a top-level command tree with inline comments.
- A separate CLI capability map explains implemented command groups and boundaries.
- Detailed procedures may be linear only inside bounded tasks.

## ChatUp Alignment Applied

For ChatUp PR #9, the final accepted shape was:

- `docs/index.md` / `docs/index.en.md`: scenario table, docs-column organization, grid-card entry points, CLI/help section.
- `docs/commands.md` / `docs/commands.en.md`: annotated CLI tree plus command-group cards and service contracts.
- `docs/capability-map.md` / `docs/capability-map.en.md`: ChatTea-style CLI capability map.
- `docs/quickstart.md` / `docs/quickstart.en.md`: recommended-path cards before command details.
- `mkdocs.yml`: `attr_list` and `md_in_html` enabled for Material cards.
- README files: scenario table plus grouped capability overview.

## Verification Pattern

After docs changes, verify all of the following:

```bash
git diff --check
python -m pytest -q
mkdocs build --strict
python -m build
```

Then read back generated or preview pages for:

- scenario-selection headings;
- docs-column organization;
- annotated CLI-tree comments;
- capability-map pages;
- grid-card markup/rendering;
- English pages without CJK source leakage.

Report public URLs as plain URLs, not code-formatted links.
