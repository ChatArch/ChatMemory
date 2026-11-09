---
name: huggingface-hub
description: "Use when downloading Hub models or datasets. Prefer ChatHFD for public mirror/aria2 transfers; route authenticated work to native Hub tools."
version: 1.0.1
author: ChatArch
license: MIT
tags: [huggingface, chathfd, models, datasets, downloads]
---

# Hugging Face 模型与数据集下载

用于模型/数据集下载、HF-Mirror、aria2 并发与续传、旧 HFD 入口核对。沿用已有 Hugging Face CLI reference 的领域边界；这里把可复现的公开仓库下载收敛到 ChatHFD。认证、上传与仓库管理仍由官方 Hub 工具负责，先读其当前 `--help`，不混为 ChatHFD 能力。

## 先确定下载契约

1. 确认目标执行主机、仓库 ID、`model` 或 `dataset`、版本、目标目录和允许体量。询问“查看/对比 CLI”时先给真实命令树和示例，不擅自安装或下载权重。
2. 若用户提到旧脚本或旧命令，先从该主机的 shell 别名/函数和已知 rc 定位确切脚本，静态检查实际后端、参数、默认目录和初始化流程。不要仅因仓库没有文件就重新实现，也不要遍历整个共享数据盘。
3. 共享盘服务端路径与客户端挂载路径可能不同；在当前主机核对挂载并查 PrivateMemory，再选显式 `--local-dir`。这里不保存具体机器、网段或私有路径。
4. 公开仓库优先使用以下已发布 ChatHFD 流程。gated/private 仓库改用官方工具的正规授权流程；ChatHFD 不接收/转发 Token，不能用旧认证参数或占位 API Key 绕过边界。

## 检查工具

目录配置接口基线为 ChatHFD 0.1.6。复用现有 ChatArch 管理环境；需要安装时使用独立虚拟环境，避免升级破坏无关工具。新于基线的版本也先回读命令面。

```bash
python -m pip install 'ChatHFD>=0.1.6,<0.2.0'
chathfd --version
chathfd --tree
chathfd --tree-brief
chathfd setup
```

`setup` 默认只检查；缺少 aria2 时给出安装建议。只有明确需要安装时才运行 `chathfd setup --install`，仍需确认。安装错误不授权修改系统代理、网络或其他服务。

## 下载根目录

默认根目录是调用时当前目录；`CHATHFD_DOWNLOAD_ROOT`支持进程变量和ChatEnv活动profile，隐式目标为`<root>/<repo_id>`（不再套models/datasets层）。精确`--local-dir`最高优先且不追加repo ID；其次进程变量、活动profile、当前目录。真实配置只按授权人工设置，服务端实体路径不能替代客户端挂载视角；详情及ChatEnv命令见[下载参考](references/hf-mirror-aria2-downloads.md)。

## 模型与数据集的最小实测

按本次获授权的仓库类型选择对应示例，不要求每次把两类都执行。普通下载围绕用户指定仓库和文件；双样例验证只用于已明确包含两类目标的工具/发版验收。

```bash
# 默认 HF-Mirror，先预检一个小文件
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' --dry-run

# 只下载配置文件，不是完整权重
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' \
  --local-dir ./models/qwen-config --connections 4 --jobs 5

# 公开数学数据集：先预检，再下载仓库文件
chathfd download MathArena/arxivmath-0926 --repo-type dataset --dry-run
chathfd download MathArena/arxivmath-0926 \
  --repo-type dataset --local-dir ./datasets/arxivmath-0926 \
  --connections 4 --jobs 3
```

示例仓库不是“永远最新”的声明。用户要最新模型/数据集时，重新核官方发布、日期、许可与仓库文件元数据，不凭名称或修改时间猜发布时间。

## 镜像、筛选与续传

- CLI 端点优先级：`--endpoint` > 进程 `HF_ENDPOINT` > 内置 HF-Mirror；不自动回退到另一平台。
- `--include`/`--exclude` 可重复，用引号保护 glob；排除优先。`--connections` 是每文件连接数，`--jobs` 是同时下载文件数，CLI 范围均为 1–10。
- 元数据返回的 commit 会固定到文件 URL。再次运行必须匹配端点、仓库、类型、commit 与选中文件集合；分支变化或选择变化使用新目录。需要复现时显式 `--revision` 固定 commit。
- 不删除 `.chathfd/selection.json` 来假造续传，不自动覆盖未知旧文件、符号链接或无状态的错误尺寸文件。
- 大于 10 GiB 的选择先预览、检查目标盘空间并确认预算，再使用 `--allow-large`；这是元数据预检，不是网络字节硬上限。
- ModelScope 是独立仓库与 SDK，不是 `HF_ENDPOINT` 的替换地址。先确认内容确实在那里发布，再核其官方命令；不得静默替换同名仓库。

## 完成验收

回读已安装版本/CLI 树、此次授权的目标文件、大小和仓库 commit。普通任务只验收用户授权的内容，不增加另一类仓库下载；只有明确包含模型和数据集两类目标的工具/发版验收，才分别实测小模型文件和小型完整数据集。需要验证复用/续传时，在同一已授权选择上重跑。完成条件是文件存在、尺寸正确、无残留 aria2 状态；这不是上游加密哈希验证，也不是模型推理成功。

向用户说明此次授权目标及真正下载的内容；执行双样例验收时再分别解释两类样例。配置/README 小样例不能称为权重已下载。报告下载量与仓库总量分开，公开文档/共享 Skill 不出现机器身份或秘密。

详细配置与排错见 [下载参考](references/hf-mirror-aria2-downloads.md)。产品文档：https://arch.gh.wzhecnu.cn/ChatHFD/ 。
