# ChatArch Package Development Skills

这个目录收纳 ChatArch 常规包 / Python 包 / package release 相关 skills：新仓库、包模板、ChatArch style、PR/MR、CI、PyPI 发布、Trusted Publisher、从旧仓库抽包。

`reference:` 规范见 `Skills/README.md`。本 README 只负责 package-development 主题导航。

## 当前主题节点

```text
package-development/
  README.md
  chatarch-cli-package-conventions/
  python-package-release-with-chattool-pypi/
  chatgh-pr-and-ci-workflow/
  chatgh-repo-token-setup/
  chatpypi-publisher-management/
  public-repo-and-default-branch-protection/
  chattool-capability-extraction/
  chatarch-org-pr-status/
```

## 每个 skill 是什么

### `chatarch-cli-package-conventions`

用途：ChatArch Python CLI 包开发阶段的通用规范：ChatEnv 集成、ChatStyle 交互、依赖边界、模板骨架和 generated package 检查。

覆盖流程：

1. 确认包是否应该注册 ChatEnv provider、使用 ChatStyle、暴露 `--version`。
2. 确认模板生成真实 CLI 骨架、`--help` / `--version`、README 和基础测试。
3. 规范 dependency bounds、profile 选择、secret handling、package-local vs substrate 责任边界。
4. 在开发/PR 阶段决定应该修 leaf package 还是修 ChatEnv / ChatStyle / ChatUp / ChatPyPI 这类基础设施。

什么时候用：创建或修改 ChatArch Python CLI 包、模板、CLI 骨架、ChatEnv/ChatStyle 集成时。

### `python-package-release-with-chattool-pypi`

用途：新建或发布一个 ChatArch 风格 Python CLI 包。

覆盖流程：

1. 确认包名、仓库名、module 名、CLI 名、版本号和发布目标。
2. 在 `ChatArch` 组织下创建/确认 GitHub repo。
3. 用 `chatpypi init <ProjectName> -t chatarch` 初始化包模板。
4. 检查 ChatStyle / ChatEnv 依赖、CLI 入口、README、测试和 workflow。
5. 初始化 git、设置 HTTPS remote、配置 repo-local token、push。
6. 跑本地测试、`chatpypi build`、`chatpypi check`。
7. 首次发布前配置/核对 PyPI Trusted Publisher。
8. 在明确授权后走 tag-driven PyPI publish，并回读 GitHub Actions / PyPI / clean install。

什么时候用：从零创建 ChatArch Python 包，或一个 feature PR 明确包含版本准备 / 发版准备。

### `chatgh-pr-and-ci-workflow`

用途：ChatArch 仓库的 PR/MR、CI、Actions 和 repo 状态工作流。

覆盖流程：

1. 用 ChatGH 查看 repo 权限、PR 列表、PR 详情和 checks。
2. 创建/更新/评论 PR。
3. 拉取并检查 CI / Actions run / job 日志。
4. 区分 PR 引入的问题、已有 CI 问题、权限/governance gate、infra flake。
5. 在用户明确授权后执行 merge。

什么时候用：用户问 PR 状态、CI 为什么红、要更新 PR、要 review 或准备 merge。

### `chatgh-repo-token-setup`

用途：给 ChatArch repo 配置本地 HTTPS git transport auth。

覆盖流程：

1. 确认 repo 使用 HTTPS remote。
2. 在新 repo / 首次 clone / 首次 push 前运行 `chatgh set-token`。
3. 验证 `chatgh repo-perms`、`git push --dry-run`、`git remote -v`。

什么时候用：新仓库创建后、首次本地初始化后、HTTPS `git push/fetch` 失败时。

### `chatpypi-publisher-management`

用途：查看、添加、更新或验证 PyPI Trusted Publisher / publisher list / pending publisher 状态。

覆盖流程：

1. 用 ChatPyPI 登录后的账号状态读取 `whoami`、project list、publisher list、pending-list。
2. 确认 ChatArch 包的 PyPI project、GitHub owner/repo、workflow filename、environment claim。
3. 首次发布前在 PyPI 侧配置或核对 Trusted Publisher。
4. 写操作后回读 active/pending publisher 状态和项目级 publisher details。

什么时候用：创建新包进入首次发布链路、修 PyPI publish 配置、查看 publisher/pending publisher 状态。

### `public-repo-and-default-branch-protection`

用途：在用户明确批准的仓库上执行 visibility / branch protection mutation。

覆盖流程：

1. 列出当前 repo visibility 和默认分支。
2. 对用户点名批准的仓库改 public。
3. 设置默认分支 PR-only baseline protection。
4. 回读 protection 字段并保存 JSON 证据。

什么时候用：用户明确说某些 ChatArch 仓库可以公开，并要求设置默认分支保护。

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
2. 对有 open PR 的 repo 进一步拉 PR 列表。
3. 输出 compact 表格或 JSON，作为后续 PR/CI 工作的入口。

什么时候用：用户问 “ChatArch 现在有哪些 PR/MR 没处理”、“当前组织状态如何”。

## 相关主题

- `../package-review/`：package 开发完成之后的后处理审查、provider 复查和规范回看。
