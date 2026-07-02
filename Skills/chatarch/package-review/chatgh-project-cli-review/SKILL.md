---
name: chatgh-project-cli-review
description: Review ChatGH Project CLI PRs against ChatGH-native command-tree, Python API, safety gate, ChatEnv, ChatStyle, tests, docs, and CI expectations. Use when reviewing or updating ChatGH `project` / GitHub Projects v2 work.
---

# ChatGH Project CLI Review

## When to use

Use this skill when reviewing, updating, or final-checking a ChatGH PR that touches GitHub Projects v2 or `chatgh project` commands.

This skill is specifically for ChatArch / ChatGH development review. It is not a generic GitHub CLI compatibility checklist.

## Core rule

Do **not** treat official `gh project` as a command-tree compatibility requirement for ChatGH.

Official `gh project` is only a capability/API/semantic reference. ChatGH's expected Project CLI tree is ChatGH-native:

```text
chatgh project
  list
  view
  create
  edit
  close
  delete
  copy

  item
    list
    add
    create
    edit
    archive
    delete

  field
    list
    create
    delete

  link
  unlink
  mark-template
```

## Explicit non-goals

Unless the user explicitly asks for a compatibility layer, do not preserve flat official-style item/field commands:

```text
chatgh project item-list
chatgh project item-add
chatgh project item-create
chatgh project item-edit
chatgh project item-archive
chatgh project item-delete
chatgh project field-list
chatgh project field-create
chatgh project field-delete
```

These flat names recreate official `gh project` shape and hide the ChatGH-native model. For this user's ChatGH work, `item` and `field` are ChatGH-owned subdomains and should be opened as CLI groups.

## Review workflow

1. Confirm workspace and source repo:
   - workspace: `~/Playground`
   - source checkout usually: `~/Playground/core/ChatGH`
   - task record usually under `~/Playground/projects/...`
2. Read the active task PRD/spec before trusting existing tests:
   - `PRD.md`
   - `reports/*spec*.md`
   - `reports/*review*.md`
   - `progress.md`
3. Print the actual registered CLI tree from code, not docs:

   ```bash
   python3 - <<'PY'
   from chatgh.cli import main
   def walk(cmd, prefix):
       for name, sub in getattr(cmd, 'commands', {}).items():
           print(' '.join(prefix + [name]))
           walk(sub, prefix + [name])
   walk(main, ['chatgh'])
   PY
   ```

4. Compare actual tree to the active spec:
   - required groups: `project item`, `project field`;
   - required item commands: `list/add/create/edit/archive/delete`;
   - required field commands: `list/create/delete`;
   - rejected flat commands must be absent.
5. Review tests before implementation:
   - tests must lock the desired native tree;
   - tests must include negative assertions for rejected flat commands;
   - tests must use `project item ...` and `project field ...` dispatch paths.
6. Review implementation:
   - Click groups should be structured as `project_group -> item_group/field_group`;
   - item/field commands should call importable `chatgh.github.projects` functions;
   - no shell-out to official `gh`;
   - no official `gh auth` dependency;
   - ChatEnv token resolution remains ChatGH-native: explicit `--token` → repo-local credential → ChatEnv `GitHubConfig.GITHUB_ACCESS_TOKEN`.
7. Review safety and IDs:
   - destructive operations require matching `--confirm` target IDs/numbers;
   - REST numeric `id` must not be used for GraphQL mutation IDs;
   - public payload `id` should be GraphQL `node_id`; REST numeric ID should be `database_id`;
   - `--clear` must not combine with field value setters.
8. Review docs and changelog:
   - examples must use `chatgh project item ...` and `chatgh project field ...`;
   - docs must not present `item-add` / `field-list` as entrypoints;
   - mention ChatGH-native auth, JSON output, safety gates, and Python API.
9. Run local gates and independent review before commit/push.
10. Push PR branch and wait for CI / docs preview readback; do not merge without explicit user authorization.

## Minimum RED tests for tree changes

```python
def test_project_native_item_and_field_groups_are_registered(runner):
    result = runner.invoke(cli, ["project", "--help"])
    assert result.exit_code == 0
    assert "item" in result.output
    assert "field" in result.output
    for flat in ["item-add", "item-list", "field-list", "field-create"]:
        assert flat not in result.output


def test_project_item_group_commands_are_registered(runner):
    result = runner.invoke(cli, ["project", "item", "--help"])
    assert result.exit_code == 0
    for command in ["list", "add", "create", "edit", "archive", "delete"]:
        assert command in result.output


def test_project_field_group_commands_are_registered(runner):
    result = runner.invoke(cli, ["project", "field", "--help"])
    assert result.exit_code == 0
    for command in ["list", "create", "delete"]:
        assert command in result.output
```

## Required verification commands

Run at least:

```bash
python3 -m pytest -q
python3 -m compileall -q src tests
git diff --check
python3 -m chatgh.cli project --help
python3 -m chatgh.cli project item --help
python3 -m chatgh.cli project field --help
```

For remote PR readiness, also run:

```bash
chatgh pr view <PR> --repo ChatArch/ChatGH --json-output
chatgh pr checks <PR> --repo ChatArch/ChatGH --json-output
```

If checks are still in progress, wait for the specific workflow runs and re-read PR state for the final head SHA.

## Common failure modes to flag

- CI is green because tests still lock the old flat official-style tree.
- `project item ...` / `project field ...` are documented but not actually registered.
- Flat `item-*` / `field-*` aliases remain registered by accident.
- The implementation uses GitHub REST numeric `id` in follow-up GraphQL mutations.
- `deleteProjectV2Field` assumes `projectV2Field { id }` is a valid selection, but it is a union; use safe scalar selection or inline fragments.
- Docs describe official `gh project` compatibility as the goal instead of ChatGH-native command organization.
- Review ignores current task PRD/spec and only checks existing tests/CI.

## Link persistence

When this review involves a Feishu doc, PR, preview, or other external artifact, write links back into the active task project:

- `progress.md` for minimum durable record;
- `reports/links.md` as the explicit external link index;
- `reports/README.md` when adding a report artifact.
