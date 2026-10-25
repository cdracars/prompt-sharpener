# prompt-sharpener

A prompt improver that works in both **Claude Code** and **Codex**. When you type something vague, the AI asks you a few short questions, rewrites your prompt, and waits while you choose to run it, edit it, or copy it.

It has two parts:

- **A hook** (`hooks/sharpen_hook.py`) runs on every prompt you send. It doesn't judge your prompt itself. It adds a short note asking the AI to check whether the prompt is clear and to use the skill only if it's genuinely vague. Replies like "yes", "lgtm", or "1 yes, 2 no" are skipped, so they cost nothing.
- **A skill** (`skills/sharpen-prompt/SKILL.md`) does the work. It looks up what it can first, asks at most 4 numbered questions with a recommended answer for each, writes the sharpened prompt, and asks **"Run it, edit it, or copy it?"**

The skill also works alone, with no hook, anywhere that reads `SKILL.md` skills: the Claude app, and ChatGPT if your workspace allows skill uploads. Without the hook it runs only when you ask for it (say "sharpen this") or when the AI decides to use it.

## Example

You type `make it better`. The AI replies:

> Flagged because "it" has no clear target and "better" has no definition of done.
>
> 1. **What should I improve?** Recommended: `stats.py` and `io_utils.py`, the only code here.
> 2. **What does "better" mean?** Recommended: fix the bugs, then add type hints.
> 3. ...
>
> Sharpened prompt:
> > Fix the bugs in `stats.py` (rename `total` to `mean`, raise a clear error on an empty list) and `io_utils.py` (use a `with` block, UTF-8). Add type hints and tests. Leave the README alone.
>
> Run it, edit it, or copy it?

That's real output from a headless Claude Code test run, shortened. Headless mode can't stop for answers, so it wrote the prompt right away using its recommended answers. In a normal session it waits for your answers first.

## Install

Clone the repo somewhere stable, such as `~/code/prompt-sharpener`. You need Python 3.8 or newer. The hook uses only the standard library.

### Claude Code

1. Copy `skills/sharpen-prompt/` to `~/.claude/skills/sharpen-prompt/`.
2. Add the hook to `~/.claude/settings.json`, merging it with anything already there. See `config/claude-settings.example.json`, and fix the path.
3. Restart Claude Code.

### Codex (CLI or IDE extension)

1. Copy `skills/sharpen-prompt/` to `~/.agents/skills/sharpen-prompt/`.
2. Add the hook to `~/.codex/hooks.json`. See `config/codex-hooks.example.json` and fix both paths: `command` is for macOS and Linux, `commandWindows` is for Windows.
3. Start Codex and run `/hooks` to review and trust the hook. Codex skips hooks you haven't trusted, and it asks again whenever the script changes.

A work account's admin can block personal hooks (`allow_managed_hooks_only` in `requirements.toml`). If that's the case, the skill still works on its own: type `$sharpen-prompt`, or say "sharpen this".

### Claude app and ChatGPT

Zip the `sharpen-prompt/` folder and upload it as a skill. In ChatGPT Enterprise, skills have to be enabled by your workspace admin.

## Use

- Type as usual. Clear prompts go straight through.
- Start a prompt with `*` to skip the check for that one prompt.
- Slash commands (`/...`) are never checked.

## Test

```
python -m unittest discover tests
```

The tests feed the hook payloads shaped like those of both Claude Code and Codex, plus replies, bypasses, UTF-8 text, and broken input. The hook never blocks a prompt: if anything goes wrong it prints nothing and exits 0.

## Credits

This project borrows the design of two others. No code was copied: everything here was written from scratch, and it is MIT-licensed too (see `LICENSE`).

| Project | License | What we borrowed |
|---|---|---|
| [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver) (checked at v0.6.3) | MIT, Copyright (c) 2025 severity1 | Having the AI judge vagueness instead of a keyword filter, researching before asking, the `*` bypass, and skipping harness messages |
| [hairglasses-studio/prompt-improver](https://pkg.go.dev/github.com/hairglasses-studio/prompt-improver) (checked at v0.1.0, now archived and merged into ralphglasses) | MIT, Copyright (c) 2024-2026 hairglasses-studio | The skip filter for short replies, the hook output shape that both tools accept, and the checklist for writing the prompt (concrete values, a reason for each rule, no shouting) |

Both licenses were read from each project's own `LICENSE` file on 2026-10-25.

What's new here is that it works in both tools, the questions are plain text so they work anywhere, and you review the rewritten prompt before anything runs.
