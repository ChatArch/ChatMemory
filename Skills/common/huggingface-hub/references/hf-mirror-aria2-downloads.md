# HF-Mirror、aria2 与下载边界

## 真实命令面

使用发布版 `chathfd --tree`、`chathfd download --help` 和 `chathfd setup --help`；不要从旧 shell 封装猜新参数。当前下载入口是 `download REPO_ID`，数据集用 `--repo-type dataset`；没有 `-d`、`-x`、`--tool wget` 或用户名/Token 参数。查看旧工具时应给旧接口和当前接口各自的实际树，并标明缺失能力，不生成兼容参数的假示例。

## 端点选择

```bash
HF_ENDPOINT=https://hf-mirror.com chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
chathfd download Qwen/Qwen3.8-Flash-Next --endpoint https://huggingface.co --include config.json --dry-run
```

兼容端点必须是无凭据、无路径/查询/片段的 HTTPS origin。默认镜像与原站的网络路径要分别验证，元数据成功不证明 CDN 重定向均可达。复用执行主机原有获授权代理，只在子进程中配置且不打印认证 URL。

ModelScope 使用独立仓库身份和 SDK；不要向 `HF_ENDPOINT` 填入其网站地址来伪装兼容。认证仓库也不应把 Token 静默送给第三方镜像。

## 下载根目录与ChatEnv

ChatHFD0.1.6起，`CHATHFD_DOWNLOAD_ROOT`默认`.`，每次调用按当前目录解析；模型和数据集均为`<root>/<repo_id>`，不再自动加models/datasets层。优先级为精确`--local-dir`/Python`local_dir` > 进程变量 > ChatEnv活动profile > 当前目录。显式最终目录不追加repo ID；空进程变量显式选当前目录，不读取低优先级profile。升级不迁移旧文件。

同一个已安装ChatHFD的Python环境中，用`chatenv set CHATHFD_DOWNLOAD_ROOT=<root> -I`手动配置，`chatenv cat -t chathfd`确认默认/字段值，`chatenv list -t chathfd`列已有profiles，`chatenv test -t chathfd -I`做只读目录验证。空home的list只会报告没有profiles，并不列schema；不要把此输出误判为provider缺失。指定profile的test必须使用dispatcher已经加载的field.value，不重新读取active/process。下载普通调用则应按调用时环境重新解析，不能复用上一次命名profile测试留下的类值。

共享根目录必须按执行机器的挂载视角选择；服务端实体目录与客户端NFS挂载目录不能直接互换。一个通用根变量不按仓库类型切换两个导出；模型/数据集分流用活动profile、单次进程变量或精确目录。未经授权不修改真实配置、挂载或共享目录。

## 大模型持续下载

- 对明确授权的完整权重，先枚举GGUF量化档和目标版本，避免把仓库误当单一权重；按选择固定commit，模型进标准根目录加完整repo ID，日志/manifest留任务目录。
- 长下载使用单一可续跑托管进程、受限仓库/文件/连接并发、逐项日志和原子状态清单。对话交接后保持任务，但running/queued不等于完成；收尾逐项核对请求ID、文件数量、大小与无侧车状态，不能用启动成功或一片增长代替全量完成。
- 多连接写入的稀疏权重文件可能提前呈现很大逻辑长度，不要把st_size当传输量。分配块数只能标为近似，进度以下载器和完成文件为准；可轻量验证GGUF/safetensors头与index分片，不加载模型，也不把尺寸/头验证称为上游哈希验证。用户说以后对比，不等于当前授权启动推理。

## 可恢复下载

1. 用 `--dry-run` 读取选中文件、字节数、端点、版本和目标目录。
2. 普通下载始终围绕用户指定仓库和授权文件，不替换成另一套公开样例。工具初始化/发版验证需要小样例时，模型可选配置、README 或 tokenizer，数据集可选已授权的小仓库或明确分片；双样例测试须在任务范围内，不盲目取完整训练语料。
3. 实际传输使用元数据 commit，目录身份记录端点、repo/type/commit 和排序后的文件名/大小集合。
4. 相同身份下重跑：完整文件跳过，有合法 `.aria2` 状态的部分文件续传。改变选择或 commit 时新建目录，不删除记录绕过检查。
5. 完成后核对所有文件尺寸并确认无残留状态。自行计算样例 SHA256 可用于后续追踪，但不能冒充已经与上游哈希比对。

`--allow-large` 只解除元数据选择的体量门槛；先核目标文件系统空间和用户授权，不是解除网络或配额约束。

## 初始化与失败处理

`setup` 默认打印 aria2 可执行文件或安装建议；只有 `--install` 加确认才调用已识别的包管理器。无人确认、权限不足或管理器失败时保留错误，不要求用户在聊天里发送密码。机器缺少工具不意味着可修改共享代理、挂载或系统服务。

目录冲突应保留旧内容并换目录；不要按文件大小猜它属于本次 commit。路径、内部控制目录和 aria2 侧车状态可能互相碰撞，含符号链接的目标应拒绝而不是跟随。aria2 默认配置/netrc 不作为隐藏凭据来源。

## 文档与复用

正式指南入口：

- https://arch.gh.wzhecnu.cn/ChatHFD/quickstart/
- https://arch.gh.wzhecnu.cn/ChatHFD/cli-tree/
- https://arch.gh.wzhecnu.cn/ChatHFD/configuration/
- https://arch.gh.wzhecnu.cn/ChatHFD/python-api/

从 Python 复用时核对 `download_repo`/`fetch_metadata` 的真实签名。当前前者返回 `None` 并使用 Click 输出/异常；不要把它描述为已有 HTTP/MCP 服务或结构化后台任务 API。
