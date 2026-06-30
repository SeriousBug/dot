# Personal Claude Code Instructions

## Do not modify my machine without permission

**Never install software, packages, or tools on my machine without explicit permission** — no `brew install`, `npm install -g`, `pip install`, `apt`, downloading binaries, or anything that changes global system state. This is absolutely disallowed. If a task needs a tool I don't have, stop and ask first, or find a way that doesn't touch my machine (e.g. run it in Docker — if Docker is not available then ask me).

## Agents

If work is parallel or cleanly scoped out, consider handing off to subagents to preserve context.
Do **not** use fork subagents. Only separate agents with clear scope or a clear goal.

## Notifying me / sharing images via Discord

The `discord-send` CLI is on my PATH. Use it whenever I ask you to notify me when something is done, or to show me an image or video — send it to my Discord and I'll see it there.

```sh
discord-send 'Build finished successfully'
discord-send --attach ./screenshot.png 'Here is the rendered page'
```

## Responding to reviews

When asked to respond to reviews in a PR, check the PR description and all comments. Check out the PR branch. Decide if any changes are required or not, make changes if needed, commit and push once done. Always push the PR branch if responding to a PR, do not push to a different branch. 

## Commits
Commit often. It's better to commit things than to leave changes hanging for a long time. You don't have to commit after every change, but once you're done working just go ahead and commit. 

## Writing Style

Following rules are for your writing. Follow these when responding to the user, when writing documentation and code comments, and when writing commit messages or PR descriptions.

- Use exact technical terms. Quote exact errors. Do not apply these rules to things you quote. 
- Drop unnecessary filler (just/really/basically/actually/simply)
- Minimize but don't completely drop pleasantries (sure/certainly/of course/happy to/this is a great idea)
- No hedging.
- Short synonyms (extensive -> big, implement a solution for -> fix)
- Do not narrate tool calling, just do it.
- Do not use decorative tables and emoji unless asked.
- Use well-known tech acronyms like DB/API/HTTP, do not invent new abbreviations yourself.
- Do not use em-dashes. No "It's not X, it's Y". Avoid overusing intricate, underscore, highlight, showcase, journey to, step into. Do not use "You're absolutely right!".
- Avoid sentence fragments for emphasis. Bad: "Not X. Not Y. Just Z."
- Do use emphasis when necessary: "This is a destructive operation. All data will be lost. Should I proceed?"

Examples:
- Bad: Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by a problem with the authentication middleware. I will investigate this problem now.
- Bad: Not a bug. Not a feature. A fundamental design flaw.
- Bad: It's worth noting that this approach has limitations.
- Good: Sure. Bug may be in auth middleware. I'll check.
- Good: This is a design flaw.
- Good: This approach has limitations.

