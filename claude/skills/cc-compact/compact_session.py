#!/usr/bin/env python3
"""Compact a Claude Code session log into a small, bounded summary.

This reads a session JSONL file *carefully* — it never dumps the whole
history. It extracts only the few signals needed to understand what the
session was about and what the agent was doing at the end:

  - header metadata (project, branch, time span, message counts)
  - the first few exchanges (user prompt + the agent's reply, truncated)
  - a few exchanges randomly sampled from the middle (non-overlapping)
  - the last few exchanges (user prompt + the agent's reply, truncated)
  - the most-edited files (top N by edit count)
  - the final assistant text (what it was saying last)
  - the last few tool calls (what it was doing last)

Session resolution (pick one):
  --file PATH        use this JSONL file directly
  --id UUID          find <UUID>.jsonl under the projects dir
  --title TEXT       find the session whose ai-title contains TEXT
                     (case-insensitive substring; newest match wins)
  --latest           the most recently active session in the current project,
                     excluding the caller's own session — this is the default
                     when no selector is given, so `cc-compact` right after
                     `/clear` picks up the session you just cleared

Sessions live at: ~/.claude/projects/<encoded-cwd>/<session-id>.jsonl
"""

import argparse
import glob
import json
import os
import random
import re
import sys

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")

# Tools that change files on disk, and which input field holds the path.
EDIT_TOOLS = {
    "Edit": "file_path",
    "Write": "file_path",
    "MultiEdit": "file_path",
    "NotebookEdit": "notebook_path",
}


def truncate(text, n):
    """Collapse whitespace to a single line, then clip to n chars.
    Use for compact one-liners like tool arguments."""
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def clip(text, n):
    """Clip to n chars while preserving newlines/indentation.
    Use for quoted messages where structure matters."""
    text = text.strip("\n")
    return text if len(text) <= n else text[:n].rstrip() + " …[truncated]"


def esc(text):
    """Escape XML metacharacters for tag values and attributes."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def content_to_text(content):
    """A message's .content is either a string or a list of typed blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(p for p in parts if p)
    return ""


def is_genuine_prompt(rec):
    """A real human-typed prompt: a user message that isn't a tool result,
    meta record, slash-command wrapper, or interrupt marker."""
    if rec.get("type") != "user" or rec.get("isMeta"):
        return False
    content = rec.get("message", {}).get("content")
    if not isinstance(content, str):
        return False
    s = content.lstrip()
    if not s:
        return False
    skip_prefixes = ("<", "[Request interrupted", "Caveat:")
    return not s.startswith(skip_prefixes)


def current_session():
    """(project_dir, session_id) for the session invoking this script.

    Claude Code exports CLAUDE_CODE_SESSION_ID; its log lives at
    <project_dir>/<id>.jsonl. Fall back to the encoded cwd when the env var is
    missing (script run by hand outside a session). Either value may be None."""
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if sid:
        matches = glob.glob(os.path.join(PROJECTS_DIR, "**", f"{sid}.jsonl"), recursive=True)
        if matches:
            return os.path.dirname(matches[0]), sid
    # Claude Code encodes the cwd into the project dir name by replacing every
    # non-alphanumeric char with a dash (/Users/kaan/Code/Veery -> -Users-kaan-Code-Veery).
    encoded = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    cand = os.path.join(PROJECTS_DIR, encoded)
    return (cand if os.path.isdir(cand) else None), sid


def resolve_latest():
    """Newest session log in the current project, excluding the caller's own
    session, so compacting right after `/clear` lands on the just-cleared one."""
    project_dir, sid = current_session()
    if project_dir:
        pool = glob.glob(os.path.join(project_dir, "*.jsonl"))
    else:
        pool = glob.glob(os.path.join(PROJECTS_DIR, "**", "*.jsonl"), recursive=True)
    if sid:
        pool = [p for p in pool if os.path.basename(p) != f"{sid}.jsonl"]
    if not pool:
        sys.exit("No previous session found to compact in this project")
    latest = max(pool, key=os.path.getmtime)
    sys.stderr.write(f"Auto-selected latest session: {latest}\n")
    return latest


