# ChatEnv Provider Checklist

## Provider Wiring

- Confirm `[project.entry-points."chatenv.configs"]` exists in `pyproject.toml`.
- Confirm the entry point imports the module that registers the config class.
- Confirm the config class defines `_title`, `_aliases`, and `_storage_dir`.

## Config Fields

- Verify required fields and defaults are sensible.
- Mark secrets with `is_sensitive=True`.
- Make alias names short and predictable for `chatenv cat -t ...` and `chatenv test -t ...`.

## Discovery

- Install the package into the environment that runs `chatenv`.
- Verify `chatenv cat -t <alias>` loads the provider after install.
- Document clearly that source checkout alone may not expose entry-point discovery.

## Test Command

- Implement `ConfigClass.test()` so it does not raise `NotImplementedError`.
- Prefer local schema/provider validation by default.
- Avoid printing tokens, cookies, passwords, auth headers, or decoded credentials.
- If remote checks are used, document them explicitly and keep failure messages readable.

## CLI Experience

- Confirm `chatenv cat`, `test`, and `use` behavior matches the interaction model.
- Add tests for provider loading and `test()` behavior.
- Update docs with exact commands users should run after installation.
