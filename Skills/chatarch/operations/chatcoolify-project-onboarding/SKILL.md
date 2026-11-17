---
name: chatcoolify-project-onboarding
description: "Use for ChatCoolify client setup and app publishing."
version: 0.3.0
---

# ChatCoolify 项目接入

将新项目接入已有的自建托管平台，并交付可复用的访问入口与发布方法。普通接入使用 `coolify platform`；**Coolify 是原生构建与运行引擎，ChatCoolify 是其上的 Python API／CLI、项目与授权控制面**。不要给其他工具站追加一套临时静态托管器。

## 何时使用

- 用户要给新机器配置 ChatCoolify 客户端，或让这台机器以后能上架／更新应用。
- 用户要上传本地构建目录、开预览、上线网站、回退版本或处理项目访问权限。
- 用户要“给新机器一段提示词”时，使用 [新机器应用上架提示词](templates/new-machine-publish-prompt.md)，填入本次私有上下文，不把实际入口和账号写回共享文件。

## 新机器：接入一次，后续直接上架

新机器是客户端和本地构建端；镜像构建、托管运行仍由已有平台完成。复用当前机器既有 ChatArch Python 环境，安装／升级 ChatCoolify（此流程需要0.2.5或更新版本）和 ChatEnv（具名test命令需要0.2.15或更新版本），再回读 `coolify --version`、`coolify --tree`、`chatenv test --help` 和 `coolify platform --help`。客户端不需要另外安装 Coolify、Docker、Nginx、服务端 typed profile 或部署 SSH key。

按用户当前目标选择终点，不把所有请求都收缩成只读配置：

| 当前目标 | 实际完成标准 |
| --- | --- |
| 配置客户端，尚未给应用 | 登录、`whoami`、项目列表均真实通过，留下可复制上架方法；不随意发布演示站 |
| 只做预览 | 复用／登记项目、本地构建、上传、预览验证，停止在预览 |
| 上架／上线／更新正式站 | 预览验证后继续发布同一 release，核对正式运行状态并交付真实 URL，不追加例行二次确认 |
| 已有项目换一台机器操作 | 本机独立登录后复用同一平台项目 ID、域名、访问方式和后端数据，不重复创建项目 |

先配置同名 ChatEnv profile 的平台地址、账号和敏感密码，再查询身份和项目。有效会话直接复用；缓存缺失或会话检查返回401时，SDK从该profile登录一次后再执行原操作，不重放结果未知的写请求。`403` 先核对项目授权，不反复重登或自行新增管理员。ChatEnv管理凭据，TokenStore仅缓存签发的会话；不要从其他机器复制token、Cookie、密码文件或原生Team token。浏览器和CLI会话独立，opaque session会过期，不是另一套账号或永久API key。

## 先定位现有平台

- 从当前 workspace 的本地 skill、MEMORY 或目标 project 交付记录取得 `<platform-origin>`、`<profile>`、账号开通方式及现有项目 ID。`<platform-origin>` 是包含 `https://` 的完整 origin，不含业务路径、query 或 fragment。共享文件只使用占位符，不填写真实域名、账号、机器路径或凭据。
- 检查 `coolify --version`、`coolify --tree`、`coolify platform --help`。需要安装时使用该环境既有包管理方式，确认来源和 `platform` 子命令；不要把源码／候选版本号当成 PyPI 已发行版本。
- 在当前项目记录稳定需求：构建目录、是否私人、是否已有平台项目、是否需要独立后端及持久数据。优先复用已登记项目；CI 可调用同一接口，但本地 CLI 不要求先建设 CI。
- 此接入流程不负责重建 Coolify、修改共享 DNS／证书／tunnel，或替换平台的账号系统。平台缺失时先报告缺少的部署前置，不能把上线一个样例页面当成平台已经建成。

## 登录与账号边界

```sh
chatenv new <profile> -t coolify-platform -i
chatenv test <profile> -t coolify-platform
coolify platform --profile <profile> login
coolify platform --profile <profile> whoami
coolify platform --profile <profile> projects list
coolify platform --profile <profile> limits
```

ChatEnv字段为 `CHATCOOLIFY_PLATFORM_URL`、`CHATCOOLIFY_PLATFORM_USERNAME`、敏感的 `CHATCOOLIFY_PLATFORM_PASSWORD`，由同一 `coolify-platform` 具名profile管理；不用另设一套鉴权。交互输入隐藏密码，成功登录保留该profile的凭据，TokenStore只存会话。非交互仍可用 `--password-env <environment-variable-name>` 指定变量名，通过现有私有凭据通道注入，不把秘密写进命令、skill、归档或报告。不向普通用户分发原生Coolify Team token。

