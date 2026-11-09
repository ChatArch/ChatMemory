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
