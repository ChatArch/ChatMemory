# Local Skill Templates

This group stores copy-and-adapt templates for machine-local skills. These templates are useful when setting up a new machine, but they are not active shared skills by themselves.

Important boundaries:

- `Skills/local/` is **not** a default shared skill group.
- Workspace setup should not link or sync it automatically with `Skills/common`, `Skills/chatarch`, or `Skills/agents`.
- Each machine should copy only the needed template into its workspace-local `skills/local/` directory and adapt paths, branch names, credentials policy, and environment-specific notes before use.
- Templates should use placeholders such as `<workspace>`, `<chatmemory-repo>`, and `<machine-branch>` instead of naming a specific user's machine or branch.
- Do not edit this template just to reflect the current machine's branch. Put machine-specific changes in the workspace-local copy, for example `<workspace>/skills/local/...`.
- Do not checkout, merge, reset, or force-push another machine/robot's long-running branch while maintaining this machine's local skill loop.

## Skills

- `chatmemory-local-branch-loop/` — copy-and-adapt template for creating a machine-local ChatMemory/Skills refresh workflow. The active per-machine skill belongs in that machine's workspace-local `skills/local/` and may contain concrete branch names such as `rex/chatmini`.
- `server-chatarch-bot-setup/` — copy-and-adapt template for configuring a managed server as a ChatArch Playground host with CC Connect, selected agent CLI, Feishu onboarding, and a user-level service.
