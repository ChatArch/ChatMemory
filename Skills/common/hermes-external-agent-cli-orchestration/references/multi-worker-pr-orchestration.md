# Multi-worker external-agent PR orchestration

Date added: 2026-08-25.

Use this when Hermes is supervising several external coding-agent CLI workers in parallel and the user expects Hermes to keep global control rather than implement the work itself.

## Supervisor contract

Hermes is the coordinator, not the implementer.

Hermes should:

- open the group task/project;
- define worker lanes, worktrees, issue/PR targets, and stop conditions;
- launch/resume workers through their CLI session mechanisms;
- monitor liveness and real repository state;
- feed corrections back into the worker conversation;
- independently verify reports, diffs, tests, and PR URLs;
- record progress and residual risk.

Hermes should not:

- edit the worker's implementation directly when the user explicitly delegated implementation to workers;
- let several workers edit one checkout;
- treat a worker's prose summary as proof;
- keep launching anonymous one-shot workers without durable resume IDs.

## Group-task layout

Create a project with at least:

```text
PRD.md
progress.md
workers/
  01-<lane>.md
  02-<lane>.md
  prompts/
reports/
playground/worktrees/
```

`PRD.md` states the group goal and supervisor responsibilities. Each worker brief states:

- issue/PR target;
- source branch/ref and target base;
- dedicated worktree path;
- exact scope and exclusions;
- expected tests;
- report path;
- whether opening a draft PR is allowed;
- what not to do, such as deploy, merge, reset, or edit another worker's tree.

`progress.md` must track:

- worktree path and branch for every worker;
- external CLI session/chat id for every worker;
- Hermes `process` session id only as process-lifecycle evidence, not as durable resume state;
- current status: running, exited, killed, blocked, report written, PR opened, supervisor verified;
- all supervisor decisions to preserve, restart, kill, or resume worker state.

## Cursor Agent durable worker pattern

For multi-worker tasks, do not rely on `proc_*` alone. Create a Cursor chat per worker and record it before doing substantial work.

```bash
CHAT_ID=$(cursor-agent create-chat | tr -d '\r' | tail -n 1)
```

Then start or continue that exact worker:

```bash
cursor-agent --resume "$CHAT_ID" --print --force --trust "$PROMPT"
```

If using the top-level `agent` binary on a machine where it is configured, the equivalent pattern is:

```bash
CHAT_ID=$(agent create-chat | tr -d '\r' | tail -n 1)
agent --resume "$CHAT_ID" --print --force --trust "$PROMPT"
```

Record both:

- Cursor chat id: durable conversation handle;
- Hermes `process` session id: current OS process handle.

If a process is killed or times out, resume with the Cursor chat id, not a new blank session. Inspect the worktree before resuming; tell the worker whether to preserve current dirty/conflict state.

## Other CLI resume handles

- Codex: record the session id shown by `codex resume` / `codex exec resume`; resume by explicit id, not "latest", when several workers are active.
- Claude Code: use `--session-id <uuid>` where possible, or record the `--resume` value. Avoid `--continue` for multi-worker orchestration unless only one Claude session exists.
- OpenCode: record `--session` / exported session identifiers; use `--continue` only when unambiguous.

The exact commands vary by installed CLI version. Always inspect `--help` for the active binary before writing the final worker launch command.

## Worker prompt requirements

Every worker prompt should include:

1. Worker lane and issue/PR target.
2. Dedicated worktree path.
3. Source branch/ref and target base.
4. Scope and explicit exclusions.
5. Safety rules: no reset/discard/clean, no cross-worktree edits, no secrets in public artifacts.
6. Required terminal output/report: branch, head, changed files, tests, PR URL or blocker.
7. Resume instruction: if current worktree is dirty/conflicted, preserve it and continue from current state.
8. Stop condition: open/update PR, or write a checkpoint report before exit.

Use prompt files under `workers/prompts/` for repeatability. Avoid huge shell-quoted inline prompts once the task is nontrivial.

## Supervision loop

1. Poll worker processes and check repo state.
2. If worker reports completion, verify independently:
   - read report;
   - inspect `git status` and `git log`;
   - inspect diff against target base;
   - run focused tests/checks;
   - fetch/read PR URL and compare head SHA;
   - scan public diff for private host/IP/account/path/token details.
3. If worker exits without report:
   - inspect worktree for changes/conflicts;
   - write a supervisor checkpoint if needed;
   - resume the same external chat id with a smaller checkpoint-oriented prompt.
4. If worker is silently running too long:
   - inspect logs and worktree changes;
   - if non-observable, resume/restart by chat id with a first-milestone/checkpoint demand;
   - do not take over implementation unless the user changes the assignment.
5. If worker opened a PR:
   - verify the PR exists, target repo/base/head are correct, and head SHA matches local branch;
   - run local focused tests;
   - record CI state and blockers;
   - do not merge upstream PRs unless explicitly asked.

## Common failure modes

- **Only recorded `proc_*`:** not durable. Once killed, the conversation may be gone. Create/record CLI-native session ids.
- **One-shot worker runs forever silently:** require an early milestone and checkpoint report.
- **Worker exits without report but changed files:** do not discard. Inspect, checkpoint, and resume by chat id.
- **Large sync worker resolves conflicts but leaves staged merge:** supervisor must review, run checks, and explicitly authorize commit/deploy.
- **Public upstream PR from non-fork mirror fails:** push branch to a GitHub fork that can be used as PR head, then open PR against official.
- **Scope creep:** enforce exclusions in the worker prompt and in supervisor diff review.
