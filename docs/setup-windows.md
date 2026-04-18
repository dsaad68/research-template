# Windows Setup Guide

Complete walkthrough to set up **research-template** on Windows 10 or 11 (x86_64 or ARM64).

> All commands below use **PowerShell**. Open it from Start Menu → "Windows PowerShell" or "Terminal". For some commands you'll need an **Administrator** PowerShell (right-click → "Run as administrator").

---

## 0. Choose your terminal

Windows 11 ships with **Windows Terminal**. On Windows 10 install it from the Microsoft Store — it's a much better experience than the legacy console.

Check your PowerShell version:

```powershell
$PSVersionTable.PSVersion
```

PowerShell 5.1 (built-in) works for everything below, but PowerShell 7+ is recommended.

### Allow scripts to run (one-time)

Some installers below pipe a script into PowerShell. If you see "execution of scripts is disabled on this system", run this in an **Administrator** PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## 1. Install Git

### Check if Git is installed

```powershell
git --version
```

If you get a version number → skip to step 2.

### Option A — winget (recommended, ships with Windows 11)

```powershell
winget install --id Git.Git -e --source winget
```

### Option B — Official installer (most control)

1. Download from <https://git-scm.com/download/win>.
2. Run the installer. Recommended choices:
   - **Editor**: pick something other than `vim` (e.g., VS Code) unless you know vim.
   - **PATH adjustment**: choose **"Git from the command line and also from 3rd-party software"** so `git` works in PowerShell.
   - **Line endings**: **"Checkout Windows-style, commit Unix-style"** (`core.autocrlf=true`) — the safe default for cross-platform projects.
   - **Credential helper**: **Git Credential Manager** (default).
   - **Default branch**: `main`.

### Option C — Chocolatey

```powershell
choco install git
```

### Option D — Scoop

```powershell
scoop install git
```

### Verify

Close and reopen PowerShell, then:

```powershell
git --version
```

### One-time Git config

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

---

## 2. Install uv

`uv` is Astral's fast Python package and environment manager.

### Option A — Standalone installer (recommended)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

This installs `uv.exe` and `uvx.exe` to `%USERPROFILE%\.local\bin` and updates your user `PATH`.

### Option B — winget

```powershell
winget install --id=astral-sh.uv -e
```

### Option C — Scoop

```powershell
scoop install main/uv
```

### Verify

**Close and reopen PowerShell** (so `PATH` updates take effect), then:

```powershell
uv --version
uvx --version
```

### (Optional) PowerShell autocompletion

```powershell
Add-Content -Path $PROFILE -Value 'Invoke-Expression (& uv generate-shell-completion powershell | Out-String)'
Add-Content -Path $PROFILE -Value 'Invoke-Expression (& uvx --generate-shell-completion powershell | Out-String)'
. $PROFILE
```

If `$PROFILE` doesn't exist yet:

```powershell
if (!(Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
```

### Updating uv later

```powershell
uv self update           # standalone installer
winget upgrade astral-sh.uv
```

---

## 3. Install APM (Agent Package Manager)

APM requires Git (step 1). Python 3.10+ is only needed for the `pip` install method.

### Option A — Quick install script (recommended)

```powershell
irm https://aka.ms/apm-windows | iex
```

This downloads the matching binary (x86_64 or ARM64), places it in a user directory, and updates `PATH`.

### Option B — Scoop

```powershell
scoop bucket add apm https://github.com/microsoft/scoop-apm
scoop install apm
```

### Option C — pip (requires Python 3.10+)

```powershell
uv tool install apm-cli
```

### Option D — Manual download

1. Go to <https://github.com/microsoft/apm/releases/latest>.
2. Download `apm-windows-x86_64.zip` (or the ARM64 variant).
3. Extract to a permanent location, e.g. `C:\Tools\apm\`.
4. Add that folder to your user `PATH`:
   ```powershell
   [Environment]::SetEnvironmentVariable(
     "Path",
     [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Tools\apm",
     "User"
   )
   ```
5. Close and reopen PowerShell.

### Verify

```powershell
apm --version
```

---

## 4. Clone and set up the project

```powershell
# Pick a working directory
cd $HOME
mkdir Code -ErrorAction SilentlyContinue
cd Code

# Clone (replace with the actual remote URL)
git clone <repo-url> research-template
cd research-template

# Install all APM dependencies from apm.yml
apm install
```

`apm install` will:

- Clone the `anthropics/skills/skills/pdf` skill into the project
- Wire up the local `.\agents` directory
- Register the `parallel-search` and `deepwiki` MCP servers for Claude

---

## 5. Verify the full setup

```powershell
git --version
uv --version
apm --version
```

All three should print a version number. Open the project in your editor:

```powershell
code .   # if you use VS Code
```

---

## Troubleshooting (Windows)

**`'apm' is not recognized as an internal or external command`**
Close and reopen PowerShell — installers update `PATH` only for **new** shells. If it still fails:

```powershell
$env:Path -split ';'
```

Confirm the install directory (often `$HOME\.local\bin` or `C:\Tools\apm`) is listed. If not, add it via System Properties → Environment Variables → User `Path`, or:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";$HOME\.local\bin",
  "User"
)
```

**Script execution is disabled**

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Long path errors during `apm install` or `git clone`**
Enable long paths (Administrator PowerShell):

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
git config --global core.longpaths true
```

**Windows Defender / antivirus blocking installer**
Whitelist the install directory. The APM installer notes that you can set `APM_DEBUG=1` to see retry diagnostics for file-access errors:

```powershell
$env:APM_DEBUG = 1
apm install
```

**SSL / proxy errors behind a corporate network**
Configure proxy variables before running installers:

```powershell
$env:HTTPS_PROXY = "http://proxy.example.com:8080"
$env:HTTP_PROXY  = "http://proxy.example.com:8080"
```

**Line-ending warnings in Git**
This is normal on Windows with `core.autocrlf=true`. Ignore unless your editor is fighting the conversion.
