---
name: python-package-release-with-chattool-pypi
description: ChatArch Python 包从仓库创建、ChatTool PyPI/ChatStyle 模板初始化、提交推送到 PyPI 发版的完整流程。
version: 0.1.4
tags:
  - ChatArch
  - Python
  - PyPI
  - ChatTool
  - ChatStyle
  - ChatGH
reference:
  - package-development: "主题索引；用于定位 ChatArch package development 相关 skill"
  - chatarch-cli-package-conventions: "ChatArch CLI/package 模板、ChatEnv、ChatStyle、dependency bounds 等约定"
  - chatgh-repo-token-setup: "新仓库或首次 checkout 后配置 HTTPS repo-local git token"
  - chatgh-pr-and-ci-workflow: "PR、CI、Actions 与 review/merge 前状态检查"
  - python-package-publishing: "PyPI release gates、Trusted Publishing、version continuity 与 post-publish verification"
  - chatpypi-publisher-management: "PyPI project/publisher list 与 Trusted Publisher 配置/验证"

---

# ChatArch Python 包创建与发版流程

## 适用场景

当需要创建一个新的 ChatArch 风格 Python CLI 包，并完整跑通以下流程时使用：

1. 在 GitHub `ChatArch` 组织下创建远程仓库。
2. 用独立 `chatpypi init ... -t chatarch` 初始化包模板。
3. 确认 ChatStyle / ChatEnv 依赖、CLI 入口、README、测试、workflow。
4. 初始化 git、commit、设置 remote、push。
5. 本地测试、`chatpypi build`、`chatpypi check`、tag-driven publish。
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

### 版本连续性硬门槛

对已有 PyPI 项目，版本必须从当前已发布版本连续推进：默认只允许 next patch，例如 `7.0.3 -> 7.0.4`。除非用户明确批准 minor/major bump，否则禁止跳到 `7.1.0`、`7.2.0` 或更高版本。

如果 feature PR/MR 预期合并后就要发版，版本号和 `CHANGELOG.md` 必须在这个 feature PR/MR 中提前准备好，而不是等 feature 合并后再补一个重复的 release PR/MR。标准顺序是：

1. 在 feature 分支进入 PR/MR 前或最终 review 前，查询 PyPI latest、recent releases、本地 tag、远端 tag，计算连续 next patch 版本。
2. 在同一个 feature PR/MR 中更新包内版本号、版本测试和 `CHANGELOG.md`。
3. 在 PR/MR review 阶段完成版本连续性、构建、`twine check`、测试和 CI gate。
4. 合并 feature PR/MR 后，同步本地默认分支。
5. 只在合并后的默认分支 commit 上创建并推送 `vX.Y.Z` tag，触发 publish workflow。

只有当 feature PR/MR 原本没有发版意图、合并后才临时决定要发版时，才允许补一个 release-only PR/MR 来更新版本号和 `CHANGELOG.md`；这不是常规路径。

发布准备或正式发版前必须同时检查三层状态。当前 `chatpypi probe` 可以替代手写 PyPI JSON 脚本做 first-pass 包名/latest metadata 检查；recent releases 列表仍需要 PyPI JSON 脚本或未来的 `chatpypi versions/status` 命令：

```bash
chatpypi probe <ProjectName> || true
git fetch --tags origin
git tag --list 'v*' --sort=-v:refname | head -20
git ls-remote --tags origin 'v*' | tail -20
```

如必须列出 recent releases，暂时保留脚本：

```bash
python3 - <<'PY'
import json, urllib.error, urllib.request
name = '<ProjectName>'
try:
    with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/json', timeout=20) as r:
        data = json.load(r)
    print('pypi_latest', data['info']['version'])
    print('pypi_releases', sorted(data.get('releases', {}))[-10:])
except urllib.error.HTTPError as exc:
    print('pypi_http', exc.code)
PY
```

如果 `[project].version` / `src/<module>/__init__.py` / `tests/test_version.py` 已经写成非连续版本，必须先停止发版，开修正 PR/MR 把版本改回连续目标版本；不得继续 tag 或 upload。

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

创建/确认仓库后，必须立即为当前本地仓库配置 repo-local HTTPS token。ChatArch / Chat-series 仓库不应为了绕过 HTTPS 鉴权问题改用 SSH clone/push；`chatgh set-token` 是仓库创建的伴生动作。详细流程使用 ChatArch skill `chatgh-repo-token-setup`。

最小形状：

```bash
cd ~/Playground/core/<ProjectName>
git remote add origin https://github.com/ChatArch/<ProjectName>.git 2>/dev/null || \
  git remote set-url origin https://github.com/ChatArch/<ProjectName>.git
git remote set-url --push origin https://github.com/ChatArch/<ProjectName>.git

# Prefer the password-style interactive prompt; avoid putting a real PAT in shell history or process listings.
chatgh set-token
chatgh repo-perms --repo ChatArch/<ProjectName> --json-output
git push --dry-run origin main
```

