# Interactive agent supervision and closeout

Date added: 2026-08-05.

Use this reference when Hermes is supervising an external coding-agent CLI as the executor, especially for release tasks where the user expects Hermes to keep watching, intervene by conversation, and stop promptly once the real artifacts are complete.

## Pattern

1. **Use an interactive PTY for tasks that may need steering.**
   - Long `--print` / one-shot runs can be non-observable and cannot receive follow-up instructions.
   - Prefer a Hermes-managed process: `terminal(background=true, pty=true, notify_on_complete=true, ...)`.
   - Submit the task prompt with `process(action="submit")`; if text is pasted but not executed, send raw carriage return with `process(action="write", data="\r")`.

2. **Start with a visible milestone.**
   - The first prompt should ask the external agent to read governing workspace rules/skills, identify the canonical repo, record initial git status, and then continue.
   - This creates an early checkpoint for Hermes to verify rather than waiting silently for a final report.

3. **Report current state first.**
   - When the user asks where the task stands, answer running/exited, process/session id, latest visible activity, repo/artifact state, and whether progress is healthy, blocked, or likely stalled.
   - Do not bury the status behind a postmortem or a long explanation.

4. **Intervene through the agent conversation, not by taking over implementation.**
   - If the user gives a mid-run authorization such as “this repo can be public”, send that authorization into the same external-agent PTY as a concise follow-up.
   - Require the agent to record the authorization in the active project before making the side-effecting change.
   - If the agent is blocked, send a concrete next-step instruction and acceptance criteria. Do not start editing the repo yourself when the user delegated execution to the external agent.

5. **Verify independently after the agent claims completion.**
   - Treat the external agent’s report as a lead, not proof.
   - For a release, Hermes should read back default-branch status, commit/tag, remote tag, workflow runs, registry/PyPI JSON or simple index, docs HTTP, clean install smoke, and final report paths.

6. **Do not confuse a live follow-up prompt with incomplete work.**
   - Some interactive agents remain alive at an “add follow-up” prompt after all artifacts have been created and verified.
   - If the user asks to close out and Hermes verification shows the task is complete, gracefully close stdin / send EOF (`process(action="close")`) instead of continuing to poll for more prose.
   - Capture the external resume/session id printed on exit, then report the concise final status.

7. **Use graceful lifecycle controls.**
   - Prefer EOF/normal exit for a waiting interactive agent.
   - Do not use `kill` / `kill -9` merely to stop a completed agent session unless explicitly authorized or the process is truly unresponsive and the user approved termination.

## Closeout checklist

Before telling the user the delegated task is finished:

- external-agent process is either still usefully working or has been closed/exited intentionally;
- if closed, exit code and resume/session id were captured when available;
- active project `progress.md` records the final state and any residual risk;
- final report exists if the task requested one;
- Hermes independently verified the important external artifacts;
- todos for watching/acceptance are completed or explicitly cancelled.
