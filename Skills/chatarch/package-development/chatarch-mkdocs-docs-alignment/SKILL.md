---
name: chatarch-mkdocs-docs-alignment
description: "Align ChatArch package docs to the ChatArch MkDocs bilingual documentation standard, GitHub Pages previews, About URLs, package metadata, and verification flow."
version: 0.1.13
---

# ChatArch MkDocs Docs Alignment

Use this skill when a ChatArch package needs a documentation site, README documentation links, MkDocs navigation, bilingual docs, GitHub Pages workflows, GitHub About metadata, or package documentation metadata aligned to the ChatArch project standard.

Use mature package documentation sites as reference implementations when useful, but treat the governing rule as the ChatArch-series MkDocs documentation standard. Apply it even when the current repository has no relationship to the reference package.

For the ChatUp session where the user corrected CLI-tree annotation, non-linear docs, column/card layout, ChatTea-style alignment, and plain-link reporting, see `references/chatup-chattea-docs-alignment-session.md`.

For the ChatPyPI template follow-up that clarified package scaffolds should keep command/capability maps but drop development-plan placeholders and default CNAME files, see `references/chatpypi-chatarch-template-map-alignment.md`.

For the later ChatPyPI review that hardened this further—no CNAME concept in the standard scaffold, no docs/nav references to development-plan/CNAME, and ChatTea-style segmented CLI trees for both generator docs and generated template docs—see `references/chatpypi-cname-cli-tree-hardening.md`.

For the Gitea self-hosted Pages session that validated PR preview Pages with a Gitea native bot user, stable/dev channels, and unified entry routing, see `references/gitea-pages-native-bot-preview-flow.md`.

For the Gitea bot/user/trigger/executor explanation that emerged from the native-bot PR preview practice and `@bot` mention discussion, see `references/gitea-bot-trigger-executor-practice.md`.

For the ChatBlog Docusaurus session that aligned a non-MkDocs static site to ChatArch Pages preview/deploy, Pages API enablement, About homepage sync, and lowercase URL aliases, see `references/chatblog-docusaurus-pages-deploy.md`.

For the ChatArch root homepage session that converted `ChatArch.github.io` from legacy `main:/` Pages serving to CI + PR preview + merge deploy via `gh-pages:/`, see `references/chatarch-root-pages-hub-preview-deploy.md`.

## Trigger Conditions

Use this when the user says any of:

- "补文档站"
- "对齐 MkDocs 文档规范"
- "对齐 ChatArch 文档规范"
- "文档站域名不对"
- "Preview Docs 链接不对"
- "Gitea Pages / 自托管 Pages / Gitea Actions preview"
- "Gitea bot / 机器人评论 PR / PR 预览链接"
- "ChatBlog / Docusaurus 博客站 / 公开知识站部署"
- "ChatArch.github.io / 主页面 / 组织主页 / root Pages hub"
- "PR 自动生成文档 / 合并自动更新文档"
- "给主页面补 CI / Preview Docs / Deploy Docs 模板"
- "Pages 没启用 / Pages 404 / gh-pages 有但站点打不开"
- "About URL / homepage 没同步"
- "PyPI Documentation 链接没同步"
- "补中英文文档 / i18n / 栏目分栏"
- "不要线性文档 / 文档不是线性说明书"
- "首页要像导航入口 / 文档要卡片分栏"
- "把旧文档改成标准模式"

If the user names an existing package docs site as an example, treat it as a reference repo to inspect, not as the naming center of the norm.

When the user is explicitly discussing Gitea, stay on Gitea unless they ask for GitHub/GitLab comparison. If they ask about a "bot" in Gitea, first check or use Gitea's native `--user-type bot` user model before proposing a custom bot daemon/service; this user corrected the workflow when the assistant treated the bot as an external service abstraction. Explain the automation model as identity/trigger/executor/credential: the bot is the API identity, while behavior is triggered by Actions events, webhooks, notification polling, cron, CLI, or service code.

## Target Shape

Do not blindly copy another package's product content. Copy the documentation mechanics and adapt the information architecture to the current package's real domain.

For ChatArch CLI package docs, treat ChatTea's mature docs as the primary structural reference when no better domain-specific reference is named: README/docs index should provide a scenario-selection table, docs-column organization, a CLI/help section, and a first-class `CLI 树` / `CLI Tree` page when the command surface is non-trivial. The CLI tree must be visually direct: show the command topology with inline comments before higher-level grouping. For non-trivial CLIs, match the ChatTea shape: top-level command overview first, then major command groups as separate sections with their own annotated trees and boundary/status notes. Do not stop at one giant tree block plus generic cards if the command surface has several responsibility areas. Adapt the nouns and workflows to the current package rather than copying ChatTea's Gitea content. When aligning a scaffold generator such as ChatPyPI, align both the generated template docs and the generator package's own docs to this CLI-tree standard.

