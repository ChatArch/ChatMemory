# 账号、项目协作与独立服务

仅在需要新协作者或独立后端时阅读。下列命令使用已有平台，不能据此自行 bootstrap 第二套 owner 或启动新控制面。

## 邀请制账号与协作

管理员人工开通普通账号，私下交付初始密码；这不是邀请邮件／token 接受流程，也不会自动创建原生 Coolify Team 成员。`--email` 是管理员赋予的可信邮箱，不能从评论昵称或前端输入推导。

下列是按场景选择的命令，不是从开通到停用连续执行的脚本；三种 grant 也只选当前需要的一种。

```sh
# 管理员 profile；密码交互隐藏输入。
coolify platform --profile <admin-profile> users create <account> \
  --display-name '<display-name>' --email '<trusted-email>'
coolify platform --profile <admin-profile> users list

# 以下由项目 owner 操作，USER_ID 来自实际已开通用户。
# 只读协作：
coolify platform --profile <owner-profile> grant PROJECT_ID USER_ID --role viewer
# 允许发布：
coolify platform --profile <owner-profile> grant PROJECT_ID USER_ID --role deployer
# 后续需要撤回授权时：
coolify platform --profile <owner-profile> grant PROJECT_ID USER_ID --role none

# 管理员停用／重新启用账号。
coolify platform --profile <admin-profile> users disable USER_ID
coolify platform --profile <admin-profile> users disable USER_ID --enable
```

viewer 可以阅读，deployer 可以预览／发布／回退；owner 管授权和 service binding。撤权、停用、退出后的 reader 会话应按当前中央权限失效。不要通过共享全局凭据实现协作，或把 admin 角色当成跨项目隐式 owner。`coolify platform --profile <profile> logout` 会撤销该 control 会话及其 reader 子会话；CLI 与浏览器单独登录的会话不是同一个实例。

## 原生后端准备与平台关联

1. 定位该平台项目映射的原生 Coolify project。由有授权的 operator 通过原生 Coolify／既有 `CoolifyClient` 部署独立后端，核实镜像来源、监听端口、健康路径、受控内部网络别名、环境变量和持久卷。不另造所有语言的前端 upload 后端运行器。
2. `services list --candidates` 实时枚举该项目映射的原生 project 各 environment 下的应用，并核实资源归属和单一监听端口；不是维护另一份手工候选登记库。若没有候选，operator 核对应用是否位于正确原生项目、类型／端口是否符合要求。普通用户不能提交任意原生 UUID／upstream URL，不能伪造 candidate ID。
3. project owner 查询候选并登记绑定：

```sh
coolify platform --profile <owner-profile> services list PROJECT_ID --candidates
coolify platform --profile <owner-profile> services register PROJECT_ID comments \
  --registration-id CANDIDATE_REGISTRATION_ID \
  --site-id <comment-site-id> --adapter chatcomment
coolify platform --profile <owner-profile> services list PROJECT_ID
```

`CANDIDATE_REGISTRATION_ID` 是候选输出中的 `registration_id`；资源须属于当前原生项目。`comments` 是所选 binding ID，前端同源前缀为 `/__platform/services/comments`。登记会配置服务端密钥／内部网络别名，并触发已有后端的原生部署；不创建后端资源、初始化评论站点或迁移数据库。登记前核实持久挂载和备份，返回queued后等待服务状态与实际health通过。binding 属于项目，preview／production 共用同一关联，测试写入可能触及相同数据；需要数据隔离时先设计独立后端／站点及其权限。

当前 adapter 只提供 `chatcomment`。其他原生后端仍能独立部署；需要获得平台 reader 的身份与权限时，必须实现明确的服务 adapter／HTTP 合同。一个 SDK 或共用账号数据库不等于跨服务统一登录已经成立。

## ChatComment 初始化与嵌入

