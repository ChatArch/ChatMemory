# Local Skill Templates

This group stores machine-local skill templates that may be copied into a workspace's local skill area and adapted for that machine.

Important boundaries:

- `Skills/local/` is **not** a default shared skill group.
- Workspace setup should not link it automatically with `Skills/common`, `Skills/chatarch`, or `Skills/agents`.
- Each machine should copy only the needed local skill into its workspace-local `skills/local/` directory and adapt paths, branch names, credentials policy, and environment-specific notes before use.
- Local templates may mention one machine's branch or path as a concrete example; do not treat those values as portable defaults.
- Do not edit this template just to reflect the current machine's branch. Put machine-specific changes in the workspace-local copy, for example `~/Playground/skills/local/...`.
- Do not checkout, merge, reset, or force-push another machine/robot's long-running branch while maintaining this machine's local skill loop.

## Skills

- `chatmemory-local-branch-loop/` — example local ChatMemory PR/merge/reset loop for this machine's long-running branch; copy and adapt on new machines.
