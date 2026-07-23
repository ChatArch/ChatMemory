# ChatVideo Strict MkDocs Style Audit

Session lesson: after a ChatArch package docs PR looked mechanically correct and was merged, the user asked to review it strictly against the MkDocs style. The stricter pass found formal-docs style gaps that basic CI/MkDocs checks did not catch.

## Durable Findings

A docs site can pass `mkdocs build --strict`, CI, Preview Docs, Deploy Docs, and HTTP readback while still missing the ChatArch docs style.

For CLI package docs, strict acceptance must check content architecture in addition to mechanics:

- Formal docs must not contain PR-history wording such as `当前 PR`, `本 PR`, `Phase 1`, `Phase 2`, `第一阶段`, or `第二阶段`.
- A CLI package needs a first-class CLI tree page when it has even a small command surface. The tree lists implemented commands only; planned commands must be marked as planned or moved to design/capability pages.
- Docs home pages should be hub/card entry pages, not only tables or linear explanations.
- If cards are used, `mkdocs.yml` needs `markdown_extensions: attr_list` and `md_in_html`.
- Bilingual docs need equivalent zh/en surfaces: for example `docs/cli-tree.md` and `docs/cli-tree.en.md`.
- Internal links in zh/en pages should use stable anchors when mixed-language headings generate uncertain slugs.
- README language labels should fit the page context: Chinese README can use `英文版`, English README can use `Simplified Chinese`.

## Example Follow-Up Shape

For ChatVideo, the strict follow-up PR did the following:

- Added `docs/cli-tree.md` and `docs/cli-tree.en.md`.
- Converted `docs/index.md` and `docs/index.en.md` into Material card hub pages.
- Added `attr_list` and `md_in_html` to `mkdocs.yml`.
- Updated nav to `命令与工作流` with `CLI 树` and `设计蓝图`.
- Replaced formal-doc PR-history wording with `当前能力`, `规划边界`, `已实现`, `规划中`, and `安全默认值`.
- Kept `generate image` / `generate frames` as planned blueprints while `chatvideo design` remained the only implemented non-trivial command.

## Extra Checks

Run the normal checks, then add strict content checks:

```bash
python -m pytest -q
python -m build
python -m mkdocs build --strict
rg -n "当前 PR|本 PR|Phase [0-9]|第一阶段|第二阶段|ChatTea-style|Pages/CNAME|docs/CNAME|custom-domain CNAME|github\.io" .
```

Generated-site checks should include the new style surfaces:

```bash
python -m mkdocs build --strict
test -f site/index.html
test -f site/en/index.html
test -f site/cli-tree/index.html
test -f site/en/cli-tree/index.html
rg -n "grid cards|cli-tree|md-content" site/index.html site/en/index.html
rm -rf site
```

If `mkdocs build --strict` prints `Doc file ... contains a link ... but the doc ... does not contain an anchor`, treat it as a style/readability failure even when the command exits 0. Prefer explicit stable heading IDs such as `{ #review-to-final }` or link to simpler anchors.
