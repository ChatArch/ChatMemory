# Gitea Pages Native Bot Preview Flow

## Session Lesson

When implementing GitHub-like Pages previews on self-hosted Gitea, use Gitea's own platform primitives:

- `.gitea/workflows/*.yml` for Actions events.
- `gitea-runner` as a worker registered at instance/org/repo scope.
- A Pages-like static publisher/service for built artifacts.
- A Gitea native bot user for PR comments, not a custom long-running bot daemon.

The user explicitly corrected an over-abstract answer: in Gitea, the closest analogue to `github-actions[bot]` is a native Gitea bot user created by the Gitea admin command. Do not detour into GitLab or an external bot service unless the user asks for that comparison.

## Native Gitea Bot

Confirm support with:

```bash
gitea admin user create --help | grep -- --user-type
```

Create a bot account:

```bash
gitea admin user create \
  --username chattea-pages-bot \
  --email chattea-pages-bot@example.invalid \
  --user-type bot \
  --fullname "ChatTea Pages Bot"
```

Generate a scoped token:

```bash
gitea admin user generate-access-token \
  --username chattea-pages-bot \
  --token-name chattea-pages-preview \
  --scopes write:issue,read:repository \
  --raw
```

Store the token as a repository or organization Actions secret, e.g. `CHATTEA_BOT_TOKEN`. Do not print the token in logs or docs.

## Workflow Shape

Use two channels:

```text
pull_request -> build docs -> publish --channel dev/pr-<number> -> bot comment
push main    -> build docs -> publish --channel stable           -> formal Pages update
```

Preview URL:

```text
https://<entry-host>/pages/<owner>/<repo>/dev/pr-<number>/
```

Stable URL:

```text
https://<entry-host>/pages/<owner>/<repo>/
```

The preview workflow should:

1. Read the PR number from `GITHUB_EVENT_PATH`.
2. Build MkDocs into `site/`.
3. Publish to `dev/pr-<number>`.
4. Call Gitea issue comment API using `CHATTEA_BOT_TOKEN`.
5. Create/update one comment with marker `<!-- chattea-pages-preview -->`.

The stable workflow should publish to `stable`. If stable and preview share one repo directory, stable publish must preserve the `dev/` subtree; otherwise merging to main will delete active preview URLs.

## Verification Checklist

After configuring the workflow:

```text
- Open a PR and verify a `pull_request` run completes successfully.
- Verify preview URL returns HTTP 200.
- Verify the PR has one comment containing the marker and preview URL.
- Verify the comment author is the native Gitea bot user, e.g. `comment.user.login == chattea-pages-bot`.
- Merge the PR and verify a `push` run on main completes successfully.
- Verify stable URL returns HTTP 200.
- Verify the prior preview URL still returns HTTP 200 unless preview cleanup was intentionally run.
```

## Acceptance Review Sequence

Do not collapse practice, documentation, and merge into one hidden step. For this user, a Gitea Pages/native-bot flow is not accepted until there is a visible internal Gitea PR they can inspect.

Minimum review evidence to provide before merging related docs or claiming completion:

```text
- Open Gitea PR URL, kept unmerged until the user reviews it.
- Gitea Actions run URL for the `pull_request` workflow.
- Job ID / runner name / status / conclusion.
- Bot comment URL on the PR.
- Comment author from API: `comment.user.login == <native-bot-user>`.
- Preview URL and HTTP 200 readback.
- Stable URL and HTTP 200 readback only after an intentional merge/stable deploy test.
```

If the user asks for screenshots, capture and add tutorial images for the Gitea control-plane evidence, not the final Pages/MkDocs output:

```text
- Workflow file showing `on: pull_request` trigger config.
- Actions run created by the PR event.
- Job log showing preview publish and `created preview comment: HTTP 201` / equivalent API result.
- Native Gitea bot comment in the PR timeline with the preview link.
```

Do not put a screenshot of the final Pages/MkDocs site into the tutorial as acceptance evidence; the user can open the Pages URL directly, and a MkDocs screenshot inside MkDocs is not meaningful proof. Verify Pages availability with HTTP status, HTML title, or metadata instead.

Keep real tokens, private paths, and credentials out of screenshots and public docs. If internal hostnames are visible, make sure the user explicitly wants that evidence in the repository docs; otherwise put screenshots in an internal report instead.

## Documentation Pitfalls

- Say "Gitea native bot user" when describing the commenting identity; avoid vague wording such as "some bot service".
- Do not imply Git itself has bot accounts; bot identity is provided by Gitea as the hosting platform.
- Keep GitHub comparisons limited to the mental model (`github-actions[bot]` analogue) and immediately map to Gitea primitives.
- Do not bring in GitLab unless the user explicitly asks for GitLab comparison.
- Public docs should describe reusable commands and placeholders, not internal hostnames, real tokens, run IDs, or machine paths.
