"""Tests for hooks/sharpen_hook.py. Run with: python -m unittest discover tests"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "sharpen_hook.py"
sys.path.insert(0, str(HOOK.parent))
import sharpen_hook  # noqa: E402

# Payload shapes from each tool's documentation.
CLAUDE_PAYLOAD = {
    "session_id": "abc123",
    "transcript_path": "/home/u/.claude/projects/x/abc123.jsonl",
    "cwd": "/home/u/code/app",
    "permission_mode": "default",
    "hook_event_name": "UserPromptSubmit",
    "prompt": "fix the bug",
}
CODEX_PAYLOAD = {
    "session_id": "s-1",
    "transcript_path": "/home/u/.codex/sessions/s-1.jsonl",
    "cwd": "/home/u/code/app",
    "hook_event_name": "UserPromptSubmit",
    "model": "gpt-5-codex",
    "permission_mode": "workspace-write",
    "turn_id": "t-7",
    "prompt": "fix the bug",
}


def run_hook(stdin_bytes):
    """Run the hook as the tools do: a separate process fed stdin."""
    return subprocess.run(
        [sys.executable, str(HOOK)], input=stdin_bytes, capture_output=True, timeout=10
    )


class ShouldCheckTest(unittest.TestCase):
    def test_checks_real_prompts(self):
        for prompt in [
            "fix the bug",
            "deploy",
            "make the export faster",
            "Refactor getUserById in src/api/users.ts to async/await",
        ]:
            self.assertTrue(sharpen_hook.should_check(prompt), prompt)

    def test_skips_replies_and_approvals(self):
        for prompt in ["yes", "OK.", "lgtm", "go ahead!", "build it", "Run it", "copy it", "  no  "]:
            self.assertFalse(sharpen_hook.should_check(prompt), prompt)

    def test_skips_numbered_answers(self):
        for prompt in ["1 yes, 2 no", "2: the second one", "1. yes", "Q1 yes"]:
            self.assertFalse(sharpen_hook.should_check(prompt), prompt)

    def test_skips_bypass_slash_and_machine_events(self):
        for prompt in ["*just do it my way", "/review", "<system-reminder>x</system-reminder>",
                       "  <task-notification>done</task-notification>"]:
            self.assertFalse(sharpen_hook.should_check(prompt), prompt)

    def test_skips_paths_and_empty(self):
        for prompt in ["./src/app.py", "~/notes/*.md", "", "   "]:
            self.assertFalse(sharpen_hook.should_check(prompt), prompt)


class ProcessTest(unittest.TestCase):
    def assert_note(self, result):
        self.assertEqual(result.returncode, 0)
        out = json.loads(result.stdout)
        spec = out["hookSpecificOutput"]
        self.assertEqual(spec["hookEventName"], "UserPromptSubmit")
        self.assertIn("sharpen-prompt", spec["additionalContext"])

    def test_claude_code_payload(self):
        self.assert_note(run_hook(json.dumps(CLAUDE_PAYLOAD).encode()))

    def test_codex_payload(self):
        self.assert_note(run_hook(json.dumps(CODEX_PAYLOAD).encode()))

    def test_utf8_prompt(self):
        payload = dict(CODEX_PAYLOAD, prompt="arregla el café ☕ bug")
        self.assert_note(run_hook(json.dumps(payload, ensure_ascii=False).encode("utf-8")))

    def test_reply_prints_nothing(self):
        result = run_hook(json.dumps(dict(CLAUDE_PAYLOAD, prompt="yes")).encode())
        self.assertEqual((result.returncode, result.stdout), (0, b""))

    def test_bad_input_never_blocks(self):
        for stdin in [b"", b"not json", b"[1, 2]", json.dumps({"prompt": 5}).encode()]:
            result = run_hook(stdin)
            self.assertEqual((result.returncode, result.stdout), (0, b""), stdin)


if __name__ == "__main__":
    unittest.main()
