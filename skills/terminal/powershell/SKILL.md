---
name: powershell
description: >-
  PowerShell 5.1 and 7+ command syntax: pipelines, redirection, here-strings,
  backtick continuation, and copy-paste-safe blocks. Use when the detected shell
  is PowerShell or when writing .ps1 scripts on Windows or cross-platform PS 7+.
---

# PowerShell

PowerShell syntax for live commands and `.ps1` scripts. Activate via [terminal/SKILL.md](../SKILL.md) after context detection.

## Version awareness

| Edition | Version | Notes |
|---------|---------|-------|
| Windows PowerShell | 5.1 | `$PSVersionTable.PSEdition` = `Desktop`; Windows only |
| PowerShell | 7+ | `$PSVersionTable.PSEdition` = `Core`; cross-platform |

Probe:

```powershell
$PSVersionTable.PSVersion
$PSVersionTable.PSEdition
```

When docs say "PowerShell" without version, write 7+-compatible syntax when possible; note 5.1 gaps.

## Copy-paste rules (live)

- Comments: `#` only — not `REM`
- Line continuation: backtick `` ` `` as last character on line
- No prose inside fenced blocks
- Prefer single-quoted strings when no expansion needed

Multiline example:

```powershell
Get-ChildItem -Path . `
  -Filter *.md `
  | Select-Object Name
```

## Pipelines and redirection

```powershell
Get-Process | Where-Object CPU -gt 100
command 2>&1 | Out-File log.txt
command *> log.txt
```

Operators: `|`, `;`, `&&`, `||` (7+), `-and`, `-or`.

## Variables and paths

```powershell
$env:PATH
$env:USERPROFILE
Join-Path $PSScriptRoot 'config.json'
```

Inspect commands:

```powershell
Get-Command node
Get-Command git -ErrorAction SilentlyContinue
```

## Here-strings (scripts and paste)

```powershell
@'
Line one
Line two
'@

@"
Hello $env:USERNAME
"@
```

Use `@' ... '@` when content must be literal (no expansion).

## Admin and elevation

Prefer non-admin. See [admin-elevation.md](references/admin-elevation.md).

Elevated one-liner (offer explicitly):

```powershell
Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command "yourcommand"'
```

## Script conventions

```powershell
#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Target
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
```

## Copy-paste vs documentation

- **Live:** one fence, detected PS version when known
- **Docs:** separate **Windows PowerShell 5.1** and **PowerShell 7+** sections when syntax differs

## Additional resources

- [admin-elevation.md](references/admin-elevation.md)
