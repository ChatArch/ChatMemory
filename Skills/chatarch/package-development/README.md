# ChatArch Package Development Skills

这个主题用于 ChatArch 常规包 / Python 包 / package release 工作：新仓库、包模板、ChatArch style、PR/MR、CI、PyPI/npm 发布、Trusted Publisher、从旧仓库抽包。

这是分类归档与导航页。先看下面每个 skill 的职责和流程，再根据任务场景组合加载。

## 当前收纳的主题内 skills

```text
package-development/
  README.md
  python-package-release-with-chattool-pypi/
  chatgh-pr-and-ci-workflow/
  chatgh-repo-token-setup/
  public-repo-and-default-branch-protection/
  chatenv-provider-workflow/
  chattool-capability-extraction/
  chatarch-org-pr-status/
```

## 每个 skill 是什么

### `python-package-release-with-chattool-pypi`

用途：新建或发布一个 ChatArch 风格 Python CLI 包。

覆盖流程：

1. 确认包名、仓库名、module 名、CLI 名、版本号和发布目标。
2. 在 `ChatArch` 组织下创建/确认 GitHub repo。
3. 用 `chatpypi init <ProjectName> -t chatarch` 初始化包模板。
4. 检查 ChatStyle / ChatEnv 依赖、CLI 入口、README、测试和 workflow。
5. 初始化 git、设置 HTTPS remote、配置 repo-local token、push。
6. 跑本地测试、`chatpypi build`、`chatpypi check`。
7. 在明确授权后走 tag-driven PyPI publish，并回读 GitHub Actions / PyPI / clean install。

什么时候用：从零创建 ChatArch Python 包，或一个 feature PR 明确包含版本准备 / 发版准备。

### `chatgh-pr-and-ci-workflow`

用途：ChatArch 仓库的 PR/MR、CI、Actions 和 repo 状态工作流。

覆盖流程：

1. 用 ChatGH 查看 repo 权限、PR 列表、PR 详情和 checks。
2. 创建/更新/评论 PR。
3. 拉取并检查 CI / Actions run / job 日志。
4. 区分 PR 引入的问题、已有 CI 问题、权限/governance gate、infra flake。
5. 只在用户明确授权后执行 merge。

什么时候用：用户问 PR 状态、CI 为什么红、要更新 PR、要 review 或准备 merge。

不要用它做：直接发布包；merge 不是 release。

### `chatgh-repo-token-setup`

用途：给 ChatArch repo 配置本地 HTTPS git transport auth。

覆盖流程：

1. 确认 repo 使用 HTTPS remote。
2. 在新 repo / 首次 clone / 首次 push 前运行 `chatgh set-token`。
3. 验证 `chatgh repo-perms`、`git push --dry-run`、`git remote -v`。

什么时候用：新仓库创建后、首次本地初始化后、HTTPS `git push/fetch` 失败时。

### `public-repo-and-default-branch-protection`

用途：在用户明确批准的仓库上执行 visibility / branch protection mutation。

覆盖流程：

1. 列出当前 repo visibility 和默认分支。
2. 只对用户点名批准的仓库改 public。
3. 设置默认分支 PR-only baseline protection。
4. 回读 protection 字段并保存 JSON 证据。

什么时候用：用户明确说某些 ChatArch 仓库可以公开，并要求设置默认分支保护。

不要用它做：为了绕过 GitHub private repo protection 限制而擅自 public 仓库。

### `chatenv-provider-workflow`

用途：新增、审查或 debug ChatEnv typed-config provider。

覆盖流程：

1. 检查 package 是否注册 `[project.entry-points."chatenv.configs"]`。
2. 检查 config class 的 title、aliases、storage dir、required/sensitive fields。
3. 验证安装后的 provider discovery。
4. 让 `chatenv test -t <alias>` 成为安全、可解释的 schema/provider check。
5. 区分本地 schema validation 和真实服务连通性检查。

什么时候用：包需要接入 ChatEnv，或 `chatenv list/cat/test/use/new` 行为缺失、混乱、不可发现。

### `chattool-capability-extraction`

