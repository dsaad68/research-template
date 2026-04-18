# Linux Setup Guide

Complete walkthrough to set up **research-template** on Linux (Ubuntu/Debian, Fedora/RHEL, Arch, openSUSE). Works on `x86_64` and `arm64`.

> Commands assume `bash` or `zsh`. The shell name decides which file installers update (`~/.bashrc` for bash, `~/.zshrc` for zsh).

---

## 0. Open a terminal

`Ctrl + Alt + T` on most desktop environments. Check your shell:

```bash
echo $SHELL
```

---

## 1. Install Git

### Check if Git is installed

```bash
git --version
```

If you see a version number → skip to step 2.

### Install per distro

**Ubuntu / Debian / Mint / Pop!_OS**

```bash
sudo apt update
sudo apt install -y git
```

**Fedora / RHEL 8+ / CentOS Stream / Rocky / Alma**

```bash
sudo dnf install -y git
```

**Arch / Manjaro / EndeavourOS**

```bash
sudo pacman -S --needed git
```

**openSUSE**

```bash
sudo zypper install -y git
```

**Alpine**

```bash
sudo apk add git
```

### Verify

```bash
git --version
```

### One-time Git config

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

### (Optional) Install Git Credential Manager

Useful if you push to GitHub frequently:

```bash
# GCM is distributed via dotnet on Linux; an easier path is to use SSH keys.
ssh-keygen -t ed25519 -C "you@example.com"
cat ~/.ssh/id_ed25519.pub        # then add this to GitHub → Settings → SSH keys
```

---

## 2. Install uv

`uv` is Astral's fast Python package and environment manager.

### Option A — Standalone installer (recommended, distro-agnostic)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you don't have `curl`:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

This installs `uv` and `uvx` to `~/.local/bin` and appends a `PATH` line to your shell profile.

### Option B — Homebrew on Linux

```bash
brew install uv
```

(Requires [Homebrew on Linux](https://brew.sh/).)

### Option C — Cargo (if you have a Rust toolchain)

```bash
cargo install --locked uv
```

### Option D — pipx

```bash
pipx install uv
```

### Verify

Open a **new terminal** (so the updated `PATH` loads), then:

```bash
uv --version
uvx --version
```

If `uv: command not found`, ensure `~/.local/bin` is on your `PATH`:

```bash
# bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### (Optional) Shell autocompletion

```bash
# bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
echo 'eval "$(uvx --generate-shell-completion bash)"' >> ~/.bashrc
source ~/.bashrc

# zsh
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
echo 'eval "$(uvx --generate-shell-completion zsh)"' >> ~/.zshrc
source ~/.zshrc

# fish
uv generate-shell-completion fish > ~/.config/fish/completions/uv.fish
uvx --generate-shell-completion fish > ~/.config/fish/completions/uvx.fish
```

### Updating uv later

```bash
uv self update     # standalone installer
brew upgrade uv    # Homebrew
```

---

## 3. Install APM (Agent Package Manager)

APM requires Git (step 1). Python 3.10+ is only needed for the `pip` install method.

### Option A — Quick install script (recommended)

```bash
curl -sSL https://aka.ms/apm-unix | sh
```

Auto-detects architecture (x86_64 or arm64), downloads the binary, and configures `PATH`.

### Option B — Homebrew on Linux

```bash
brew install microsoft/apm/apm
```

### Option C — pip (requires Python 3.10+)

```bash
uv tool install apm-cli
```

`uv tool install` installs `apm` as a globally-available CLI in an isolated environment.

### Option D — Manual binary

1. Download from <https://github.com/microsoft/apm/releases/latest> (`apm-linux-x86_64.tar.gz` or `apm-linux-arm64.tar.gz`).
2. Extract and link:
   ```bash
   tar -xzf apm-linux-*.tar.gz
   sudo mv apm /usr/local/bin/apm
   sudo chmod +x /usr/local/bin/apm
   ```

### Verify

Open a **new terminal**:

```bash
apm --version
```

---

## 4. Clone and set up the project

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

## 5. Verify the full setup

```bash
git --version
uv --version
apm --version
```

All three should print a version number.

---

## Troubleshooting (Linux)

**`command not found: uv` / `apm`**
Open a new terminal. Installers update `~/.bashrc` or `~/.zshrc` only for new sessions. If it still fails:

```bash
echo $PATH
ls ~/.local/bin
```

Add `~/.local/bin` to `PATH` (see step 2 verify section).

**Permission denied installing to `/usr/local/bin`**
Don't `sudo` the user installers. Either use the default user-local install path (`~/.local/bin`), or for the manual download, place the binary under `~/bin` and add it to `PATH`.

**Old Git on RHEL / CentOS 7**
Stock repos ship Git 1.x. Use the [IUS repo](https://ius.io/) or build from source if you need a modern version.

**SSL certificate errors behind a corporate proxy**

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
export HTTP_PROXY=http://proxy.example.com:8080
git config --global http.proxy http://proxy.example.com:8080
```

**`apm install` fails cloning a dependency**
Most APM dependencies are GitHub repos. Check that `git clone https://github.com/anthropics/skills.git /tmp/test-clone` works from your shell. If your org requires SSH, configure an SSH key and ensure GitHub uses it (`ssh -T git@github.com`).

**WSL users**
WSL2 with an Ubuntu/Debian distro is the easiest Windows option. Install everything inside WSL using the Linux instructions above. Avoid mixing Windows-installed and WSL-installed copies of the same tool — they'll fight over PATH.

**`apm` runs but can't write files inside the project**
Check ownership:
```bash
ls -la
sudo chown -R "$USER":"$USER" .
```

This usually happens after running `apm install` with `sudo` once by mistake.
