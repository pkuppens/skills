# CMD syntax reference

Extended reference for [../SKILL.md](../SKILL.md). Tables and edge cases not needed for every activation.

## Special variables

| Variable | Value |
|----------|-------|
| `%CD%` | Current directory |
| `%ERRORLEVEL%` | Exit code of last command |
| `%USERNAME%` | Current user |
| `%USERPROFILE%` | Profile path |
| `%TEMP%` / `%TMP%` | Temp directory |
| `%COMSPEC%` | Path to cmd.exe |
| `%~dp0` | Drive + path of batch file |

## Argument modifiers

| Syntax | Meaning |
|--------|---------|
| `%~1` | Arg 1, quotes stripped |
| `%~f1` | Full path |
| `%~nx0` | Batch file name + extension |
| `%~dp0` | Batch file directory |

## FOR loops

```bat
for %%i in (a b c) do echo %%i
for /l %%i in (1,1,10) do echo %%i
for %%f in (*.txt) do echo %%f
for /r %%f in (*.log) do echo %%f
for /f "tokens=*" %%a in ('command') do echo %%a
```

Use `%%` in batch files, `%` on interactive command line.

## Arithmetic

```bat
set /a _R=10 * 5
set /a _M=14 %% 3
```

Modulo in batch files: `%%` not single `%`.

## Error handling

```bat
mycommand || (echo failed & exit /b 1)
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
```

## Escape and multiline

| Case | Rule |
|------|------|
| Literal `&` in echo | `^&` |
| Line break in paste | `^` at end of line |
| `%` in batch file | `%%` |
| After `\|` in pipeline | May need `^^^` before special chars |

## Essential commands (quick)

| Area | Commands |
|------|----------|
| Files | `COPY`, `ROBOCOPY`, `MOVE`, `DEL`, `MKDIR`, `MKLINK` |
| Search | `FIND`, `FINDSTR`, `WHERE` |
| System | `TASKLIST`, `SC`, `REG`, `SETX` |
| Network | `PING`, `IPCONFIG`, `CURL` (Win10+) |

## Security

- Quote user input: `"%_INPUT%"`
- Never embed credentials in batch files
- Validate paths before `DEL` / `RD` / `ROBOCOPY /MIR`
