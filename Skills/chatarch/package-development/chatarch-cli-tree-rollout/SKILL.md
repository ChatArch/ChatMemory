---
name: chatarch-cli-tree-rollout
description: "Roll out ChatArch CLI --tree/--tree-brief with ChatStyle, workers, PR/tag/PyPI gates."
version: 0.1.0
related_skills:
  - cli-tree-contract
  - chatarch-cli-package-conventions
  - chatgh-pr-and-ci-workflow
  - hermes-external-agent-cli-orchestration
---

# ChatArch CLI Tree Rollout

Use this skill when standardizing Chat-series Python CLI packages on the shared `--tree` / `--tree-brief` contract and releasing the result through the normal ChatArch PR/tag/PyPI flow.

## Target Inventory

Do not use an old touched-repo ledger as the universe. Build the target list from ChatGlance / GitHub org inventory first. Inventory is only for discovering repositories that must be brought up to the standard; it must not weaken or redefine the standard.

Default target class:

1. Start from ChatArch org inventory, preferably the current host's ChatGlance/ChatArch project inventory path when present, recorded in workspace-local notes as `<chatarch-projects-inventory>`.
2. Remove forks and archived repositories.
3. Keep Python packages with detected console-script CLI commands.
4. For Chat-series scope, keep repos whose names start with `Chat` and then audit them against the current creation-time package standard.
5. Treat missing or stale ChatStyle/ChatEnv integration as a compliance gap in the repository or template. Fix the package/template to match the standard rather than recording the gap as a new exception.
6. List non-Chat Python CLIs such as `TermCap` or `hermes-agent` separately and include them only when the user explicitly expands scope.

Maintain separate machine-readable ledgers for completed full-gate repos, remaining Chat-series CLI targets, excluded forks/non-CLI/non-Python/non-Chat repos, and special cases.

## Creation-Time Standard

New Chat-series Python CLI packages should be created from a template that already includes the current CLI/runtime standard:

- `chatstyle>=0.2.0,<0.3.0` is the required ChatArch CLI tree/runtime dependency for real console-script CLIs.
- The root CLI exposes `--version`, `--tree`, and `--tree-brief` from day one.
- Click CLIs use ChatStyle `add_tree_option()` / registered tree renderer; local tree renderers are not copied into the package.
- Packages with env/profile/config behavior register with ChatEnv and use `chatenv>=0.2.10,<0.3.0` plus ChatEnv's typed profile/storage paths from the start.
- README, DEVELOP/CONTRIBUTING, tests, CHANGELOG, and release workflow are generated or updated with the same baseline; do not defer tree/runtime alignment until after the first release.

## CLI Runtime Standard

- Prefer Click root commands with explicit public names, e.g. `@click.group(name="chatdns")` or `@click.command(name="chatevent")`.
- For Click CLIs, use ChatStyle `add_tree_option()` / registered tree renderer from `chatstyle>=0.2.0,<0.3.0`.
- Do not copy package-local tree renderers across repos.
- `--tree` must render the real registered command surface, with root options, visible groups/leaves, one-line comments, and argument/option signatures.
- `--tree-brief` must render the same command surface without argument/option signatures.
- If the package is argparse/hand-rolled, classify the migration explicitly: convert to Click when safe so ChatStyle owns `--tree`/`--tree-brief`, or record a design blocker/exception before release. A hand-written argparse `--tree` without `--tree-brief` is not compliant.
- If the package depends on ChatEnv, use `chatenv>=0.2.10,<0.3.0`. `chatenv 0.2.9` is not final-compliant because it lacks published `--tree-brief`.

## Repo Classification

Classify every repo before assigning a worker:

- `fresh`: no prior rollout work; start from latest default branch.
- `partial-worker`: dirty/local/stale rollout changes exist; preserve a snapshot, then create a clean worktree from latest `origin/HEAD` and adapt only relevant changes.
- `released-evidence`: release already exists; read-only worker verifies PR/tag/workflow/PyPI/clean install/published CLI and writes PASS/BLOCKED.
- `full-flow`: explicitly authorized worker may push/open PR/merge/tag/publish for one named repo/release branch and must write a final evidence report.

