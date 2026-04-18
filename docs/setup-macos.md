# macOS Setup Guide

Complete walkthrough to set up **research-template** on macOS (Intel or Apple Silicon).

> Tested on macOS 12+ (Monterey and later). Works on both `x86_64` and `arm64` (M1/M2/M3/M4).

---

## 0. Open a Terminal

- Press `⌘ + Space`, type **Terminal**, press Enter.
- Or use [iTerm2](https://iterm2.com/), [Warp](https://www.warp.dev/), etc.

To check your shell:

```bash
echo $SHELL
```

Most modern macOS uses **zsh** (`/bin/zsh`). The shell name decides which file installers update (`~/.zshrc` for zsh, `~/.bash_profile` for bash).

---

## 1. Install Git

macOS often already has Git via the Xcode Command Line Tools.

### Check if Git is installed

```bash
git --version
```

If you see a version number → skip to step 2.

If not, macOS will prompt you to install the Command Line Tools. You can also trigger the install manually:

```bash
xcode-select --install
```

A GUI dialog opens — click **Install** and accept the license. This downloads ~1–2 GB and takes a few minutes.

### Alternative: install Git via Homebrew (newer version)

If you want a more recent Git than what Apple ships:

```bash
brew install git
```

(Install Homebrew first if you don't have it — see step 2.)

### Verify

```bash
git --version
# git version 2.4x.x
```

### One-time Git config

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

---

## 2. Install Homebrew (recommended package manager)

Homebrew makes installing the rest easier. Skip if you already have it.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After install, the script tells you to run two `eval` lines so `brew` is on your `PATH`. On Apple Silicon they look like:

```bash
echo >> ~/.zshrc
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"
```

On Intel Macs Homebrew lives in `/usr/local/bin` and is already on `PATH`.

Verify:

```bash
brew --version
```

---

## 3. Install uv

`uv` is Astral's fast Python package and environment manager.

### Option A — Homebrew (simplest)

```bash
brew install uv
```

### Option B — Standalone installer (no Homebrew)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This installs `uv` and `uvx` to `~/.local/bin` and adds that directory to your shell profile.

### Verify

Open a **new terminal**, then:

```bash
uv --version
uvx --version
```

### (Optional) Shell autocompletion for zsh

```bash
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
echo 'eval "$(uvx --generate-shell-completion zsh)"' >> ~/.zshrc
source ~/.zshrc
```

### Updating uv later

```bash
uv self update     # if installed via standalone installer
brew upgrade uv    # if installed via Homebrew
```

---

## 4. Install APM (Agent Package Manager)

APM requires Git (step 1). Python 3.10+ is only needed for the `pip` install method.

### Option A — Homebrew (recommended)

```bash
brew install microsoft/apm/apm
```

### Option B — Quick install script

```bash
curl -sSL https://aka.ms/apm-unix | sh
```

The installer detects your architecture (Intel vs. Apple Silicon), downloads the matching binary, and configures `PATH`.

### Option C — pip (requires Python 3.10+)

```bash
uv tool install apm-cli
```

(Using `uv tool install` keeps it isolated and globally available.)

### Verify

Open a **new terminal**:

```bash
apm --version
```

---

## 5. Clone and set up the project

```bash
# Clone (replace with the actual remote URL)
git clone <repo-url> research-template
cd research-template

# Install all APM dependencies declared in apm.yml
apm install
```

`apm install` will:

- Clone the `anthropics/skills/skills/pdf` skill into the project
- Wire up the local `./agents` directory
- Register the `parallel-search` and `deepwiki` MCP servers for Claude

---

## 6. Verify the full setup

```bash
git --version
uv --version
apm --version
```

All three should print a version number. Open the project in your editor:

```bash
code .   # if you use VS Code
```

---

## Troubleshooting (macOS)

**`command not found: brew/uv/apm`**
Open a new Terminal window. Installers append to `~/.zshrc` but the change only applies to new shells. If it still fails:

```bash
echo $PATH
```

For uv, ensure `~/.local/bin` is on `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**`xcrun: error: invalid active developer path` after a macOS update**
Reinstall Command Line Tools:

```bash
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install
```

**Apple Silicon: "bad CPU type in executable"**
You downloaded an Intel binary. Use Homebrew or the official installer scripts instead of manual downloads — they pick the right architecture.

**Permission denied during install**
Don't `sudo` Homebrew. For manual installs, prefer a user-writable location like `~/.local/bin` rather than `/usr/local/bin`.

**APM auth issues against private GitHub orgs**
Make sure you have a working `gh auth login` or an `~/.netrc` / SSH key configured. See APM's authentication docs.