Never print the token, `.git/config` extraHeader, or decoded Authorization value. Verify by `repo-perms` capability output and HTTPS push dry-run only.

新建仓库后，尽量立即尝试给默认分支预置 branch protection。默认保护规则只做安全底线，不默认要求 code review：

- require pull request before merging / 禁止直接 push 到默认分支；
- required approving review count = `0`；
- enforce admins = `true`；
- 禁止 force push；
- 禁止 deletion。

如果 private 仓库因为 GitHub plan/visibility 限制无法设置 protection，只记录 blocker，不要自动改 public。只有用户明确批准某个仓库 public 时，才切到 `public-repo-and-default-branch-protection` skill 去执行 public + protection。

如果当前 ChatGH 尚未提供可复用的 branch-protection apply 命令，不要把官方 `gh api` 当作 ChatArch 运行/ops fallback。应先使用 `public-repo-and-default-branch-protection` skill 检查现有 ChatGH 能力；若确实缺少 apply capability，先补 ChatGH 可复用命令或把该步骤记录为 blocker。官方 `gh` 只能作为接口/manual reference。

如果 GitHub 对 private 仓库返回以下限制，则记录 blocker，等仓库 public 或账号/组织 plan 支持 private branch protection 后再补：

```text
Upgrade to GitHub Pro or make this repository public to enable this feature.
```

### 3. 用 ChatPyPI / ChatStyle 模板初始化

推荐直接使用最终品牌名作为模板 name，避免生成错误的 kebab-case 分发名：

```bash
cd ~/Playground
chatpypi init <ProjectName> \
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

Shortcut form is also available when the first argument is not a known subcommand:

```bash
chatpypi <ProjectName> -t chatarch --project-dir ~/Playground/core/<ProjectName> -I
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
- 依赖 `chatstyle>=0.1.0,<0.2.0` 与 `chatenv>=0.2.0,<0.3.0`
- 默认 publish workflow 不应包含 `environment: pypi`，除非 PyPI Trusted Publisher 明确配置了同名 environment。

ChatArch 模板的 CLI skeleton 细节归 `chatarch-cli-package-conventions` 管；这里不重复展开模板内部命令形态。初始化后按 conventions 检查真实 package command skeleton、ChatEnv/ChatStyle wiring、tests、build/check、publish workflow，不把示例/demo 命令当作发布验收点。

### 4. 本地验证

使用项目本地 venv，不全局安装：

```bash
cd ~/Playground/core/<ProjectName>
uv venv .venv
. .venv/bin/activate
uv pip install -e '.[dev]'
python -m pytest -q
rm -rf dist build *.egg-info src/*.egg-info
chatpypi build --project-dir .
chatpypi check --project-dir .
<cli-command> --help
```

`chatpypi build/check` wrap `python -m build` and `twine check`; the active venv still needs those tools installed, usually through `.[dev]`.

期望：

- pytest 全部通过。
- `chatpypi build` 生成 sdist 和 wheel。
- `chatpypi check` 对所有 dist 文件 `PASSED`。
- CLI help 正常显示。

### 5. 初始化 git、commit、push

```bash
cd ~/Playground/core/<ProjectName>
git init -b main
git add .
git commit -m 'Initial <ProjectName> package scaffold'
git remote add origin https://github.com/ChatArch/<ProjectName>.git

# Repo-local HTTPS token config: use ChatGH's safe setup path.
# `chatgh set-token` uses password-style interactive input when needed;
# do not place real PATs in shell history or write auth headers by hand.
chatgh set-token
chatgh repo-perms --repo ChatArch/<ProjectName> --json-output

git ls-remote --heads origin main || true
git push --dry-run -u origin main
git push -u origin main
git ls-remote --heads origin main
```

Use the HTTPS remote plus `chatgh set-token` repo-local credential setup by default. Avoid embedding tokens in `remote.origin.url`, avoid command-line PAT arguments, and never print raw `.git/config` auth header values.

### 6. Tag-driven PyPI 发布与回读验证

发布前再次打印安全 metadata，但不要打印凭据。常规发布必须走 PR -> merge -> 默认分支 tag -> GitHub Actions publish；不要用本地 Twine 当正常发版路径：

```bash
cd ~/Playground/core/<ProjectName>
. .venv/bin/activate
python -m pytest -q
rm -rf dist build *.egg-info src/*.egg-info
chatpypi build --project-dir .
chatpypi check --project-dir .

git checkout main
git pull --ff-only origin main
git tag -a v<X.Y.Z> -m 'Release <ProjectName> <X.Y.Z>'
git push origin v<X.Y.Z>
```

发布后回读：

