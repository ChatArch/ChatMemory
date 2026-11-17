# 新机器应用上架提示词

将下文交给目标机器的 Agent。真实平台入口、账号和应用位置从用户本次输入或该机器的私有服务登记取得，不写回共享 skill。

```text
请使用 $chatcoolify-project-onboarding，将当前机器接入已有 ChatCoolify 平台，方便从这里上架和更新应用。

本次目标：<仅配置客户端 / 预览应用 / 上架应用 / 更新已有应用>
应用位置：<项目目录；尚未指定则先完成客户端接入>
平台 origin：<用户提供或从本机私有服务清单核实的完整 HTTPS origin>
profile：<独立名称，例如 work>
访问方式：<沿用已有项目设置 / 新项目 public / 新项目 private>

按目标完成实际工作：
1. 确认当前机器、工作区规范及现有 ChatArch Python 环境，复用既有环境，安装或升级 ChatCoolify>=0.2.5与ChatEnv>=0.2.15。
   新机器只是构建/上传端；不用另外部署 Coolify、Docker、Nginx 或中央账号系统。
   先运行 coolify --version、coolify --tree、chatenv test --help，读取 platform 相关 --help，以真实命令面为准。
2. 解析已有平台 origin、profile、账号及必要权限，不猜地址和凭据。
   使用coolify-platform具名ChatEnv profile管理CHATCOOLIFY_PLATFORM_URL、CHATCOOLIFY_PLATFORM_USERNAME与敏感CHATCOOLIFY_PLATFORM_PASSWORD；缺配置时安全录入并执行chatenv test。
   再检查同一profile的whoami、projects list、limits。TokenStore只缓存会话；SDK在缓存缺失/失效时从该profile登录一次，不盲目重放写请求。
   密码用隐藏交互或现有安全凭据通道；自动化用--password-env指定变量名，不传密码值。覆盖origin/账号时不复用旧密码，不能使用其他账号的缓存会话。
   不复制其他机器的token、Cookie、密码文件、SSH key或原生Team token，不新增另一套账号鉴权。
3. 区分权限：viewer能阅读；deployer能预览/发布/回退；owner能设置项目权限和关联服务。
   403先核对账号及该项目授权；admin角色不等于所有项目的owner。缺权限时清楚说明所需授权，不自行建管理员。
4. 若本次只要求客户端配置，或尚无具体应用，完成真实登录和项目列表验收后停止；不发布一个临时演示站冒充完成。
   若本次已指定应用并要求上架/上线，继续下面流程，不默认停在只读，也不在预览成功后再追加一次例行确认。
5. 先查项目列表，已有项目复用平台PROJECT_ID；换机器不等于新建项目。
   只有明确的新应用才创建项目。新项目未指定时说明平台默认public；要求私有时显式设置private；不改变已有项目访问方式。
6. 阅读应用自己的构建说明、依赖锁文件和实际构建命令，在当前机器生成前端产物。
   上传目录必须含根级index.html；不要上传源码、环境文件、密钥、数据库、node_modules或软链接。
   若是Python/Go/Node后端或需要持久数据库，先走skill的原生资源/独立后端流程，不把后端源码当静态目录上传。
   读取有效上传策略；新版默认ZIP1GiB、解包和条目数0不限，operator可经服务端ChatEnv调整。不要照旧版常量添加业务限制，也不要跳过路径/凭据/特殊文件安全检查。
7. 上传后读取真实RELEASE_ID；为本次preview记录独立request-key，排队一次并查询对应deployment。
   预览完成后核对state=finished、runtime_verified=true、runtime_active=true，并实际打开预览URL验证页面和资源。
8. 本次明确要求上架/上线/更新正式站时，为publish记录另一个request-key，发布同一个已验证RELEASE_ID。
   等待对应production部署验证通过，并回读真实正式URL；仅预览目标则停在预览，不改生产。
9. 对超时或派发结果未知的请求先查status/logs；需要重试同一次操作时复用原request-key，不换key重复排队。
   失败时保留现有生产和数据，报告实际失败；回退只选同项目曾验证成功的production release。
10. 交付真实正式/预览URL、profile、PROJECT_ID、RELEASE_ID、DEPLOYMENT_ID及最短更新命令。
    明确报告“客户端就绪/已上传/已预览/已上线/被阻塞”的实际阶段，不把queued、截图或HTTP200当成完整发布成功。

常用命令形状，替换占位符后按授权阶段执行：
chatenv new <profile> -t coolify-platform -i
chatenv test <profile> -t coolify-platform
coolify platform --profile <profile> login
coolify platform --profile <profile> whoami
coolify platform --profile <profile> projects list
coolify platform --profile <profile> limits
coolify platform --profile <profile> projects create <site-slug> --visibility <public-or-private>
coolify platform --profile <profile> upload PROJECT_ID <dist-directory>
coolify platform --profile <profile> preview PROJECT_ID RELEASE_ID --request-key <preview-request-key>
coolify platform --profile <profile> status PROJECT_ID
coolify platform --profile <profile> publish PROJECT_ID RELEASE_ID --request-key <publish-request-key>
coolify platform --profile <profile> logs PROJECT_ID DEPLOYMENT_ID
```