When the repository has no real docs site yet, treat the review as a first-site alignment rather than a small README edit: add a minimal product-facing MkDocs scaffold (`mkdocs.yml`, default-language docs, `.en.md` mirrors, README/README.en links, docs extra, CI docs build, preview/deploy workflows), remove placeholder docs that conflict with `index.md`, and prove the preview with HTTP readback. For the ChatUp first-site pattern, see `references/chatup-mkdocs-first-docs-site.md`.

Do not stop a docs review at MkDocs mechanics. After `mkdocs.yml`, workflows, metadata, and preview URLs look correct, verify that README/docs/design pages express the user's corrected product model and clearly separate implemented commands from planned blueprints. For the ChatVideo image-to-video correction pattern, see `references/chatvideo-image-to-video-keyframe-docs.md`.

When a package has workflow/design material, keep documentation blueprints in docs and keep the CLI reserved for executable tool behavior. Do not create a `design` command whose only job is to print Markdown-like plans. If no real subcommands exist yet, the CLI tree should list only real entries such as `--help` and `--version`, and the planned capabilities should be marked as documentation-only. For the ChatVideo rollback and language-separation follow-up, see `references/chatvideo-cli-doc-boundary-and-language.md`.

When the user asks to apply the MkDocs style strictly, audit formal docs architecture even if the PR already merged and all workflows passed. Check for first-class CLI tree pages, Material card hub pages, `attr_list`/`md_in_html`, stable internal anchors, README language-label context, and absence of PR-history wording in formal docs. For the ChatVideo strict follow-up, see `references/chatvideo-strict-mkdocs-style-audit.md`.

Before editing any repository, create or reuse a Playground project under `<WORKSPACE_ROOT>/projects/...` when the work is non-trivial. Put worktrees, patches, logs, scripts, smoke-output, and other intermediate files under that project's `playground/`, `scripts/`, `reports/`, or `reference/`. Do not put task work in `/tmp`; if an accidental `/tmp` worktree exists, migrate its diff into the project and remove the `/tmp` worktree before continuing.

Use the Chat-series tools by responsibility:

- ChatGH owns GitHub repository metadata, PRs, Actions, GitHub About metadata, and GitHub Pages API calls.
- Git edits remain normal repo work in a project-local worktree or in `core/` when explicitly appropriate.
- If a Chat-series CLI is missing a GitHub Pages capability, add or fix that interface first when feasible; otherwise use a short token-safe REST bridge for the immediate readback and record the missing command as a ChatGH capability gap.

For non-package static content sites in ChatArch, such as Docusaurus-based ChatBlog, preserve the site's framework when it already fits the product goal. Do not convert Docusaurus to MkDocs solely to match this skill's package-docs examples. Instead apply the shared ChatArch Pages mechanics: canonical public-domain URL, PR preview under `/dev/`, merge deploy to `gh-pages`, GitHub Pages source/readback, About homepage sync, and HTTP verification. See `references/chatblog-docusaurus-pages-deploy.md` for the Docusaurus workflow shape.

A standard package docs PR should usually align:

