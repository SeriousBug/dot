---
name: new-work
description: Prepare the repo to start a new piece of work. Use this skill when the user asks to start a new task, begin new work, create a new branch, or start working on something new.
---

You are helping the user start a new piece of work in a git repository. Follow these steps in order:

## Step 1: Check for uncommitted changes

Run `git status --short` to check for uncommitted changes.

If there are uncommitted changes:
- Evaluate the changes:
  - If there are build artifacts, etc. then ignore them. If they are tracked by git, note for user that they might want to gitingore these.
  - If changes look important, such as code changes, new code files that are not empty, changes to build workflows etc., then ask user if they want to stash

## Step 2: Switch to main and pull latest

- Attempt to check out `main`, or failing that `master`.
- Then pull the latest changes.

You **must** do this. Unless instructed to continue on the same branch, make sure you start from latest main.

## Step 3: Create a new branch

Based on the description of the work the user has provided, create a short, descriptive, kebab-case branch name (e.g. `add-user-auth`, `fix-checkout-crash`, `refactor-api-client`).
Create and check out the new branch.
Once branch is created, proceed with work as usual.

