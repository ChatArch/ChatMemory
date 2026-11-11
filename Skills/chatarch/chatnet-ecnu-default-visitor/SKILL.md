---
name: chatnet-ecnu-default-visitor
description: Use for ECNU campus login and default/visitor profiles. Verify direct egress and credentials safely.
version: 0.1.1
---

# ChatECNU Campus Login and Default Profiles

## When To Use

Use when a user asks for campus-network login, the established ECNU login script, a server's online state, default account/profile setup, or visitor-account maintenance. Also load for a campus server that is reachable by SSH/NFS while public downloads time out or redirect to a login page.

## Ownership and network layers

- Campus-network and portal/visitor operations belong to **ChatECNU**. Generic diagnostics belong to ChatNet; do not invent a `chatnet ecnu` namespace.
- Treat management SSH, campus-network authentication, and application proxy routing as separate facts. Internal reachability, a listener, process exit zero, `online=true`, and a successful direct public request are different evidence levels.
- Resolve the actual installed `ecnu`/`chatecnu` launcher, interpreter, package and backend before acting. Read its real help/tree; if an older CLI lacks `--tree`, use registered help instead of guessing flags or silently upgrading a global environment.
- Resolve per-server account references from the private infrastructure inventory. Public/shared skills contain only generic provider names, never real accounts, hosts or credential locations beyond the public ChatArch convention.

## Campus-network diagnosis and authorized login

1. Verify host/user/cwd and inspect the existing owner CLI. Test public reachability with proxy variables removed from the child; preserve captive-portal redirect host/status without retaining its personalized query or HTML.
2. Use the installed `net check`/importable backend. A known legacy helper can be checked with bare `auth_client check`; do not add unsupported setting flags from a different release. Report online separately from return code, and redact account identifiers from the result.
3. Inspect ChatEnv `ECNU` active **and named** profiles through its native store, emitting credential-presence booleans only. An absent default `.env` is not proof that no named account exists. Select the approved profile explicitly when needed.
4. Login only when authorized and offline. Prefer the supported native Python backend consuming secrets in memory. If an old binary-backed contract refuses password argv, retain that refusal and do not silently opt into `--allow-argv-password`; use a verified safe owner runtime or obtain the specifically required permission. A safety refusal is not a server password rejection.
5. After login, read back the owner check and the intended direct HTTPS target. For model downloads, check the actual weight redirect/Range route as well as metadata. Do not logout another active session to manufacture a test or change system interfaces, DNS or proxy configuration under mere diagnosis scope.

## Credentials and temporary reuse

- Stable settings use the existing ChatEnv `ECNU` namespace under `$CHATARCH_HOME/envs/ECNU/`; use native `EnvStore` APIs, not a leaf dotenv implementation.
- Never print or retain real ECNU usernames, visitor identities, passwords, cookies, sessions, CSRF, verification codes or secret fingerprints in chat/project notes/shared skills. Safe outputs are key names, profile role, field-presence booleans, status and fixed error classifications.
- A specific user-approved temporary credential reuse is not permission to migrate all profiles or overwrite the target default. Keep authorized transfer protected and scoped, consume in memory when possible, and retain only source-reference/preservation booleans. Do not copy private keys or expose passwords in argv.
- SMS/2FA requires an approved masked/secure input handoff. If unavailable, stop at that gate; do not ask for codes in chat or put them into example command arguments.
- Preserve native endpoint and AC-ID configuration semantics. A missing legacy settings file is a configuration problem only for the backend that actually owns that contract, not evidence of a wrong password.

## Proxy and traffic-budget boundary

HF-Mirror is an origin choice, not proof that the request bypasses a paid proxy. Check the current child routing first. When the user prohibits paid traffic, do not blindly source a global proxy or use it to mask an offline campus session. An explicitly authorized existing LAN forwarder may use DIRECT egress, but require mirror and actual CDN rules plus live DIRECT-chain/Range evidence; do not count that as proof the caller's own campus login was restored.

## Visitor-account maintenance

Saving a campus login profile and maintaining visitor accounts are distinct operations. `visitor default` may create/update accounts and passwords, so it is not a network-login shortcut.

After reading the installed command surface, the owner flow is typically:

```bash
ecnu visitor --help
ecnu visitor default
```

If portal login is required, use the approved `ecnu home login` flow; handle any verification through the secure input boundary above. Do not substitute legacy ChatNet commands. Record actual account-write readback without identifiers or secrets, and keep profile existence, session validity and permissions separate.

## Verification

- Campus login acceptance: real online state plus intended direct public request; no unrelated/default profile changes.
- Visitor acceptance: exact requested operation succeeded and read back, not just CLI exit zero.
- Document actual per-machine executable/provider/profile/backend references and observation date in private infrastructure knowledge. Keep current task progress and unresolved gates in its project, not shared skills.