Always fetch remote refs/tags through the machine proxy when needed, identify the real default branch from `origin/HEAD`, and never release from stale local dirty state.

## Completion Gate

Local implementation and local tests are not completion. A repo is complete only after all of these are true and independently verified:

1. Version bumped to the next patch version unless the repo already contains an intended unpublished forward patch.
2. PR opened against the default branch.
3. PR CI/docs/checks completed successfully; any red GitHub Action is a blocker.
4. PR merged.
5. Tag `vX.Y.Z` created on the merged default-branch commit.
6. Tag-driven publish workflow completed with conclusion `success`.
7. PyPI exact-version JSON exists with wheel and sdist.
8. Clean venv installs exact `Package==X.Y.Z` from PyPI without `PYTHONPATH`.
9. Published console script runs `<cli> --version`, `<cli> --tree`, and `<cli> --tree-brief`.
10. Worker final report includes PR URL/number, check/workflow URLs, merge commit, tag target, publish workflow URL/run id/conclusion, PyPI URL/artifacts, clean-install proof, published CLI readback, final git status, and risks.

If any item is missing, report `BLOCKED`, not `PASS`.

## Worker Pattern

Use `hermes-external-agent-cli-orchestration` for exact agent invocation. For Cursor durable workers, use the current host's verified full worker executable, not an unverified one-shot wrapper:

```bash
NODE_BIN=<node-bin-dir>
CHAT_ID=$(agent create-chat | tr -d '\r' | tail -n 1)
PROMPT=/path/to/prompt.txt
prompt=$(PROMPT="$PROMPT" python - <<'PY'
import os
from pathlib import Path
print(Path(os.environ["PROMPT"]).read_text())
PY
)
source <workspace>/.env
source <proxy-helper-if-needed>
PATH="$NODE_BIN:$PATH" agent --print --resume "$CHAT_ID" --force --trust "$prompt"
```

Per repo, persist: `chat_id`, repo path, clean worktree path, release branch, prompt path, report path, process session id, target version, and current stage in a run JSON.

After Cursor timeout or `kill_all`, inspect real state before resuming: local worktree status, open/closed PRs, remote release branch, tags, workflow runs, PyPI exact version, and report file. Resume with the same `chat_id`; do not start a new chat for the same repo unless the old session is unrecoverable and recorded.

## Prompt Requirements

Worker prompts must include:

- repo class (`fresh`, `partial-worker`, `released-evidence`, or `full-flow`)
- exact repo, worktree, release branch, target version, CLI command, package name, and report path
- latest default-branch base and instruction to refetch/resolve against remote latest
- allowed side effects; only `full-flow` may push/PR/merge/tag/publish
- secret redaction and no destructive git commands
- ChatStyle/ChatEnv dependency baselines
- local gates and final external completion gate
- final report contract with PASS/BLOCKED semantics

## GitHub/PyPI Tooling

- Use source/current ChatGH for PR/run/merge operations when installed `chatgh` may be stale: `PYTHONPATH=<workspace>/core/ChatGH/src python -m chatgh.cli ...`.
- Load the current host's approved proxy helper for GitHub/PyPI network operations when needed; keep concrete proxy helper paths in workspace-local notes, not shared skills.
- Never print tokens, PyPI sessions, git extraHeaders, proxy credentials, passwords, cookies, or raw auth files.

## Pitfalls

- Counting a repo complete from local diff/tests only.
- Leaving repository/template drift in place after the current creation-time standard is known. Update the repository or template to the current ChatStyle/ChatEnv baseline.
- Blindly retrying a timed-out Cursor worker and creating duplicate PRs/tags.
- Trusting worker self-report without external readback.
- Using a PATH `chatgh` that is older than the source checkout.
- Assuming Codex is installed as a fallback; verify `command -v codex` and smoke first.
- Tagging the release branch instead of the merged default-branch commit.
- Letting any red PR/default/docs/publish workflow pass as acceptable.
