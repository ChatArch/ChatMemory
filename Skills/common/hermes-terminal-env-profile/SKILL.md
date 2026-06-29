---
name: hermes-terminal-env-profile
description: Configure Hermes terminal-tool subprocesses to use a project/dev environment such as ChatArch without changing Hermes core runtime or source code.
version: 0.1.0
---

# Hermes Terminal Environment Profile

Use this skill when the user wants Hermes Agent itself to remain a stable core runtime, but wants `terminal` tool commands such as `python3`, `pip`, `pytest`, `chatgh`, or project CLIs to default to a project/dev environment.

Canonical example: make Hermes `terminal` tool default to the ChatArch venv at `~/.chatarch/venv`, while Hermes gateway/agent runtime stays in its own `~/.hermes/hermes-agent/venv`.

## Key principle

Do **not** replace Hermes' runtime venv and do **not** modify Hermes official source code.

Use Hermes' supported terminal config layer:

```yaml
terminal:
  shell_init_files:
    - ~/.hermes/shell-init/chatarch-terminal.sh
  auto_source_bashrc: false
```

This changes the shell snapshot used by newly-created `terminal` environments. It does not change the Python interpreter running Hermes itself.

## Official support surface

Hermes supports this through official terminal configuration keys:

- `terminal.shell_init_files`
- `terminal.auto_source_bashrc`

Useful source references in a local Hermes checkout:

```text
~/.hermes/hermes-agent/tools/environments/local.py
~/.hermes/hermes-agent/tests/tools/test_local_shell_init.py
```

The implementation resolves configured init files, expands `~` and `${VAR}`, skips missing files safely, and prepends guarded `source` lines while building the local backend shell snapshot.

## Configure ChatArch as the terminal environment

### 1. Create a small shell init file

Create:

```text
~/.hermes/shell-init/chatarch-terminal.sh
```

Recommended content:

```bash
# Hermes terminal-tool shell profile for ChatArch development.
# This file is sourced only by terminal tool shell snapshots when listed in
# ~/.hermes/config.yaml under terminal.shell_init_files. It does not change the
# Hermes gateway/agent runtime interpreter.

CHATARCH_VENV="${CHATARCH_VENV:-$HOME/.chatarch/venv}"

if [ -d "$CHATARCH_VENV" ]; then
  export HERMES_TERMINAL_ENV_PROFILE="chatarch"
  export VIRTUAL_ENV="$CHATARCH_VENV"

  # Put ChatArch's venv first even when it already exists later in PATH.
  _chatarch_path="$CHATARCH_VENV/bin"
  _new_path="$_chatarch_path"
  _old_ifs="$IFS"
  IFS=:
  for _p in ${PATH:-}; do
    if [ -n "$_p" ] && [ "$_p" != "$_chatarch_path" ]; then
      _new_path="$_new_path:$_p"
    fi
  done
  IFS="$_old_ifs"
  export PATH="$_new_path"
  unset _chatarch_path _new_path _old_ifs _p
fi
```

### 2. Update Hermes config

Preferred manual config shape:

```yaml
terminal:
  shell_init_files:
    - ~/.hermes/shell-init/chatarch-terminal.sh
  auto_source_bashrc: false
```

Notes:

- `auto_source_bashrc: false` keeps the terminal profile narrow and avoids importing unrelated user shell rc behavior.
- `hermes config set terminal.shell_init_files ...` may serialize a list value as a string in some versions. For list-typed values, use `hermes config edit` or Hermes' Python config writer and then verify YAML type.

Python config-writer fallback:

```bash
python3 - <<'PY'
from hermes_cli.config import read_raw_config, save_config
cfg = read_raw_config() or {}
terminal = cfg.setdefault('terminal', {})
terminal['shell_init_files'] = ['~/.hermes/shell-init/chatarch-terminal.sh']
terminal['auto_source_bashrc'] = False
save_config(cfg)
PY
```

### 3. Verify config readback

```bash
python3 - <<'PY'
import yaml
from pathlib import Path
cfg = yaml.safe_load(Path('~/.hermes/config.yaml').expanduser().read_text())
print(type(cfg['terminal']['shell_init_files']).__name__)
print(cfg['terminal']['shell_init_files'])
print(cfg['terminal']['auto_source_bashrc'])
PY
```

Expected:

```text
list
['~/.hermes/shell-init/chatarch-terminal.sh']
False
```

### 4. Restart or reset terminal snapshots

The config affects newly-created terminal environments. Existing long-lived terminal snapshots can keep their old PATH/VIRTUAL_ENV until reset.

Options:

- Gateway: use `/restart` when appropriate.
- CLI/session: start a fresh session or reset the current terminal environment.
- Immediate one-off current-session activation:

```bash
export HERMES_TERMINAL_ENV_PROFILE=chatarch
export VIRTUAL_ENV="$HOME/.chatarch/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
```

## Verify active terminal environment

Run inside the Hermes `terminal` tool:

```bash
printf 'profile=%s\n' "${HERMES_TERMINAL_ENV_PROFILE:-}"
printf 'VIRTUAL_ENV=%s\n' "${VIRTUAL_ENV:-}"
command -v python3
python3 - <<'PY'
import sys, os
print('exe=', sys.executable)
print('prefix=', sys.prefix)
print('VIRTUAL_ENV=', os.environ.get('VIRTUAL_ENV'))
PY
python3 -m pip --version
```

Expected for ChatArch:

```text
profile=chatarch
VIRTUAL_ENV=/Users/<user>/.chatarch/venv
.../.chatarch/venv/bin/python3
pip ... from .../.chatarch/venv/...
```

## Known pitfall: unconditional bash-profile exec

Hermes local terminal backend builds a shell snapshot using `bash -l -c`. If `~/.bash_profile` contains an unconditional exec such as:

```bash
exec /bin/zsh -l
```

then the `-c` command body never runs and `terminal.shell_init_files` will not be sourced.

Guard the exec for interactive shells only:

```bash
case $- in
  *i*) exec /bin/zsh -l ;;
esac
```

Verify:

```bash
/bin/bash -l -c 'echo LOGIN_CMD_RAN'
```

Expected:

```text
LOGIN_CMD_RAN
```

## Roll back to normal behavior

To stop using the ChatArch terminal profile, remove the configured init file:

```yaml
terminal:
  shell_init_files: []
  auto_source_bashrc: true
```

or delete/rename `~/.hermes/shell-init/chatarch-terminal.sh`. Missing init files are skipped safely, but an explicit clean config is preferred.

## Safety boundaries

- This does not modify Hermes source code.
- This does not install packages into Hermes' runtime venv.
- This does not change model/provider credentials.
- File tools such as `read_file`, `write_file`, `patch`, and `search_files` are not affected by the shell PATH; only shell commands executed by terminal-like tools are affected.
- For release clean-install checks, still prefer a task-local `uv venv --seed` to prove the package works outside both Hermes and ChatArch dev environments.
