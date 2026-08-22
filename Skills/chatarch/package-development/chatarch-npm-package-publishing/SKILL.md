---
name: chatarch-npm-package-publishing
description: ChatArch npm 包发版流程：npm 组织/scope 管理、包创建、GitHub Actions + npm Trusted Publishing/OIDC 发布、验证回读。
version: 0.1.0
tags:
  - ChatArch
  - npm
  - Node.js
  - OIDC
  - Trusted Publishing
reference:
  - chatarch-cli-package-conventions: "ChatArch CLI/package 模板、scope 命名和 repo 规范"
  - chatgh-repo-token-setup: "新仓库或首次 checkout 后配置 HTTPS repo-local git token"
  - chatgh-pr-and-ci-workflow: "PR、CI、Actions 与 review/merge 前状态检查"
  - public-repo-and-default-branch-protection: "仓库 public 化和默认分支保护"
---

# ChatArch npm 包发版流程

## 适用场景

当需要创建或发布一个 ChatArch 组织下的 npm 包时使用。包括：

1. 纯 npm 包（如 `hermes`、`hermes-agent-feishu-inline-media`）
2. Go CLI 安装器 npm 包装包（如 `@chatarch/cc-connect`，`npm/` 子目录下发布 npm 安装器，实际二进制通过 GitHub Release 分发）
3. 其他 Node.js 服务或 CLI 的 npm 发布

## 前置条件

- ChatArch 已注册 npm 组织（`@chatarch` 或按用户指定的 scope）
- 操作者通过 `npm login` 完成了本地登录，或通过 CI 的 Trusted Publishing 发布
- 包名遵循 npm 规则：小写、scope 前缀、`@org/package` 格式

## ChatArch npm 身份模型

| Python / PyPI | npm |
|---|---|
| PyPI 项目名 | npm 包名（小写，scope 可选） |
| `twine upload` | `npm publish` |
| `chatpypi pkg probe` | `npm view <pkg> --json` |
| PyPI API token / OIDC | npm access token / OIDC Trusted Publishing |
| `pyproject.toml` | `package.json` |
| wheel / sdist | npm tarball |

## 发版流程

### 标准链路（纯 npm 包）

1. 确认 `package.json` 中的 `name`、`version`、`private: false`（或 absent）
2. 确认 npm 登录状态：`npm whoami --registry https://registry.npmjs.org/`
3. 确认组织/scope 成员身份：`npm org ls <org> --json --registry https://registry.npmjs.org/`
4. 检查目标版本是否已存在：`npm view <pkg>@<version> --json || true`
5. 运行 `npm publish --dry-run --access public --registry https://registry.npmjs.org/`
6. 用户确认目标后执行 `npm publish --access public`（或 `--access public --provenance` 开启 OIDC 出处证明）

### 首次发布 bootstrap：先创建 npm package，再配置 Trusted Publishing

npm Trusted Publishing / OIDC 是后续发版的首选，但**首次发布通常不能完全自动**：npm 的 Trusted Publisher 配置入口在 package 设置页里，而 package 设置页只有 package 已存在后才可配置。

推荐顺序：

1. 用本地 npm 登录态或一次性 Granular Access Token 发布第一个公开版本（通常 `0.0.1` placeholder）。
2. 发布前必须 `npm pack --dry-run`，确认 tarball 内容、安全边界和 `--access public`。
3. 发布成功后，在 npm package settings 中配置 Trusted Publisher：
   - Package: `<package>`
   - GitHub owner/org: `<owner>`
   - Repository: `<repo>`
   - Workflow filename: `publish.yml` 或实际 npm publish workflow
4. 从第二个版本起，通过 GitHub Actions OIDC 发布，不再使用本地 token。

如果第一次 tag-driven `npm publish --provenance` 失败，而 package 还不存在，优先判断为 bootstrap gate，不要反复重推 tag。先完成本地/短期 token 首发，再配置 Trusted Publisher，后续 rerun 或新 tag 才会成功。

### GitHub Actions 发布（推荐，用于 package 已存在后的持续发版）

在 CI 中使用 npm Trusted Publishing / OIDC，无需长期 token：

