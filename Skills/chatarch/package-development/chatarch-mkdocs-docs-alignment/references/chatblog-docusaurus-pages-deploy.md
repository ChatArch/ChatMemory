# ChatBlog Docusaurus Pages Deployment Session

Use when a ChatArch static content site is Docusaurus rather than MkDocs, especially ChatBlog-style public knowledge/blog sites.

## Durable Lessons

- Keep the ChatArch public-domain convention even for non-MkDocs sites: `https://arch.gh.wzhecnu.cn/<Repo>/` and PR preview at `https://arch.gh.wzhecnu.cn/<Repo>/dev/`.
- Docusaurus project pages need canonical `url` and `baseUrl` aligned with the shared domain. Prefer env-overridable config so the same source builds production and preview:
  - `CHATBLOG_SITE_URL=https://arch.gh.wzhecnu.cn`
  - `CHATBLOG_BASE_URL=/ChatBlog/` for production
  - `CHATBLOG_BASE_URL=/ChatBlog/dev/` for PR preview
- If the repo uses Docusaurus, do not force-convert to MkDocs just to satisfy the package-docs norm. Copy the ChatArch Pages mechanics: PR preview, default-branch deploy, About homepage sync, Pages API readback, HTTP verification.
- For Docusaurus preview deploys, publish the built `build/` directory under `gh-pages/dev/`; for production deploys, publish `build/` to the `gh-pages` root while preserving `dev/` previews.
- After merge, enable GitHub Pages if `/repos/<Owner>/<Repo>/pages` returns 404, with source `gh-pages:/`, then wait for `status=built` and HTTP 200 on the public-domain URL.
- Sync GitHub About homepage to the canonical public docs URL with `chatgh repo edit <Owner>/<Repo> --homepage <site_url> --json-output`, then verify via REST payload if the local ChatGH view command lacks a `homepage` JSON field.

## URI Case Handling

- URL hostnames are case-insensitive, but GitHub Pages paths are case-sensitive. `/ChatBlog/` and `/chatblog/` are different paths.
- GitHub Pages has no general server rewrite config. For user-friendly lowercase entry points, add explicit aliases in the org/root Pages repo, e.g. `ChatArch.github.io/chatblog/index.html` redirecting to `/ChatBlog/`.
- For deeper lowercase paths such as `/chatblog/blog/...`, add a root `404.html` script with a small alias map from lowercase repo segment to canonical repo segment. This is a convenience redirect, not true global case-insensitivity.
- Do not put lowercase aliases in every project repo. A wrong-case first segment is resolved before a project Pages repo can serve content, so the root org Pages repo is the right place.
- For all-project coverage, generate aliases from the public `ChatArch` repo list: `<lowercase>/index.html` for direct root visits plus `404.html` aliases for nested paths. Preserve path suffix, query, and hash.
- Treat root homepage alias refreshes as PR work. In the validated session, `ChatArch.github.io` PR #1 refreshed the public project map to 47 repos, generated 41 lowercase aliases, and added nested fallback redirects.
- Keep private/internal guards when regenerating the organization index or aliases; do not leak private names into `index.html`, `README.md`, alias directories, or `404.html`.

## Verification Pattern

1. Build production: `npm run build`.
2. Build preview: `CHATBLOG_BASE_URL=/ChatBlog/dev/ CHATBLOG_SITE_URL=https://arch.gh.wzhecnu.cn npm run build`.
3. Run `git diff --check`.
4. Push PR and wait for both CI and Preview Docs workflows.
5. Verify `https://arch.gh.wzhecnu.cn/<Repo>/dev/` returns HTTP 200 before claiming preview live.
6. Merge PR, wait for default-branch Deploy Docs and CI.
7. Verify canonical site, a representative deep page, and lowercase alias with browser or HTTP readback.
