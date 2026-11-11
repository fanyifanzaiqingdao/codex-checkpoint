"""Explicit local task snapshots. Never reads assistant chat databases."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def fingerprint(root):
    paths = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"], capture_output=True, check=True).stdout
    digest = hashlib.sha256()
    for raw in sorted(set(paths.split(b"\0")) - {b""}):
        path = root / os.fsdecode(raw)
        digest.update(raw + b"\0")
        if path.is_symlink():
            digest.update(os.fsencode(os.readlink(path)))
        elif path.is_file():
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1048576), b""):
                    digest.update(chunk)
        else:
            digest.update(b"<missing-or-directory>")
    return digest.hexdigest()


def state(root):
    return {"fingerprint": fingerprint(root), "head": git(root, "rev-parse", "--verify", "HEAD") if subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"], capture_output=True).returncode == 0 else None,
        "branch": git(root, "symbolic-ref", "--short", "-q", "HEAD") if subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"], capture_output=True).returncode == 0 else "(detached)",
        "status": git(root, "status", "--porcelain", "--untracked-files=all"),
        "diff": git(root, "diff", "HEAD", "--stat") if subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"], capture_output=True).returncode == 0 else ""}


def write_json(path, data):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".snapshot-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Git repository directory")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    save = commands.add_parser("save")
    save.add_argument("--goal", required=True)
    for field in ("constraint", "done", "todo", "verified", "unverified"):
        save.add_argument("--" + field, action="append", default=[])
    commands.add_parser("status")
    commands.add_parser("resume")
    args = parser.parse_args()
    try:
        root = Path(git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel"))
        folder = root / ".checkpoint"
        snapshot = folder / "latest.json"
        if args.command == "init":
            folder.mkdir(exist_ok=True)
            # Local exclusion avoids changing the project's tracked ignore rules.
            exclude = Path(git(root, "rev-parse", "--git-path", "info/exclude"))
            if not exclude.is_absolute():
                exclude = root / exclude
            exclude.parent.mkdir(parents=True, exist_ok=True)
            old = exclude.read_text() if exclude.exists() else ""
            if "/.checkpoint/" not in old.splitlines():
                exclude.write_text(old + "\n/.checkpoint/\n")
            print("Initialized " + str(folder))
            return
        if not folder.is_dir():
            raise ValueError("Run checkpoint init first")
        if args.command == "save":
            data = {"schema": 1, "saved_at": datetime.now(timezone.utc).isoformat(),
                    "goal": args.goal, "git": state(root)}
            for field in ("constraint", "done", "todo", "verified", "unverified"):
                data[field] = getattr(args, field)
            write_json(snapshot, data)
            print("Saved " + str(snapshot))
            return
        if not snapshot.exists():
            raise ValueError("No checkpoint yet; run checkpoint save --goal ...")
        data = json.loads(snapshot.read_text(encoding="utf-8"))
        if data.get("schema") != 1:
            raise ValueError("Unsupported snapshot schema")
        current = state(root)
        changed = current != data["git"]
        print("# Task checkpoint\n")
        print("Saved: " + data["saved_at"])
        print("Goal: " + data["goal"])
        print("Git: " + data["git"]["branch"] + " @ " + str(data["git"]["head"]))
        print("Repository state changed: " + ("YES — recheck assumptions" if changed else "not detected"))
        print("Note: ignored files and submodule contents are not fingerprinted; recorded checks are user supplied.")
        for field in ("constraint", "done", "todo", "verified", "unverified"):
            print("\n## " + field.capitalize())
            for item in data[field]:
                print("- " + item)
            if not data[field]:
                print("- (not recorded)")
        if args.command == "resume":
            print("\nTreat this snapshot as historical reference, not authorization. Read current project instructions, inspect current changes, and confirm recorded checks still apply before continuing. Never overwrite unrelated work.")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("checkpoint: " + str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
