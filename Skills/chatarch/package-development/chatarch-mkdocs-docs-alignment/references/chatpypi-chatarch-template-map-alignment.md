# ChatPyPI ChatArch Template Map Alignment

Session lesson from a ChatPyPI `chatpypi init -t chatarch` template review after ChatUp/ChatTea docs alignment.

## User Corrections

- Do not copy every mature package docs page into a scaffold template.
- Placeholder-style scaffold content is reasonable: the template should create correct structural slots, then future model/project work fills those slots with real package details.
- ChatTea is a useful structural reference, but borrow its documentation patterns rather than its project-specific content.
- Keep reusable review structures such as CLI tree / command-map surface, capability map, and interface tree.
- Drop `development-plan` / plan-like placeholders from generated formal docs.
- Fix default `docs/CNAME`: normal package scaffolds should not generate a per-repo custom-domain file by default.
- Home pages should include a navigation hub, not only linear setup prose.
- Chinese is the default language context; English belongs in `.en.md` files and the MkDocs language switch, not as parallel English labels in default Chinese README/docs pages.
- Important correction: do not remove the CLI tree. The CLI tree is the most intuitive command display entry; it should remain the default command-map page for generated CLI-package scaffolds.
- If the package is itself a CLI template/scaffold generator, align the generator's own docs too. ChatPyPI's own `docs/cli-tree.md` initially existed but was too thin and mislabeled as a generic capability map; it needed a first-class `CLI 树` nav label, full command topology with inline comments, an English mirror, and homepage cards pointing to it.
- Important follow-up: for CLI tools like ChatPyPI/ChatStyle, a standard CLI tree should match ChatTea's segmented style, not merely contain one big tree or generic cards. Start with `顶层命令`, then split major command groups into their own sections, each with an annotated tree block and a short implementation/checkpoint boundary paragraph.

## Template Contract

For ChatArch package scaffolds, default generated MkDocs should include:

- `docs/index.md` and `docs/index.en.md` with scenario navigation and card-style entry points.
- `docs/cli-tree.md` and `docs/cli-tree.en.md` as the command-map surface: tree first, then command status, grouping, interactive conventions, and update checklist.
- `docs/capability-map.md` and `docs/capability-map.en.md` for capability ownership, verification state, safety/defaults, and out-of-scope notes.
- `docs/interface-tree.md` for importable Python API boundaries.
- `mkdocs.yml` with i18n plus `attr_list` and `md_in_html` when Material cards are used.

Default generated MkDocs should not include:

- `docs/development-plan.md` or equivalent plan/roadmap placeholder pages.
- Generic `docs/commands.md` / `docs/commands.en.md` as a replacement for the CLI tree, unless the user explicitly asks for that naming.
- `docs/CNAME`; keep CNAME opt-in via an explicit flag such as `--with-docs-cname`.

## CLI Tree vs Capability Map

- CLI tree answers: how is this invoked? It owns the real command topology, command groups, command status, interactive conventions, and command-update checklist.
- Capability map answers: what does this package own? It owns first-class capabilities, verification state, scope boundaries, and explicit out-of-scope notes.
- Small templates may keep both pages short, but keeping both prevents command details from being mistaken for product capability boundaries.
- If a user asks for “命令地图” in a CLI scaffold, prefer keeping the page named `cli-tree.md` while making its content satisfy the command-map role; do not silently rename it away from the more visual CLI-tree entry.

## Chinese-First Default Pages

Bilingual scaffolds should generate English mirrors, but the default Chinese pages should remain Chinese-first:

- Use Chinese link labels such as `英文版`, `命令与接口`, `CLI 树`, and `能力地图`.
- Keep English prose and English navigation wording inside `.en.md` pages and `nav_translations`.
- Do not put `[English](README.en.md)`, `CLI / API`, or English scenario headings in default Chinese README/docs bodies unless they are unavoidable code/product literals.
- Add tests or generated-template readback checks for this, because regressions are easy when copying bilingual examples.

## Validation Pattern

After patching a scaffold template:

1. Run focused and full template tests.
2. Generate a sample project under the active Playground project, not `/tmp`.
3. Run the generated package tests.
4. Run `mkdocs build --strict` in the generated package.
5. Read generated HTML/sitemap to confirm:
   - home page navigation/card hub exists;
   - CLI tree and capability map pages exist in both languages;
   - `docs/CNAME`, `docs/commands.md`, and `docs/development-plan.md` are absent by default;
   - sitemap includes CLI-tree/capability pages for default and English sites.
