# Official Harbor CLI and REST interface

## 直接使用：客户端、CLI、Docker 与 REST

以下是 Bash 示例（Linux/macOS）；Windows 使用发布的对应二进制，并用当前 shell 的路径/变量写法。先将占位符替换成 canonical SITES 或受控运行配置的值，不能把示例当成真实账号。官方归档可能命名为 `harbor-cli`；环境中的薄入口可命名 `harbor`，`HARBOR_BIN` 指向已校验的实际可执行文件。管理 CLI 不需要 SSH、Docker daemon 或与服务同机。

### 1. 参数与私有配置

```bash
export HARBOR_BIN=harbor
export REGISTRY_HOST='<registry-host>'
export HARBOR_ORIGIN="https://${REGISTRY_HOST}"
export HARBOR_USER='<catalog-user>'
export HARBOR_CONTEXT='<context-name>'
export HARBOR_PROJECT='<project-name>'
export HARBOR_REPO='<repository-name>'
export IMAGE_TAG='<image-tag>'
export CHATARCH_HOME="${CHATARCH_HOME:-$HOME/.chatarch}"
export HARBOR_CLI_CONFIG="$CHATARCH_HOME/harbor/cli/config.yaml"
export DOCKER_CONFIG="$CHATARCH_HOME/harbor/docker"
umask 077
mkdir -p "$(dirname "$HARBOR_CLI_CONFIG")" "$DOCKER_CONFIG"
```

`REGISTRY_HOST` 仅为 `host[:port]`，不含 scheme、路径或镜像名；`HARBOR_ORIGIN` 是无结尾斜线的 HTTPS origin。每个客户端建立自己的受限配置，不复制服务端整个凭据目录。统一网站登录按 SITES 规则使用，CI 凭据走下述 Robot Account。

### 2. 登录、验证与多个实例

```bash
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" login "$HARBOR_ORIGIN" \
  --username "$HARBOR_USER" --context-name "$HARBOR_CONTEXT"
chmod 600 "$HARBOR_CLI_CONFIG"
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" version
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" health
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" context list
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" context switch "$HARBOR_CONTEXT"
```

在受信任终端的密码提示中输入密码，不用 `--password`。只有首次初始化/凭据变更时需要登录；日常查询复用已验证 context。v0.0.26 普通管道的 `--password-stdin` 有 TTY 限制，不据此制造密码 argv 或声称无交互登录已支持。避免输出可能含凭据的完整 context/config dump。

### 3. 日常查询：项目 → 仓库 → 制品

```bash
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" --output-format json \
  project list --name "$HARBOR_PROJECT"
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" --output-format json \
  repo list "$HARBOR_PROJECT"
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" --output-format json \
  artifact list "$HARBOR_PROJECT/$HARBOR_REPO"
```

项目是权限/配额边界；仓库位于项目下；制品对应镜像/OCI内容，tag可变、digest定位内容。命令的 JSON 有的直接返回数组，有的包在 `Payload` 中；分页完成后核对 `XTotalCount`，不能把默认一页当全部。

创建项目是写操作，仅在获准范围内运行，随后回读是否私有：

```bash
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" project create --help
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" project create "$HARBOR_PROJECT"
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" --output-format json \
  project list --name "$HARBOR_PROJECT"
```

v0.0.26 的项目名是位置参数，不是臆造的 `--name` 创建参数；`--public` 会公开项目，不能为了让拉取成功而加它。帮助中的其他可写参数包括 `--storage-limit`、proxy-cache和registry-id，使用前查当前版本帮助及真实目标。

### 4. 镜像 push/pull：用 Docker 数据面

```bash
docker login "$REGISTRY_HOST" --username "$HARBOR_USER"
docker tag '<local-image>:<local-tag>' \
  "$REGISTRY_HOST/$HARBOR_PROJECT/$HARBOR_REPO:$IMAGE_TAG"
docker push "$REGISTRY_HOST/$HARBOR_PROJECT/$HARBOR_REPO:$IMAGE_TAG"
docker pull "$REGISTRY_HOST/$HARBOR_PROJECT/$HARBOR_REPO:$IMAGE_TAG"
```

Shell里的 `DOCKER_CONFIG` 已指向私有目录；Docker登录与Harbor管理CLI登录是两个独立客户端的认证缓存。前者登录成功不等于后者context已配置。验收时保存实际push digest，再按该digest拉取并与管理API回读对照。测试结束仅清除本次测试认证，不能退出或删除其他运行中的业务配置。

