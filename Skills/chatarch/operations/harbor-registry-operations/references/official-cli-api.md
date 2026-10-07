# Official Harbor CLI and REST interface

## Client/server placement

Treat the official `harbor` executable as a remote management client, not as the registry server. It communicates with the configured HTTPS Harbor origin and can run on a different machine. Published v0.0.26 clients cover macOS/Linux/Windows on amd64 and arm64. Management clients do not need the server's Docker daemon, a local database, SSH access, or colocated deployment.

The Harbor service itself still needs a supported container/orchestrator runtime, persistent storage and ingress. Moving a CLI context does not move the service or its images. Keep server migration separate from client installation/login.

## Interface responsibilities

- **Management CLI:** projects and memberships; repositories/artifacts/tags/labels; human and robot identities; quotas, immutable/retention rules and CVE allowlists; upstream registry/replication; webhooks; scanner/vulnerability management; preheat, job queues, schedules, health/logs; system configuration and local contexts.
- **Management REST API:** JSON operations under `<https-origin>/api/v2.0/`. The CLI is one client of this contract. Use `/api/v2.0/health`, `/api/v2.0/users/current`, `/api/v2.0/projects`, and `/api/v2.0/projects/<project>/repositories` for bounded connectivity/identity/list smoke tests.
- **API Explorer:** `<https-origin>/devcenter-api-2.0` provides the Harbor Swagger UI. Read the live schema before crafting writes; a help command does not prove every server feature is deployed or accessible to that identity.
- **Registry data plane:** `/v2/` provides OCI/Docker manifests and blob transfer. An anonymous HTTPS Bearer challenge is expected. Prefer Docker/OCI clients for push/pull rather than treating project-management endpoints as image-upload APIs.

Native database-auth accounts support HTTP Basic for the management API; other auth modes and robot identities follow the configured Harbor contract and permission scope. Put passwords/tokens in private context files or a secret provider, not argv, URLs, reports or shared source. For example, `curl --user '<shared-user>' '<https-origin>/api/v2.0/projects'` prompts for the password without embedding it in the command.

## Verified capability boundary

Read-only login/health/project/repository/artifact workflows of CLI v0.0.26 work with Harbor v2.15.2. Treat this as bounded compatibility evidence, not proof of every administrative mutation, LDAP/replication integration, or scanner backend. A scanner command existing in the CLI is not evidence that a scanner is installed.

In v0.0.26, ordinary piped `--password-stdin` still requires terminal IO and can fail with an ioctl error. Interactive login or an owned non-echoing PTY initializes the explicit private context; automation can then reuse that context. Recheck this behavior after upgrading rather than hard-coding the limitation forever. Docker's password-stdin is a separate implementation.

## Real command-tree extraction

The v0.0.26 CLI rejects `--tree`. Recurse through each advertised command's real `--help` instead, preserving command identifiers. Cobra groups and variable padding matter: the longest command can have only one space before its description. Collect by command sections rather than a fixed two-space name/description separator; deduplicate full paths, persist batches, and verify every advertised child was visited.

The following visible-help snapshot contains 30 top-level commands and 172 command nodes excluding the root. Parent groups are included in that node count; it is not a count of independent business actions. Rebuild it from the installed version when using another release.

