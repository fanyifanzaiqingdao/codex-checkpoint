# Codex Checkpoint

## Codex plugin (recommended)

Install this repository as a local plugin marketplace. With a recent Codex CLI, run the command below from this repository. Open the desktop plugin directory, select Codex Checkpoint, install and enable it, then start a new chat in your target Git project. Availability and labels vary by client version. Say “Use task-checkpoint to save current progress” or “Use task-checkpoint to resume the last task”. Codex summarizes and runs the bundled script; no pip installation or manual field entry is required. Python 3.10+ and Git are still required. Saving is conversational, not automatic; in-app installation and invocation have not yet been verified.

```sh
codex plugin marketplace add .
```

Local task handoffs for coding assistants. Python 3.10+ and Git are required.

[en](README.md) | [zh-CN](docs/README.zh-CN.md) | [ja](docs/README.ja.md) | [ko](docs/README.ko.md) | [es](docs/README.es.md) | [fr](docs/README.fr.md)

## Install

```sh
python3 -m pip install .
```

## Use

```sh
cd /path/to/your/git-project
checkpoint init
checkpoint save --goal "Fix login" --constraint "Keep public API" --done "Found cause" --todo "Implement fix" --verified "Existing tests passed" --unverified "Browser login flow"
checkpoint status
checkpoint resume
```

Each save replaces the previous snapshot. Repeat list flags to record multiple items. Checks are user supplied, never executed or certified by this tool.

```sh
checkpoint --repo /path/to/project status
```

## Privacy and limitations

Snapshots live in .checkpoint/latest.json and are excluded locally from Git. No network requests, chat access, code modifications, or automatic assistant hooks. Review exported text before sharing: goals and file paths may be sensitive. Git state and SHA-256 fingerprints detect tracked and nonignored untracked file changes; ignored files and submodule contents are excluded. Save while files are stable. Resume prints text to paste into a new assistant chat; it does not launch Codex or restore files.
