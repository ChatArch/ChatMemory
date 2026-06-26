# ChatArch Package Development Skills

这个目录收纳 ChatArch 常规包 / Python 包 / package release 相关 skills：新仓库、包模板、ChatArch style、PR/MR、CI、PyPI/npm 发布、Trusted Publisher、从旧仓库抽包。

使用方式：先看每个 skill 的职责和流程；需要理解关联关系时，看各 `SKILL.md` header/frontmatter 里的 `reference:` 字段。

## Reference 字段约定

这个目录下的 `SKILL.md` 可以在 frontmatter/header 里声明可选 `reference:` 字段，用来表达 skill 图结构里的关联边。

格式保持简洁：每一项是一个 skill 或主题节点，加一句说明它在当前 skill 里的作用。

规则：

- `reference` 的 key 必须使用目标节点的规范名。
- 对普通 skill，规范名应等于目标 skill 的 frontmatter `name`，通常也等于文件夹名。
- 对主题节点，可以使用主题目录名，例如 `package-development`。
- description 只写这个目标在当前 skill 中发挥的作用，不写长流程。

```yaml
reference:
  - other-skill: "这个 skill 在当前 skill 中发挥的作用"
```

这个字段用于构建/阅读 skill graph；正文只保留必要流程，不重复展开所有关联说明。

## 当前主题节点

### 主题内 skills

```text
package-development/
  README.md
  python-package-release-with-chattool-pypi/
  chatgh-pr-and-ci-workflow/
  chatgh-repo-token-setup/
  public-repo-and-default-branch-protection/
  chattool-capability-extraction/
  chatarch-org-pr-status/
```

### 外部常用 references

- `workspace-task-kickoff` — 建立 `~/Playground` task、PRD/progress/report。
- `chatarch-cli-package-conventions` — ChatArch Python CLI package conventions：ChatEnv、ChatStyle、模板、dependency bounds、CLI 行为。
- `python-package-publishing` — PyPI / Trusted Publishing / version continuity / release gates / post-publish verification。
- `chatpypi-publisher-management` — PyPI project list / publisher list / Trusted Publisher add/verify。
- `requesting-code-review` — PR 前 review、安全扫描、质量 gates。
- `extracting-capabilities-to-packages` — 通用抽包方法论。
- `npm-package-publishing` — npm package identity、scope、publish gate 和 CI automation。
- `chatenv-provider-workflow` — ChatEnv provider discovery / `chatenv test` / provider schema 排查；这个流程相对独立，保留在 `Skills/chatarch/` 外层。

## 每个 skill 是什么

### `python-package-release-with-chattool-pypi`

用途：新建或发布一个 ChatArch 风格 Python CLI 包。

Reference：

- 代码/模板约定：`chatarch-cli-package-conventions`
- Git transport auth：`chatgh-repo-token-setup`
- PyPI release gate：`python-package-publishing`
- PyPI Trusted Publisher：`chatpypi-publisher-management`
- PR/CI：`chatgh-pr-and-ci-workflow`

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

Reference：

- 快速组织 PR 概览：`chatarch-org-pr-status`
- Repo-local HTTPS auth：`chatgh-repo-token-setup`
- Public / branch protection mutation：`public-repo-and-default-branch-protection`
- Pre-commit / pre-push review：`requesting-code-review`

覆盖流程：

1. 用 ChatGH 查看 repo 权限、PR 列表、PR 详情和 checks。
2. 创建/更新/评论 PR。
3. 拉取并检查 CI / Actions run / job 日志。
4. 区分 PR 引入的问题、已有 CI 问题、权限/governance gate、infra flake。
5. 在用户明确授权后执行 merge。

什么时候用：用户问 PR 状态、CI 为什么红、要更新 PR、要 review 或准备 merge。

### `chatgh-repo-token-setup`

用途：给 ChatArch repo 配置本地 HTTPS git transport auth。

Reference：

- 新建 Python 包时通常由 `python-package-release-with-chattool-pypi` 调用。
- PR/CI 能力检查可与 `chatgh-pr-and-ci-workflow` 组合。

覆盖流程：

1. 确认 repo 使用 HTTPS remote。
2. 在新 repo / 首次 clone / 首次 push 前运行 `chatgh set-token`。
3. 验证 `chatgh repo-perms`、`git push --dry-run`、`git remote -v`。

什么时候用：新仓库创建后、首次本地初始化后、HTTPS `git push/fetch` 失败时。

### `public-repo-and-default-branch-protection`

用途：在用户明确批准的仓库上执行 visibility / branch protection mutation。

Reference：

- Repo/PR readback：`chatgh-pr-and-ci-workflow`
- Repo-local HTTPS auth：`chatgh-repo-token-setup`

覆盖流程：

1. 列出当前 repo visibility 和默认分支。
2. 对用户点名批准的仓库改 public。
3. 设置默认分支 PR-only baseline protection。
4. 回读 protection 字段并保存 JSON 证据。

什么时候用：用户明确说某些 ChatArch 仓库可以公开，并要求设置默认分支保护。

### `chattool-capability-extraction`

用途：把 ChatTool 中已经成形的能力拆成独立 ChatArch Python package。

Reference：

- 通用抽包流程：`extracting-capabilities-to-packages`
- 新 standalone package bootstrap/release：`python-package-release-with-chattool-pypi`
- Parent / standalone PR/CI：`chatgh-pr-and-ci-workflow`
- Release gates：`python-package-publishing`

覆盖流程：

1. 盘点父仓库命令、module tree、tests、docs、aliases、dependencies。
2. 创建/强化 standalone repo/package。
3. 迁移能力，保持必要 CLI 行为，删除旧 parent-only 逻辑。
4. 发布 standalone package 后，再更新父仓库依赖、docs、tests 和 PR。
5. 明确 merge / tag / publish 的独立授权边界。

什么时候用：ChatPyPI、ChatDNS、ChatUp 这类从 ChatTool 拆出的独立包。

### `chatarch-org-pr-status`

用途：快速查看 ChatArch organization 里哪些 repo 有 open PR。

Reference：

- 单个 PR 详情 / CI / readiness：`chatgh-pr-and-ci-workflow`

覆盖流程：

1. 用 `chatgh repo list --owner ChatArch --json-output` 做组织级过滤。
2. 对有 open PR 的 repo 进一步拉 PR 列表。
3. 输出 compact 表格或 JSON，作为后续 PR/CI 工作的入口。

什么时候用：用户问 “ChatArch 现在有哪些 PR/MR 没处理”、“当前组织状态如何”。

## 后续待整理

- Hermes 本地 skills 暂不主动改动；后续逐步看 `chatgh-repo-token-setup`、`chattool-capability-extraction` 的 canonical / 同步策略。
- ChatPyPI `chatarch` 模板源码已先移除默认 `hello` demo；后续按 ChatPyPI 正常 PR/release 流程处理。
