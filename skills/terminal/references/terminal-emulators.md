# Terminal emulators (reference)

Phase 2 will expand this document. Phase 1 stub: detection and routing only.

## Role

Terminal emulators host shell sessions. Agents route **syntax** to shell sub-skills (cmd, powershell, bash). Use this file when the user names an emulator or README declares **Terminal:**.

## Common emulators

| Emulator | Typical OS | Notes |
|----------|------------|-------|
| **Windows Terminal** | Windows | Default tabbed host over cmd, PowerShell, or WSL profiles |
| **cmux** | macOS | [cmux](https://cmux.com/) — multiplexer with tabs/splits (like tmux on Linux) |
| **tmux** | Linux, macOS, WSL | Multiplexer; commands run inside panes still use the configured shell |
| **zellij** | Linux, macOS, WSL | Multiplexer alternative to tmux |
| **iTerm2** | macOS | Tabbed terminal; shell syntax unchanged |
| **WezTerm** | Cross-platform | Config-driven profiles |
| **Alacritty**, **Ghostty**, **Kitty** | Cross-platform | GPU terminals; shell syntax unchanged |

## Detection

1. README **Development environment** → **Terminal:** field
2. `.vscode/settings.json` → `terminal.integrated.defaultProfile.*` and profile `source` / `icon`
3. User message mentions emulator by name

## Agent behavior

- Do **not** load a separate skill per emulator
- Paste blocks remain shell-native (cmd `^`, PowerShell `` ` ``, bash `\`)
- Multiplexer shortcuts (attach, split) are out of scope unless user asks

## Phase 2

Full paste quirks, config paths, and cmux vs tmux workflow notes will be added in Epic #10 Phase 2.
