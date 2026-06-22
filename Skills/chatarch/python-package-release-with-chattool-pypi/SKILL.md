---
name: python-package-release-with-chattool-pypi
description: ChatArch Python 包从仓库创建、ChatTool PyPI/ChatStyle 模板初始化、提交推送到 PyPI 发版的完整流程。
version: 0.1.0
tags:
  - ChatArch
  - Python
  - PyPI
  - ChatTool
  - ChatStyle
  - ChatGH
---

# ChatArch Python 包创建与发版流程

## 适用场景

当需要创建一个新的 ChatArch 风格 Python CLI 包，并完整跑通以下流程时使用：

1. 在 GitHub `ChatArch` 组织下创建远程仓库。
2. 用 `chattool pypi init ... -t chatarch` 初始化包模板。
3. 确认 ChatStyle / ChatEnv 依赖、CLI 入口、README、测试、workflow。
4. 初始化 git、commit、设置 remote、push。
5. 本地测试、构建、`twine check`、上传 PyPI。
6. 回读 GitHub 与 PyPI，确认真实可用。

## 硬性安全门槛

发布前必须明确并记录以下信息，不能凭模板默认值发布：

- 品牌 / 仓库名，例如 `ChatNPM`。
- PyPI `[project].name` exact name，例如 `ChatNPM`。
- PyPI normalized name，例如 `chatnpm`。
- Python import module，例如 `chatnpm` 或 `chat_npm`。
- CLI 入口，例如 `chatnpm`。
- 版本号，例如 `0.1.0`。
- GitHub 目标仓库，例如 `ChatArch/ChatNPM`。
- GitHub visibility：默认 `private`；只有用户明确点名批准 public 时才改 public。
- 发布目标：PyPI production 还是 TestPyPI。

如发现错误包名已经发布，先停止写操作；不要尝试其他相似名绕过。先检查 PyPI JSON、项目页、版本、normalized name，再继续。

仓库 visibility 是单独的远端风险门槛：不要因为 PyPI 要发布、branch protection 需要生效、或 GitHub private repo 返回 plan/visibility blocker，就自动把仓库 public。需要 public + 默认分支保护时，使用 ChatArch skill `public-repo-and-default-branch-protection`，并且只处理用户明确批准的仓库 allowlist。

## 标准流程

### 1. 建立 workspace 与任务记录

从 `~/Playground` 开始：

```bash
cd ~/Playground
sed -n '1,140p' AGENTS.md
sed -n '1,180p' projects/README.md
```

如果是新任务，创建或确认：

```text
projects/MM-DD-<task-name>/PRD.md
projects/MM-DD-<task-name>/progress.md
core/<ProjectName>/
```

源码仓库放 `core/<ProjectName>/`；任务进展写 `projects/.../progress.md`。

### 2. 预检查远程和包名

检查 PyPI 名称状态：

```bash
python3 - <<'PY'
import json, urllib.error, urllib.request
for name in ['ChatNPM', 'chatnpm', 'chat-npm']:
    try:
        with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/json', timeout=20) as r:
            data=json.load(r)
        print(name, 'EXISTS', data['info']['name'], data['info'].get('version'), data['info'].get('project_url'))
    except urllib.error.HTTPError as e:
        print(name, 'HTTP', e.code)
PY
```

检查或创建 GitHub 仓库。优先用 ChatGH：

```bash
chatgh repo list --owner ChatArch --limit 20
chatgh repo create \
  --owner ChatArch \
  --name <ProjectName> \
  --description '<description>' \
  --if-exists use
```

如果当前安装的 `chatgh` 没有 `repo` 子命令，但 `~/Playground/core/ChatGH` 源码包含新版命令，可用源码版执行：

```bash
cd ~/Playground/core/ChatGH
. .venv/bin/activate 2>/dev/null || uv venv .venv && . .venv/bin/activate
uv pip install -e .
PYTHONPATH=src python -m chatgh.cli repo list --owner ChatArch --limit 20
PYTHONPATH=src python -m chatgh.cli repo create \
  --owner ChatArch \
  --name <ProjectName> \
  --description '<description>' \
  --if-exists use
```

默认创建 private 仓库；只有用户明确要求 public 时才传 `--public` 或后续修改 visibility。

