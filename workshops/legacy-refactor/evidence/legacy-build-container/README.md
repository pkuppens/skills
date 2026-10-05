# Evidence — `/legacy-build-container` from a foreign project root

This directory holds the output of one real run. The run happened on
2026-10-05. Nothing here was written by hand, except this file.

**The claim under test.** The skill
[`legacy-build-container`](../../../../skills/legacy-build-container/SKILL.md)
can be started in the root of a project it has never seen, work out which
toolchain that project needs, and produce a container build with instructions.

**How it was tested.** Clone fo-dicom 4.0.8. Install the skill into the clone.
Start one Claude Code session in the clone root, with the single prompt
`/legacy-build-container`. Keep everything the session produced.

## What is in here

| File | What it is |
| --- | --- |
| [`transcript.md`](transcript.md) | every tool call and every word, in order, rendered for reading |
| [`session.jsonl`](session.jsonl) | the raw record of the session. `transcript.md` is generated from this file |
| [`Dockerfile`](Dockerfile) | written by the session |
| [`BUILD.md`](BUILD.md) | written by the session: commands, measurements, the offline proof |
| [`nuget.offline.config`](nuget.offline.config) | written by the session |

The session also wrote `nuget-feed/` (22 `.nupkg` files, 11 MB) and a
`.gitignore`. The feed is not committed here, because 11 MB of third-party
packages is not evidence of anything. `BUILD.md` holds the command that
rebuilds it.

## Repeating it

```bash
# 1. A clone, at a fixed tag. Any directory outside this repository will do.
git clone --depth 1 --branch 4.0.8 https://github.com/fo-dicom/fo-dicom.git
cd fo-dicom

# 2. The skill, installed into the clone.
npx --yes skills add pkuppens/skills --skill legacy-build-container -y -a claude-code

# 3. One session, one prompt, in the clone root.
claude -p "/legacy-build-container" \
  --allowedTools "Skill,Bash,Read,Write,Edit,Glob,Grep,TodoWrite" \
  --permission-mode acceptEdits
```

**One honest difference.** Step 2 above is the published install command, and
it installs the skill from `main`. This run used the version on the
`philips-workshop` branch, copied straight into
`.claude/skills/legacy-build-container/`. The command above is correct once the
branch is merged.

`--permission-mode acceptEdits` is what makes the run unattended. A person at a
terminal answers the prompts instead and gets the same result.

## What the run produced

```text
Base image:   mcr.microsoft.com/dotnet/sdk:8.0@sha256:78235e09001f52b6592c45...
Target built: FO-DICOM.Core -> fo-dicom.core.dll, netstandard2.0, 1540096 bytes
Build matrix: ["FO-DICOM.Core/netstandard2.0"]
Build time:   image 0.9 s; restore 5.7 s online, 5.3 s offline; build 7.1 s
Network:      not needed after the image exists, proved with a negative control
Warnings:     0 errors, 11 warnings, 5 distinct codes
Session:      22 tool calls, 24 turns, 310 s, USD 2.05
```

## What this proves

1. **The skill works from a cold start in a foreign repository.** The session
   had no prior knowledge of fo-dicom. It read the `.csproj` files, found
   `netstandard2.0` and `LangVersion 8.0`, and chose the SDK from that.
2. **It followed the rules it was given.** It picked the newest image that
   still builds the target rather than an old one, pinned that image by digest,
   mounted the source instead of copying it, wrote the one-entry build matrix
   down, and kept every file it wrote inside `build-container/`.
3. **It proved the offline claim instead of asserting it.** Cold cache,
   `<clear />`, `--network none`, and a negative control that fails. That is
   the discipline the skill asks for in Step 8, applied without a reminder.
4. **It proposed a row and stopped.** It did not edit
   `verified-environments.md`. Rule 6 says a human merges that, and it asked.

## What this does not prove

- **Not a hard case.** fo-dicom 4.0.8 is SDK-style C# that a current SDK builds
  directly. The skill exists for the case where no current toolchain works, and
  that case is still only shown on the small C++ fixture in
  [`00_setup.ipynb`](../../notebooks/00_setup.ipynb). A run against DCMTK is
  task B1 and has not happened.
- **Not the "cannot decide" path.** The skill has a report for the case where
  the repository holds no evidence. No run has exercised it.
- **One machine.** Windows 11, Docker 29.8.0 with Linux containers, 32 cores.
  The Git Bash path-rewriting trap in `BUILD.md` is a Windows symptom.
- **One matrix entry.** Any claim of complete recall from this build is limited
  to `FO-DICOM.Core/netstandard2.0`. `net462`, `netcoreapp2.1` and
  `netcoreapp3.1` were deliberately not built; `BUILD.md` says why.
