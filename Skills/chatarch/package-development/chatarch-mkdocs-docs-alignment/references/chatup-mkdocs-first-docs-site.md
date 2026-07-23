# ChatUp First MkDocs Site Alignment

## When this reference applies

Use this when a ChatArch package has little or no real documentation surface yet: no `mkdocs.yml`, no bilingual docs pages, no `README.en.md`, no docs extra, and no preview/deploy workflows. Treat it as a first-site alignment, not as a small README cleanup.

## Observed gaps in the ChatUp session

The package had a working CLI and README, but the documentation review found:

- no `mkdocs.yml`
- no product docs source pages beyond a placeholder `docs/README.md`
- no `README.en.md`
- no `[project.urls].Documentation`
- no `docs` optional dependency group
- CI did not run `mkdocs build --strict`
- no `Preview Docs` or `Deploy Docs` workflow
- GitHub Pages disabled even though the preview workflow could push `gh-pages`

## First-site patch shape

A minimal ChatArch-standard patch should include:

- `mkdocs.yml` with `site_url: https://arch.gh.wzhecnu.cn/<Repo>/`, Material theme, sectioned nav, `mkdocs-static-i18n`, and `extra.alternate`
- `README.md` as the default-language README and `README.en.md` as the English counterpart
- `docs/index.md` plus `docs/index.en.md`
- at least two scenario pages such as `quickstart` and `commands`, each with `.en.md` mirrors
- domain-specific page(s), e.g. ChatUp used `workspace.md` / `workspace.en.md`
- `[project.urls] Documentation`, Source, and Issues in `pyproject.toml`
- `[project.optional-dependencies].docs` with `mkdocs`, `mkdocs-material`, `mkdocs-static-i18n`, and `mike`
- CI installing `.[docs]` and running `mkdocs build --strict`
- `.github/workflows/preview.yaml` using `mike deploy dev -p --allow-empty`
- `.github/workflows/deploy.yaml` using `mkdocs gh-deploy --force`
- `.gitignore` entry for generated `site/`
- `CHANGELOG.md` entry for user-visible docs/workflow additions

## Pitfalls

- Delete or rename placeholder `docs/README.md` when it conflicts with `docs/index.md`; in strict mode MkDocs can abort with a warning like `Excluding 'README.md' from the site because it conflicts with 'index.md'`.
- Do not treat a successful `gh-pages` push as preview proof. If preview URLs 404 and `/repos/<Owner>/<Repo>/pages` returns 404, enable Pages for `gh-pages` `/`, then retry public-domain HTTP readback.
- Do not set the GitHub About homepage as “done” before the formal default-branch deploy is live. It can be prepared in the PR body, but final About synchronization should be verified after merge/deploy.
- Keep English source pages free of CJK text, including labels like `中文 README`; use English phrasing such as `Chinese README`.
- Keep formal docs product-facing. Do not describe the PR journey or “this patch added...” inside the docs pages.

## Validation ladder

Run locally:

```bash
git diff --check
python -m pytest -q
mkdocs build --strict
python -m build
```

Then verify generated output:

```bash
test -f site/index.html
test -f site/en/index.html
test -f site/sitemap.xml
rg -n 'md-select|hreflang="en"|hreflang="zh"|arch\.gh\.wzhecnu\.cn/<Repo>' site/index.html site/en/index.html site/sitemap.xml
```

Also scan English source files for CJK characters:

```bash
python - <<'PY'
from pathlib import Path
import re, sys
files = [Path('README.en.md'), *Path('docs').glob('*.en.md')]
bad = [str(p) for p in files if re.search(r'[\u4e00-\u9fff]', p.read_text(encoding='utf-8'))]
print(bad)
sys.exit(bool(bad))
PY
```

After pushing the PR:

- require CI success
- require Preview Docs success
- require public-domain preview HTTP 200 for the home page, English home, and at least one important content page in both languages
- record the preview readback and Pages source in the PR body without printing tokens