新建仓库后，尽量立即尝试给默认分支预置 branch protection。默认保护规则只做安全底线，不默认要求 code review：

- require pull request before merging / 禁止直接 push 到默认分支；
- required approving review count = `0`；
- enforce admins = `true`；
- 禁止 force push；
- 禁止 deletion。

如果 private 仓库因为 GitHub plan/visibility 限制无法设置 protection，只记录 blocker，不要自动改 public。只有用户明确批准某个仓库 public 时，才切到 `public-repo-and-default-branch-protection` skill 去执行 public + protection。

如果有 GitHub CLI，可用 `gh api` 直接设置，例如：

```bash
OWNER=ChatArch
REPO=<ProjectName>
BRANCH=main

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/$OWNER/$REPO/branches/$BRANCH/protection" \
  --input - <<'JSON'
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
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON
```

如果 GitHub 对 private 仓库返回以下限制，则记录 blocker，等仓库 public 或账号/组织 plan 支持 private branch protection 后再补：

```text
Upgrade to GitHub Pro or make this repository public to enable this feature.
```

### 3. 用 ChatTool PyPI / ChatStyle 模板初始化

推荐直接使用最终品牌名作为模板 name，避免生成错误的 kebab-case 分发名：

```bash
cd ~/Playground
chattool pypi init <ProjectName> \
  -t chatarch \
  --project-dir ~/Playground/core/<ProjectName> \
  --description '<ProjectName>: <short description>' \
  --author 'ChatArch' \
  --email '1073853456@qq.com' \
  --license MIT \
  --python '>=3.10' \
  --version 0.1.0 \
  -I
```

生成后核对：

```bash
cd ~/Playground/core/<ProjectName>
python3 - <<'PY'
import tomllib, pathlib, json
p=tomllib.loads(pathlib.Path('pyproject.toml').read_text())
print(json.dumps({
  'project_name': p['project']['name'],
  'dependencies': p['project'].get('dependencies'),
  'scripts': p['project'].get('scripts'),
}, ensure_ascii=False, indent=2))
PY
```

ChatArch 模板应包含：

- `src/<module>/cli.py`
- `tests/test_cli.py`
- `tests/test_version.py`
- `tests/cli-tests/`
- `README.md` / `README.en.md`
- `DEVELOP.md`
- `CHANGELOG.md`
- `.github/workflows/*`
- 依赖 `chatstyle>=0.1.0` 与 `chatenv>=0.1.1`

### 4. 本地验证

使用项目本地 venv，不全局安装：

```bash
cd ~/Playground/core/<ProjectName>
uv venv .venv
. .venv/bin/activate
uv pip install -e '.[dev]'
python -m pytest -q
rm -rf dist build *.egg-info src/*.egg-info
python -m build
python -m twine check dist/*
<cli-command> --help
```

期望：

- pytest 全部通过。
- `python -m build` 生成 sdist 和 wheel。
- `twine check` 对所有 dist 文件 `PASSED`。
- CLI help 正常显示。

### 5. 初始化 git、commit、push

```bash
cd ~/Playground/core/<ProjectName>
git init -b main
git add .
git commit -m 'Initial <ProjectName> package scaffold'
git remote add origin https://github.com/ChatArch/<ProjectName>.git

# Repo-local HTTPS token config: write the auth header into this repository's
# .git/config, not into the remote URL. Do not print the token or the base64 value.
TOKEN=$(cd ~/Playground/core/ChatGH && . .venv/bin/activate && PYTHONPATH=src python - <<'PY'
from chatgh.github.api import resolve_token_with_source
r = resolve_token_with_source(None)
t = r.get('token') if isinstance(r, dict) else None
if not t:
    raise SystemExit('missing GitHub token')
print(t)
PY
)
BASIC=$(TOKEN="$TOKEN" python3 - <<'PY'
import base64, os
print(base64.b64encode(("x-access-token:" + os.environ["TOKEN"]).encode()).decode())
PY
)
git config --local "http.https://github.com/ChatArch/<ProjectName>.git.extraHeader" "Authorization: Basic $BASIC"
unset TOKEN BASIC

git ls-remote --heads origin main || true
git push --dry-run -u origin main
git push -u origin main
git ls-remote --heads origin main
```

