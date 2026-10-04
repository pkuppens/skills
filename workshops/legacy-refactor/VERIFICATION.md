# Verification

How to prove that the workshop works. Verify each item by inspection or by a
command. Do not assume an item.

## Rule

A claim without a command is an opinion. Each claim in
[THESIS.md](THESIS.md) must have one command that the audience watches, or one
stored cell output that the audience can read.

## Claim verification

| Claim | Verified by | Where |
| --- | --- | --- |
| 1. It is an oracle problem | The readiness table names the oracle that each code base has and does not have. | `01_precondition_checks` |
| 2. The compiler finds the call sites | Two counts on one screen: the text-search count and the compiler count. The sets differ. | `05_refactoring` |
| 3. Static types are an asset | The compiler produces the list without extra work. No oracle was written first. | `05_refactoring` |
| 4. A green test run is not proof | One deliberate failure of the output comparison, while the build and the unit tests stay green. | `03_test_driven_development` |
| 5. Reconstruct the intent first | A glossary and an invariant list exist, and each entry names the code that supports it. | `02_requirements_engineering` |
| 6. The context discipline is auditable | The stored transcript shows that no file was opened before a tool named the lines. | Every notebook |

## Acceptance checks

Run these checks before the session. Each check must pass.

### The repository

- [ ] The directory is on the default branch, or the branch is named in the URL
      that the audience receives.
- [ ] The URL opens in a browser without a login.
- [ ] Each notebook shows stored output in the browser.
- [ ] No notebook contains output that its cell did not produce.
- [ ] `npx --yes skills-ref validate skills/<name>` passes for each new skill.
- [ ] `skills/SKILL_TREE.md` lists each new skill.
- [ ] `.claude-plugin/marketplace.json` lists each new skill as a plugin.

### Offline operation

Switch the network off. Then run these checks.

- [ ] Each notebook opens and shows its stored output.
- [ ] `docker load` restores each image from the local file.
- [ ] `dotnet build --no-restore` completes for the C# example.
- [ ] The text-search count and the compiler count are readable from stored
      output, without a new run.

### The demonstration laptop

- [ ] The repository is cloned to the laptop.
- [ ] The saved images are on the laptop disk, not on removable media.
- [ ] `00_setup` runs offline.
- [ ] `05_refactoring` runs offline.
- [ ] The font size is readable from the back of the room.
- [ ] The screen resolution works with the projector.

### Content

- [ ] The limits of claim 2 are written in the notebook, not only spoken.
- [ ] The version-control limit is named: this method needs cheap branches and
      bisect.
- [ ] The confidentiality answer is ready. See
      [ADR 003](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md).
- [ ] Each notebook has the standard header cell.
- [ ] Each notebook can be read alone.

## Fallbacks

| Failure | Action |
| --- | --- |
| No network and no model API | Use the stored output. This is the designed path. It is not a degraded path. |
| `dotnet restore` tries to reach the network | Use `--no-restore` with the vendored package folder. |
| Docker does not start | Read the notebooks. No part of the argument needs a live run. |
| An image is missing | Restore it with `docker load` from the local file. |
| A build fails on stage | Continue. Point at the stored output. Do not debug on stage. |
| The agent is slow or unavailable | The compiler output alone proves claims 2 and 3. Read the stored diff. |
| A question uses 20 minutes | Remove block `04`, then `02`, then `03`. |
| The projector shows a wrong resolution | Use a large font. Show the terminal and the notebook only. |