- `mkdocs.yml`: site metadata, repo URL, Material theme, sectioned nav, docs-domain `site_url`, and `mkdocs-static-i18n` plugin config.
- `README.md` and `README.en.md`: documentation links and short navigation. Keep the Chinese default README in Chinese and the English README in English; do not leave English badge HTML/prose in `README.md` if the language checker will treat it as Chinese source.
- `docs/index.md` and `docs/index.en.md`: Chinese default docs home plus English counterpart; `.en.md` files are language-source mirrors, not separate nav entries.
- Domain-specific docs pages: quickstart, command map, capability map, interface tree, workflow guide, API/CLI alignment, design docs, or operations notes as appropriate.
- For package scaffolding templates, placeholder content is expected and useful: the template should create correct structural slots that future model/project work fills with real package details. Keep only durable review surfaces by default: index/home, CLI tree, capability map, and interface tree. Do not default-generate development-plan/roadmap placeholders, generic `commands.md` replacements for the CLI tree, or per-repository domain ownership files. In the normal ChatArch Pages model, project docs live under the organization public-domain path `https://arch.gh.wzhecnu.cn/<Repo>/`, so scaffolds should generate URLs/badges/preview links from the docs domain + repo path and should not expose a `CNAME` file or `--with-docs-cname` option unless the user explicitly asks for a nonstandard custom-domain workflow.
- If the repository is a scaffold/template generator, align both the generated scaffold output and the generator package's own docs. A generator whose template emits a standard CLI tree should also expose its own standard CLI tree in README/docs/nav.
- `pyproject.toml`: `[project.urls] Documentation` when package metadata has docs URLs, plus `mkdocs-static-i18n` in the `docs` extra.
- GitHub repository About / homepage URL: use `chatgh repo edit <Owner>/<Repo> --homepage <site_url> --json-output` so the About panel points to the built docs site.
- `.github/workflows/ci.yml`: install `.[dev,docs]` when package metadata/workflows are touched and run `mkdocs build --strict`.
- `.github/workflows/preview.yaml`: PR preview deploys to the project Pages `/dev/` path and comments the public-domain preview URL.
- `.github/workflows/deploy.yaml`: default-branch deploy publishes the built MkDocs site to `gh-pages`.
- `.gitignore`: ignores generated `site/` output.
- `CHANGELOG.md`: user-visible docs/metadata/workflow changes. In a Chinese-default package, keep changelog prose Chinese unless the repo deliberately maintains a separate English changelog surface.

## ChatTea Pattern Reuse For Scaffolds

When using ChatTea as a documentation reference for a scaffold or another ChatArch package, borrow patterns rather than content:

- Use the homepage as a navigation hub with a scenario-selection table and docs-column organization.
- For CLI packages, keep `CLI 树` / `CLI Tree` as a required first-class entry. It is the most direct way to see what the package supports, so do not replace it with only a higher-level command map or capability map.
- CLI tree pages should show the real command tree with inline comments, status/boundary notes, and update rules. For non-trivial CLIs, use ChatTea's segmented layout: `顶层命令` / `Top-Level Commands` first, then separate sections for each major command group with annotated tree blocks and short boundary paragraphs.
- Capability maps explain product/package responsibility boundaries; they complement the CLI tree but do not replace it.
- Provide maps that guide review: CLI tree, capability map, and interface tree.
- Keep status contracts such as implemented/verified/not implemented, but adapt nouns and examples to the current package.
- Keep generated scaffold pages placeholder-oriented; placeholders are good when they are structural slots, not project-specific plans.
- Do not import ChatTea-specific service content, Gitea details, or operational workflows unless the current package truly owns them.

## Public URL Rules

For ChatArch package project pages, the canonical public docs URL should be the ChatArch Pages public-domain path. This is an organization-level domain plus repository path model, not a per-repository custom-domain model:

```text
site_url: https://arch.gh.wzhecnu.cn/<Repo>/
preview: https://arch.gh.wzhecnu.cn/<Repo>/dev/
zh home: https://arch.gh.wzhecnu.cn/<Repo>/
en home: https://arch.gh.wzhecnu.cn/<Repo>/en/  # when true i18n is enabled
```

Do not add or document `docs/CNAME` for the standard ChatArch package path. A configurable docs domain may be used to compute URLs, badges, package metadata, preview comments, and `site_url`; it does not imply writing a custom-domain ownership file into each repo.

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
- GitHub Pages paths are case-sensitive even though hostnames are not; keep the canonical repo-cased path, and add explicit root-site aliases such as `/chatblog/ -> /ChatBlog/` only as user convenience redirects.
- Lowercase convenience aliases belong in the organization/root Pages repo (`ChatArch.github.io`), not in every project repo. A project repo cannot handle a request whose first path segment has the wrong case.
- For new project docs sites, add the alias once when the project is first connected to ChatArch Pages; routine content updates should not touch aliases.
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

## Gitea Actions Pages Preview Pattern

For self-hosted Gitea Pages-like docs previews, mirror the GitHub Pages mental model with Gitea-native pieces rather than inventing a separate bot service:

