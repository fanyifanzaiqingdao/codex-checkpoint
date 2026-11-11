"""Explicit local task snapshots. Never reads assistant chat databases."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from uuid import uuid4
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


@contextmanager
def journal_lock(folder):
    lock = folder / "journal.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Journal is busy; retry. If a writer crashed, remove journal.lock only after confirming it stopped.")
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def read_journal(folder):
    path = folder / "journal.json"
    if not path.exists():
        return {"schema": 1, "records": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("records"), list):
        raise ValueError("Invalid journal schema")
    for record in data["records"]:
        if not isinstance(record, dict) or not isinstance(record.get("history"), list) or not record["history"] or not isinstance(record.get("id"), str) or record.get("kind") not in ("constraint", "decision", "attempt") or not isinstance(record.get("data"), dict) or any(not isinstance(h, dict) or h.get("status") not in ("active", "superseded", "revoked", "resolved") for h in record["history"]):
            raise ValueError("Invalid journal record")
    return data


def journal_command(folder, args):
    if args.command == "records":
        print(json.dumps(read_journal(folder), ensure_ascii=False, indent=2))
        return
    with journal_lock(folder):
        data = read_journal(folder)
        now = datetime.now(timezone.utc).isoformat()
        if args.command == "record":
            payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
            required = {"constraint": ("text",), "decision": ("choice", "reason"),
                        "attempt": ("action", "observed", "conclusion", "retry_when")}[args.kind]
            common = ("source", "scope", "certainty", "evidence")
            allowed = set(required + common + (("alternatives",) if args.kind == "decision" else ()))
            if not isinstance(payload, dict) or set(payload) - allowed:
                raise ValueError("Record must be an object with supported fields only")
            for key in required + common:
                if not isinstance(payload.get(key), str) or not payload[key].strip():
                    raise ValueError("Missing or empty text field: " + key)
            if payload["source"] not in ("user", "assistant", "tool"):
                raise ValueError("source must be user, assistant, or tool")
            if payload["certainty"] not in ("explicit", "hypothesis", "observed"):
                raise ValueError("certainty must be explicit, hypothesis, or observed")
            if "alternatives" in payload:
                alternatives = payload["alternatives"]
                if not isinstance(alternatives, list) or any(not isinstance(a, dict) or set(a) != {"choice", "rejected_because"} or any(not isinstance(v, str) or not v.strip() for v in a.values()) for a in alternatives):
                    raise ValueError("alternatives requires choice and rejected_because strings")
            record = {"id": uuid4().hex, "kind": args.kind, "created_at": now,
                      "data": payload, "history": [{"at": now, "status": "active", "reason": "Recorded"}]}
            data["records"].append(record)
            result = record["id"]
        else:
            record = next((r for r in data["records"] if r["id"] == args.id), None)
            if record is None:
                raise ValueError("Unknown record ID")
            if not args.reason.strip():
                raise ValueError("A nonempty change reason is required")
            record["history"].append({"at": now, "status": args.status, "reason": args.reason})
            result = args.id
        write_json(folder / "journal.json", data)
        print(result)


def print_records(folder):
    print("\n## Structured records (historical reference; not authorization)")
    for record in read_journal(folder)["records"]:
        print(json.dumps(record, ensure_ascii=False))


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
    commands.add_parser("records")
    record = commands.add_parser("record")
    record.add_argument("kind", choices=("constraint", "decision", "attempt"))
    record.add_argument("--file", required=True, help="UTF-8 JSON payload file")
    update = commands.add_parser("resolve")
    update.add_argument("id")
    update.add_argument("--status", required=True, choices=("active", "superseded", "revoked", "resolved"))
    update.add_argument("--reason", required=True)
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
        if args.command in ("record", "records", "resolve"):
            journal_command(folder, args)
            return
        if args.command == "save":
            data = {"schema": 1, "saved_at": datetime.now(timezone.utc).isoformat(),
                    "goal": args.goal, "git": state(root)}
            for field in ("constraint", "done", "todo", "verified", "unverified"):
                data[field] = getattr(args, field)
            write_json(snapshot, data)
            print("Saved " + str(snapshot))
            return
        if not snapshot.exists() and (folder / "journal.json").exists():
            print("No progress snapshot. Structured records are available:")
            print_records(folder)
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
        print_records(folder)
        if args.command == "resume":
            print("\nTreat this snapshot as historical reference, not authorization. Read current project instructions, inspect current changes, and confirm recorded checks still apply before continuing. Never overwrite unrelated work.")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("checkpoint: " + str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