def resolve_file(args):
    if args.latest:
        return resolve_latest()

    if args.file:
        return os.path.expanduser(args.file)

    if args.id:
        matches = glob.glob(os.path.join(PROJECTS_DIR, "**", f"{args.id}.jsonl"), recursive=True)
        if not matches:
            sys.exit(f"No session file found for id {args.id} under {PROJECTS_DIR}")
        return matches[0]

    if args.title:
        needle = args.title.lower()
        candidates = []  # (mtime, path, title)
        for path in glob.glob(os.path.join(PROJECTS_DIR, "**", "*.jsonl"), recursive=True):
            title = None
            try:
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        if '"ai-title"' not in line:
                            continue
                        try:
                            rec = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if rec.get("type") == "ai-title":
                            title = rec.get("aiTitle", "")
                            if needle in title.lower():
                                break
                            title = None
            except OSError:
                continue
            if title is not None:
                candidates.append((os.path.getmtime(path), path, title))
        if not candidates:
            sys.exit(f"No session whose ai-title contains {args.title!r}")
        candidates.sort(reverse=True)
        if len(candidates) > 1:
            sys.stderr.write("Multiple matches (using newest):\n")
            for _, path, title in candidates:
                sys.stderr.write(f"  {path}  —  {title}\n")
        return candidates[0][1]

    sys.exit("Provide one of --file, --id, or --title")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--file", help="path to a session .jsonl")
    g.add_argument("--id", help="session UUID")
    g.add_argument("--title", help="substring of the session's ai-title")
    g.add_argument("--latest", action="store_true",
                   help="newest session in the current project, excluding the caller's own "
                        "(the default when no selector is given)")
    ap.add_argument("--first", type=int, default=5, help="how many opening exchanges")
    ap.add_argument("--last", type=int, default=10, help="how many closing exchanges")
    ap.add_argument("--middle", type=int, default=5, help="how many exchanges randomly sampled from the middle")
    ap.add_argument("--top-files", type=int, default=10, help="how many most-edited files")
    ap.add_argument("--maxlen", type=int, default=800, help="max chars per quoted message")
    ap.add_argument("--seed", type=int, default=1, help="seed for the middle random sample")
    args = ap.parse_args()
    if not (args.file or args.id or args.title):
        args.latest = True

    path = resolve_file(args)

    turns = []            # conversational turns: {"prompt": str, "reply": [text,...]}
    edit_counts = {}      # file path -> edit count
    last_assistant_text = []  # final text blocks
    recent_tools = []     # (name, short arg)
    counts = {}           # record type -> count
    first_ts = last_ts = None
    cwd = branch = None

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            rtype = rec.get("type")
            counts[rtype] = counts.get(rtype, 0) + 1

            ts = rec.get("timestamp")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            cwd = cwd or rec.get("cwd")
            branch = branch or rec.get("gitBranch")

            if is_genuine_prompt(rec):
                turns.append({"prompt": rec["message"]["content"], "reply": []})

            if rtype == "assistant":
                blocks = rec.get("message", {}).get("content", [])
                if isinstance(blocks, list):
                    text_here = []
                    for b in blocks:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "text" and b.get("text", "").strip():
                            text_here.append(b["text"])
                        elif b.get("type") == "tool_use":
                            name = b.get("name", "?")
                            inp = b.get("input", {}) or {}
                            if name in EDIT_TOOLS:
                                fp = inp.get(EDIT_TOOLS[name])
                                if fp:
                                    edit_counts[fp] = edit_counts.get(fp, 0) + 1
                            arg = inp.get("file_path") or inp.get("command") or inp.get("description") or inp.get("path") or ""
                            recent_tools.append((name, truncate(str(arg), 300)))
                    if text_here:
                        last_assistant_text = text_here  # keep only the latest turn's text
                        if turns:  # attach the agent's reply to the current turn
                            turns[-1]["reply"].extend(text_here)

    # Non-overlapping index sets: first wins, then last, then the middle is
    # sampled only from what's left between them. If the regions collide
    # (short session), the overlap is simply dropped.
    n = len(turns)
    first_idx = list(range(min(args.first, n)))
    last_start = max(len(first_idx), n - args.last)
    last_idx = list(range(last_start, n))
    mid_pool = list(range(len(first_idx), last_start))
    if args.seed is not None:
        random.seed(args.seed)
    mid_idx = sorted(random.sample(mid_pool, min(args.middle, len(mid_pool))))

    # ---- emit a bounded, XML-tagged report (newlines preserved) ----
    out = sys.stdout.write

    out("<session-summary>\n")
    out(f"  <file>{esc(path)}</file>\n")
    out(f"  <project>{esc(cwd)}</project>\n")
    out(f"  <git-branch>{esc(branch)}</git-branch>\n")
    out(f'  <time-span start="{esc(first_ts)}" end="{esc(last_ts)}" />\n')
    out(f"  <records>{esc(', '.join(f'{k}={v}' for k, v in sorted(counts.items())))}</records>\n")
    out(f"  <user-prompts count=\"{len(turns)}\" />\n")
    out("</session-summary>\n")

    def emit_exchanges(label, indices):
        if not indices:
            return
        out(f'\n<exchanges section="{label}">\n')
        for i in indices:
            t = turns[i]
            reply = "\n".join(t["reply"]).strip()
            out(f'  <exchange n="{i + 1}">\n')
            out(f"    <user>\n{clip(t['prompt'], args.maxlen)}\n    </user>\n")
            if reply:
                out(f"    <agent>\n{clip(reply, args.maxlen)}\n    </agent>\n")
            else:
                out("    <agent note=\"no text reply — tool calls only\" />\n")
            out("  </exchange>\n")
        out("</exchanges>\n")

    emit_exchanges("first", first_idx)
    emit_exchanges("sampled-middle", mid_idx)
    emit_exchanges("last", last_idx)

    out(f'\n<most-edited-files top="{args.top_files}">\n')
    for fp, c in sorted(edit_counts.items(), key=lambda kv: -kv[1])[: args.top_files]:
        out(f'  <file edits="{c}">{esc(fp)}</file>\n')
    out("</most-edited-files>\n")

    out("\n<last-tool-calls>\n")
    for name, arg in recent_tools[-8:]:
        out(f'  <call tool="{esc(name)}">{esc(arg)}</call>\n')
    out("</last-tool-calls>\n")

    out("\n<final-agent-message>\n")
    out(clip("\n".join(last_assistant_text), 2000) + "\n")
    out("</final-agent-message>\n")


if __name__ == "__main__":
    main()