缓存必须绑定签发平台origin，配置账号时核对实际会话身份；CLI覆盖到另一origin或账号时提供新密码，不自动复用旧profile的密码。保持原账号，不为接入客户端重置密码或bootstrap另一套owner。旧URL+token-only profile仍可使用，需自动续签时补齐ChatEnv账号字段。

平台采用管理员人工开通可信账号，公开注册关闭。项目 owner 授予 viewer／deployer；账号 admin 不因此获得他人私有项目权限。新账号、协作授权和停用命令见 [账号与独立服务](references/accounts-and-services.md)。

网页登录和 CLI 登录使用同一批平台账号，但各自建立会话。私人应用经平台登录及一次性回调取得自己的 reader 会话；不需要为了每个前端再造登录页。ChatLogin 是嵌入身份库；此平台的登录不表示所有独立后端或整个组织已共享全局 SSO。当前 reader 协议适用于同一站点下的 HTTPS origins，跨站自定义域名需另行验证。

## 前端：本地构建到预览

先读应用实际构建说明、依赖锁文件和现有脚本，在当前机器运行正确的构建命令；不要假定所有项目都用同一条 `npm run build`。先列出现有项目，只有新应用才 create；已登记应用复用原 ID。

只上传已经构建完成、含根级 `index.html` 的目录，例如 `./dist`。源代码、`.env`、密钥、数据库和依赖目录不属于静态产物。新版ZIP默认上限1 GiB，解包大小与归档条目数默认不限；先用 `coolify platform limits` 读取服务端有效策略，不沿用旧版8 MiB/32 MiB/2000项常量。不额外添加业务体积、条目或发布审批门槛；保留软链接、越界、特殊文件与凭据文件等安全拒绝，隐藏文件不上传。上传自定义Dockerfile不是运行后端的入口。

operator通过既有 `coolify-platform-server` ChatEnv配置 `CHATCOOLIFY_MAX_UPLOAD_BYTES`（默认1073741824）、`CHATCOOLIFY_MAX_EXPANDED_BYTES`（默认0）、`CHATCOOLIFY_MAX_ARTIFACT_FILES`（默认0），0表示不限；原生受管环境/服务重新加载后读回策略。增大尺寸时同时确认各层反代不会先拦截，不修改其他站点的共享限制。客户端只读已认证的 `/api/platform/v1/limits`，不读取server私有profile；仅旧服务器明确404时兼容旧策略，鉴权或网络错误不能当成旧版。

```sh
# 已有项目时复用其 ID；仅新项目执行 create。
coolify platform --profile <profile> projects create <site-slug> --visibility <visibility>
coolify platform --profile <profile> upload PROJECT_ID ./dist
coolify platform --profile <profile> preview PROJECT_ID RELEASE_ID --request-key <preview-request-key>
coolify platform --profile <profile> status PROJECT_ID
coolify platform --profile <profile> logs PROJECT_ID DEPLOYMENT_ID
```

`<visibility>` 必须替换为 `public` 或 `private`。平台新项目默认 public；未指定时明确说明默认行为，要求私有时显式设置，不静默改变已有私有项目。preview 与 publish 分别记录各自 request key；同次请求重试复用原 key，更换 release／环境／动作时生成新 key。

`PROJECT_ID` 是 create／list 返回的平台项目 `id`，`RELEASE_ID` 是 upload 返回的 `id`，`DEPLOYMENT_ID` 是 preview／publish 返回的 `id`；不要替换成原生 UUID。命令返回 JSON，默认上传只创建不可变 release；preview 和 production 是两个原生应用，不把“已上传”说成“已发布”。

在预览 URL 核对主要功能和必要资源。私人项目用授权会话读取，并检查匿名访问实际应用域名／资源被拒；公开前端只开放读取，不开放发布或管理。若有后端，验证同源服务路由和持久数据；按用户实际需要核对移动端布局，不为普通内容更新重复整个平台的多用户验收。

## 明确发布、状态与回退

本次请求包含上线授权且预览符合要求时继续发布，不另加每次部署都要询问的审批步骤。只要求预览时停在预览。

```sh
coolify platform --profile <profile> publish PROJECT_ID RELEASE_ID --request-key <publish-request-key>
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

明确标注当前阶段是“客户端就绪／已上传／已预览／已上线／被阻塞”。完整的新机器执行交接见 [可复制提示词](templates/new-machine-publish-prompt.md)，账号开通和原生后端关联仅在需要时读取 [账号与独立服务](references/accounts-and-services.md)。
