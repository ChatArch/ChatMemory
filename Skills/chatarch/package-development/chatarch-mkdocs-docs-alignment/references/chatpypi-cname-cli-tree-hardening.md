# ChatPyPI Template CNAME And CLI Tree Hardening

Session lesson from a ChatPyPI PR review where the user corrected the assistant several times. This applies to future ChatArch package scaffold/template reviews.

## Durable Rules

- ChatArch project docs use an organization-level Pages domain plus repository path:
  - `https://arch.gh.wzhecnu.cn/<Repo>/`
  - `https://arch.gh.wzhecnu.cn/<Repo>/dev/`
  - `https://arch.gh.wzhecnu.cn/<Repo>/en/` for i18n.
- That URL model does **not** require per-repository `docs/CNAME` files.
- For standard ChatArch package scaffolds, remove the CNAME concept entirely from default user-facing docs and template CLI help. Do not stop at “default off” if the user is asking for the standard scaffold.
- A `--docs-domain` option can still be valid when it only controls generated URLs, badges, package metadata, `site_url`, and preview links. It should not imply domain ownership files.
- Remove development-plan/roadmap placeholders from generated scaffold output and from the generator docs/nav when they are being shown as formal template structure.
- Keep explicit negative tests that the generated scaffold lacks `docs/CNAME`, `docs/development-plan.md`, and generic `docs/commands.md` replacements.

## Review Checklist

When reviewing a scaffold generator like ChatPyPI:

1. Search the full repository, not only generated sample output:
   - `CNAME`, `with-docs-cname`, `without-docs-cname`, `include_docs_cname`, `_build_docs_cname`
   - `development-plan`, `Development Plan`, `开发计划`, `路线图`
   - `commands.md` if the intended command-map surface is `cli-tree.md`
2. Classify matches:
   - user-facing docs/nav/help: should not mention CNAME for the standard ChatArch package path;
   - implementation path: should not write `docs/CNAME`;
   - tests: may keep “must not exist / must not appear in help” assertions.
3. Check the generator package’s own docs too. A template generator whose scaffold emits a CLI tree must expose its own standard CLI tree in README/docs/nav.
4. Generate a sample project and assert:
   - `docs/cli-tree.md` and `.en.md` exist;
   - `docs/capability-map.md` and `.en.md` exist;
   - `docs/interface-tree.md` exists;
   - `docs/CNAME`, `docs/development-plan.md`, and `docs/commands.md` do not exist;
   - `chatpypi init --help` does not expose CNAME options.

## CLI Tree Shape

The user emphasized that CLI trees are non-optional for ChatArch/ChatStyle CLI tools because they are the quickest way to see supported commands.

For non-trivial CLIs, use ChatTea-style segmented CLI trees:

- top-level command overview first;
- then one section per major command group;
- every command line has an inline comment;
- each section has status/checkpoint/boundary notes;
- capability maps complement CLI trees but do not replace them.

Avoid a single huge tree plus generic cards when the command surface has multiple responsibilities. Avoid replacing the CLI tree with `commands.md` unless the user explicitly asks for that filename.
