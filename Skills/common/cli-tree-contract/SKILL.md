---
name: cli-tree-contract
description: "Use when designing/reviewing CLI tools: require --tree, --tree-brief, and real registered command tree output."
version: 0.1.1
---

# CLI Tree Contract

## When To Use

Use this skill whenever a task asks to design, review, document, template, or align a CLI tool.

Trigger phrases include:

- “CLI 树” / “command tree” / “命令树”
- “每个接口长什么样”
- “每个接口在做什么”
- “对齐 CLI”
- adding or reviewing `--help`, `--tree`, `--tree-brief`, command groups, aliases, or CLI templates

## Definition

A CLI tree is the **actual registered command surface**, not a prose summary and not a list of random examples.

For ChatArch Python CLIs, the current shared baseline is ChatStyle `chatstyle>=0.2.0,<0.3.0`. Click CLIs should use ChatStyle's shared tree runtime (`add_tree_option()` / registered tree renderer) rather than copying package-local tree renderers. `--tree` should include signatures; `--tree-brief` should omit signatures while preserving nodes and descriptions.

A valid CLI tree must show:

1. The root command.
2. Every visible command group.
3. Every actual reachable leaf command.
4. The leaf command signature: positionals and important options.
5. A short right-side purpose comment for every group and leaf.
6. Side-effect class for leaves where it matters: read-only, artifact-producing, login checkpoint, write/create, publish/delete/destructive.
7. Output contract for leaves where it matters: JSON/text, receipt path, artifact path, URL, IDs, etc.
8. Security boundary: which sensitive values must not be printed or stored.

Do **not** count a token after a leaf command as a subcommand merely because `<leaf> something --help` still prints help. Confirm the registered tree from the Click/Typer/app registry or equivalent command metadata.

## Required Display Shape

Use a tree with right-side comments:

```text
chatpost
├── account                         # account alias registry; read-only metadata
│   ├── list [--registry PATH]       # list aliases; no credentials
│   └── show TARGET [--registry PATH]# show one alias; no credentials
├── login                           # login checkpoints and auth checks
│   └── status TARGET               # read-only auth check
└── post
    └── draft TARGET SOURCE         # create exactly one review draft; writes receipt
```

Then provide a leaf table when the tree is non-trivial:

| Leaf | Purpose | Required inputs | Outputs | Side effects | Boundary |
|---|---|---|---|---|---|
| `chatpost account list` | List aliases | optional registry | text/json | read-only | no secrets |

## `--help` vs `--tree` vs `--tree-brief`

Every ChatArch/ChatStyle CLI template and substantial CLI package should expose all three:

- `--help`: command-specific usage, arguments, options, and examples for the current command or group.
- `--tree`: the registered CLI tree for the current CLI, with one-line purpose comments and actual reachable leaf commands.
- `--tree-brief`: the same registered tree without argument/option signatures, for compact summaries and dashboards.

Recommended behavior:

- Root: `<tool> --tree` prints the full visible registered tree.
- Root: `<tool> --tree-brief` prints the signature-free visible registered tree.
- Group: `<tool> <group> --tree` may print that subtree when the framework supports inherited/group options cleanly.
- Machine output: support `--tree --output json` or a sibling `tree --output json` only when automation needs it; human tree output is mandatory first.
- Hidden compatibility aliases must be omitted from the visible tree unless the user explicitly asks for compatibility inventory.
- Reserved/planned commands must not appear as successful leaves. If shown in docs, mark them as planned and make the runtime command exit non-zero until implemented.

## Required Workflow For Agents

When asked to align a CLI:

1. Run the real CLI help for root and subcommands.
2. Inspect the command registry or source registration to determine actual groups and leaves.
3. Produce both the full and brief CLI tree first, before design prose.
4. For every leaf, state what it does, inputs, outputs, side effects, and boundary.
5. Mark problems explicitly: ambiguous names, leaf/group confusion, platform coupling, missing `--tree`, missing `--tree-brief`, stale docs, hidden aliases, or commands that are examples but not registered.
6. Only after the tree and contract are aligned should implementation begin.

## Template Requirement

ChatPyPI / ChatArch package templates that create a ChatStyle CLI must include:

1. A top-level `--version`.
2. A top-level `--help`.
3. A top-level `--tree` that prints the actual registered CLI tree.
4. A top-level `--tree-brief` that prints the same tree without signatures.
5. Focused tests that assert `--tree` includes the expected root, groups, leaves, signatures, and one-line purpose comments; and that `--tree-brief` exits 0 and omits representative signatures.
6. A docs section named “CLI tree” or “命令树” generated from or checked against the same registered command structure.

## Verification Checklist

For a concrete CLI package:

```bash
<venv>/bin/<tool> --help
<venv>/bin/<tool> --tree
<venv>/bin/<tool> --tree-brief
<venv>/bin/<tool> <group> --help
PYTHONPATH=src <venv>/bin/python -m pytest -q tests/test_cli*.py
```

Tests should verify:

- `--tree` exits 0.
- `--tree-brief` exits 0 and omits argument/option signatures.
- The root command appears exactly once.
- All visible registered groups and leaf commands appear.
- Rejected aliases or platform-specific delivery protocols do not appear.
- Leaf comments describe actual behavior, not vague slogans.

## Common Pitfalls

- Answering with a principle like “platform neutral” but not showing the command tree.
- Using README examples as proof of the CLI tree without checking registered commands.
- Treating `--help` output of a leaf command with extra words as evidence those words are subcommands.
- Listing platform delivery details such as Feishu/Hermes `MEDIA:` inside a platform-neutral CLI tree.
- Hiding side effects: if a command writes, publishes, opens a browser, waits for login, or creates a receipt, say so on the leaf.
- Updating docs but not adding `--tree` / `--tree-brief` to the runtime CLI and tests.
