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
