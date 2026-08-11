# Gitea Bot Trigger And Executor Practice

## Core Model

For Gitea automation, keep these concerns separate:

```text
identity   = Gitea native bot user or normal user whose token is used
trigger    = event or signal that starts automation
executor   = runner, webhook receiver, polling daemon, cron, CLI, or service that runs logic
credential = token/secret used by executor to call Gitea APIs
behavior   = workflow YAML, service code, webhook config, polling loop, or CLI command
```

A bot account does not create automatic behavior by itself. Creating the bot defines identity and credentials. The automatic behavior is defined elsewhere.

## Bot vs User

- A normal user represents a human; a bot represents an automation subject.
- Both need repository/organization permissions plus token scopes.
- Both can be used by automation if a token exists, but using a user token makes audit logs look like a human did it.
- Use a bot token for PR comments, releases, mirrors, and maintenance jobs so Gitea history shows an automation identity.

## Practice Case: PR Preview Comment

Validated Gitea-like GitHub behavior:

```text
PR opened
  -> Gitea emits pull_request event
  -> .gitea/workflows/pages-preview.yml matches `on: pull_request`
  -> Gitea creates an Actions run
  -> runner executes preview job
  -> job publishes dev/pr-N preview
  -> job reads CHATTEA_BOT_TOKEN
  -> job calls POST /api/v1/repos/{owner}/{repo}/issues/{pr}/comments
  -> PR timeline shows comment author as chattea-pages-bot
```

The bot is not the trigger. `pull_request` is the trigger; the runner is the executor; the bot token is the identity used for the final API write.

Document this as a classic case when explaining Gitea bot behavior.

## Practice Case: @bot Mention

`@bot` is also not magic execution. It is a signal that must be consumed:

```text
user comments: @chattea-bot rebuild preview
  -> Gitea records mention notification and/or sends issue_comment webhook
  -> polling daemon or webhook receiver reads the event
  -> service parses command and checks permissions
  -> service calls Gitea API with bot token
  -> result comment appears as chattea-bot
```

Implementation options:

- **Notification polling**: easiest first version; poll `/api/v1/notifications` with the bot token.
- **Webhook receiver**: lower latency; receive `issue_comment`, `issues`, `pull_request`, and parse `@bot` or slash commands.
- **Actions workflow**: good when the trigger is already a workflow-supported event such as `pull_request`, `push`, `schedule`, or `issue_comment`.

## Documentation Guidance

When updating docs for this user:

- Explain bot behavior from the practice case, not abstractly.
- Say exactly where each behavior is defined: `chattea bot ...` for identity/token, `.gitea/workflows/*.yml` for workflow triggers, bot service/webhook/polling code for `@bot` commands.
- Before claiming a bot flow works, provide a reviewable PR/run/comment trail.
- Screenshots should show workflow trigger, Actions run, job log/API result, and bot comment; do not use final output pages as the main proof.
