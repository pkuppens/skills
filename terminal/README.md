# Terminal Skill

This skill provides terminal execution capabilities for Claude Code. It allows executing shell commands and scripts in various environments (bash, PowerShell, cmd).

## Features

- Cross-platform command execution (bash, PowerShell, cmd)
- Script execution capabilities
- Environment variable support
- Error handling and output capture

## Usage

The terminal skill can be used to execute shell commands and scripts directly from Claude Code. It supports:

- Running individual commands
- Executing multi-line scripts
- Handling different shell environments
- Capturing command output and errors

## Examples

```bash
# Execute a simple command
ls -la

# Run a script file
./script.sh

# Execute PowerShell commands
Get-ChildItem
```

## Configuration

The skill supports configuration through environment variables:
- `TERMINAL_TIMEOUT` - Command execution timeout in milliseconds (default: 30000)
- `TERMINAL_MAX_OUTPUT` - Maximum output size in characters (default: 100000)