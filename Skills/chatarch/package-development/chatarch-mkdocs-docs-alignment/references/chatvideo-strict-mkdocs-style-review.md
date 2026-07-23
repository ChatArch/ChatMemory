# ChatVideo Strict MkDocs Style Review

Use this reference when a package already has MkDocs mechanics but the user asks to check it strictly against the ChatArch docs style.

## What Happened

ChatVideo PR #1 added a working MkDocs/i18n site, Preview Docs, Deploy Docs, package metadata links, and image-to-video content. It passed local tests, remote CI, Preview Docs, and production HTTP readback.

A later strict style review still found formal-docs issues:

- The docs home pages were table/list based rather than Material hub/card entry pages.
- The package lacked first-class `CLI 树` / `CLI Tree` pages.
- Formal docs included PR-history wording such as `当前 PR` and `本 PR`.
- `mkdocs.yml` lacked `attr_list` and `md_in_html`, so the standard card/grid markup was not enabled.
- Planned generation commands could be mistaken for implemented interfaces unless a CLI tree listed only real commands and marked planned groups as boundaries.

## Corrected Shape

The follow-up PR added:

- `docs/cli-tree.md` and `docs/cli-tree.en.md`.
- A command topology that lists only currently implemented entries:
  - `chatvideo --help`
  - `chatvideo --version`
  - `chatvideo design`
  - `chatvideo design --workflow ...`
  - `chatvideo design --format ...`
- Explicit planned-boundary tables for future `edit`, `generate`, `review`, and `final` command groups.
- Material `grid cards` on both Chinese and English home pages.
- `markdown_extensions: attr_list` and `md_in_html` in `mkdocs.yml`.
- Formal wording such as `当前能力`, `规划中`, `规划边界`, and `安全默认值` instead of PR-history text.

## Review Rule

Do not approve a ChatArch package docs PR just because it has MkDocs and a live preview. Check all three layers:

1. Mechanics: `mkdocs.yml`, i18n, workflows, docs extra, metadata, Pages/About/readback.
2. Product model: docs reflect the user's corrected product intent.
3. Formal style: hub/card home pages, first-class CLI tree for CLI packages, implemented-vs-planned boundaries, no PR-history wording in formal docs.

## Commands Used

```bash
git diff --check
python -m pytest -q
python -m build
python -m mkdocs build --strict
python -m mkdocs build --strict 2>&1 | tee <project>/reports/mkdocs-build.log
! rg -n "contains a link" <project>/reports/mkdocs-build.log
! rg -n "当前 PR|本 PR|本轮|Phase [0-9]|第一阶段|第二阶段" docs README.md README.en.md
```

Generated-site checks should confirm:

```text
site/index.html
site/en/index.html
site/cli-tree/index.html
site/en/cli-tree/index.html
site/sitemap.xml
```

For PR preview and after merge, also HTTP-read back the important pages:

```text
https://arch.gh.wzhecnu.cn/<Repo>/dev/
https://arch.gh.wzhecnu.cn/<Repo>/dev/en/
https://arch.gh.wzhecnu.cn/<Repo>/dev/cli-tree/
https://arch.gh.wzhecnu.cn/<Repo>/dev/en/cli-tree/
https://arch.gh.wzhecnu.cn/<Repo>/
https://arch.gh.wzhecnu.cn/<Repo>/en/
https://arch.gh.wzhecnu.cn/<Repo>/cli-tree/
https://arch.gh.wzhecnu.cn/<Repo>/en/cli-tree/
```