- Platform event triggers workflow: `pull_request` builds preview; `push` to the default branch builds stable.
- Runner is a worker registered at instance/org/repo scope and matched by `runs-on` label; it is not a public Web service.
- Preview publish channel should be PR-scoped, for example `/pages/<owner>/<repo>/dev/pr-<number>/`.
- Stable publish channel should be canonical, for example `/pages/<owner>/<repo>/`, and must preserve existing `dev/pr-*` preview directories unless cleanup is an explicit operation.
- Use a Gitea native bot user created with `gitea admin user create --user-type bot`; store its scoped token in an Actions secret such as `CHATTEA_BOT_TOKEN`.
- The preview workflow should create or update a single PR comment identified by a marker such as `<!-- chattea-pages-preview -->`, so PR synchronization updates the same comment instead of spamming.
- Verify author identity through the issue-comment API: the comment `user.login` should be the native bot, for example `chattea-pages-bot`, analogous to GitHub's `github-actions[bot]` identity.
- Before claiming the flow is complete or merging related docs, leave a real internal Gitea PR open for user review, and report the PR URL, Actions run URL, bot-comment URL, preview URL, run/job status, and comment author. The user corrected this workflow after a docs PR was merged without a visible acceptance PR.
- When the user asks for screenshots or tutorial evidence, capture the open PR overview, pull_request Actions run, native-bot comment, and preview Pages page; add them to the usage tutorial rather than only reporting links in chat.

See `references/gitea-pages-native-bot-preview-flow.md` for the validated command shape, documentation pitfalls, acceptance-review sequence, and verification checklist.

## Root Homepage Lowercase Alias And Deploy Pattern

When updating `ChatArch.github.io` for user-friendly lowercase routes or root Pages automation:

- Treat `ChatArch.github.io` as the single owner of aliases such as `/chatblog/ -> /ChatBlog/`; do not duplicate this in each project repo.
- Generate aliases from the current public ChatArch repo list, excluding private/internal guard names and the root Pages repo itself.
- For every mixed-case public repo, create `<lowercase>/index.html` as the root shortcut and update `404.html` with a lowercase-to-canonical first-segment map so nested paths redirect too.
- Preserve the rest of the path, query string, and hash: `/chatblog/blog/x?y#z` should redirect to `/ChatBlog/blog/x?y#z`.
- Open a PR for root-homepage alias-map refreshes instead of merging directly; this user explicitly prefers the org homepage update to be reviewed as a PR.
- When the user then says to "review" and "直接合版" / "做第一点", do a concise code-review pass first, then merge the PR without asking again. After merge, wait for default-branch `CI` and `Deploy Docs`, verify public URLs, and fast-forward the local `main` worktree.
- For root homepage CI, use the same class-level shape as project docs: `CI` validates, `Preview Docs` publishes `site/` to `gh-pages:/dev/`, and `Deploy Docs` publishes `site/` to `gh-pages:/` while preserving `dev/`.
- Before switching `ChatArch.github.io` from legacy `main:/` serving to `gh-pages:/`, seed `gh-pages` from current production content so the root site remains live.
- After changing Pages source or pushing preview output, do not rely on the push alone. Read the Pages API, queue a Pages build if stale, and verify `/`, `/dev/`, and a representative preview alias such as `/dev/chatblog/` return HTTP 200.
- Verify `git diff --check`, alias count, expected key aliases, and the private-name guard before pushing. See `references/chatarch-root-pages-hub-preview-deploy.md` for scripts and acceptance checks.

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

When this user says "About" in this docs/Pages context, assume they mean the GitHub repository About/sidebar homepage URL unless they explicitly ask for an in-site About page.

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
8. Default Chinese pages should stay in a Chinese reading context. Do not expose parallel English labels such as `[English](README.en.md)`, `CLI / API`, or English scenario headings in the Chinese README/docs body unless they are unavoidable product names or code literals. Use Chinese link labels such as `英文版`, `命令与接口`, `命令地图`, and `能力地图`; keep English prose in `.en.md` pages and the Material language switch.

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
- Treat quickstart pages as a chooser: group independent flows into cards before detailed commands.
- Treat command reference pages as a map: show the CLI tree, then group commands by responsibility with cards/tables and deep links.
- Use hub-and-spoke information architecture: overview pages help readers jump to task pages; task pages can be linear only inside one bounded task.
- If a page has three or more peer concepts, commands, flows, or decision paths, use columns/cards/table grouping before prose.
- Prefer MkDocs Material `grid cards` / `cards` markup with `attr_list` and `md_in_html`; do not rely only on plain lists when a page is a navigation hub.
- `mkdocs.yml` for first-site package docs should include `markdown_extensions: attr_list` and `md_in_html` when cards/grids are used.
- Verify the generated page contains the grid/card markup and still works on both default and English i18n pages.

Linear content is allowed only for narrow procedures where step order matters, and even then the page should start with a compact non-linear summary or decision card when there are multiple paths.

Formal package docs are product/user documentation, not development history. Write what exists, what is planned, what is out of scope, and what safety contract applies. Do not describe the PR journey or implementation sequence inside formal pages.