```bash
chatpypi probe <ProjectName> || true
python3 - <<'PY'
import json, urllib.request
for name in ['<ProjectName>', '<normalized-name>']:
    with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/json', timeout=20) as r:
        data=json.load(r)
    print(data['info']['name'], data['info']['version'], data['info']['project_url'])
    print('releases:', sorted(data.get('releases', {}))[-5:])
PY
```

`chatpypi probe` gives a fast latest-version/project metadata check. Keep the JSON snippet only when you need recent release lists until ChatPyPI grows a dedicated `versions/status` command.
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
- 使用命令：`chatpypi init ChatNPM -t chatarch --project-dir ~/Playground/core/ChatNPM ...`。
- 生成结果：`project.name = "ChatNPM"`，module 为 `chatnpm`，CLI 为 `chatnpm`。
- GitHub 仓库通过 ChatGH 源码版创建：`ChatArch/ChatNPM`，初始为 private。
- local commit：`a6434a7 Initial ChatNPM package scaffold`。
- remote：`https://github.com/ChatArch/ChatNPM.git`，并通过 `chatgh set-token` 配置 repo-local HTTPS token。
- PyPI：`ChatNPM==0.1.0` 上传成功，项目页 `https://pypi.org/project/ChatNPM/0.1.0/`。
- 隔离安装验证：`uv pip install 'ChatNPM==0.1.0'` 后 `chatnpm --help` 正常。
- 后续只有在用户明确批准后，才将 `ChatArch/ChatNPM` 改为 public 并设置默认分支保护；这不是 Python/PyPI 发布流程的默认步骤。

## 结束同步硬门槛

不论是 PR/MR 合并、版本准备 PR 合并，还是正式发版完成，结束前都必须把本地分支同步到远端最终状态，不能停在旧 feature/release 分支或未同步的本地 head。

最小收尾命令：

```bash
git fetch --prune --tags origin
git checkout main 2>/dev/null || git checkout master
git pull --ff-only origin $(git branch --show-current)
git status --short --branch
git log -1 --oneline --decorate
```

如果当前工作还涉及仍然 open 的后续 PR/MR，必须明确说明本地当前停在哪个分支、该分支是否已推送、base 是否已更新、CI 是否到终态；不能把“远端已合并/已发布”和“本地已同步”混为一谈。

## 常见坑

- 不要把品牌名 `ChatNPM` 自动改成 `chat-npm`；PyPI 会规范化显示文件名，但 `[project].name` 应使用确认过的 exact name。
- PyPI 的 normalized name 与显示名可能不同：`ChatNPM` 会归一到 `chatnpm`。
- 删除错误 PyPI 项目不能靠 `twine`；`twine` 只有 `check/register/upload`。删除通常需要 PyPI Web UI，且不保证立即释放相似名限制。
- 如果全局 `chatgh` 没有某个子命令，先检查 `~/Playground/core/ChatGH` 的源码版，不要绕过 ChatGH 流程。
- `.pypirc`、GitHub token、ChatEnv token 都不能输出内容；日志只记录凭据是否存在和使用的工具路径。
- 新建 ChatArch 仓库后，默认把 local `origin` 设为 HTTPS，并通过 `chatgh set-token` 配置 repo-local git transport credential。不要手写或展示 raw auth header；不要把 token 放进 remote URL；写完后必须用 `chatgh repo-perms`、`git ls-remote --heads origin main` 和 `git push --dry-run origin main` 验证。
- Trusted Publishing 的 `environment` 必须与 PyPI Publisher 配置完全一致。不要在 publish workflow 中默认写 `environment: pypi`；只有确认 PyPI Trusted Publisher 的 claim 包含 `environment:pypi` 时才加。若 PyPI 配置是无 environment 的 publisher，workflow 必须移除 `environment`，否则会失败为 `invalid-publisher`，claim 类似 `repo:OWNER/REPO:environment:pypi`。
- 正式发版必须走标准链路：PR 绿灯 -> merge 到默认分支 -> 在默认分支 merge commit 上打 `vX.Y.Z` tag -> GitHub Actions publish -> PyPI JSON/simple index -> clean install。不要为了省事用本地 Twine key 代替 tag workflow；本地 Twine 只能作为已明确记录的异常救援，并且之后必须修复标准 workflow。
- build/pytest 会产生 `.venv`、`dist`、`.pytest_cache`、`*.egg-info` 等中间产物；commit 前确认 `.gitignore` 生效，必要时清理或保持未跟踪文件不入库。

## 完成汇报模板

完成后汇报：

```text
- GitHub: https://github.com/ChatArch/<ProjectName>
- PyPI: https://pypi.org/project/<ProjectName>/<version>/
- Local source: ~/Playground/core/<ProjectName>
- Tests: python -m pytest -q -> ... passed
- Build: `chatpypi build --project-dir .` -> wheel + sdist
- Check: `chatpypi check --project-dir .` -> PASSED
- Install check: uv pip install '<ProjectName>==<version>' + <cli-command> --help OK
```
