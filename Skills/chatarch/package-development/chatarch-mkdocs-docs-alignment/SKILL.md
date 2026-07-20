---
name: chatarch-mkdocs-docs-alignment
description: "Align ChatArch package docs to the ChatTea-style MkDocs structure, bilingual docs, GitHub Pages custom-domain previews, and CNAME/Page settings."
version: 0.1.0
---

# ChatArch MkDocs Docs Alignment

Use this skill when a ChatArch package needs its documentation site, README links, MkDocs navigation, or GitHub Pages workflows aligned to the current ChatTea-style pattern.

## Trigger Conditions

Use this when the user says any of:

- "对齐 ChatTea 文档模式"
- "文档站域名不对"
- "确保 CNAME / Pages 正常"
- "Preview Docs 链接不对"
- "补中英文文档 / i18n / 栏目分栏"
- "把旧文档改成标准模式"

## Target Shape

Do not blindly copy ChatTea's product content. Copy the documentation mechanics and adapt the information architecture to the package's real domain.

A standard package docs PR should usually align:

- `mkdocs.yml`: site metadata, repo URL, Material theme, nav, docs-domain `site_url`.
- `README.md` and `README.en.md`: docs links and short navigation.
- `docs/index.md` and `docs/index.en.md`: Chinese-first docs home plus English counterpart.
- Domain-specific docs pages: capability map, interface tree, quickstart, API/CLI alignment, or design docs as appropriate.
- `pyproject.toml`: `[project.urls] Documentation` when package metadata has docs URLs.
- `.github/workflows/preview.yaml`: preview comment URL generated from `mkdocs.yml site_url`, not hardcoded `github.io`.
- `.github/workflows/deploy.yaml`: deploys the built MkDocs site to `gh-pages`.
- `CHANGELOG.md`: user-visible docs/metadata/workflow changes.

## Domain Rules

For ChatArch package project pages, the canonical public docs URL should be the ChatArch Pages custom domain path:

```text
site_url: https://arch.gh.wzhecnu.cn/<Repo>/
preview: https://arch.gh.wzhecnu.cn/<Repo>/dev/
zh home: https://arch.gh.wzhecnu.cn/<Repo>/
en home: https://arch.gh.wzhecnu.cn/<Repo>/en/  # when true i18n is enabled
```

Keep normal repository, badge, and source links on `github.com` when they point to GitHub itself. The custom-domain rule is specifically for built docs URLs, canonical/sitemap URLs, language alternates, package metadata documentation links, and Preview Docs comments.

## CNAME And Pages Settings

Do not add a project-level `docs/CNAME` just because a project uses `https://arch.gh.wzhecnu.cn/<Repo>/`.

Current ChatArch pattern:

- The organization Pages repository owns the root CNAME.
- `https://arch.gh.wzhecnu.cn/CNAME` should return `arch.gh.wzhecnu.cn`.
- Project pages such as `ChatTea` and `ChatGH` use `gh-pages` branch `/` as source.
- Project pages normally show `cname: null` in the GitHub Pages API; that is expected because they inherit the org custom domain path.

Readback pattern:

```bash
# Safe fields only; do not print tokens.
GET /repos/ChatArch/ChatArch.github.io/pages
GET /repos/ChatArch/<Repo>/pages
```

Expected safe result:

```text
ChatArch.github.io: source main /, cname arch.gh.wzhecnu.cn, html_url https://arch.gh.wzhecnu.cn/
<Repo>: source gh-pages /, cname null, html_url http(s)://arch.gh.wzhecnu.cn/<Repo>/
```

If `/repos/ChatArch/<Repo>/pages` returns `404` but `gh-pages` exists, enable Pages for that repository with source `gh-pages` `/`, then verify the custom-domain URL returns HTTP 200.

## Preview Workflow Pattern

Avoid hardcoded preview URLs such as:

```text
https://${owner}.github.io/${repo}/dev/
```

Instead derive the preview URL from `mkdocs.yml` `site_url` so custom-domain changes are reflected in PR comments and summaries:

```yaml
      - run: |
          git fetch origin
          mike deploy dev -p --allow-empty
          site_url=$(python - <<'PY'
          from pathlib import Path

          for line in Path("mkdocs.yml").read_text(encoding="utf-8").splitlines():
              if line.startswith("site_url:"):
                  print(line.split(":", 1)[1].strip().rstrip("/"))
                  break
          else:
              raise SystemExit("mkdocs.yml is missing site_url")
          PY
          )
          preview_url="${site_url}/dev/"
          echo "CHATARCH_PREVIEW_URL=${preview_url}" >> "$GITHUB_ENV"
          echo "Preview URL: ${preview_url}" >> "$GITHUB_STEP_SUMMARY"

      - name: Comment PR with Preview Link
        uses: actions/github-script@v6
        with:
          script: |
            const { payload, repo } = context;
            const previewLink = process.env.CHATARCH_PREVIEW_URL;
```

If the workflow already created a wrong `github.io` preview comment, delete or update only that bot-generated comment after the correct custom-domain comment exists.

## Bilingual / i18n Guidance

Use Chinese as the default public docs language unless the page is explicitly English.

Two acceptable maturity levels:

1. Simple bilingual pages: keep `docs/index.md` and `docs/index.en.md`, and list English pages explicitly in `mkdocs.yml`.
2. Full suffix-mode i18n: add `mkdocs-static-i18n`, use `docs_structure: suffix`, Chinese default, English under `/en/`, `fallback_to_default: true`, `reconfigure_material: true`, and `reconfigure_search: true`.

Do not claim full i18n if the repo only has explicit `.en.md` pages without the i18n plugin.

## Information Architecture

Prefer sectioned nav by user scenario:

- Home / overview
- Quick start
- Interface tree or capability map
- Core workflows
- CLI/API alignment
- Agent/bot/runtime design where relevant
- Development / release / operations notes
- English section or full i18n alternate

For formal interface trees, list implemented commands only. Put planned commands in a capability map or roadmap with status labels.

## Verification Checklist

Local checks:

```bash
git diff --check
mkdocs build --strict
python -m pytest -q  # when the package has tests and the docs PR touches package metadata/workflows
rg -n "github\.io|arch\.gh\.wzhecnu\.cn|CNAME|site_url|Preview URL" -g '*.md' -g '*.toml' -g '*.yml' -g '*.yaml' . .github
```

Generated-site checks:

```bash
mkdocs build --strict
test -f site/index.html
test -f site/sitemap.xml
rg -n "arch\.gh\.wzhecnu\.cn/<Repo>" site/sitemap.xml site/index.html
rm -rf site
```

Remote checks after PR push:

```text
- PR `CI` workflow completed successfully.
- PR `Preview Docs` workflow completed successfully.
- `https://arch.gh.wzhecnu.cn/<Repo>/dev/` returns HTTP 200.
- Any important new docs page under `/dev/` returns HTTP 200.
- The PR body records Pages/CNAME readback without secrets.
```

## Safety Notes

- Do not print tokens, repo-local `extraHeader` values, or GitHub API auth headers.
- Do not add or change a CNAME file in a project repo unless the user explicitly asks for a dedicated custom domain for that exact repo.
- Do not claim a preview is live until the Preview Docs workflow has completed and HTTP readback returns 200.
- Do not claim the formal docs site is updated until the PR is merged, deploy completes on the default branch, and HTTP readback confirms the new content.
- If the skill repo is dirty with unrelated changes, edit only the new/target skill files and report the unrelated dirty files as untouched.
