# Preview-preserving documentation deployment

## Shared branch contract

When a package publishes production at the documentation root and a PR preview under `dev/` on the same `gh-pages` branch, preserve the preview explicitly. A whole-tree `mkdocs gh-deploy --force` can erase a previously verified preview after merge.

- Build the production tree with `mkdocs build --strict`.
- Read the latest published branch; distinguish an absent branch from a failed network/auth lookup. Do not mask a failed lookup and then publish without the preview.
- Copy only the reserved preview directory and version index into the fresh production output. Do not restore the old production tree, which would retain deleted pages.
- Configure the Git author before using `ghp-import` directly.
- Use one `concurrency` group in both Preview and Deploy, with `cancel-in-progress: false`.
- Keep preview paths reserved; check for a source-page collision before adopting this layout in an existing product.

## Workflow steps

Add this to both documentation workflows:

```yaml
concurrency:
  group: docs-pages
  cancel-in-progress: false
```

After checkout, Python setup, and installation of the existing docs extra, the production job can use:

```yaml
- name: Configure Git Credentials
  run: |
    git config user.name github-actions[bot]
    git config user.email 41898282+github-actions[bot]@users.noreply.github.com
- name: Build and deploy docs
  run: |
    set -euo pipefail
    mkdocs build --strict
    published_ref=$(git ls-remote --heads origin gh-pages)
    if [ -n "${published_ref}" ]; then
      git fetch --no-tags origin gh-pages:refs/remotes/origin/gh-pages
      published="${RUNNER_TEMP}/docs-published"
      git worktree add --detach "${published}" refs/remotes/origin/gh-pages
      if [ -d "${published}/dev" ]; then
        cp -R "${published}/dev" site/dev
      fi
      if [ -f "${published}/versions.json" ]; then
        cp "${published}/versions.json" site/versions.json
      fi
      git worktree remove "${published}"
    fi
    ghp-import --no-jekyll --push --force --message "Deploy docs for ${GITHUB_SHA}" site
```

This uses the existing docs dependency chain and does not require a new daemon, custom domain, DNS change, per-repository CNAME, or package version bump. Make workflow changes through a focused PR; leave product behavior and unrelated release lines unchanged.

## Regression and live gates

Test the extracted deployment shell against a disposable local Git remote and fake build/publish executables. Cover:

1. no existing publication branch;
2. existing preview and version index survive;
3. obsolete production pages do not survive;
4. the temporary Git worktree is removed;
5. Preview and Deploy use the same non-cancelling lock.

After the focused tests, validate the real chain: exact PR head CI and Preview success → preview root and deep page HTTP 200 → authorized merge → exact merged-main CI and Deploy success → Pages deployment success for the current `gh-pages` commit → production and preview roots, English homes, and deep pages HTTP 200 with expected content and canonical URLs. A Pages API status by itself is weaker than the deployment run plus live content.

For multi-repository work, save each batch to a JSON ledger, verify unique target counts, and compute the final totals from the ledger. Reuse a known successful package publishing chain; a documentation-only repair does not authorize another PyPI release.