### 5. REST API：不用 CLI 也能管理

```bash
curl --fail --show-error --max-time 15 \
  "$HARBOR_ORIGIN/api/v2.0/health"
curl --fail --show-error --max-time 15 --user "$HARBOR_USER" \
  "$HARBOR_ORIGIN/api/v2.0/users/current"
curl --fail --show-error --max-time 15 --user "$HARBOR_USER" \
  "$HARBOR_ORIGIN/api/v2.0/projects"
curl --fail --show-error --max-time 15 --user "$HARBOR_USER" \
  "$HARBOR_ORIGIN/api/v2.0/projects/$HARBOR_PROJECT/repositories"
```

curl按提示读密码，不把密码放进命令。`users/current` 的返回身份/角色是认证证据，不能只看JWT形状。浏览器 API Explorer 为 `$HARBOR_ORIGIN/devcenter-api-2.0`，管理REST前缀是 `/api/v2.0/`；镜像manifest/blob传输则是另一套 `/v2/`。原生db_auth支持Basic，OIDC等模式需遵循当前服务的CLI secret/会话规则。写接口先看live Swagger schema，明确scope/payload，执行后GET精确目标。

### 6. CI：项目级 Robot Account，而不是统一管理员密码

在授权的项目/有效期范围内创建，仅授予必要pull/push权限。用文件工具将下面的非secret定义放进私有配置文件，再由受信任交互终端执行；占位符先替换。

```yaml
name: "<robot-name>"
description: "CI image push and pull"
duration: 90
project: "<project-name>"
permissions:
  - resource: "repository"
    actions: ["pull", "push"]
```

```bash
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" project robot create --help
"$HARBOR_BIN" --config "$HARBOR_CLI_CONFIG" project robot create \
  --robot-config-file '<private-robot-config>' --export-to-file
```

v0.0.26的 `--export-to-file` 是布尔选择，不接受臆造的输出路径参数；创建可能交互选择导出位置。默认行为可能复制secret到剪贴板/显示secret，因此必须先核对当前实现与终端/导出路径，使用受限文件或secret provider，不能在会被转发的捕获日志中执行。不要使用 `--all-permission`。当前仅验证了真实帮助契约，不把上述创建示例写成已创建/轮换账户。

CI中分别配置 `HARBOR_ROBOT_USERNAME` 与 `HARBOR_ROBOT_TOKEN` 为受控secret，禁止shell tracing；使用Docker自己的stdin实现：

```bash
set +x
printf '%s' "${HARBOR_ROBOT_TOKEN:?supply from CI secret provider}" | \
  docker login "$REGISTRY_HOST" \
  --username "${HARBOR_ROBOT_USERNAME:?supply from CI secret provider}" \
  --password-stdin
docker push "$REGISTRY_HOST/$HARBOR_PROJECT/$HARBOR_REPO:$IMAGE_TAG"
docker logout "$REGISTRY_HOST"
```

此片段只用于任务专属 `DOCKER_CONFIG`；不能在共享业务认证目录中任意logout。机器人secret轮换会影响已部署客户端，应先识别消费者并按批准步骤更新/回读。

### 7. 诊断与危险操作

- **找不到命令**：区分 `harbor` 薄入口和归档中的 `harbor-cli`，先验证实际二进制/版本与 `HARBOR_BIN`，不要因此重装服务。
- **连接/TLS失败**：检查origin、DNS/代理/CA及health；不启用insecure-registry、`-k`或skip-verify来掩盖问题。
- **401**：确认是预期Registry challenge还是管理身份认证失败，检查正确客户端的context/凭据。
- **403**：回读当前身份、项目成员和具体permission，不把网络可达等同于拥有权限。
- **查不到所有条目**：核对页码/page-size、`Payload`包装和总数，不能凭一页下结论。
- **扫描不可用**：先查已部署/注册的scanner；CLI有scan命令不等于安装了扫描组件。
- **写/删除/批量操作**：project/repo/artifact delete、config apply、robot refresh、replication/scan-all/queue stop会改变外部状态。先明确真实目标、权限、影响/消费者和可回退方案；只有批准的写范围才能执行，并对精确目标读回。更新Skill/查询功能不授权执行这些操作。

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
