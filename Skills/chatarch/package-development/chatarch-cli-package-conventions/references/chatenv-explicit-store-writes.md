# ChatEnv explicit store writes

Use this reference when a ChatArch leaf package needs to update one ChatEnv-backed value, such as a refreshed session token.

## Boundary

Leaf packages should use ChatEnv's public store primitives instead of implementing package-local dotenv/profile writers:

```python
store = EnvStore(get_paths(home).envs_dir)
values = store.load_active(ConfigClass)
values[FIELD_ENV_KEY] = new_value
store.save_active(ConfigClass, values)
```

For named profiles:

```python
store = EnvStore(get_paths(home).envs_dir)
values = store.load_profile(ConfigClass, profile_name)
values[FIELD_ENV_KEY] = new_value
store.save_profile(ConfigClass, profile_name, values)
```

This keeps profile paths, rendering, normalization, and future ChatEnv behavior centralized in ChatEnv.

## Important distinction

Do not confuse these two layers during review:

- `EnvStore.load_active/load_profile/load_path` read values from ChatEnv env files.
- `BaseEnvConfig.load_from_sources` may merge configured values with process environment fallbacks when loading runtime config state.

If a leaf package uses `EnvStore.load_*` and passes an explicit `values` dict into `save_*`, review the actual installed/source ChatEnv implementation before claiming it backfills unrelated `os.environ` secrets. A false positive here can push the package toward reimplementing ChatEnv storage locally, which is the wrong direction.

## Review pattern for suspected secret backfill

1. Inspect the exact ChatEnv version/source used by the package.
2. Confirm whether the code path calls `EnvStore.load_*` or `BaseEnvConfig.load_from_sources`.
3. Add or run a focused regression with unrelated process secrets set, then assert they are not persisted to the target profile file.
4. If the bug is real and belongs to general storage/parsing behavior, patch ChatEnv itself rather than adding a divergent leaf-package writer.
5. Only keep package-local file handling for explicit import/export compatibility paths outside ChatEnv profile storage.
