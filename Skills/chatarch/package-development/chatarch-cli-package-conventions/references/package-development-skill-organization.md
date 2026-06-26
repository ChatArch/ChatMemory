# ChatArch Package Development Skill Organization

Use this reference when organizing ChatArch shared skills around package/repo/release workflows.

## Theme layout

For ChatMemory shared skills, a `package-development/` topic directory should be a true classification home, not a duplicated index with compatibility symlinks left in the old directory.

Preferred shape:

```text
Skills/chatarch/package-development/
  README.md
  chatarch-cli-package-conventions/
  python-package-release-with-chattool-pypi/
  chatgh-pr-and-ci-workflow/
  chatgh-repo-token-setup/
  chatpypi-publisher-management/
  public-repo-and-default-branch-protection/
  chattool-capability-extraction/
  chatarch-org-pr-status/
```

Post-review / post-release package audit skills belong in a separate `Skills/chatarch/package-review/` topic. For example, `chatenv-provider-workflow` is a post-review skill for checking or repairing provider behavior in an already-existing package, not part of the active package-development layout.

Do not keep outer `Skills/chatarch/<skill-name>` symlinks for the moved skills unless the user explicitly asks for compatibility. For this user, classification/archive means the skill lives in one place.

## README style

The topic README should first expand each contained skill individually:

- what it is for
- what workflow steps it covers
- when to use it
- when not to use it

Only after that should it provide composition recipes such as:

- new ChatArch Python package
- update existing package and open PR
- inspect PR/CI status
- configure PyPI Trusted Publisher
- extract a ChatTool capability into a standalone package

Avoid a README that only lists “load A + B + C” without explaining the skills themselves.

## Boundary between navigation and conventions

The package-development README is a router. It should not carry detailed package-template rules. Template CLI skeleton requirements belong in `chatarch-cli-package-conventions`; release/tag/registry gates belong in `python-package-publishing`; publisher form details belong in `chatpypi-publisher-management`.

If a user corrects template behavior, update the actual template source and tests first when possible, then keep skill docs as concise routing/convention references.

## Template correction captured from ChatPyPI

The ChatPyPI `chatarch` scaffold should not generate a default `hello` / `Hello, ChatArch!` demo command/test/docs as the package's user-facing command or release-readiness proof. The scaffold should start as a real package skeleton:

- click group with top-level `--version`
- README quick start using `--help` and `--version` smoke paths
- generated tests for version output and real package command skeletons
- package-specific commands added by the actual package work

If old docs or skills still talk about the `hello` demo, treat them as stale and update the governing convention/template rather than repeating the warning in every release workflow.