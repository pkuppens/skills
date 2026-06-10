---
name: cmd
description: >-
  Windows cmd.exe and batch file (.bat/.cmd) syntax for live CMD execution and batch
  script authoring: variables, control flow, pipes, redirection, multiline caret
  continuation, and copy-paste-safe blocks. Use when running cmd.exe commands, writing
  or editing .bat/.cmd files, Windows shell automation, or when the detected shell is
  cmd.exe. Replaces the external batch-files skill.
---

# Windows CMD

cmd.exe and batch file syntax for **live commands** and **`.bat`/`.cmd` script files**. Activate via [terminal/SKILL.md](../SKILL.md) after context detection.

## When to use

### Live execution

- cmd.exe one-liners or interactive paste blocks
- Agent Shell tool commands when probe or docs indicate cmd

### Script authoring

- Creating or editing `.bat` / `.cmd` files in the repo
- Windows Task Scheduler scripts, PATH-based CLI tools
- When README or probe indicates **Shell: cmd**

## Copy-paste rules (live)

- Comments: `REM` (preferred) or `::` — **not** `#`
- Line continuation: caret `^` as last character on line; next line continues
- No prose inside fenced blocks
- In batch **files**, use `%%` for `%` and `%%i` in `FOR` loops; on command line use single `%`

Example multiline paste (cmd.exe):

```bat
echo Line one^
 && echo Line two
```

Example with `REM`:

```bat
REM Install deps
npm install^
 && npm test
```

## Command interpretation (summary)

1. Variable substitution — `%VAR%`, `%0`–`%9`, `%*`
2. Quoting — `"path with spaces"`; caret `^` escapes `& | < > ^`
3. Pipelines — `|`, `&`, `&&`, `||`, `( )`
4. Redirection — `>`, `>>`, `<`, `2>`, `2>&1`, `>NUL`

Details: [syntax-reference.md](references/syntax-reference.md)

## Variables (essentials)

```bat
set _MY_VAR=Hello
echo %_MY_VAR%
setlocal EnableDelayedExpansion
set /a _COUNT+=1
echo !_COUNT!
endlocal
```

- No spaces around `=` in `set`
- Use `!VAR!` inside `( )` blocks when values change at runtime
- Script directory: `%~dp0`

## Control flow (essentials)

```bat
if exist "file.txt" echo found
if "%_A%"=="x" (echo match) else (echo no)
command1 && command2
command1 || (echo failed & exit /b 1)
for %%f in (*.txt) do echo %%f
```

## Pipes and redirection

```bat
dir /b *.log > list.txt
command 2>&1 | findstr /i error
command >NUL 2>&1
```

After a pipe, triple caret may be needed to escape: `echo x ^^^& y | findstr x`

## Inspect PATH and commands

```bat
where.exe node
where.exe git
echo %PATH%
```

When `where` finds nothing, suggest install path or `set PATH=...` for the session — document persistent changes with `setx` only when user wants that.

## Admin and elevation

Prefer non-admin commands. Operations that require elevation (for example `mklink /D`, some `reg` writes):

- Detect: `net session` succeeds only when elevated (approximate check)
- Offer elevated variant explicitly; never run silently

See [admin-windows.md](references/admin-windows.md).

## Script structure (minimal)

```bat
@echo off
setlocal EnableDelayedExpansion
call :main %*
exit /b %ERRORLEVEL%

:main
    echo Running...
    exit /b 0
```

## Best practices

1. `@echo off` + `setlocal` at top of scripts
2. Quote paths: `"%~dp0config.ini"`
3. `exit /b` not `exit` (avoid closing parent console)
4. Errors to stderr: `echo ERROR: msg 1>&2`
5. Prefer `ROBOCOPY` over legacy `XCOPY`

## Cross-platform escape hatch

For Linux tooling on Windows, route to [bash/SKILL.md](../bash/SKILL.md) (WSL2) or PowerShell — see [terminal/SKILL.md](../SKILL.md).

## Additional resources

- [syntax-reference.md](references/syntax-reference.md)
- [admin-windows.md](references/admin-windows.md)