```text
harbor
├── artifact  # Manage artifacts
│   ├── delete  # delete an artifact
│   ├── label  # label command for artifacts
│   │   ├── add  # Attach a label to an artifact in a Harbor project repository
│   │   ├── delete  # Detach a label from an artifact in a Harbor project repository
│   │   └── list  # Display labels attached to a specific artifact
│   ├── list  # List container artifacts (images, charts, etc.) in a Harbor repository with metadata
│   ├── scan  # Scan an artifact
│   │   ├── start  # Start a scan of an artifact
│   │   └── stop  # Stop a scan of an artifact
│   ├── tags  # Manage tags of an artifact
│   │   ├── create  # Create a tag of an artifact
│   │   ├── delete  # Delete a tag of an artifact
│   │   └── list  # List tags of an artifact
│   └── view  # Get information of an artifact
├── cve-allowlist  # Manage system CVE allowlist
│   ├── add  # Add cve allowlist
│   └── list  # List system level allowlist of cve
├── info  # Display detailed Harbor system, statistics, and CLI environment information
├── label  # Manage labels in Harbor
│   ├── create  # create label
│   ├── delete  # delete label
│   ├── list  # list labels
│   └── update  # update label
├── ldap  # Manage ldap users and groups
│   ├── import  # import ldap user by registered userid
│   ├── ping  # ping ldap server
│   └── search  # search ldap user by registered userid
├── project  # Manage projects and assign resources to them
│   ├── config  # Manage project configuration
│   │   ├── list  # List configuration of a Harbor project by name or ID
│   │   └── update  # Interactively or via flags update project configuration in Harbor
│   ├── create  # create project
│   ├── delete  # Delete project by name or ID
│   ├── list  # List projects
│   ├── logs  # get project logs
│   ├── member  # Manage members in a Project
│   │   ├── create  # create project member
│   │   ├── delete  # delete member by username
│   │   ├── list  # list members in a project
│   │   └── update  # update member by name
│   ├── preheat  # Manage project preheat resources
│   │   ├── execution  # Manage preheat executions
│   │   │   ├── list  # List preheat executions
│   │   │   ├── stop  # Stop preheat execution
│   │   │   └── view  # View preheat execution details
│   │   └── policy  # Manage preheat policies
│   │       ├── create  # Create a preheat policy
│   │       ├── delete  # Delete a preheat policy
│   │       ├── list  # List preheat policies under a project
│   │       ├── start  # Manually trigger a preheat policy
│   │       ├── update  # Update a preheat policy
│   │       └── view  # View details of a preheat policy
│   ├── robot  # Manage robot accounts
│   │   ├── create  # create robot
│   │   ├── delete  # delete robot by name
│   │   ├── list  # list robot
│   │   ├── refresh  # refresh robot secret by id
│   │   ├── update  # update robot by id
│   │   └── view  # get robot by id
│   ├── search  # search project based on their names
│   ├── summary  # Get summary of a project
│   └── view  # get project by name or id
├── quota  # Manage quotas
│   ├── list  # list quotas
│   ├── update  # update quotas for projects
│   └── view  # get quota by quota ID
├── repo  # Manage repositories
│   ├── delete  # Delete a repository
│   ├── list  # list repositories within a project
│   ├── search  # search repository based on their names
│   ├── update  # Update a repository
│   └── view  # Get repository information
├── robot  # Manage robot accounts
│   ├── create  # create robot
│   ├── delete  # delete robot by name
│   ├── list  # list robot
│   ├── refresh  # refresh robot secret by id
│   ├── update  # update robot by id
│   └── view  # get robot by id
├── tag  # Manage tags in Harbor registry
│   ├── immutable  # Manage Immutability rules in the project
│   │   ├── create  # create immutable tag rule
│   │   ├── delete  # delete immutable rule
│   │   └── list  # Display all immutable tag rules for a project
│   └── retention  # Manage tag retention rules in the project
│       ├── create  # Create a tag retention rule in a project
│       ├── delete  # Delete a tag retention rule for a project
│       └── list  # List tag retention rules of a project
├── webhook  # Manage webhook policies in Harbor
│   ├── create  # Create a new webhook for a Harbor project
│   ├── delete  # Delete a webhook from a Harbor project
│   ├── edit  # Edit an existing webhook for a Harbor project
│   └── list  # List all webhook policies for a Harbor project
├── login  # Log in to Harbor registry
├── logout  # Log out from Harbor registry
├── password  # Change your password
├── user  # Manage users
│   ├── create  # create user
│   ├── delete  # delete user by name or id
│   ├── elevate  # elevate user
│   ├── list  # List users
│   └── password  # Reset user password by name or id
├── config  # Manage system configurations
│   ├── apply  # Update system configurations from local config file
│   └── view  # View Harbor configurations
├── context  # Manage locally available contexts
│   ├── delete  # Delete (clear) a specific config item
│   ├── get  # Get a specific config item
│   ├── list  # List contexts
│   ├── switch  # Switch to a new context
│   └── update  # Set/update a specific config item
├── health  # Get the health status of Harbor components
├── instance  # Manage preheat provider instances in Harbor
│   ├── create  # Create a new preheat provider instance in Harbor
│   ├── delete  # Delete a preheat provider instance by its name or ID
│   ├── list  # List all preheat provider instances in Harbor
│   ├── ping  # Ping preheat provider instance by name or id
│   ├── update  # Update a preheat provider instance in Harbor
│   └── view  # get preheat provider instance by name or id
├── jobservice  # Manage Harbor job service (admin only)
│   └── queues  # Manage job queues (list, stop, pause, resume)
│       ├── list  # List all job queues
│       ├── pause  # Pause queue(s) (--type or --interactive)
│       ├── resume  # Resume queue(s) (--type or --interactive)
│       └── stop  # Stop queue(s) (--type or --interactive)
├── registry  # Manage registries
│   ├── create  # create registry
│   ├── delete  # delete registry by name or id
│   ├── list  # list registry
│   ├── update  # update registry
│   └── view  # get registry information
├── replication  # Manage replications
│   ├── executions  # Manage replication executions
│   │   ├── list  # List replication executions
│   │   └── view  # get replication execution by id
│   ├── log  # get replication execution logs by execution and task id
│   ├── policies  # Manage replication policies
│   │   ├── create  # create replication policies
│   │   ├── delete  # delete replication policy by name or id
│   │   ├── list  # List replication policies
│   │   ├── update  # Update an existing replication policy
│   │   └── view  # get replication policy by name or id
│   ├── start  # start replication
│   └── stop  # stop replication
├── scan-all  # Scan all artifacts
│   ├── metrics  # Get the metrics of the latest scan all process
│   ├── run  # Scan all artifacts now
│   ├── stop  # Stop scanning all artifacts
│   ├── update-schedule  # update-schedule [schedule-type: none|hourly|daily|weekly|custom]
│   └── view-schedule  # View the scan all schedule
├── scanner  # scanner commands
│   ├── create  # Create a scanner
│   ├── delete  # Delete a scanner registration
│   ├── list  # List scanners
│   ├── metadata  # Retrieve metadata for a specific scanner
│   ├── set-default  # Set the default scanner for Harbor
│   ├── update  # Update a scanner registration
│   └── view  # Display detailed information about a scanner registration
├── schedule  # Schedule jobs in Harbor
│   └── list  # show all schedule jobs in Harbor
├── vulnerability  # Manage vulnerabilities in Security Hub
│   ├── list  # List vulnerabilities in Security Hub
│   └── summary  # Get Security Hub vulnerability summary
├── logs  # Get recent logs of the projects which the user is a member of
├── version  # Version of Harbor CLI
├── completion  # Generate the autocompletion script for the specified shell
│   ├── bash  # Generate the autocompletion script for bash
│   ├── fish  # Generate the autocompletion script for fish
│   ├── powershell  # Generate the autocompletion script for powershell
│   └── zsh  # Generate the autocompletion script for zsh
└── help  # Help about any command
```

## Authoritative sources

- https://github.com/goharbor/harbor-cli
- https://github.com/goharbor/harbor
- https://goharbor.io/docs/
