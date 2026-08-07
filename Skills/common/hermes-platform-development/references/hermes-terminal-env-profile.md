# Hermes Terminal Environment Profile

Use this reference when configuring or debugging the default environment seen by Hermes `terminal`, file tools, and `execute_code` on local and SSH backends.

## Core model

Keep these layers separate:

1. **Hermes runtime**: the gateway/agent Python environment. Do not repoint this to project or ChatArch venvs.
2. **Local terminal backend**: commands run on the local machine. Its first snapshot can be seeded by `terminal.shell_init_files`.
3. **SSH terminal backend**: commands run on the selected remote SSH target. Its first snapshot is seeded by the remote user's login shell, not by the local `terminal.shell_init_files`.
4. **File tools**: `read_file`, `write_file`, `search_files`, and `patch` are Hermes Python tool handlers wrapping `ShellFileOperations`, but `ShellFileOperations` executes shell commands through the selected terminal backend (`env.execute`). They follow the backend/cwd and shell snapshot, not the model's local filesystem by default.
5. **Project Python**: repo-local `.venv`, ChatArch's shared `~/.chatarch/venv`, system Python, etc.

Hermes terminal environments are stateful by shell snapshot: a backend creates a snapshot once, each command sources it, then writes exports/aliases/functions/cwd back. Changing an init file affects newly-created backend snapshots; an already-running snapshot may need an explicit `source ...` or backend/session recreation.

For ordinary file reads/writes/search/patch, the target backend and cwd matter more than which `python3` is first on `PATH`: the file operation wrapper runs in Hermes, while backend access uses commands such as `wc`, `head`, `sed`, `cat`, `mv`, `find`/`rg` through `env.execute`. The selected Python only matters when a validation/extraction/helper path actually invokes Python or Python libraries (for example `execute_code`, document extraction in the Hermes runtime, or extension-specific lint checks). Therefore diagnose file tools by checking backend/cwd first, and Python environment second.

## Local backend: default ChatArch terminal environment

Goal: newly-created local `terminal` backends should default to ChatArch's shared Python without changing the Hermes gateway runtime.

1. Create a secret-free local init script:

```bash
mkdir -p "$HOME/.hermes/shell-init"
cat > "$HOME/.hermes/shell-init/chatarch-terminal.sh" <<'SH'
# Hermes local terminal initialization for ChatArch.
# Secret-free: selects the standard ChatArch Python environment only.
CHATARCH_VENV="$HOME/.chatarch/venv"
if [ -d "$CHATARCH_VENV" ]; then
  export HERMES_TERMINAL_ENV_PROFILE="chatarch"
  export VIRTUAL_ENV="$CHATARCH_VENV"
  case ":$PATH:" in
    *":$CHATARCH_VENV/bin:"*) ;;
    *) export PATH="$CHATARCH_VENV/bin:$PATH" ;;
  esac
fi
SH
chmod 0644 "$HOME/.hermes/shell-init/chatarch-terminal.sh"
```

2. Persist the local terminal config through Hermes's supported config surface, not raw config-file patching:

```bash
hermes config set terminal.cwd "$HOME/Playground"
hermes config set terminal.shell_init_files '["~/.hermes/shell-init/chatarch-terminal.sh"]'
hermes config set terminal.auto_source_bashrc false
```

If the CLI/config surface differs on a particular Hermes version, inspect `hermes config --help` / official docs and use the equivalent supported writer. Do not directly patch protected runtime config unless the user explicitly asks and the verifier allows it.

3. Verify the local `terminal` backend:

```bash
source "$HOME/.hermes/shell-init/chatarch-terminal.sh"
printf 'profile=%s\n' "${HERMES_TERMINAL_ENV_PROFILE:-}"
printf 'VIRTUAL_ENV=%s\n' "${VIRTUAL_ENV:-}"
command -v python3
python3 - <<'PY'
import sys
print(sys.executable)
print(sys.version.split()[0])
PY
```

Expected shape:

```text
profile=chatarch
VIRTUAL_ENV=$HOME/.chatarch/venv
$HOME/.chatarch/venv/bin/python3
```

### Local `execute_code` caveat

Local `execute_code` does not source the local terminal snapshot. In project mode it may select the Hermes gateway process venv from `VIRTUAL_ENV`/`CONDA_PREFIX`, then fall back to `sys.executable`. Diagnose local `terminal` and local `execute_code` separately.

