---
name: chatarch-server-preinstall
description: Preinstall standard ChatArch Python environment on a server: uv, uv-managed Python, ~/.chatarch/venv, env.sh shell integration, and ChatUp.
version: 0.1.0
---

# ChatArch Server Preinstall

## When to use

Use this skill before installing ChatArch Python CLI packages on a new or underprepared server, especially when:

- system Python is too old or lacks `venv` / `pip` support;
- a package install would otherwise require ad-hoc `apt install python*-venv` or global pip;
- the user asks for a standard ChatArch environment;
- a remote machine needs `chatup`, `chatclash`, `chatgh`, `chattool`, or another ChatArch CLI.

## Principle

Prefer the standard ChatArch stack instead of ad-hoc system Python environments:

```text
~/.local/bin/uv
~/.chatarch/venv
~/.chatarch/env.sh
chatup inside ~/.chatarch/venv
```

Do not install task-specific packages directly into system Python. Do not create one-off venvs under `~/.chatarch/venvs/<tool>` unless the user explicitly wants isolated tool venvs. If an ad-hoc venv was already created, move it to the nearest `.trash/` and restart from this preinstall flow.

## Remote inventory first

Run a redacted inventory before writes:

```bash
whoami
hostname
printf 'HOME=%s\n' "$HOME"
command -v uv || true; uv --version 2>/dev/null || true
command -v python || true; python --version 2>/dev/null || true
command -v python3 || true; python3 --version 2>/dev/null || true
command -v chatup || true; chatup --version 2>/dev/null || true
[ -f ~/.chatarch/env.sh ] && sed -n '1,80p' ~/.chatarch/env.sh
```

Never print secrets from `.env`, ChatEnv profiles, provider credentials, or shell history.

## Standard install flow

Install `uv` if missing:

```bash
mkdir -p "$HOME/.local/bin" "$HOME/.chatarch"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

Install a uv-managed Python and create the ChatArch venv:

```bash
uv python install 3.12
uv venv --python 3.12 --seed "$HOME/.chatarch/venv"
```

Write `~/.chatarch/env.sh`:

```bash
cat > "$HOME/.chatarch/env.sh" <<'SH'
# ChatArch standard environment
export PATH="$HOME/.local/bin:$HOME/.chatarch/venv/bin:$PATH"
export VIRTUAL_ENV="$HOME/.chatarch/venv"
SH
chmod 0644 "$HOME/.chatarch/env.sh"
```

Source it from login shell files idempotently:

```bash
for rc in "$HOME/.bashrc" "$HOME/.profile"; do
  touch "$rc"
  grep -q 'source "$HOME/.chatarch/env.sh"' "$rc" || \
    printf '\n# ChatArch environment\n[ -f "$HOME/.chatarch/env.sh" ] && source "$HOME/.chatarch/env.sh"\n' >> "$rc"
done
. "$HOME/.chatarch/env.sh"
```

Install or upgrade ChatUp in the standard venv:

```bash
python -m pip install -U pip setuptools wheel
python -m pip install -U chatup
chatup --version
```

## Installing ChatArch packages after preinstall

After the preinstall flow, install ChatArch CLIs into the standard venv unless the package has a documented isolated runtime:

```bash
. "$HOME/.chatarch/env.sh"
python -m pip install -U <package>
<command> --version
```

For packages with their own setup commands, prefer ChatUp when available, for example:

```bash
chatup nodejs -I
chatup workspace base "$HOME/Playground" --language zh -I
```

## Cleanup rule

If an earlier ad-hoc install was created, move it to `.trash` rather than deleting:

```bash
TS=$(date +%Y%m%d%H%M%S)
mkdir -p "$HOME/.trash/chatarch-preinstall-$TS"
# example only: move the actual temporary paths that were created
mv "$HOME/.chatarch/venvs/<tool>" "$HOME/.trash/chatarch-preinstall-$TS/" 2>/dev/null || true
```

Do not move real ChatEnv profiles such as `~/.chatarch/envs/<tool>/.env`; those are operator config and may contain the intended secrets/endpoints.

## Verification checklist

Before using the machine for ChatArch package work, verify:

- `uv --version` works.
- `python --version` resolves inside `~/.chatarch/venv` after sourcing `~/.chatarch/env.sh`.
- `python -m pip --version` points under `~/.chatarch/venv`.
- `chatup --version` works.
- `~/.chatarch/env.sh` is sourced from `.bashrc` and `.profile`.
- Any package installed afterward reports its expected `--version`.
