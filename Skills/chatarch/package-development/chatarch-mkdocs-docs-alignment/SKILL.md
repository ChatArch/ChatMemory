---
name: chatarch-mkdocs-docs-alignment
description: "Align ChatArch package docs to the ChatArch MkDocs bilingual documentation standard, GitHub Pages previews, About URLs, package metadata, and verification flow."
version: 0.1.12
---

# ChatArch MkDocs Docs Alignment

Use this skill when a ChatArch package needs a documentation site, README documentation links, MkDocs navigation, bilingual docs, GitHub Pages workflows, GitHub About metadata, or package documentation metadata aligned to the ChatArch project standard.

ChatTea can be used as one reference implementation, but it is not the source of the rule. The rule is the ChatArch-series MkDocs documentation standard and applies even when the current repository has no relationship to ChatTea.

For the ChatVideo strict-style follow-up where an already-merged MkDocs site still failed the full style review, see `references/chatvideo-strict-mkdocs-style-review.md`. That case is the reminder that mechanics, content model, and formal documentation style must all pass before merge.

## Trigger Conditions

Use this when the user says any of:

- "补文档站"
- "对齐 MkDocs 文档规范"
- "对齐 ChatArch 文档规范"
- "文档站域名不对"
- "Preview Docs 链接不对"
- "Pages 没启用 / Pages 404 / gh-pages 有但站点打不开"
- "About URL / homepage 没同步"
- "PyPI Documentation 链接没同步"
- "补中英文文档 / i18n / 栏目分栏"
- "把旧文档改成标准模式"

If the user names ChatTea, ChatGH, ChatData, or another package as an example, treat it as a reference repo to inspect, not as the naming center of the norm.

## Target Shape

Do not blindly copy another package's product content. Copy the documentation mechanics and adapt the information architecture to the current package's real domain.

Before editing any repository, create or reuse a Playground project under `<WORKSPACE_ROOT>/projects/...` when the work is non-trivial. Put worktrees, patches, logs, scripts, smoke-output, and other intermediate files under that project's `playground/`, `scripts/`, `reports/`, or `reference/`. Do not put task work in `/tmp`; if an accidental `/tmp` worktree exists, migrate its diff into the project and remove the `/tmp` worktree before continuing.

Use the Chat-series tools by responsibility:

- ChatGH owns GitHub repository metadata, PRs, Actions, GitHub About metadata, and GitHub Pages API calls.
- Git edits remain normal repo work in a project-local worktree or in `core/` when explicitly appropriate.
- If a Chat-series CLI is missing a GitHub Pages capability, add or fix that interface first when feasible; otherwise use a short token-safe REST bridge for the immediate readback and record the missing command as a ChatGH capability gap.

A standard package docs PR should usually align:

- `mkdocs.yml`: site metadata, repo URL, Material theme, sectioned nav, docs-domain `site_url`, `mkdocs-static-i18n` plugin config, and `markdown_extensions: attr_list` / `md_in_html` when hub/cards are used.
- `README.md` and `README.en.md`: documentation links and short navigation; Chinese README should use Chinese link labels such as `英文版`, while English README uses English labels.
- `docs/index.md` and `docs/index.en.md`: Chinese default docs home plus English counterpart; `.en.md` files are language-source mirrors, not separate nav entries. Treat the home page as a navigation hub, not a linear progress note.
- Domain-specific docs pages: quickstart, CLI tree, command map, capability map, interface tree, workflow guide, API/CLI alignment, design docs, or operations notes as appropriate.
- For CLI packages, add first-class `CLI 树` / `CLI Tree` pages when commands exist or command blueprints are being reviewed. The CLI tree page must list implemented commands only and must mark planned command groups as planned boundaries.
- `pyproject.toml`: `[project.urls] Documentation` when package metadata has docs URLs, plus `mkdocs-static-i18n` in the `docs` extra.
- GitHub repository About / homepage URL: use `chatgh repo edit <Owner>/<Repo> --homepage <site_url> --json-output` so the About panel points to the built docs site.
- `.github/workflows/ci.yml`: install `.[dev,docs]` when package metadata/workflows are touched and run `mkdocs build --strict`.
- `.github/workflows/preview.yaml`: PR preview deploys to the project Pages `/dev/` path and comments the public-domain preview URL.
- `.github/workflows/deploy.yaml`: default-branch deploy publishes the built MkDocs site to `gh-pages`.
- `.gitignore`: ignores generated `site/` output.
- `CHANGELOG.md`: user-visible docs/metadata/workflow changes.

## Public URL Rules

For ChatArch package project pages, the canonical public docs URL should be the ChatArch Pages public-domain path:

```text
site_url: https://arch.gh.wzhecnu.cn/<Repo>/
preview: https://arch.gh.wzhecnu.cn/<Repo>/dev/
zh home: https://arch.gh.wzhecnu.cn/<Repo>/
en home: https://arch.gh.wzhecnu.cn/<Repo>/en/  # when true i18n is enabled
```

For OmniCAS project pages, use the OmniCAS docs domain when the user asks to align OmniCAS docs:

