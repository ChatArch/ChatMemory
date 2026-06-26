# ChatArch Package Review Skills

这个目录收纳 ChatArch package 的 post-review / 后处理规范检查类 skills。

这里的 package review 不是 active development，也不是发布前 release readiness。它指的是：一个包已经开发到一定阶段、通常已经发版并运行过一段时间之后，我们又形成了新的规范、治理经验或基础设施约定，需要回头审查已有仓库并补齐规范。

它和 `package-development/` 的边界不同：

- `package-development/` 关注从零创建、抽包、repo 初始化、PR/CI、发版链路等开发执行流程；
- `package-review/` 关注已经存在、已经阶段性完成甚至已经发版过的包，按新的规范做后处理检查、补齐和治理。

## 当前主题节点

```text
package-review/
  README.md
  chatenv-provider-workflow/
```

## 每个 skill 是什么

### `chatenv-provider-workflow`

用途：在已有包的 post-review 中 review、补齐或 debug ChatEnv typed-config provider。

覆盖流程：

1. 确认包是否应该暴露 `chatenv.configs` entry point。
2. 检查 config class 的 title、alias、storage、required/sensitive fields。
3. 验证 editable/install 后 provider 是否能被 ChatEnv 发现。
4. 检查 `chatenv test` 是否安全、可解释、不会泄露 secret。
5. 区分本地 schema/provider wiring 检查和真实远端连通性检查。

什么时候用：已有包暴露出 `Env list` / `chatenv cat/test/use` 不符合预期，或后续规范要求回头检查 ChatEnv provider 时。

后续如果要对“已发版一段时间的包”按新规范做专项后处理 review，再按具体问题创建新的 review skill；这些 review skill 可以引用 `../package-development/` 里的开发阶段技能作为背景，但不把开发阶段技能本体放进 review 主题。
