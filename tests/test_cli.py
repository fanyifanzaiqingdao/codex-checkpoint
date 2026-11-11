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

if __name__ == "__main__":
    unittest.main()
