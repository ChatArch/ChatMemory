---
name: chatcoolify-project-onboarding
description: "Use an existing ChatCoolify self-hosted platform to log in, register frontend projects, upload local build artifacts, preview, publish, roll back, and connect supported independent backend services with project permissions."
---

# ChatCoolify 项目接入

将新项目接入已有的自建托管平台，并交付可复用的访问入口与发布方法。普通接入使用 `coolify platform`；**Coolify 是原生构建与运行引擎，ChatCoolify 是其上的 Python API／CLI、项目与授权控制面**。不要给其他工具站追加一套临时静态托管器。

## 先定位现有平台

- 从当前 workspace 的本地 skill、MEMORY 或目标 project 交付记录取得 `<platform-origin>`、`<profile>`、账号开通方式及现有项目 ID。`<platform-origin>` 是包含 `https://` 的完整 origin，不含业务路径、query 或 fragment。共享文件只使用占位符，不填写真实域名、账号、机器路径或凭据。
- 检查 `coolify --version`、`coolify platform --help`。需要安装时使用该环境既有包管理方式，确认来源和 `platform` 子命令；不要把源码／候选版本号当成 PyPI 已发行版本。
- 在当前项目记录稳定需求：构建目录、是否私人、是否已有平台项目、是否需要独立后端及持久数据。优先复用已登记项目；CI 可调用同一接口，但本地 CLI 不要求先建设 CI。
- 此接入流程不负责重建 Coolify、修改共享 DNS／证书／tunnel，或替换平台的账号系统。平台缺失时先报告缺少的部署前置，不能把上线一个样例页面当成平台已经建成。

## 登录与账号边界

```sh
coolify platform --profile <profile> login \
  --url '<platform-origin>' --username <account>
coolify platform --profile <profile> whoami
coolify platform --profile <profile> projects list
```

交互输入隐藏密码。非交互时用 `--password-env <environment-variable-name>`，该参数是变量名，不是密码值；通过现有私有凭据通道注入，不把秘密写进命令、skill、归档或报告。profile 保存 endpoint 与私有 opaque session，不向普通用户分发原生 Coolify Team token。

平台采用管理员人工开通可信账号，公开注册关闭。项目 owner 授予 viewer／deployer；账号 admin 不因此获得他人私有项目权限。新账号、协作授权和停用命令见 [账号与独立服务](references/accounts-and-services.md)。

网页登录和 CLI 登录使用同一批平台账号，但各自建立会话。私人应用经平台登录及一次性回调取得自己的 reader 会话；不需要为了每个前端再造登录页。ChatLogin 是嵌入身份库；此平台的登录不表示所有独立后端或整个组织已共享全局 SSO。当前 reader 协议适用于同一站点下的 HTTPS origins，跨站自定义域名需另行验证。

## 前端：本地构建到预览

只上传已经构建完成、含根级 `index.html` 的目录，例如 `./dist`。源代码、`.env`、密钥、数据库和依赖目录不属于静态产物。当前归档上限为 2,000 文件、8 MiB ZIP、32 MiB 解包内容；拒绝软链接、越界与凭据文件，隐藏文件不会上传。上传自定义 Dockerfile 不是运行后端的入口。

```sh
# 已有项目时复用其 ID；仅新项目执行 create。
coolify platform --profile <profile> projects create <site-slug> --visibility private
coolify platform --profile <profile> upload PROJECT_ID ./dist
coolify platform --profile <profile> preview PROJECT_ID RELEASE_ID
coolify platform --profile <profile> status PROJECT_ID
coolify platform --profile <profile> logs PROJECT_ID DEPLOYMENT_ID
```

`PROJECT_ID` 是 create／list 返回的平台项目 `id`，`RELEASE_ID` 是 upload 返回的 `id`，`DEPLOYMENT_ID` 是 preview／publish 返回的 `id`；不要替换成原生 UUID。命令返回 JSON，默认上传只创建不可变 release；preview 和 production 是两个原生应用，不把“已上传”说成“已发布”。

在预览 URL 核对主要功能和必要资源。私人项目用授权会话读取，并检查匿名访问实际应用域名／资源被拒；公开前端只开放读取，不开放发布或管理。若有后端，验证同源服务路由和持久数据；按用户实际需要核对移动端布局，不为普通内容更新重复整个平台的多用户验收。

## 明确发布、状态与回退

本次请求包含上线授权且预览符合要求时继续发布，不另加每次部署都要询问的审批步骤。只要求预览时停在预览。

```sh
coolify platform --profile <profile> publish PROJECT_ID RELEASE_ID
coolify platform --profile <profile> status PROJECT_ID
coolify platform --profile <profile> logs PROJECT_ID DEPLOYMENT_ID
coolify platform --profile <profile> releases PROJECT_ID
# 回退选择同项目曾通过验证的 production release。
coolify platform --profile <profile> rollback PROJECT_ID OLD_SUCCESSFUL_RELEASE_ID
```

派发返回不是完成。等待有限时间并核对目标部署 `state=finished`、`runtime_verified=true`、当前目标 `runtime_active=true`，运行 artifact SHA 与 release 一致，再读取实际生产 URL。失败构建／健康检查应保留旧生产，报告失败和仍在运行的版本。已验证的历史部署不要求仍 active；从未验证的 `superseded_unverified` 不能充当回退来源。

请求超时或派发结果不明时先查 status／logs；需要重试同一次部署时复用其 `--request-key`，避免换新 key 盲目再排队。生成的原生构建 commit 与本地源码 commit 是两种来源，分别记录。源代码 PR 合并／正式包发行与网站发布是不同动作，不凭本 skill 扩张授权。

## Python 复用

复用 CLI 已登录的同名 profile，不在代码里复制密码或 Team token：

```python
from chatcoolify import PlatformClient

client = PlatformClient.from_profile("<profile>")
project = client.create_project("<site-slug>", visibility="private")
release = client.upload(project["id"], "./dist")
preview = client.deploy(project["id"], release["id"], environment="preview")
# 预览验证且本次已授权发布时：
# production = client.deploy(project["id"], release["id"], environment="production")
```

## 独立后端及交付

需要 Python／Go／Node 等后端时保留原生 Coolify Application／Service 的部署能力，按项目部署独立进程、环境变量和持久卷。当前前端 upload 不是通用后端打包命令；已交付的关联 adapter 为 ChatComment。其原生资源准备、登记、JS 嵌入与认证边界见 [账号与独立服务](references/accounts-and-services.md)。其他服务先定义并实现 adapter，不能把任意 URL 填成已支持的网关。

交付当前阅读 URL、预览 URL、控制台入口、profile／项目／release／deployment ID、已验证范围和最短更新命令。运行状态、真实域名与具体版本保存在私有 project 记录；共享 skill 保留稳定流程。静态回退不恢复独立服务数据库；需要迁移时先做一致备份和新写入对账，再停旧入口。
