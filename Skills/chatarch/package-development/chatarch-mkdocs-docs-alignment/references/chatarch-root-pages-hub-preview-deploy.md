# ChatArch Root Pages Hub Preview/Deploy Pattern

Session context: ChatArch.github.io root homepage was updated from direct `main:/` GitHub Pages publishing to the same PR-preview / merge-deploy pattern used for project docs, while adding lowercase project aliases.

## Durable Pattern

- Treat `ChatArch.github.io` as the organization-level public project map and alias router, not as a single package docs repo.
- Keep public source files in the default branch, but publish served output from `gh-pages:/`.
- Add a small staging script (`scripts/build_site.py`) that copies only public static assets into `site/`; do not deploy source-only automation files under `.github/` or `scripts/` unless intentionally public.
- Add a validation script (`scripts/validate_site.py`) that checks:
  - required public files exist: `index.html`, `404.html`, `README.md`, `CNAME`, `.nojekyll`;
  - `CNAME` matches `arch.gh.wzhecnu.cn`;
  - lowercase aliases are current;
  - alias pages point to canonical mixed-case repo paths;
  - private/internal guard names do not leak into public text files.
- Generate lowercase aliases from the root `index.html` public repo links with a deterministic script (`scripts/generate_lowercase_aliases.py`), then validate with `--check` in CI.

## Workflow Shape

Use three workflows:

- `CI`: on push/PR, run `python scripts/validate_site.py`, `python scripts/build_site.py --output site`, and assert key staged files exist.
- `Preview Docs`: on PR, validate/build, then publish `site/` into `gh-pages:/dev/` and upsert a marker-based PR comment pointing to `https://arch.gh.wzhecnu.cn/dev/`.
- `Deploy Docs`: on default-branch push or `workflow_dispatch`, validate/build, then publish `site/` to `gh-pages:/` while preserving existing `dev/` preview output.

## Pages Source Bootstrap

When converting the root homepage from legacy `main:/` Pages source:

1. Create a `gh-pages` branch seeded from current production content before switching source, so the live homepage does not disappear.
2. Update GitHub Pages source to `gh-pages:/` and keep existing CNAME/HTTPS settings.
3. If Pages does not rebuild after changing source, explicitly queue a Pages build through the GitHub Pages builds API.
4. Verify the API reports `source.branch == gh-pages` and `source.path == /`.
5. Verify production root still returns HTTP 200 before reporting the migration complete.

## Verification Evidence

Minimum evidence before telling the user it is done:

- Local: `python3 scripts/validate_site.py`, `python3 scripts/build_site.py --output site`, `git diff --check`.
- PR: `CI` successful and `Preview Docs` successful.
- Preview: `https://arch.gh.wzhecnu.cn/dev/` returns 200, plus one representative alias under preview such as `/dev/chatblog/` returns 200.
- Production source: Pages API source is `gh-pages:/`.
- After merge: `Deploy Docs` successful and `https://arch.gh.wzhecnu.cn/` plus representative lowercase aliases return 200.

## Pitfalls

- Do not leave `ChatArch.github.io` serving from `main:/` after adding preview/deploy workflows; otherwise the deploy workflow is decorative and not authoritative.
- Do not assume pushing `gh-pages` immediately changes the live site. Read the Pages API and, if needed, trigger a Pages build before HTTP verification.
- Do not claim `/dev/` is live just because the preview workflow pushed `gh-pages:/dev/`; the root Pages build may still be stale.
- Keep PR preview comments marker-based so repeated pushes update one comment instead of spamming.