使用实际已发布的 ChatComment 包。新建评论站点或沿用已有站点时，核实其 site ID、允许页面、preview／production origins、匿名字段规则和管理设置。已有数据库迁移必须只读预检、在线一致备份、保留软删除和设置；用 `--require-existing-db` 拒绝空／坏库初始化。该保护需包含只读 SQLite header／schema／WAL 预检修复，已验证基线为 ChatComment0.2.1；0.2.0 虽有同名参数仍有空库初始化缺口，不能只检查参数是否存在。后端镜像部署与持久数据分开，静态发布不覆盖数据库。

下列 operator 命令在**实际后端持久数据所属运行环境**执行，显式指定 `<comment-db>`，不能在本机默认空库注册后声称线上已经接入。已有数据先核实路径与有效schema，再备份；`site register` 只用于新站点，已有站点追加 origin 用 `allow-origin` 保留其他设置。origin 占位符均替换为包含 `https://` 的实际完整 origin。

```sh
chatcomment --db '<comment-db>' site list
chatcomment --db '<comment-db>' backup '<new-backup-file>'
# 仅创建新站点，默认private；两个origin必须是实际前端地址。
chatcomment --db '<comment-db>' site register <comment-site-id> \
  --origin '<preview-origin>' --origin '<production-origin>' \
  --page /<stable-page-key>/
# 已有站点迁入新前端域名时：
chatcomment --db '<comment-db>' site allow-origin <comment-site-id> '<new-origin>'
```

平台模式的后端启动参数需与网关合同一致；容器内部监听端口和原生配置保持相同：

```sh
chatcomment --db '<comment-db>' serve --host 0.0.0.0 --port <port> \
  --gateway-key-env CHATCOMMENT_GATEWAY_KEY \
  --session-endpoint /__platform/session --reauth-endpoint /__platform/reauth \
  --return-path / --require-existing-db
```

网关共享 key 只在平台和后端的私有服务配置中保管，不能写进静态 JS、镜像构建参数或共享文档。平台从当前真实 reader 生成受限上下文；后端核验签名、TTL、audience、method/path/query/body、站点与权限。除 health 外，原始后端域名的 widget、API 和管理入口也必须拒绝未签名访问。不能靠隐藏域名保护私人评论。

在前端加入稳定容器，再在**有效平台会话确认后**加载同源 widget。以下示例的 site/page 必须换成已配置的值，绑定名必须与登记一致：

```html
<div id="comments"></div>
<script>
(async () => {
  const response = await fetch('/__platform/session', {credentials: 'same-origin'});
  if (!response.ok || !(await response.json()).authenticated) return;
  const prefix = '/__platform/services/comments';
  const script = document.createElement('script');
  script.src = prefix + '/widget.js';
  Object.assign(script.dataset, {
    chatcomment: '', target: '#comments', api: prefix,
    site: '<comment-site-id>', page: '/<stable-page-key>/',
    csrfEndpoint: '/__platform/session'
  });
  document.getElementById('comments').append(script);
})().catch(() => { /* Keep the host page readable if comments are unavailable. */ });
</script>
```

采用外部脚本时保持等价行为并遵守宿主 CSP；不要为嵌入而放开全站 CSP。`page` 是评论归档的稳定键，不一定等于站点现在的部署根路径；改键前先核实已有留言归属。公开前端的匿名评论需要明确的 guest policy／adapter 支持，不能由上述 authenticated 示例推断支持；私人页面上的空署名留言仍来自获准登录会话。

管理入口机制：只有真正已登录 owner 填对可信邮箱时出现单个齿轮；邮箱匹配只控制入口可见性，管理仍需邮箱＋密码再认证。原密码验证留在平台，管理授权绑定当前 subject/session/project/site 并有期限。预期邮箱不得下发到 JS／公开配置，不能靠邮箱、昵称或隐藏按钮授予权限。

用本次授权范围内的真实留言验证提交→刷新／另一会话读回；核对未登录、非 owner、错误密码、缺 CSRF、异源及原始后端绕过被拒。涉及重部署／迁移时确认换容器后数据与设置仍保留，新增留言不被旧快照覆盖。一次普通页面更新无须重复写入验收留言或重跑整个平台安全矩阵。
