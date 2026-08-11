# ChatUp MkDocs CLI Tree Lesson

## Context

During a ChatUp docs alignment PR, the standard MkDocs scaffold added README, bilingual docs pages, CI docs build, preview/deploy workflows, and package metadata. The user then corrected the documentation deliverable: the command reference needed an explicit CLI tree.

## Reusable Lesson

For ChatArch CLI packages, a command reference page should not only list commands in prose or tables. It should include a compact CLI tree that shows the current command topology and clarifies any important absent subtree.

For ChatUp specifically, the important product point was that ChatUp uses first-level commands and does **not** have a `chatup setup ...` subtree. The command reference therefore included a section like:

```text
chatup
|-- doctor
|-- uv
|-- workspace
|-- nodejs
|-- docker
|-- zsh
|-- chrome
|-- frp
|-- gitea
|-- crs
|-- cc-connect
|-- claude
|-- codex
|-- opencode
|-- hermes
`-- lark-cli
```

Use ASCII tree glyphs (`|--`, `` `-- ``) unless the file already uses Unicode tree drawing characters; this keeps docs consistent with the default ASCII editing constraint.

## Validation Pattern

- Run `mkdocs build --strict`.
- Inspect the generated command-reference page for the CLI tree text.
- Keep Chinese and English docs synchronized (`CLI 树` / `CLI Tree`).
- Make sure the tree reflects implemented commands only; future or planned commands belong in a roadmap/capability map, not the implemented command tree.
