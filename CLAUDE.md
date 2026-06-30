# Dotfiles Configuration Notes

## Commit Directly to Main

Commit directly to `main` in this repo. It reflects the current state of my machine, so feature branches don't make sense here. Do not create branches or open PRs for changes.

## Dotter Template Handling

Dotter automatically treats files with `{{` as templates. For files that contain `{{` in their code (like Lua tables), disable templating by setting `type = "symbolic"` in `.dotter/global.toml`.

**Example:**
```toml
[nvim.files."nvim/lua/plugins/hop.lua"]
target = "~/.config/nvim/lua/plugins/hop.lua"
type = "symbolic"
```

## Directory Symlinks in setup.sh

For directories where programs create new files that should be tracked (e.g., fish's `funcsave` command), use the `ensure_dir_symlink` function in `setup.sh` instead of Dotter. This symlinks the entire directory so dynamically created files are automatically tracked in the repository.

## Git Destructive Operations

Do **not** use destructive git operations like `git checkout <file>` without first confirming you are sure what will be destroyed.

If you made a change to a file and you'd like to revert it, first use `git diff --shortstat <file>` at minimum to confirm the file only has your changes
and no pre-existing uncommitted changes.


