#!/usr/bin/env python3
"""UserPromptSubmit hook for Claude Code and Codex.

Reads the hook payload (JSON) on stdin. For a real prompt it prints a short
note asking the AI to judge whether the prompt is clear, and to run the
sharpen-prompt skill only when it is genuinely vague. Replies, approvals,
file paths and harness messages are skipped, so they cost nothing.

Both tools accept the same output shape:
    {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                            "additionalContext": "..."}}

Standard library only. Never blocks a prompt: any error means no output.
"""
import json
import re
import sys

# Start a prompt with "*" to skip the check. "/" is a slash command.
BYPASS_PREFIXES = ("*", "/")

# Harness messages that arrive as prompts but were not typed by the user.
MACHINE_PREFIXES = (
    "<task-notification>",
    "<command-name>",
    "<command-message>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<local-command-caveat>",
    "<system-reminder>",
)

# Short replies and approvals, including answers to the skill's own
# "Run it, edit it, or copy it?" question.
REPLY = re.compile(
    r"(?i)^(y|n|yes|yep|yeah|no|nope|nah|ok|okay|k|sure|thanks|thank you|ty|"
    r"done|continue|go|go ahead|looks good|lgtm|ship it|do it|build it|next|"
    r"proceed|approve|approved|reject|cancel|stop|undo|revert|"
    r"run it|edit it|copy it|run|edit|copy)[\s.!]*$"
)

# Answers to numbered questions, such as "1 yes, 2 no" or "Q2: skip". A
# number alone is not enough: "2 bugs need fixing" is a real prompt.
NUMBERED_ANSWER = re.compile(
    r"(?i)^\s*q?\d{1,2}\s*[:.)\-]?\s*"
    r"(y|n|yes|yep|yeah|no|nope|ok|okay|sure|skip|both|none|agree|recommended)\b"
)

# A bare file path or glob, Unix or Windows style.
PATH_ONLY = re.compile(r"^(?:[A-Za-z]:[\\/]|[./~\\])[\w\\/.*\- ]+$")

NOTE = """Prompt check (sharpen-prompt hook). Before acting, judge the user's latest message against the whole conversation.

Proceed normally and ignore this note if the message is clear enough to do well, answers a question you asked, or is a small request where a wrong guess is cheap to fix.

Only if it is genuinely vague, so that a wrong guess would waste real work:
1. Say in one line why it was flagged (unclear goal, scope, target, or what "done" means).
2. Use the sharpen-prompt skill. If the skill is not available, follow its steps directly: look up what you can yourself, ask at most 4 numbered questions each with a recommended answer, write the sharpened prompt, and ask "Run it, edit it, or copy it?"
3. Do not start the task until the user picks."""


def should_check(prompt):
    """True if the prompt is worth a clarity check."""
    text = prompt.strip()
    if not text:
        return False
    if text.startswith(BYPASS_PREFIXES) or text.startswith(MACHINE_PREFIXES):
        return False
    if REPLY.match(text) or NUMBERED_ANSWER.match(text):
        return False
    if PATH_ONLY.match(text):
        return False
    return True


def build_output(payload):
    """Return the hook's stdout text for a decoded payload, or ""."""
    prompt = payload.get("prompt") if isinstance(payload, dict) else None
    if not isinstance(prompt, str) or not should_check(prompt):
        return ""
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": NOTE,
            }
        }
    )


def main():
    try:
        # Decode as UTF-8 ourselves: Windows consoles default to a code page.
        # utf-8-sig drops the byte-order mark Windows PowerShell may prepend.
        raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
        out = build_output(json.loads(raw))
    except Exception:
        out = ""
    if out:
        sys.stdout.write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
