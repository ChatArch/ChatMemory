---
name: public-repo-and-default-branch-protection
description: 将用户明确批准的 ChatArch 仓库改为 public，并设置默认分支 PR-only 保护。
version: 0.1.0
tags:
  - ChatArch
  - GitHub
  - branch-protection
  - repository-visibility
  - ChatGH
reference:
  - package-development: "主题索引；用于定位 ChatArch package/repo workflow 相关 skill"
  - chatgh-pr-and-ci-workflow: "repo/protection readback 与 PR-only workflow 检查"
  - chatgh-repo-token-setup: "需要本地 git push/fetch 时配置 repo-local HTTPS auth"

---

# ChatArch 仓库 public + 默认分支保护流程

## 适用场景

当用户明确指定一个或一组 ChatArch 仓库可以公开，并要求把默认分支设为只能通过 PR 更新时使用。

本 skill 只适用于**已经被用户逐个点名/批准**的仓库。不要把它当成批量公开所有 private 仓库的默认流程。

## 硬性边界

- 默认不把 private 仓库改 public。
- 只有用户明确说出仓库名并允许 public 时，才对该仓库执行 visibility 修改。
- 如果用户说“剩下的我再看一下”“需要审核”，只输出 private 清单，不做 visibility 修改。
- 不要为了绕过 private branch protection 的 GitHub plan/visibility 限制而擅自 public 仓库。
- 不改未被点名的仓库。
- 不打印 GitHub token、ChatEnv token、`.git/config` extraHeader、Authorization header 或 base64 auth 值。

## 工作区记录

从 `~/Playground` 开始，读取 workspace 规则，并复用当前项目目录；如果没有对应任务，再创建 `projects/<topic>/<task>/`：

```bash
cd ~/Playground
sed -n '1,140p' AGENTS.md
sed -n '1,180p' projects/README.md
```

记录内容建议包括：

- 用户明确批准 public 的仓库列表；
- 执行前 visibility / default branch；
- 执行后 protection 回读字段；
- 未处理仓库列表与原因；
- raw JSON 输出路径。

## 预检查：列出当前 visibility

优先用 ChatGH。若全局 `chatgh` 版本较旧，使用源码版：

```bash
cd ~/Playground/core/ChatGH
PYTHONPATH=src python -m chatgh.cli repo list \
  --owner ChatArch \
  --limit 100 \
  --json-output > <project>/playground/chatarch-repo-list-current.json
```

从 JSON 中筛选 private 仓库，先反馈给用户审核。不要只凭记忆或历史报告。

## 设置流程

对每个用户明确批准的仓库：

1. `GET /repos/{owner}/{repo}` 读取当前 visibility 和 default branch。
2. 如果仍是 private，`PATCH /repos/{owner}/{repo}`：
   ```json
   {"private": false}
   ```
3. 回读 repo，确认 visibility 已变成 `public`。
4. `PUT /repos/{owner}/{repo}/branches/{default_branch}/protection` 设置 classic branch protection。
5. 回读 branch/protection，确认严格字段。
6. 保存 JSON 输出到当前项目 `playground/`。

## Branch protection payload

默认规则是“安全底线”，不是强制 review 流程：

```json
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0,
    "require_last_push_approval": false,
    "bypass_pull_request_allowances": {"users": [], "teams": [], "apps": []}
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

语义：

- 默认分支必须走 PR；
- approving review 数量为 `0`，即不默认要求 review；
- `enforce_admins=true`，owner/admin 也不能绕过直接 push；
- 禁止 force push；
- 禁止删除默认分支；
- 不设置 PR bypass 白名单。

如果仓库已经有 required status checks，优先保留已有 status checks，不要无意清空 CI 门槛；如果本任务明确只是给新公开仓库加基线保护且没有现有 checks，可设为 `null`。

## 验证命令

单仓库查看：

```bash
cd ~/Playground/core/ChatGH
PYTHONPATH=src python -m chatgh.cli repo protection \
  --repo ChatArch/<RepoName> \
  --json-output
```

全量回捞：

```bash
PYTHONPATH=src python -m chatgh.cli repo protection \
  --owner ChatArch \
  --limit 100 \
  --jobs 8 \
  --json-output > <project>/playground/chatarch-protection-after.json
```

严格成功标准：

```text
default_branch_protected = true
branch_protection.required_pull_request_reviews = true
branch_protection.required_approving_review_count = 0
branch_protection.enforce_admins = true
branch_protection.allow_force_pushes = false
branch_protection.allow_deletions = false
```

## 剩余 private 仓库处理

执行结束后必须重新列出当前 private 仓库，并明确标注“未获用户批准前不处理”：

```bash
PYTHONPATH=src python -m chatgh.cli repo list \
  --owner ChatArch \
  --limit 100 \
  --json-output > <project>/playground/chatarch-repo-list-current.json
```

汇报时用简短清单，不要把这些仓库自动加入下一轮 public 操作。

## 完成汇报模板

```text
已处理并验证：
- ChatArch/<Repo>@<branch>: public, protected, reviews=0, enforce_admins=true

剩余 private，等待用户审核：
- ChatArch/<PrivateRepo>

记录：
- <project>/playground/<raw-output>.json
- <project>/reports/<report>.md
```

## 常见坑

- 把 GitHub 返回的 private branch protection blocker 当成自动 public 的理由。必须等用户明确批准。
- 只看 table 输出，不看 JSON 里的 `enforce_admins`、`allow_force_pushes`、`allow_deletions`。
- 拼错语音转写仓库名，例如把 `ChatBlog` 写成 `ChatLog` 或 `CahtBlog`；执行前必须匹配真实 `ChatArch/<Repo>`。
- 批量脚本误处理未点名仓库。批量操作时必须用显式 allowlist。
- 把 `required_approving_review_count` 设成 1。默认规则不要求 review，应为 `0`。
