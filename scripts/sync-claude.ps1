# Symlink .apm/ primitives into .claude/ so Claude Code discovers them natively.
# Windows counterpart to scripts/sync-claude.sh. Workaround for APM <=0.8.11,
# which does not yet deploy local `.apm/` content to `.claude/` during
# `apm install --target claude`. See microsoft/apm#94.
#
# Run from the repo root: `apm run sync-claude:win`
# (or `pwsh -File scripts/sync-claude.ps1`). Safe to re-run.
#
# Symlinks on Windows require either Administrator privileges OR Developer
# Mode enabled (Settings > Privacy & security > For developers > Developer
# Mode). Directory symlinks fall back to junctions automatically.

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

New-Item -ItemType Directory -Force -Path ".claude\skills" | Out-Null
New-Item -ItemType Directory -Force -Path ".claude\agents" | Out-Null

# Skills: .apm\skills\<name>\  ->  .claude\skills\<name>  (directory link)
Get-ChildItem -Path ".apm\skills" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $name   = $_.Name
    $target = $_.FullName
    $link   = Join-Path ".claude\skills" $name
    if (Test-Path -LiteralPath $link) { Remove-Item -LiteralPath $link -Recurse -Force }
    try {
        New-Item -ItemType SymbolicLink -Path $link -Target $target | Out-Null
    } catch {
        # Fallback: directory junction (no elevation required on any Windows version)
        New-Item -ItemType Junction -Path $link -Target $target | Out-Null
    }
    Write-Host "skill:  $link -> $target"
}

# Agents: .apm\agents\<name>.agent.md  ->  .claude\agents\<name>.md  (file link)
Get-ChildItem -Path ".apm\agents" -Filter "*.agent.md" -File -ErrorAction SilentlyContinue | ForEach-Object {
    $name   = $_.BaseName -replace '\.agent$',''
    $target = $_.FullName
    $link   = Join-Path ".claude\agents" "$name.md"
    if (Test-Path -LiteralPath $link) { Remove-Item -LiteralPath $link -Force }
    New-Item -ItemType SymbolicLink -Path $link -Target $target | Out-Null
    Write-Host "agent:  $link -> $target"
}

Write-Host "[+] Sync complete."