Use the HTTPS remote plus repo-local `.git/config` auth header by default. Avoid embedding tokens in `remote.origin.url`. The token will be stored in `.git/config` as an `http.<url>.extraHeader`; this is repository-local and not committed, but it is still sensitive, so never print raw `git config --get-regexp http.*extraHeader` output.

### 6. PyPI 上传与回读验证

上传前再次打印安全 metadata，但不要打印凭据：

```bash
cd ~/Playground/core/<ProjectName>
. .venv/bin/activate
python -m pytest -q
rm -rf dist build *.egg-info src/*.egg-info
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

上传后回读：

```bash
python3 - <<'PY'
import json, urllib.request
for name in ['<ProjectName>', '<normalized-name>']:
    with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/json', timeout=20) as r:
        data=json.load(r)
    print(data['info']['name'], data['info']['version'], data['info']['project_url'])
    print('releases:', sorted(data.get('releases', {}))[-5:])
PY
```

再做隔离安装验证：

```bash
uv venv ~/Playground/projects/<task>/playground/install-check
. ~/Playground/projects/<task>/playground/install-check/bin/activate
uv pip install '<ProjectName>==<version>'
<cli-command> --help
```

## ChatNPM 案例记录

本流程已用 `ChatNPM` 跑通过一次：

- 旧错误本地目录已移到 `~/Playground/.trash/ChatNPM-old-20260622-012703`。
- 使用命令：`chattool pypi init ChatNPM -t chatarch --project-dir ~/Playground/core/ChatNPM ...`。
- 生成结果：`project.name = "ChatNPM"`，module 为 `chatnpm`，CLI 为 `chatnpm`。
- GitHub 仓库通过 ChatGH 源码版创建：`ChatArch/ChatNPM`，初始为 private。
- 本地 commit：`a6434a7 Initial ChatNPM package scaffold`。
- remote：`git@main.github.com:ChatArch/ChatNPM.git`。
- PyPI：`ChatNPM==0.1.0` 上传成功，项目页 `https://pypi.org/project/ChatNPM/0.1.0/`。
- 隔离安装验证：`uv pip install 'ChatNPM==0.1.0'` 后 `chatnpm --help` 正常。
- 后续只有在用户明确批准后，才将 `ChatArch/ChatNPM` 改为 public 并设置默认分支保护；这不是 Python/PyPI 发布流程的默认步骤。

## 常见坑

- 不要把品牌名 `ChatNPM` 自动改成 `chat-npm`；PyPI 会规范化显示文件名，但 `[project].name` 应使用确认过的 exact name。
- PyPI 的 normalized name 与显示名可能不同：`ChatNPM` 会归一到 `chatnpm`。
- 删除错误 PyPI 项目不能靠 `twine`；`twine` 只有 `check/register/upload`。删除通常需要 PyPI Web UI，且不保证立即释放相似名限制。
- 如果全局 `chatgh` 没有某个子命令，先检查 `~/Playground/core/ChatGH` 的源码版，不要绕过 ChatGH 流程。
- `.pypirc`、GitHub token、ChatEnv token 都不能输出内容；日志只记录凭据是否存在和使用的工具路径。
- 新建 ChatArch 仓库后，默认把 local `origin` 设为 HTTPS，并在该仓库自己的 `.git/config` 写入 repo-specific `http.https://github.com/ChatArch/<ProjectName>.git.extraHeader = Authorization: Basic <base64(x-access-token:TOKEN)>`。不要把 token 放进 remote URL；不要打印 raw extraHeader。写完后必须用 `git ls-remote --heads origin main` 和 `git push --dry-run origin main` 验证。
- build/pytest 会产生 `.venv`、`dist`、`.pytest_cache`、`*.egg-info` 等中间产物；commit 前确认 `.gitignore` 生效，必要时清理或保持未跟踪文件不入库。

## 完成汇报模板

完成后汇报：

```text
- GitHub: https://github.com/ChatArch/<ProjectName>
- PyPI: https://pypi.org/project/<ProjectName>/<version>/
- Local source: ~/Playground/core/<ProjectName>
- Tests: python -m pytest -q -> ... passed
- Build: python -m build -> wheel + sdist
- Twine check: PASSED
- Install check: uv pip install '<ProjectName>==<version>' + <cli-command> --help OK
```