```yaml
name: npm Publish

on:
  workflow_dispatch:
    inputs:
      expected_version:
        description: 'Expected package.json version, e.g. 1.0.0'
        required: true
      publish:
        description: 'Set true to publish; false runs dry-run only'
        required: true
        default: false
        type: boolean

permissions:
  contents: read
  id-token: write

jobs:
  dry-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          registry-url: 'https://registry.npmjs.org/'
      - run: npm ci
      - name: Verify package metadata
        run: |
          node -e "const p=require('./package.json');
          if (p.name !== '@<org>/<package>') throw new Error('unexpected name');
          if (p.version !== '${VERSION}') throw new Error('version mismatch');
          if (p.private) throw new Error('package is private');"
      - name: npm publish dry-run
        run: npm publish --dry-run --access public --registry https://registry.npmjs.org/

  publish:
    needs: dry-run
    if: ${{ inputs.publish }}
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          registry-url: 'https://registry.npmjs.org/'
      - run: npm ci
      - name: Publish with npm trusted publishing
        run: npm publish --access public --provenance --registry https://registry.npmjs.org/
```

### Go CLI 安装器包装包（cc-connect 模式）

当 npm 包不包含实际代码，而是下载 GitHub Release 二进制的安装器时：

1. **GitHub Release 层**：tag 触发 `release.yml`，构建多平台二进制（Go）→ 校验 sha256 和 `--version` → 上传到 GitHub Release
2. **npm 层**：手动 `workflow_dispatch` 触发 `npm-publish.yml`，输入 tag + publish 布尔
   - 先从 `npm/` 子目录读取 `package.json`，校验 name/version/private
   - 再校验 GitHub Release 资产是否齐全（各平台 tarball + checksums）
   - `npm pack --dry-run` 验证
   - `npm publish --access public --provenance`（OIDC）
3. **Git tag 层**：两者共用同一 tag，npm 包版本与 CLI 版本保持一致

关键顺序：**先完成 Git tag 和 GitHub Release 资产，再发布 npm 包**。npm 包只是安装器，依赖 Release 资产存在。

### 2FA / 网页认证门禁

当 `npm publish` 返回 `EOTP` 或弹出网页认证 URL：

1. 保持目标版本不变，不重新打开版本决策
2. 如果返回 `https://www.npmjs.com/auth/cli/***` 这类 URL，重试 `--auth-type=legacy` 获取可操作的认证 URL
3. 用 `chatnpm auth parse-output --format json` 解析 npm 输出中的 `login_url`、`otp_required` 和 `status`，由宿主平台（Hermes/Feishu/Slack 等）把 `login_url` 渲染成卡片按钮并等待用户点击完成；ChatNPM 本身不绑定具体消息平台
4. 打开认证 URL（或通过卡片交给用户完成浏览器/安全密钥认证）
5. 如果 npm 要求 authenticator code，只问用户当前的 6 位 OTP，然后 `npm publish --otp <code>` 或向等待中的 publish 进程提交 OTP
6. 认证后立即验证：`npm view <pkg>@<version> --json`、clean install、bin smoke

## 只读审计（ChatNPM 模式）

当需要审计一个 npm 仓库的发布状态而不实际登录/发布时：

1. 读取 `package.json` 的 name/version/private/publishConfig（只读，只输出 allowlist 字段）
2. 检查 `.github/workflows/*.yml` 中是否有 OIDC/provenance 证据
3. 查询 registry packument：`npm view <pkg> --json`（只读，不写任何配置）
4. 报告：包名、版本、private 状态、registry 发布状态、CI 是否支持 OIDC/provenance
5. 不出输 token、URL 凭证、`publishConfig` 中未 allowlist 的字段

## 发版后验证

1. `npm view <pkg>@<version> --json` 回读包元数据
2. 干净环境安装：`npm install <pkg>@<version> --registry https://registry.npmjs.org/`
3. 对于 CLI 包：运行 `--version` / `--help` 验证
4. 对于包装器包：验证二进制文件存在于预期路径

## 注意事项

- npm 包名一旦发布即为 registry 历史，不可撤销删除（仅 72 小时内可 unpublish）
- `@chatarch` scope 下的包首次发布需要 `--access public`
- 不要将 `NPM_TOKEN` 作为 ChatArch 默认发布方式；优先使用 OIDC Trusted Publishing
- 不要直接修改全局 `~/.npmrc` 作为 token 存储机制
- 区分 npm 包、GitHub Release 和 Git tag 为三层独立状态，分别验证
- `npm login` 适合辅助性手动发布，CI 应使用 OIDC 或 scope 限定的 Granular Access Token
- 只读审计时，HTTP 失败、malformed JSON、非对象 payload 都应返回干净 CLI 错误，不输出 traceback
- URL 等多字段应脱敏：strip userinfo/query/fragment，catch parse 异常