For CLI packages, include a compact implemented-command tree in the command reference, in both Chinese and English pages when bilingual docs exist. The tree should show the real command topology and clarify important absent subtrees (for example a first-level CLI that intentionally has no `setup ...` subtree). Keep it to implemented commands only, use ASCII tree glyphs unless the file already uses Unicode tree drawing characters, and verify the generated command page renders the tree. See `references/chatup-mkdocs-cli-tree.md`.

Separate command maps from capability maps when both are useful:

- Command map answers "how do I invoke it?": CLI tree, command groups, command status, interactive conventions, command-update checklist, and links to deeper command docs.
- Capability map answers "what does this package own?": first-class capabilities, verification state, safety/defaults, boundaries, and explicit out-of-scope notes.
- Small packages may keep these pages short, but do not collapse the distinction when the user asks for both maps; they support different review questions.
- For generated templates, keep `cli-tree.md` / `cli-tree.en.md` as the default command-map surface because the CLI tree is the most intuitive command display entry. The CLI tree page can carry the command-map role: tree first, then status, grouping, interactive conventions, and update checklist. Pair it with `capability-map.md` / `capability-map.en.md`; do not replace the CLI tree with a generic `commands.md` page unless the user explicitly asks for that naming. For scaffolded CLI pages, provide a ChatTea-style structure even when most content is placeholder: top-level command tree, base entries, business-command slots, status contract, and implementation contract.

For formal interface trees, list implemented commands only. Put planned commands in a capability map or roadmap with status labels. Do not make future commands look like implemented user-facing interfaces.

Avoid progress-history headings in formal docs:

- Do not write `第一阶段` / `第二阶段` / `第三阶段` or `Phase 1` / `Phase 2` / `Phase 3`.
- Do not write `本轮`, `本 PR`, `Implemented Scope In This PR`, or other PR-history wording.
- Prefer `当前能力`, `规划中的能力`, `不在当前范围`, `最小可用能力`, `接口范围`, and `当前 CLI 到 Python API 映射`.
- Keep PR history in the PR body, `progress.md`, or `CHANGELOG.md`; keep formal docs stable and reader-facing.

See `references/formal-docs-i18n-and-progress-cleanup.md` for a compact rewrite table and the exact user correction that motivated this rule.

## User-Facing Reporting

When reporting PRs, Actions runs, preview pages, or docs URLs back to this user, write URLs as plain clickable text. Do not wrap full links in backticks or code blocks; reserve code formatting for file paths, commands, commit SHAs, and literal config keys.

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
mkdocs build --strict
test -f site/index.html
test -f site/en/index.html
test -f site/sitemap.xml
rg -n "md-select|/<Repo>/en/|hreflang=\"en\"|arch\.gh\.wzhecnu\.cn/<Repo>" site/index.html site/en/index.html site/sitemap.xml
python /path/to/chatarch-mkdocs-docs-alignment/scripts/check_doc_language.py
rm -rf site
```

Strict style checks for CLI package docs:

```bash
rg -n "当前 PR|本 PR|Phase [0-9]|第一阶段|第二阶段|ChatTea-style|Pages/CNAME|docs/CNAME|custom-domain CNAME|github\.io" .
mkdocs build --strict 2>&1 | tee reports/mkdocs-style-build.log
! rg "contains a link" reports/mkdocs-style-build.log
test -f site/cli-tree/index.html
test -f site/en/cli-tree/index.html
rg -n "grid cards|cli-tree" site/index.html site/en/index.html
rm -rf site
```

The bundled `scripts/check_doc_language.py` checks source-language separation, generated English article bodies, and formal-doc progress/history labels. Treat it as a merge gate before pushing or merging a docs PR that touches bilingual pages, README surfaces, changelogs, or interface docs. Do not rely on `mkdocs build --strict` alone for Chinese/English separation.

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
- Do not create, preserve, or document per-repository custom-domain files as part of a normal ChatArch package docs alignment task. Standard ChatArch docs use the organization public-domain path `https://arch.gh.wzhecnu.cn/<Repo>/`; remove `docs/CNAME` from scaffold/template outputs and public docs unless the user explicitly asks for a nonstandard custom-domain workflow.
- Do not claim a preview is live until the Preview Docs workflow has completed and HTTP readback returns 200.
- Do not claim the formal docs site is updated until the PR is merged, deploy completes on the default branch, and HTTP readback confirms the new content.
- If the skill repo is dirty with unrelated changes, edit only the new/target skill files and report the unrelated dirty files as untouched.