## SSH backend: default ChatArch terminal environment on a remote machine

Goal: newly-created SSH Mode terminal backends should default to the remote machine's ChatArch Python.

Do not assume the local init file is copied to the remote. SSH Mode uses the selected remote backend; local `~/.hermes/shell-init/...` affects only local backend snapshots.

Observed Hermes SSH behavior to account for:

- `/ssh use <alias> --cwd <remote-path>` binds the current session/thread to an SSH target.
- The target/binding decides the remote alias and cwd.
- `SSHEnvironment` bootstraps the remote snapshot with a non-interactive login shell, equivalent in practice to `bash -l -c <bootstrap>`.
- Activation guarded by `case $- in *i*) ... ;; esac` is skipped because Hermes is not running an interactive shell.
- A remote `~/.profile` is not necessarily read if `~/.bash_profile` exists; Bash login startup order matters.

1. On the remote target, create a secret-free init file:

```bash
mkdir -p "$HOME/.chatarch"
cat > "$HOME/.chatarch/hermes-terminal-init.sh" <<'SH'
# Hermes SSH Mode terminal initialization for ChatArch.
# Sourced by the remote login path for both interactive and non-interactive shells.
# Secret-free: selects the standard ChatArch Python environment only.
CHATARCH_VENV="$HOME/.chatarch/venv"
if [ -d "$CHATARCH_VENV" ]; then
  export HERMES_TERMINAL_ENV_PROFILE="chatarch"
  export VIRTUAL_ENV="$CHATARCH_VENV"
  case ":$PATH:" in
    *":$CHATARCH_VENV/bin:"*) ;;
    *) export PATH="$CHATARCH_VENV/bin:$PATH" ;;
  esac
fi
SH
chmod 0644 "$HOME/.chatarch/hermes-terminal-init.sh"
```

2. Source it from the remote login path outside any interactive-only guard. For Bash users, prefer `~/.bash_profile` when it exists:

```bash
# Hermes SSH Mode terminal init: non-interactive login shells also need ChatArch.
[ -r "$HOME/.chatarch/hermes-terminal-init.sh" ] && . "$HOME/.chatarch/hermes-terminal-init.sh"
```

Place that line in the actual login file Bash will read. If both `~/.bash_profile` and `~/.profile` exist, Bash reads `~/.bash_profile` first and usually does not read `~/.profile`.

3. Verify with a fresh non-interactive login shell, not only an interactive human shell:

```bash
env -i \
  HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" SHELL="$SHELL" \
  PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
  bash -l -c 'printf "profile=%s\n" "${HERMES_TERMINAL_ENV_PROFILE:-}"; printf "VIRTUAL_ENV=%s\n" "${VIRTUAL_ENV:-}"; command -v python3; python3 -c "import sys; print(sys.executable); print(sys.version.split()[0])"'
```

Expected shape:

```text
profile=chatarch
VIRTUAL_ENV=/home/<user>/.chatarch/venv
/home/<user>/.chatarch/venv/bin/python3
```

4. Verify through Hermes SSH Mode itself:

```text
/ssh use <alias> --cwd ~/Playground
```

Then run:

```bash
printf 'profile=%s\n' "${HERMES_TERMINAL_ENV_PROFILE:-}"
printf 'VIRTUAL_ENV=%s\n' "${VIRTUAL_ENV:-}"
command -v python3
python3 - <<'PY'
import sys
print(sys.executable)
print(sys.version.split()[0])
PY
```

For non-local backends, `execute_code` should execute on the selected backend and see the backend's Python environment. Verify separately before assuming it matches `terminal`.

## Pitfalls

- Do not put tokens, proxy URLs, private key paths, or service credentials in terminal init files. They should select paths/env profiles only.
- Do not promote machine-specific aliases, private hostnames, or identity paths into shared skills; use placeholders such as `<alias>` and `<user>`.
- Do not claim an init-file change is active until a fresh backend/login-shell probe proves it. Existing Hermes shell snapshots can keep old values.
- Do not fix SSH Mode by editing local `terminal.shell_init_files`; that only covers local backend.
- Do not guard the remote ChatArch init with `*i*` if Hermes needs it; SSH Mode's bootstrap is non-interactive.
