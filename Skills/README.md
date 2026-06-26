# ChatMemory Skills

这个目录是 ChatMemory 共享 skills 的根目录。它描述 skill 分组、同步边界，以及 `SKILL.md` header/frontmatter 中可选 `reference:` 字段的规范。

## Skill groups

```text
Skills/
  agents/    # agent / worker / orchestration 相关共享 skills
  chatarch/  # ChatArch 组织、仓库、package、发布和协作流程
  common/    # 跨项目通用的共享 skills
  local/     # 本仓库中的本地模板/示例；默认不作为共享链接组使用
```

`chatup workspace` / workspace setup 应把共享 skill groups 链接到 `~/Playground/skills/` 下。当前默认共享组是：

- `agents`
- `chatarch`
- `common`

`local` 用于本地模板、机器特定 workflow 或 copy-and-adapt 示例，不应默认当成跨机器共享 skill group。

## `reference:` field

`SKILL.md` 可以在 header/frontmatter 中声明可选 `reference:` 字段，用来表达 skill graph 的关联边。

格式：

```yaml
reference:
  - target-skill-name: "target 在当前 skill 中发挥的作用"
```

规则：

- `reference` 必须是 list。
- 每一项只包含一个 key/value。
- key 使用被引用节点的规范名。
- 对普通 skill，规范名应等于该 skill 的 frontmatter `name`，通常也等于文件夹名。
- 对主题/分类节点，可以使用主题目录名，例如 `package-development`。
- value 写一句简短说明：这个被引用节点在当前 skill 中发挥什么作用。
- `reference` 只描述 ChatMemory skills 内部可同步、可解析的节点；不要把当前机器上的 Hermes 本地 skills 写进共享 graph。

## Example

```yaml
---
name: chatgh-pr-and-ci-workflow
description: ChatArch PR/CI workflow.
reference:
  - package-development: "主题索引；用于定位 ChatArch package/repo workflow 相关 skill"
  - chatgh-repo-token-setup: "区分 GitHub API auth 与 git transport auth"
---
```

## Maintenance notes

- 新建或移动 skill 时，保持 frontmatter `name` 与文件夹名一致。
- 移动 skill 后，同步更新其他 skills 的 `reference:` key。
- `reference:` 是机器可解析结构；正文中只保留必要流程，不重复展开完整图关系。
