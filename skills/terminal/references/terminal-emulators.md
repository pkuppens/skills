# Terminal emulators (reference)

Emulators and multiplexers **host** shell sessions; they don't change shell syntax. Route syntax to the shell leaf ([cmd](../cmd/SKILL.md), [powershell](../powershell/SKILL.md), [bash](../bash/SKILL.md), [zsh](../zsh/SKILL.md)). Use this file when the user names an emulator, README declares **Terminal:**, or pasted commands behave differently than expected.

## Common emulators

| Emulator | OS | Kind | Config |
|----------|----|------|--------|
| **Windows Terminal** | Windows | Tabbed host for cmd, PowerShell, WSL profiles | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json` (Store install) |
| **VS Code / Cursor terminal** | All | Integrated terminal | `settings.json` → `terminal.integrated.defaultProfile.{windows,osx,linux}` |
| **cmux** | macOS | Native terminal app (Swift/AppKit on libghostty) with sidebar tabs, splits, workspaces | `~/.config/cmux/cmux.json`; also reads Ghostty's `~/.config/ghostty/config` for theme/font |
| **iTerm2** | macOS | Tabbed terminal | `~/Library/Preferences/com.googlecode.iterm2.plist` (edit via Settings) |
| **Ghostty** | macOS, Linux | GPU terminal | `~/.config/ghostty/config` |
| **WezTerm** | All | Lua-configured terminal + built-in multiplexer | `~/.wezterm.lua` or `~/.config/wezterm/wezterm.lua` |
| **Alacritty** | All | GPU terminal, no tabs | `~/.config/alacritty/alacritty.toml` |
| **Kitty** | macOS, Linux | GPU terminal | `~/.config/kitty/kitty.conf` |
| **tmux** | Linux, macOS, WSL | Multiplexer inside any terminal | `~/.tmux.conf` or `~/.config/tmux/tmux.conf` |
| **zellij** | Linux, macOS, WSL | Multiplexer alternative to tmux | `~/.config/zellij/config.kdl` |

## Detection

1. README **Development environment** → **Terminal:** field ([context-detection](context-detection.md))
2. `.vscode/settings.json` → `terminal.integrated.defaultProfile.*` and profile `source` / `icon`
3. Environment: `$TERM_PROGRAM` (e.g. `iTerm.app`, `vscode`, `WezTerm`, `ghostty`), `$WT_SESSION` set in Windows Terminal, `$TMUX` set inside tmux, `$ZELLIJ` set inside zellij
4. User message mentions the emulator by name

## Paste behaviour

Multiline pastes are where emulator and shell interact. What matters:

| Situation | Effect | Rule for agent output |
|-----------|--------|-----------------------|
| **Bracketed paste** on (modern terminals with zsh, bash 5.1+ readline, PowerShell PSReadLine) | The whole block lands in the edit buffer; nothing runs until Enter | Multiline blocks are safe; the user sees them before running |
| **Bracketed paste** off (cmd.exe, old bash, some SSH/serial sessions) | Each newline executes immediately, so later lines run even if an earlier one failed | Chain dependent steps with `&&`, or give a script file instead of a long paste |
| **Windows Terminal** | Warns before pasting multiple lines or very large text (can be turned off in settings) | Expect the prompt; don't tell users to disable it |
| **Trailing newline** in copied block | Last command runs on paste when bracketed paste is off | Keep the fence content exactly the commands to run |
| **Smart quotes / non-breaking spaces** (copied from rendered docs, chat apps) | `“` `”` or U+00A0 break quoting and arguments | Emit plain ASCII quotes; fenced code blocks avoid typographic substitution |

Inside tmux/zellij, bracketed paste works when both the outer terminal and the multiplexer support it (current versions do).

## cmux vs tmux

| | cmux | tmux |
|-|------|------|
| What | Local macOS GUI terminal app | Multiplexer process inside any terminal |
| Where sessions live | The app on your Mac; restores windows, panes, working dirs and scrollback on relaunch | A tmux server; detach/attach, survives SSH disconnects, runs on remote hosts |
| Tabs / splits | Sidebar tabs (show git branch, cwd, ports), split panes, workspaces | Windows and panes (prefix key, default `Ctrl-b`) |
| Agent-oriented extras | Notification rings when an agent needs attention; built-in browser pane; CLI + Unix socket to create panes, send input, read screen contents | Scriptable via `tmux send-keys` / `capture-pane` |
| Combine | Run `tmux` inside a cmux pane for remote, persistent sessions | — |

For command output, both are transparent: the pane runs the user's shell, so route to that shell's leaf.

## Agent behavior

- Do **not** load a separate skill per emulator.
- Paste blocks stay shell-native (cmd `^`, PowerShell `` ` ``, bash/zsh `\`).
- Emulator config edits, keybindings, and multiplexer workflows (attach, split, cmux CLI/socket automation) only when the user asks.