用途：把 ChatTool 中已经成形的能力拆成独立 ChatArch Python package。

覆盖流程：

1. 盘点父仓库命令、module tree、tests、docs、aliases、dependencies。
2. 创建/强化 standalone repo/package。
3. 迁移能力，保持必要 CLI 行为，删除旧 parent-only 逻辑。
4. 发布 standalone package 后，再更新父仓库依赖、docs、tests 和 PR。
5. 明确 merge / tag / publish 的独立授权边界。

什么时候用：ChatPyPI、ChatDNS、ChatUp 这类从 ChatTool 拆出的独立包。

### `chatarch-org-pr-status`

用途：快速查看 ChatArch organization 里哪些 repo 有 open PR。

覆盖流程：

1. 用 `chatgh repo list --owner ChatArch --json-output` 做组织级过滤。
2. 只对 `open_prs > 0` 的 repo 进一步拉 PR 列表。
3. 输出 compact 表格或 JSON，作为后续 PR/CI 工作的入口。

什么时候用：用户问 “ChatArch 现在有哪些 PR/MR 没处理”、“当前组织状态如何”。

不要用它做：merge、close、comment、retarget；这是 read-only status skill。

## 外部关联 skills

这些不在本目录，但 package development 经常要一起加载：

- `workspace-task-kickoff` — 任何真实任务先建 workspace task，写 PRD/progress/report。
- `chatarch-cli-package-conventions` — ChatArch Python CLI package 的通用约定：ChatEnv、ChatStyle、模板、dependency bounds、CLI 行为。
- `python-package-publishing` — PyPI / Trusted Publishing / version continuity / release gates / post-publish verification。
- `chatpypi-publisher-management` — PyPI Trusted Publisher 的 project list / publisher list / add / verify。
- `github-workflows` — 通用 GitHub 总 playbook。
- `requesting-code-review` — PR 前 review、安全扫描、质量 gates。
- `extracting-capabilities-to-packages` — 通用抽包方法论。
- `npm-package-publishing` — npm package identity、scope、publish gate 和 CI automation。

## 常见组合

### 新建 ChatArch Python 包

加载：

1. `workspace-task-kickoff`
2. `python-package-release-with-chattool-pypi`
3. `chatarch-cli-package-conventions`
4. `chatgh-repo-token-setup`
5. `python-package-publishing`
6. 需要配置 publisher 时再加载 `chatpypi-publisher-management`

### 更新已有包并开 PR

加载：

1. `workspace-task-kickoff`
2. `chatarch-cli-package-conventions`
3. `chatgh-pr-and-ci-workflow`
4. `requesting-code-review`
5. 若涉及发版准备，再加载 `python-package-publishing`

### 只看 PR / CI / 组织状态

加载：

- 快速组织概览：`chatarch-org-pr-status`
- 单 PR / CI 追踪：`chatgh-pr-and-ci-workflow`

### 只配置 PyPI Trusted Publisher

加载：

1. `chatpypi-publisher-management`
2. 如 workflow/repo 也要改，再加载 `chatgh-pr-and-ci-workflow` 或 `github-workflows`

ChatArch 默认 publisher 形态：

```text
PyPI project: <ProjectName>
GitHub repository: ChatArch/<RepoName>
Workflow: publish.yml
Environment: blank / (Any), unless explicitly configured otherwise
```

不要把 PyPI profile 名、个人仓库前缀或 `RexWzh/askchat` 这类例外推断成 ChatArch 默认 owner/repo。

### 从 ChatTool 抽独立包

加载：

1. `workspace-task-kickoff`
2. `chattool-capability-extraction`
3. `extracting-capabilities-to-packages`
4. `python-package-release-with-chattool-pypi`
5. `chatgh-pr-and-ci-workflow`
6. `python-package-publishing`

## 当前待整理项

- Hermes 本地 skills 与 ChatMemory shared skills 中重复的 `chatgh-repo-token-setup`、`chattool-capability-extraction`，后续逐步看 canonical / 同步策略。
- 修 ChatPyPI `chatarch` 模板源码，移除默认 `hello` demo command/test/docs。