```text
site_url: https://cas.gh.wzhecnu.cn/<Repo>/
preview: https://cas.gh.wzhecnu.cn/<Repo>/dev/
about homepage: https://cas.gh.wzhecnu.cn/<Repo>/
```

Keep normal repository, badge, source, issue, and PR links on `github.com` when they point to GitHub itself. The public-domain rule is specifically for built docs URLs, canonical/sitemap URLs, language alternates, package metadata documentation links, GitHub About homepage, and Preview Docs comments.

## GitHub Pages Settings

The ChatArch package-docs workflow assumes the public docs domain already exists. Do not add per-repository custom-domain files or DNS setup to a normal package docs PR.

Current ChatArch pattern:

- Project pages use `gh-pages` branch `/` as source.
- Project docs are served under the existing public-domain path, for example `https://arch.gh.wzhecnu.cn/<Repo>/`.
- A successful `gh-pages` push is not sufficient proof that Pages is live.
- If `/repos/<Owner>/<Repo>/pages` returns `404` but `gh-pages` exists, enable Pages for that repository with source `gh-pages` `/`, then verify the public-domain URL returns HTTP 200.

Readback pattern uses the GitHub Pages API. Prefer a first-class ChatGH command only if the installed ChatGH implements it; do not document or call nonexistent `chatgh repo pages ...` commands as if they are available.

Safe fields to report:

```text
html_url
status
source.branch
source.path
```

Never print tokens or auth headers. Do not make custom-domain records, DNS provider state, or per-repo domain files part of the standard package-docs acceptance path.

## Preview Docs Workflow Pattern

Avoid hardcoded preview URLs such as:

```text
https://${owner}.github.io/${repo}/dev/
```

Use the ChatArch preview-flow shape. The workflow deploys the PR docs into `gh-pages` with `mike deploy dev`, then comments the public-domain `/dev/` URL:

```yaml
name: Preview Docs

on:
  pull_request:
    branches:
      - main
      - master

permissions:
  contents: write
  pull-requests: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: ${{ !github.event.pull_request.head.repo.fork }}
    steps:
      - uses: actions/checkout@v4
      - name: Configure Git Credentials
        run: |
          git config user.name github-actions[bot]
          git config user.email 41898282+github-actions[bot]@users.noreply.github.com
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -e ".[docs]"
      - run: |
          git fetch origin
          mike deploy dev -p --allow-empty
          repo="${GITHUB_REPOSITORY#*/}"
          preview_url="https://arch.gh.wzhecnu.cn/${repo}/dev/"
          echo "Preview URL: ${preview_url}" >> "$GITHUB_STEP_SUMMARY"

      - name: Comment PR with Preview Link
        uses: actions/github-script@v6
        with:
          script: |
            const { payload, repo } = context;
            const previewLink = `https://arch.gh.wzhecnu.cn/${repo.repo}/dev/`;
            const comments = await github.rest.issues.listComments({
              owner: repo.owner,
              repo: repo.repo,
              issue_number: payload.number,
            });
            const existingComment = comments.data.find(comment => comment.body.includes(previewLink));
            if (!existingComment) {
              await github.rest.issues.createComment({
                owner: repo.owner,
                repo: repo.repo,
                issue_number: payload.number,
                body: `Preview available at: ${previewLink}`,
              });
            }
```

If the workflow already created a wrong `github.io` preview comment, update only that bot-generated comment after the correct public-domain comment exists.

## Deploy Docs Workflow Pattern

Formal docs deployment runs from the default branch after merge:

```yaml
name: Deploy Docs

on:
  push:
    branches:
      - main
      - master

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -e ".[docs]"
      - run: mkdocs gh-deploy --force
```

Do not claim the formal docs site has changed until the default-branch deploy completes and HTTP readback confirms the new content.

## About URL And Package Metadata Sync

After deciding the canonical docs URL, synchronize every public surface that claims to be documentation:

```bash
chatgh repo edit <Owner>/<Repo> --homepage <site_url> --json-output
```

For package metadata, align `[project.urls] Documentation` in `pyproject.toml` to the same `<site_url>`. For README/docs links, use the canonical docs URL for user-facing documentation and keep `github.com` links only for source, issues, PRs, or repository badges.

Verify the About homepage by reading the repo payload after update:

```bash
chatgh repo view <Owner>/<Repo> --json homepage,html_url,description
```

## Bilingual / i18n Guidance

The ChatArch package docs pattern is plugin-based language switching, not two separate nav trees and not Chinese/English text crammed into one page.

Use this mechanism:

1. Chinese is the default source page, for example `docs/index.md`.
2. English source pages use suffix names, for example `docs/index.en.md`.
3. `mkdocs-static-i18n` with `docs_structure: suffix` builds the default Chinese site at `/<Repo>/` and the English site at `/<Repo>/en/`.
4. `extra.alternate` creates the Material language switch button in the header.
5. `nav` lists only the default-language page names such as `index.md` and `agent-definition.md`; it must not list `index.en.md` or `agent-definition.en.md` as separate pages.
6. `nav_translations` maps Chinese nav labels to English labels for the `/en/` site.
7. `fallback_to_default: true` is allowed for pages without an English mirror, but do not call that a complete English translation.

Minimum config shape:

```yaml
plugins:
  - search
  - i18n:
      docs_structure: suffix
      fallback_to_default: true
      reconfigure_material: true
      reconfigure_search: true
      languages:
        - locale: zh
          default: true
          name: 中文
          build: true
          site_name: <Repo> 文档
        - locale: en
          name: English
          build: true
          site_name: <Repo> Documentation
          nav_translations:
            首页: Home
