# Windows admin and elevation

Prefer non-admin. Use elevation only when required and with user awareness.

## Detect elevation (approximate)

```bat
net session >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Running elevated
) else (
    echo Not elevated
)
```

Treat result as hint, not guarantee.

## Operations that often need elevation

| Operation | Non-admin alternative |
|-----------|------------------------|
| `mklink /D` symlink | Developer Mode + user symlink, or junction where possible |
| Write `C:\Program Files\...` | Install to user dir or `%LOCALAPPDATA%` |
| `reg add HKLM\...` | `HKCU\...` when sufficient |
| Install system service | Document manual admin step |

## Elevated patterns (offer, do not default)

**New elevated cmd window:**

```bat
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c yourcommand'"
```

**runas (different user):**

```bat
runas /user:DOMAIN\User "cmd /c yourcommand"
```

Prompts for password — never embed credentials.

## mklink

Directory symlink (often needs Admin or Developer Mode):

```bat
mklink /D "link" "target"
```

Junction (no admin for local paths on many setups):

```bat
mklink /J "link" "target"
```

## Agent rules

1. Try non-admin path first
2. State why elevation is needed
3. Never assume admin in copy-paste blocks without labeling **Admin required**
4. For IDE agent Shell tool: prefer commands that work in current non-elevated session
