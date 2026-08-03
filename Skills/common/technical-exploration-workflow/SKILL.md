---
name: technical-exploration-workflow
description: Use when researching technologies or projects. Static-first discovery, comparison, shortlist, and evidence report before any runtime work.
version: 1.0.0
tags:
  - research
  - exploration
  - comparison
reference:
  - workspace-task-kickoff: "先建立规范 Project，并持续记录范围、来源、进度和产物"
---

# Technical Exploration Workflow

## 目标

技术探索的目的，是快速而系统地回答：

1. 这个领域有哪些代表项目或方案；
2. 每个项目是什么、解决什么问题、面向谁；
3. 它们属于哪些不同类别，差异在哪里；
4. 哪些明显不适合，哪些值得进一步深读；
5. 当前证据能支持什么结论，还有哪些未知；
6. 是否值得另开实践、PoC、部署或实现任务。

探索不是逐个下载、安装、构建、启动或部署候选。默认产物是可审计的候选地图、对比分析、shortlist 和报告；runtime 实践是后续独立任务。

## 四类工作必须分开

| 阶段 | 目的 | 默认允许 | 默认禁止 |
| --- | --- | --- | --- |
| 广泛发现 | 知道有哪些项目 | 搜索、官方文档、仓库元数据、release/license/security 信息 | clone 全部项目、下载 release、安装依赖 |
| 静态深读 | 理解 shortlist 的真实设计 | README、docs、源码、配置 schema、API 路由、issue/security；必要时 shallow/sparse clone | build、运行、打开端口、容器、benchmark |
| Runtime 实践 | 验证少数关键未知 | 在独立获批环境运行冻结 shortlist | 未授权机器、本机默认试跑、同时启动多个候选 |
| 生产部署 | 提供长期服务 | 独立部署 Project、资源预算、安全与回滚方案 | 把探索现场直接升级为生产 |

如果 workspace `AGENTS.md` 规定 Local 机器只能静态探索，这是一条绝对边界：不得启动服务、listener、容器、数据库、daemon、候选 binary 或 runtime smoke。需要实践时，先让用户明确批准另一台服务器。

## 1. 先定义问题，而不是先搜项目

在 Project `PRD.md` 中明确：

- 用户真正要做的决策；
- 目标用户和核心场景；
- 必须能力、加分能力和硬性排除项；
- 关注的时间快照；
- 运行环境、资源、许可证、安全和部署边界；
- 最终交付物；
- 哪些产品语义尚未确认，不能自行补全。

把筛选维度写出来。例如文件分享探索可以关心：对象 key 与 URL、上传/下载 API、鉴权、覆盖语义、过期、Range、存储后端、单机复杂度、维护状态和许可证。

## 2. 广泛发现：先建地图

从这些来源发现候选：

1. 官方组织和项目仓库；
2. curated list、基金会目录和生态索引；
3. package registry 与 release feed；
4. 官方文档中列出的 integrations / alternatives；
5. 高质量综述用于发现名称，再回到一手来源核验。

第一轮可以有几十到上百个名称，但只采集轻量信息。不要因为找到第一个看似可用的项目就停止，也不要把每个名称都拉到本地。

按产品模型或架构先分类。不同类别不能硬排一个总分；例如临时 capability share、文件管理器和 S3 object store 解决的问题不同，应分组比较。

## 3. 每个候选先建立认知卡片

每个进入正式清单的项目至少记录：

- 名称、官方 URL、类别；
- 一句话定义；
- 解决的问题与目标用户；
- 典型使用流程或产品形态；
- 核心能力；
- API / CLI / Web UI / protocol 接口；
- 数据、对象 key、路径、文件名和 URL 语义；
- 鉴权与安全边界；
- 运行模型与主要依赖（只按官方资料描述）；
- 最新 release、最近维护、archive/deprecation 状态；
- license；
- 官方已知限制和 security advisory；
- 对当前目标的初步 fit；
- 尚未核验的问题；
- 可用于快速理解的官方截图、架构图或流程图及来源。

