#!/usr/bin/env bash

# Install
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.1

# Setup bash
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc

# Setup fish
mkdir -p ~/.config/fish
echo 'set --export ASDF_DIR $HOME/.asdf'
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

# If Go is already installed on the system (e.g. Codespaces), the built-in
# install interferes with the asdf install.
unset GOPATH
unset GOROOT
echo "export GOPATH=$(go env GOPATH)" >> ~/.bashrc
echo "export GOROOT=$(go env GOROOT)" >> ~/.bashrc
echo "export GOPATH=$(go env GOPATH)" >> ~/.zshrc
echo "export GOROOT=$(go env GOROOT)" >> ~/.zshrc
echo "set --export GOPATH (go env GOPATH)" >> ~/.config/fish/config.fish
echo "set --export GOROOT (go env GOROOT)" >> ~/.config/fish/config.fish
