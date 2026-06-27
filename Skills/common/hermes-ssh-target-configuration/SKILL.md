---
name: hermes-ssh-target-configuration
version: 0.1.0
description: Configure HERMES SSH targets safely, including targets.yaml, bindings behavior, and HERMES-owned known_hosts handling to avoid No Host / first-connection failures.
---

# HERMES SSH Target Configuration

Use this skill when configuring HERMES SSH targets, creating or importing `targets.yaml`, diagnosing `/ssh use`, or handling No Host / known_hosts failures.

## Workspace Rule

Default work must stay inside `/home/zhihong/Playground`. Source repos belong under `/home/zhihong/Playground/core`. Do not create random sibling directories outside Playground. If a spoken instruction sounds like `Call`, interpret it as `Core` unless context clearly says otherwise.

## Current Mechanism

HERMES SSH has two persistent files:

```text
$HERMES_HOME/ssh/targets.yaml
$HERMES_HOME/ssh/bindings.json
```

- `targets.yaml` is the HERMES-managed SSH target registry. `/ssh list`, `/ssh test`, and `/ssh use` read it.
- `bindings.json` stores Feishu Thread/Section bindings: section key -> target alias and optional cwd.
- `/ssh use <alias>` writes or updates `bindings.json`.
- `/ssh off` / `/ssh local` deletes the current section binding.
- Ordinary turns read the binding but do not update `updated_at`.

`/ssh list` does not automatically expose system `~/.ssh/config`. System SSH config can be used only as an explicit import/reference source.

## No Host / known_hosts Rule

When configuring a target, also prepare a HERMES-owned known_hosts file:

```text
$HERMES_HOME/ssh/known_hosts
```

Do not rely on the user's system `~/.ssh/known_hosts` as the default automation path. The goal is for HERMES SSH behavior to be self-contained and reproducible.

## Target Setup Checklist

1. Resolve HERMES home:

```bash
printf '%s\n' "${HERMES_HOME:-$HOME/.hermes}"
```

2. Create SSH state directory:

```bash
install -d -m 700 "$HERMES_HOME/ssh"
touch "$HERMES_HOME/ssh/known_hosts"
chmod 600 "$HERMES_HOME/ssh/known_hosts"
```

3. Add or update the target in `targets.yaml`:

```yaml
ssh:
  targets:
    cubebot.local:
      host: example.internal
      user: cubebot
      port: 22
      identity_file: ~/.hermes/ssh/keys/cubebot
      cwd: /home/cubebot/Playground
```

4. Pre-warm HERMES known_hosts:

```bash
host="example.internal"
port="22"
known="$HERMES_HOME/ssh/known_hosts"
ssh-keyscan -p "$port" "$host" >> "$known"
chmod 600 "$known"
```

5. Test with the HERMES known_hosts file explicitly:

```bash
ssh \
  -o BatchMode=yes \
  -o StrictHostKeyChecking=accept-new \
  -o UserKnownHostsFile="$HERMES_HOME/ssh/known_hosts" \
  -p "$port" \
  -i "$HERMES_HOME/ssh/keys/cubebot" \
  cubebot@"$host" \
  'pwd && whoami'
```

## Safer known_hosts Refresh

If a host key changes, do not silently append duplicates. Use an explicit refresh flow:

```bash
host="example.internal"
port="22"
known="$HERMES_HOME/ssh/known_hosts"
tmp="$HERMES_HOME/ssh/known_hosts.scan.$$"
ssh-keyscan -p "$port" "$host" > "$tmp"
test -s "$tmp"
ssh-keygen -R "[$host]:$port" -f "$known" >/dev/null 2>&1 || true
ssh-keygen -R "$host" -f "$known" >/dev/null 2>&1 || true
cat "$tmp" >> "$known"
rm -f "$tmp"
chmod 600 "$known"
```

Only refresh a changed key when the user expects it; changed host keys can indicate a security issue.

## Desired Runtime Mechanism

The HERMES internal SSH runtime should eventually default to:

```text
-o UserKnownHostsFile=$HERMES_HOME/ssh/known_hosts
-o StrictHostKeyChecking=accept-new
```

For stronger isolation, also consider:

```text
-o GlobalKnownHostsFile=/dev/null
```

This keeps HERMES from depending on hidden system SSH known_hosts state.

## Connection-Time Option

A future `/ssh test <alias> --connect` or `/ssh use <alias>` enhancement can pre-warm known_hosts before the first connection:

1. Resolve alias from `targets.yaml`.
2. Ensure `$HERMES_HOME/ssh/known_hosts` exists.
3. Run `ssh-keyscan` for target host/port.
4. Attempt a non-interactive SSH command with HERMES known_hosts.
5. Return clear diagnostics for missing key, host-key changed, auth failure, or cwd failure.

## Common Pitfalls

- `StrictHostKeyChecking=accept-new` does not mean HERMES owns known_hosts; without `UserKnownHostsFile`, OpenSSH still uses the system default.
- `/ssh use` is a binding write, not a full interactive login.
- Binding persists across gateway restarts, but SSH connections are runtime state and reconnect as needed.
- Changing a target alias in `targets.yaml` affects every section bound to that alias.
- `bindings.json` can grow over time; future hardening should add GC or pruning.
