# PowerShell elevation

Prefer non-admin. Elevation only when required.

## Detect admin (Windows)

```powershell
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$isAdmin
```

On PowerShell 7+ on Linux/macOS, sudo is separate — see [bash references](../bash/references/sudo-elevation.md) when in WSL.

## Patterns (offer explicitly)

**Elevated process:**

```powershell
Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File C:\path\script.ps1'
```

**Run single command elevated:**

```powershell
Start-Process powershell -Verb RunAs -Wait -ArgumentList '-Command','Install-Module Foo -Scope AllUsers'
```

## Execution policy

Scripts may fail with `UnauthorizedAccess`. Prefer:

```powershell
powershell -ExecutionPolicy Bypass -File .\script.ps1
```

Document policy change only when user requests persistent change.

## Agent rules

1. Default to current-user scope (`-Scope CurrentUser`, `%LOCALAPPDATA%`)
2. Label blocks that require **Admin** or **Run as administrator**
3. Never store credentials in scripts; use `Get-Credential` or secret stores when user asks