不能只列一个名字和 stars。每个项目应有一小段概念介绍，让读者不打开链接也能知道它是什么。

可复用模板见 `templates/candidate-card.md`。

## 4. 建立 evidence ledger

重要判断必须能回到来源。建议记录：

| 字段 | 含义 |
| --- | --- |
| claim | 要支持的判断 |
| source | 官方 URL、文件或 commit |
| source type | docs / README / code / release / license / advisory / third-party |
| snapshot | 查询日期、版本、tag 或 commit |
| confidence | confirmed / project-claimed / third-party / unknown |
| notes | 限制、冲突证据、待核验点 |

来源优先级：

1. 官方 docs、源码、release、license、security advisory；
2. 官方 issue/discussion/roadmap；
3. 论文、基金会或可信独立评测；
4. 博客、聚合站和社区评论只作补充。

严格区分：

- 仓库声明支持；
- 源码中可确认存在；
- 项目方报告的结果；
- 第三方复现的结果；
- 当前仍未知的结果。

不要把文档能力自动写成“已经验证可用”。

## 5. 图片与可视化是认知材料

第一阶段优先使用官方 README、docs、demo 或仓库 assets 中的：

- 产品截图；
- 架构图；
- 核心流程图；
- API 或对象模型示意图。

记录图片来源、原始 URL、项目和必要的许可/署名信息。图片用于帮助理解项目形态，不是为了证明已经本地运行。若要发布，只下载少量最终入选图片并压缩；不要为了截图启动候选服务。

没有合适图片时，可以根据已核验事实绘制分类图、决策树或架构对照图，但必须标明是分析者整理，不冒充官方图。

## 6. 用矩阵过滤，而不是逐个试跑

矩阵至少包含用户的硬约束和核心决策维度。每个单元格写可理解的事实或简短判断，不只写模糊分数。

过滤顺序：

1. **硬门槛**：维护终止、许可证不符、缺少关键接口、必须依赖被禁止的运行方式；
2. **产品模型**：是否解决同一类问题；
3. **核心 fit**：是否直接满足主场景；
4. **复杂度与风险**：依赖、资源、运维面、安全边界；
5. **增量价值**：相比更简单候选，多出的复杂度换来了什么。

每个淘汰项保留一句明确理由。不要删除它们后只展示赢家，否则读者无法理解筛选过程。

## 7. Shortlist 后才静态深读源码

通常保留 2–3 个 finalist。对它们进一步检查：

- API route / protocol 实现；
- config schema 和默认绑定；
- auth、path traversal、secret handling；
- metadata/database/storage layout；
- overwrite、delete、expiry、range 等关键语义；
- upgrade/migration 和 release cadence；
- open security issues 与维护响应；
- 与当前系统的封装边界。

优先通过在线源码和 raw files 阅读。只有文档不足时才 shallow/sparse clone 单个 finalist；先估算大小，只读源码，不安装依赖、不构建、不运行。

## 8. Runtime 是显式 gate，不是探索默认步骤

只有同时满足以下条件才能进入实践：

- 静态报告已经交付；
- shortlist 已冻结；
- 有一个仅靠静态证据无法回答、且影响决策的具体问题；
- 用户明确批准实践；
- 用户明确指定非 Local 的目标服务器；
- 已定义内存、CPU、磁盘、端口、网络和时限预算；
- 已定义启动前检查、停止方式和清理方式；
- 一次只实践必要的最少候选。

实践结果进入独立 Project 或独立阶段，不回写成“所有探索都应运行”。

## 9. 标准产物

调研 Project 建议包含：

