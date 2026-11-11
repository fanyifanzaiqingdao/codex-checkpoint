import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "checkpoint/cli.py"

class Workflow(unittest.TestCase):
    def test_recovery_and_changed_dirty_file(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["git", "init", folder], check=True, capture_output=True)
            def run(*args):
                return subprocess.run([sys.executable, str(CLI), "--repo", folder, *args], capture_output=True, text=True)
            self.assertNotEqual(run("status").returncode, 0)
            self.assertEqual(run("init").returncode, 0)
            path = Path(folder) / "task.txt"
            path.write_text("first")
            self.assertEqual(run("save", "--goal", "修复登录", "--todo", "test").returncode, 0)
            self.assertIn("not detected", run("status").stdout)
            path.write_text("other")
            result = run("resume")
            self.assertEqual(result.returncode, 0)
            self.assertIn("YES", result.stdout)
            self.assertIn("修复登录", result.stdout)
            self.assertIn("not authorization", result.stdout)
            self.assertNotIn(".checkpoint", subprocess.run(["git", "-C", folder, "status", "--porcelain"], capture_output=True, text=True).stdout)

class Journal(unittest.TestCase):
    def test_journal_lifecycle_and_validation(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(['git', 'init', folder], check=True, capture_output=True)
            def run(*args):
                return subprocess.run([sys.executable, str(CLI), '--repo', folder, *args], capture_output=True, text=True)
            self.assertEqual(run('init').returncode, 0)
            payload = Path(folder) / '.checkpoint/input.json'
            common = dict(source='user', scope='current task', certainty='explicit', evidence='User: no schema changes')
            payload.write_text(json.dumps(dict(common, text='不能改数据库')))
            result = run('record', 'constraint', '--file', str(payload))
            self.assertEqual(result.returncode, 0, result.stderr)
            record_id = result.stdout.strip()
            self.assertIn('不能改数据库', run('resume').stdout)
            self.assertEqual(run('resolve', record_id, '--status', 'revoked', '--reason', 'User canceled restriction').returncode, 0)
            records = json.loads(run('records').stdout)['records']
            self.assertEqual([h['status'] for h in records[0]['history']], ['active', 'revoked'])
            self.assertEqual(run('save', '--goal', 'continue').returncode, 0)
            self.assertEqual(len(json.loads(run('records').stdout)['records']), 1)
            for kind, fields in [('decision', dict(choice='refresh', reason='compatibility', alternatives=[dict(choice='rewrite', rejected_because='too broad')])), ('attempt', dict(action='retry', observed='duplicate', conclusion='unsafe without deduplication', retry_when='deduplication exists'))]:
                payload.write_text(json.dumps(dict(common, **fields)))
                self.assertEqual(run('record', kind, '--file', str(payload)).returncode, 0)
            before = (Path(folder) / '.checkpoint/journal.json').read_bytes()
            payload.write_text('{}')
            self.assertNotEqual(run('record', 'constraint', '--file', str(payload)).returncode, 0)
            lock = Path(folder) / '.checkpoint/journal.lock'
            lock.touch()
            self.assertIn('busy', run('resolve', record_id, '--status', 'active', '--reason', 'test').stderr)
            lock.unlink()
            self.assertEqual(before, (Path(folder) / '.checkpoint/journal.json').read_bytes())
            self.assertIn('revoked', run('resume').stdout)

if __name__ == "__main__":
    unittest.main()