extra:
  alternate:
    - name: 中文
      link: /<Repo>/
      lang: zh
    - name: English
      link: /<Repo>/en/
      lang: en
nav:
  - 首页: index.md
```

## Information Architecture

Prefer sectioned nav by user scenario:

- Home / overview
- Quick start
- Command reference with an explicit CLI tree for CLI packages
- Interface tree or capability map
- Core workflows
- CLI/API alignment
- Agent/bot/runtime design where relevant
- Development / release / operations notes

Use non-linear, task-oriented documentation structure by default. This is a hard requirement for formal ChatArch package docs, not a visual nice-to-have:

- Do not write docs as one long linear essay, setup diary, PR narrative, or single-column instruction stream.
- Treat the home page as a hub: expose primary entry points, use cases, safety/defaults, and next actions as parallel cards.
- If a page has three or more peer concepts, commands, flows, or decision paths, use columns/cards/table grouping before prose.
- Prefer MkDocs Material `grid cards` / `cards` markup with `attr_list` and `md_in_html`; do not rely only on plain lists when a page is a navigation hub.
- `mkdocs.yml` for first-site package docs should include `markdown_extensions: attr_list` and `md_in_html` when cards/grids are used.

Formal package docs are product/user documentation, not development history. Write what exists, what is planned, what is out of scope, and what safety contract applies. Do not describe the PR journey or implementation sequence inside formal pages.

Avoid progress-history headings and phrases in formal docs:

- Do not write `当前 PR`, `本 PR`, `本轮`, `Phase 1`, `Phase 2`, `第一阶段`, or `第二阶段` inside `docs/*.md`.
- Prefer `当前能力`, `规划中`, `规划边界`, `不在当前范围`, `安全默认值`, and `当前 CLI 到 Python API 映射`.
- Keep PR history in the PR body, `progress.md`, or `CHANGELOG.md`; keep formal docs stable and reader-facing.

For formal interface trees, list implemented commands only. Put planned commands in a capability map, design blueprint, or roadmap with status labels. Do not make future commands look like implemented user-facing interfaces.

## Verification Checklist

Local checks:

```bash
git diff --check
mkdocs build --strict
python -m pytest -q  # when the package has tests and the docs PR touches package metadata/workflows
rg -n "github\.io|arch\.gh\.wzhecnu\.cn|cas\.gh\.wzhecnu\.cn|site_url|Preview URL|homepage" -g '*.md' -g '*.toml' -g '*.yml' -g '*.yaml' . .github
```

Generated-site checks:

```bash
mkdocs build --strict 2>&1 | tee <project>/reports/mkdocs-build.log
! rg -n "contains a link" <project>/reports/mkdocs-build.log
test -f site/index.html
test -f site/en/index.html
test -f site/cli-tree/index.html  # for CLI packages
test -f site/en/cli-tree/index.html  # for bilingual CLI packages
test -f site/sitemap.xml
rg -n "md-select|/<Repo>/en/|hreflang=\"en\"|arch\.gh\.wzhecnu\.cn/<Repo>" site/index.html site/en/index.html site/sitemap.xml
rg -n "grid cards|md-grid|cli-tree" site/index.html site/en/index.html
! rg -n "当前 PR|本 PR|本轮|Phase [0-9]|第一阶段|第二阶段" docs README.md README.en.md
rm -rf site
```

Remote checks after PR push:

```text
- PR `CI` workflow completed successfully.
- PR `Preview Docs` workflow completed successfully.
- `https://arch.gh.wzhecnu.cn/<Repo>/dev/` or `https://cas.gh.wzhecnu.cn/<Repo>/dev/` returns HTTP 200, depending on owner/domain.
- Any important new docs page under `/dev/` returns HTTP 200.
- GitHub Pages API reports the expected source branch/path.
- `chatgh repo view <Owner>/<Repo> --json homepage` reports the canonical docs URL in the repository About homepage.
- The PR body records Pages/About readback without secrets.
```

## Safety Notes

- Do not print tokens, repo-local `extraHeader` values, GitHub API auth headers, or provider credentials.
- Do not use `/tmp` for code, worktrees, patches, logs, or scripts; use the active project's `playground/`, `scripts/`, `reports/`, or `reference/` directories.
- Do not create per-repository custom-domain files or DNS changes as part of a normal package docs alignment task.
- Do not claim a preview is live until the Preview Docs workflow has completed and HTTP readback returns 200.
- Do not claim the formal docs site is updated until the PR is merged, deploy completes on the default branch, and HTTP readback confirms the new content.
- If the skill repo is dirty with unrelated changes, edit only the new/target skill files and report the unrelated dirty files as untouched.
