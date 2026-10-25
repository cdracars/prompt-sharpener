---
name: sharpen-prompt
description: Turn a vague request into a clear prompt by asking the user a few short questions, then show the rewritten prompt for review before doing anything. Use when the prompt-check hook flags a request as vague, or when the user says "sharpen" or "improve my prompt".
---

The user dislikes writing long prompts. Get the missing details out of them with as little typing as possible, hand back a better prompt, and let them review it before anything runs.

## 1. Look things up first

Check the conversation, then the files, repo, and tools in front of you. Anything you can find yourself is your job, not a question for the user. Ground every question in what you found, not in guesses.

## 2. Ask one round of at most 4 questions

Ask only about things that would change the result: the goal, the target, the scope or limits, what "done" looks like, and the form of the output. Skip questions with obvious answers.

Number each question and give a recommended answer, worded so that "yes" accepts it:

```
1. Which login bug? I found a swallowed error in auth.py:145. Recommended: that one.
2. Add a test for it? Recommended: yes.
```

The user can then reply "yes", "1 yes, 2 no", or a few words. Use plain text, not a tool-specific question widget, so this works in any tool.

## 3. Write the sharpened prompt

Use this shape and leave out empty parts:

- **Goal:** one sentence on what the user is actually after.
- **Context:** the facts you found and the user's answers.
- **Task:** what to do, in steps if order matters.
- **Constraints:** what not to change or use, each with a short reason.
- **Done when:** how to tell the result is right.
- **Output:** the form of the answer.

Check it before showing it:
- Keep every specific name, number, path, and value the user gave. Replace vague amounts ("a few", "fast", "better") with concrete ones, or ask.
- Say what to do rather than what not to do, unless it's a real safety limit.
- No shouting (MUST, CRITICAL, ALL CAPS). Give a reason instead.
- Add nothing the user didn't say or imply. Mark your own assumptions as assumptions.
- Keep it short: most sharpened prompts fit in 5 to 15 lines.

## 4. Show it and wait

Show the sharpened prompt in a block, then ask: **"Run it, edit it, or copy it?"**

- **Run it:** carry out the sharpened prompt.
- **Edit it:** apply the user's changes and show it again.
- **Copy it:** stop. The user will use it somewhere else.

Do not start the task until the user picks. If the request turns out to be clear after all, say so in one line and offer to run it as is. Ask a second round of questions only if the answers opened a real new question.
