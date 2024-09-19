#!/usr/bin/env bash

# Install
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.1

# Setup bash
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc

# Setup fish
mkdir -p ~/.config/fish
echo 'source ~/.asdf/asdf.fish' >> ~/.config/fish/config.fish
mkdir -p ~/.config/fish/completions
ln -s ~/.asdf/completions/asdf.fish ~/.config/fish/completions

# Setup zsh
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.zshrc
echo 'fpath=(${ASDF_DIR}/completions $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc

# Activate asdf
. "$HOME/.asdf/asdf.sh"

# Install and activate asdf plugins
PLUGINS=(
  "air"
  "bat"
  "bottom"
  "bun"
  "delta"
  "dust"
  "eza"
  "fd"
  "golang"
  "jq"
  "lazygit"
  "neovim"
  "nodejs"
  "pnpm"
  "ripgrep"
  "xh"
)
for PLUGIN in "${PLUGINS[@]}"; do
  asdf plugin add "$PLUGIN"
  asdf install "$PLUGIN" latest
  asdf global "$PLUGIN" latest
done

#git clone --depth=1 https://github.com/mattmc3/antidote.git ${ZDOTDIR:-~}/.antidote

