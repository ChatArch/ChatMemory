# ChatMemory Skills

这个目录是 ChatMemory 共享 skills 的根目录。它描述整个 ChatMemory / Playground 共享 skill 体系的分组、同步边界，以及所有 `SKILL.md` header/frontmatter 中可选 `reference:` 字段的全局规范。

## Skill groups

```text
Skills/
  agents/    # agent / worker / orchestration 相关共享 skills
  chatarch/  # ChatArch 组织、仓库、package、review、发布和协作流程
  common/    # 跨项目通用的共享 skills
  local/     # 本仓库中的本地模板/示例；默认不作为共享链接组使用
```

`chatup workspace` / workspace setup 应把共享 skill groups 链接到 `~/Playground/skills/` 下。当前默认共享组是：

- `agents`
- `chatarch`
- `common`

`local` 用于本地模板、机器特定 workflow 或 copy-and-adapt 示例，不应默认当成跨机器共享 skill group。每台机器应维护自己 workspace 下的 `skills/local/` copy；不要把当前机器的本地分支名、路径、凭据策略写回共享组，也不要为了同步本机工作去 checkout、merge、reset 其他机器人/机器的长期分支。

## `reference:` field

`SKILL.md` 可以在 header/frontmatter 中声明可选 `reference:` 字段，用来表达整个 ChatMemory skill graph 的有向依赖边。

格式：

```yaml
reference:
  - target-skill-name: "target 在当前 skill 中发挥的作用"
```

规则：

- `reference` 必须是 list。
- 每一项只包含一个 key/value。
- key 必须使用被引用 skill 的规范名，也就是目标 `SKILL.md` frontmatter 里的 `name` 字段。
- key 不能指向只有目录/README、但没有 `SKILL.md` 和 `name` 字段的主题节点。
- value 写一句简短说明：这个被引用 skill 在当前 skill 的使用流程中发挥什么作用。
- `reference` 只描述 ChatMemory skills 内部可同步、可解析的节点；不要把当前机器上的 Hermes 本地 skills 写进共享 graph。
- `reference` 是有向关系：只有当“使用当前 skill 时可能需要先学习/调用/依赖另一个 skill”时，才把另一个 skill 写进当前 skill 的 `reference:`。
- 不要因为“别的 skill 会用到当前 skill”就在当前 skill 里反向引用对方。
- 不要为了分类、邻近、主题相似而添加 reference；reference 不是 tag，也不是双向 related list。

## Example

```yaml
---
name: chatgh-pr-and-ci-workflow
description: ChatArch PR/CI workflow.
reference:
  - chatgh-repo-token-setup: "区分 GitHub API auth 与 git transport auth"
---
```

## Maintenance notes

- 新建或移动 skill 时，保持 frontmatter `name` 与文件夹名一致。
- 移动 skill 后，同步更新其他 skills 的 `reference:` key。
- `reference:` 是机器可解析结构；正文中只保留必要流程，不重复展开完整图关系。
- 调整 `reference:` 后，应运行一次解析校验，确认每个 key 都能解析到一个真实 `SKILL.md` 的 `name`。
