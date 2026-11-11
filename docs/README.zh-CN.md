# Codex Checkpoint：任务检查点

## Codex 插件（推荐）

在本仓库目录运行下面的命令，将仓库添加为本地插件来源。然后打开桌面端插件目录，找到 Codex Checkpoint，安装并启用，在目标 Git 项目中新建聊天。入口名称与可用性因客户端版本而异。直接说“使用 task-checkpoint 保存当前进度”或“使用 task-checkpoint 继续上次任务”。Codex 会整理信息并运行附带脚本，无需 pip 安装或手动填写字段。仍需要 Python 3.10+ 和 Git。保存需要在聊天中触发，并非自动保存。目前尚未完成桌面端安装与调用验证。

```sh
codex plugin marketplace add .
```

为编程助手保存本地任务交接。需要 Python 3.10+ 和 Git。

[en](../README.md) | [zh-CN](README.zh-CN.md) | [ja](README.ja.md) | [ko](README.ko.md) | [es](README.es.md) | [fr](README.fr.md)

## 安装

```sh
python3 -m pip install .
```

## 使用

```sh
cd /path/to/your/git-project
checkpoint init
checkpoint save --goal "Fix login" --constraint "Keep public API" --done "Found cause" --todo "Implement fix" --verified "Existing tests passed" --unverified "Browser login flow"
checkpoint status
checkpoint resume
```

每次保存覆盖上一个检查点。列表参数可重复填写。验证结果由使用者填写，本工具不会执行检查，也不保证验证结论。

```sh
checkpoint --repo /path/to/project status
```

## 隐私与边界

检查点位于 .checkpoint/latest.json，通过 Git 本地排除规则忽略。工具不联网、不读取聊天、不修改代码，也没有自动触发保存的助手集成。分享交接文本前请检查敏感目标和文件路径。Git 状态与 SHA-256 指纹用于检测已跟踪及未忽略的新文件变化，不检查被忽略文件和子模块内部内容。请在文件稳定时保存。resume 仅输出可粘贴到新聊天的文本，不启动 Codex、不恢复文件。

## 结构化任务记忆

对 Codex 说：“本任务过程中，请用 task-checkpoint 持续记录用户约束、决策和失败尝试。”插件会指导助手在重要事件发生后记录，不记录每次工具调用。这依赖助手主动调用，不是后台自动监听。

记录单独保存在 .checkpoint/journal.json，每条包含 ID、类型、创建时间、不可变内容和状态历史。通用必填字段：source（user/assistant/tool）、scope（适用范围）、certainty（explicit/hypothesis/observed）、evidence（证据描述）。约束填写 text；决策填写 choice、reason，可选 alternatives（每项包含 choice、rejected_because）；尝试填写 action、observed、conclusion、retry_when。证据由助手或用户描述，并非工具独立认证。save 只覆盖 latest.json，不覆盖 journal.json。resume 即使没有进度摘要，也会读取结构化记录。最后一条历史状态决定是否有效。替代记录时先添加新记录，再将旧记录标记 superseded，并在原因中引用新 ID。并发写入会提示重试；只有确认写入进程已停止后才能清理残留 journal.lock。

```sh
checkpoint record constraint --file constraint.json
checkpoint record decision --file decision.json
checkpoint record attempt --file attempt.json
checkpoint records
checkpoint resolve RECORD_ID --status superseded --reason "Replaced by NEW_RECORD_ID"
```

```json
{
  "source": "user",
  "scope": "current release",
  "certainty": "explicit",
  "evidence": "User explicitly requested no database schema changes",
  "text": "Do not change the database schema"
}
```

## 任务隔离、历史检查点与精简恢复

在命令前使用 --task 指定任务，不共享“当前任务”状态。省略时使用旧版默认目录 .checkpoint/；命名任务保存在 .checkpoint/tasks/任务ID/。每次保存都会在 history/ 保留摘要和当时的结构化记录，latest.json 仍会替换，但历史不会自动清理。旧版无法还原过去的日志，首次归档时只能使用替换当时的日志。默认恢复只显示约束、待办、未验证事项和有效记录；--full 查看完成项、验证、证据及完整历史。读取历史不恢复代码、不覆盖最新进度，执行前需核对当前要求。

```sh
checkpoint --task login init
checkpoint --task login save --goal "Fix login" --todo "Test refresh"
checkpoint --task billing init
checkpoint tasks
checkpoint --task login history
checkpoint --task login resume
checkpoint --task login resume --full
checkpoint --task login resume --checkpoint CHECKPOINT_ID
```
