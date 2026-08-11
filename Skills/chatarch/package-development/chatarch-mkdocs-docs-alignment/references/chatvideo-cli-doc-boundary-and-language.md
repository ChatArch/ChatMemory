# ChatVideo CLI / Docs Boundary And Language Follow-Up

Use this reference when a package has workflow planning docs but the CLI has not implemented real tool behavior yet.

## What Went Wrong

ChatVideo initially added `chatvideo design` and `src/chatvideo/design.py` to print provider-neutral workflow blueprints. That mixed responsibilities:

- Markdown workflow planning belongs in docs.
- CLI commands should perform concrete tool actions.
- A command that only prints design notes is not a useful tool surface.
- Tests that assert blueprint text output can make documentation look like implemented behavior.

The user corrected this sharply: a CLI is an operation surface, not a place to dump task notes or Markdown design content.

## Correct Boundary

For a package with no real video operations implemented yet:

- Keep the CLI minimal: `chatvideo --help` and `chatvideo --version` only.
- Delete documentation-only commands such as `chatvideo design`.
- Delete code modules whose only purpose is rendering docs-like plans, such as `src/chatvideo/design.py`.
- Keep image-to-video, first/last-frame, review, and final-delivery planning in docs, for example `docs/workflow-blueprint.md` and `docs/workflow-blueprint.en.md`.
- In the CLI tree, list only real runnable entries and put future capabilities under a documentation-only planned-boundary section.
- Add tests that assert fake commands are not exposed when they are not implemented.

## Language Separation Lesson

After the CLI/doc boundary was fixed, the strict language checker still failed because Chinese-facing surfaces contained English prose:

- `README.md` used English badge HTML and `alt` text.
- `CHANGELOG.md` was written in English in a Chinese-default repository.

The final fix:

- Keep `README.md` Chinese except for literal package names, command names, URLs, and identifiers.
- Keep `README.en.md` English.
- In a Chinese-default package, write `CHANGELOG.md` in Chinese unless there is a deliberate separate English changelog.
- Run the bundled `scripts/check_doc_language.py` after `mkdocs build --strict`, not just MkDocs itself.

## Required Checks Before Merge

```bash
git diff --check
python -m pytest -q
python -m build
python -m mkdocs build --strict
python /path/to/chatarch-mkdocs-docs-alignment/scripts/check_doc_language.py
rg -n "from chatvideo\.design|workflow_keys|render_json|render_text|src/chatvideo/design|docs/cli-design|cli-design\.md|chatvideo design --|@main\.command\(|def design\(" .
```

For generated docs readback:

```bash
for url in \
  https://arch.gh.wzhecnu.cn/ChatVideo/ \
  https://arch.gh.wzhecnu.cn/ChatVideo/en/ \
  https://arch.gh.wzhecnu.cn/ChatVideo/cli-tree/ \
  https://arch.gh.wzhecnu.cn/ChatVideo/en/cli-tree/ \
  https://arch.gh.wzhecnu.cn/ChatVideo/workflow-blueprint/ \
  https://arch.gh.wzhecnu.cn/ChatVideo/en/workflow-blueprint/; do
  curl -L -sS -o /dev/null -w '%{http_code} %{url_effective}\n' "$url"
done
```

## ChatVideo PR Sequence

- PR #3 `Remove documentation-only design CLI` removed the fake CLI and moved workflow planning back into docs.
- PR #4 `Localize Chinese docs surfaces` removed English prose from Chinese-facing README/changelog surfaces.
- Final main state to verify: `55f552f Localize Chinese docs surfaces`.
- Default-branch CI, Deploy Docs, and Pages build all passed; formal docs URLs returned HTTP 200.

## Rule Of Thumb

If a command cannot perform a real operation on user input, files, provider jobs, manifests, review artifacts, or final outputs, do not put it in the CLI. Write it as documentation instead.