```text
reports/
  candidate-inventory.md   # 完整候选清单和概念介绍
  evidence-ledger.md       # 关键判断与一手来源
  comparison-matrix.md     # 分类后的横向比较
  shortlist.md             # 入围、淘汰和未知
  image-manifest.md        # 图片/图表来源与用途
  exploration-report.md    # 完整分析源稿
  chatblog-draft.mdx       # 需要公开发布时再创建
reference/
  upstream/                # 少量官方 README/docs/raw source
```

最终报告通常包含：

1. 问题定义和证据口径；
2. 一句话结论；
3. 领域分类图；
4. 完整候选表；
5. 每个重点项目的概念介绍与图片；
6. 横向矩阵；
7. 淘汰理由；
8. 按场景给出的 shortlist；
9. 风险、未知和下一步 gate；
10. 一手来源与图片来源。

## 10. ChatBlog 只是一个发布层

当探索需要公开沉淀时，可以把报告改写成 ChatBlog。可参考以下写法，但不要让写作格式反过来替代调研：

- 项目选型文章：先分类和总表，再逐项写“它解决了什么 / 适合与不适合”，配官方截图，最后按用户画像选择；
- 生态调研文章：声明查询快照和证据口径，先提出判断模型，再分组分析机制；
- 时间敏感调研：先验证入口是否有效，再按 fit 分层，给可复用检查表和 watchlist；
- 结尾列出 primary sources、图片来源和未验证边界。

发布前确保文章中的每个结论能回到 Project 的 evidence ledger。

## 11. 效率规则

- 面对 100 个项目，先抓 100 份轻量元数据，不 clone 100 个仓库；
- 第一轮每项只投入足够完成认知卡片的时间；
- 对明显不满足硬门槛的项目尽早停止深挖；
- 子任务按候选类别分组，并要求固定输出字段；
- 子任务 timeout 或无 summary 只表示未完成，不能当作结论；
- 先完成全景地图，再把主要时间投入 finalist；
- 不为“显得做过验证”而制造 runtime 工作。

## 12. Git 仓库中的任务收尾

如果探索或 skill 维护发生在 Git 仓库中，dirty 不能成为阶段结束后的长期状态。

每个有意义的阶段以及任务结束前：

1. 用 `git status` 和 `git diff` 复核自己写了什么；
2. 把改动按单一意图分组，不把无关内容混成一个 commit；
3. 运行 `git diff --check`、frontmatter/reference 校验和该改动需要的静态检查；
4. 精确 stage 对应文件；
5. 写清楚目的的 commit message；
6. 回读 `git status --short --branch`，确认工作树 clean。

如果看到已有 dirty，先读懂并解决：明确属于已完成阶段的改动，应验证并及时 commit；意图不明或可能属于其他人的改动，不得 reset、checkout、clean 或猜测处理，应停下来确认。不能一边绕开 dirty，一边继续叠加新任务。

## 13. 发生越界时

如果探索期间误启动或下载了不必要的重型内容：

1. 立即停止所有进程；
2. 确认没有 listener、容器或 daemon 残留；
3. 测量引入的内存/磁盘影响；
4. 只清理本任务明确创建的内容；
5. 在 `progress.md` 记录事件、清理和方法纠偏；
6. 更新 workspace policy / shared skill，防止重复；
7. 回到静态候选地图，不用更多运行弥补错误。

## 完成检查

- [ ] Project、问题、范围和硬约束已确认；
- [ ] 候选清单足够广，并按类别组织；
- [ ] 每个正式候选都有概念卡片，而不只是名称；
- [ ] 关键判断有一手来源和快照；
- [ ] 图片/图表有来源，且不是通过未授权运行取得；
- [ ] 矩阵覆盖用户真正关心的维度；
- [ ] 淘汰理由和 unknowns 被保留；
- [ ] Shortlist 在 runtime 之前形成并交付；
- [ ] Local/static-only 边界未被突破；
- [ ] 报告或 ChatBlog 清楚区分事实、项目方声明和分析判断；
- [ ] 如果工作位于 Git 仓库，相关改动已经按逻辑 commit，任务结束时工作树 clean。
