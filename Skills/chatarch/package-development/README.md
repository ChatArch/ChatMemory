# ChatArch Package Development Skills

这个目录收纳 ChatArch 常规包 / Python 包 / package release 相关 skills：新仓库、包模板、ChatArch style、PR/MR、CI、PyPI 发布、Trusted Publisher、从旧仓库抽包。

`reference:` 规范见 `Skills/README.md`。本 README 只负责 package-development 主题导航。

## 任务优先与收尾回写习惯

当 package-development 相关 skill 边界有交集或当前流程还不清楚时，先按具体任务开 PRD/进展记录并执行，不要在任务开始前大幅改写 skill。PRD 的完成标准应包含一项收尾复盘：根据实际执行结果判断是否需要更新本 README、某个 focused skill，或新增参考文件。对会大改仓库边界的拆包/迁移任务，优先在当前 project 的 `playground/` 下 clone/copy 工作副本，记录 source remote、base branch 和 HEAD，再把验证过的 delta 回灌到 canonical `core/` 仓库。

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

覆盖流程分两类：

**已有 PyPI project / 已发过版的包**：
1. 确认包名、仓库名、module 名、CLI 名、版本号和发布目标。
2. 查询 PyPI latest / tags / CI，保持版本连续。
3. 在现有仓库里准备版本、CHANGELOG、测试、build/check。
4. 走 PR/MR、merge 后在默认分支 tag-driven publish，并回读 GitHub Actions / PyPI / clean install。

**全新 PyPI project / “如果不在就注册”的新包**：
1. 确认 exact PyPI project name、normalized name、module、CLI、初始版本。
2. 先在当前 task 的 `playground/` 创建临时 scaffold，版本固定 `0.0.1`。
3. 构建、`twine check`，并用受控 PyPI 账号实际上传 `0.0.1` placeholder。
4. 只有 PyPI JSON 回读确认 project 已创建后，才创建/确认 GitHub `ChatArch/<Repo>`，再初始化 canonical `core/<ProjectName>`、设置 HTTPS remote/token、push。
5. 配置/核对 PyPI Trusted Publisher，再进入后续正式 feature/release 流程。

硬边界：新包 `0.0.1` placeholder 上传或回读失败时，停止；不得先创建 GitHub repo、不得先写 canonical `core/` 仓库、不得换名字绕过。

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
3. 已存在 PyPI project 的 Publisher 写操作直接用 `publisher detail` / `publisher add-github`，不走 pending。
4. pending 只用于 PyPI pre-registration / 不存在项目例外或 stale pending 清理。
5. 写操作后回读 active/pending publisher 状态和项目级 publisher details。

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
