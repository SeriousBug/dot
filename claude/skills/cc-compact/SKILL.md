---
name: cc-compact
description: Summarize ("compact") a past Claude Code session without ingesting its entire history. Resolves the session log, then extracts only the key signals — opening intent, recent prompts, most-edited files, and what the agent was doing last. Use, when asked, to resume long sessions without ingesting entire log.
---

You are reloading the context of a previous Claude Code session so you can
**continue that work in this session** — like `/resume` followed by `/compact`, but pre-compacted. The
bundled helper script extracts the key signals and prints a compact report.

**Hard rule: you may NOT read the session `.jsonl` file by any means** — no
`cat`, `head`, `tail`, `jq`, `grep`, `Read`, nothing. Run the helper script
**once** and work solely from its output. That is the only thing allowed to
touch the file.

The helper script lives at `~/.claude/skills/cc-compact/compact_session.py`.

## Step 1: Resolve the session

The argument is one of three forms:

- **Nothing** — no id or title given. This is the common case: the user ran
  `/clear` and then `cc-compact` to reload the session they just cleared. Run
  the script with no selector; it auto-picks the most recently active session
  in the current project, **excluding this session** (the fresh one `/clear`
  created). This emulates Claude Code's built-in `/compact`.
- **A session id** — when invoked like `/resume claude --resume <id>` or
  `cc-compact <id>`, the user already gave you the UUID. Pass it as `--id`.
- **A session name / title** — free text. Pass it as `--title`; the script
  matches it against the `ai-title` records inside the logs (case-insensitive
  substring, newest match wins).

Run the script exactly once with the matching form:

```sh
# Latest session before the /clear (default, no selector):
python3 ~/.claude/skills/cc-compact/compact_session.py

# By id:
python3 ~/.claude/skills/cc-compact/compact_session.py --id <session-uuid>

# By title:
python3 ~/.claude/skills/cc-compact/compact_session.py --title "the session name"
```

## Step 2: Read the output

It prints a bounded, XML-tagged report:

- header: project, git branch, time span, record/prompt counts
- the first few exchanges (user prompt + the agent's reply) — the original intent
- a few exchanges sampled from the middle (non-overlapping) — the journey
- the last few exchanges (user prompt + the agent's reply) — where things were heading
- the most-edited files, ranked by edit count
- the last several tool calls — what the agent was physically doing last
- the final assistant message — what it was saying / waiting on last

## Step 3: Pick up the work

The output is context for *you* — treat it like a resumed session, not something
to report on. From it, reconstruct what the work was, which files are in play,
and what the agent was in the middle of.

Compaction is lossy — the output may not make the next step unambiguous. Before
diving in, decide whether you actually know how to proceed:

- **If the next step is very clear, last few messages from user confirms what to do**, open with one line confirming what you're
  resuming, then continue from where it left off.
- **If it's ambiguous** (unclear what the user wants next, multiple plausible
  directions, or the session ended mid-decision), **ask the user how to proceed**
  before acting. Surface the few plausible next steps you inferred and let them
  pick or correct you. If there is any doubt, opt to ask the user first.

## If the compact report left something unclear

Compaction is lossy. If — and **only if absolutely necessary** — a specific
detail you need to proceed is missing or ambiguous (an exact command that ran,
a file path, what a tool returned, the precise wording of an earlier request),
search the full session with the companion **cc-query-chat** skill instead of
reading the raw log:

```sh
python3 ~/.claude/skills/cc-query-chat/query_session.py --chat '<same id or name>' --keyword 'the detail you need'
```

The compact report is meant to stand on its own — reach for this only to close a
concrete gap, never to re-read the session.

