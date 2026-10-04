# Preparation tasks

Each task has a limit and a gate. Stop a task at its limit. Do not continue a
task after its limit.

The tiers set the order. Tier A must be complete. Tier B is next. A tier C item
can ship as a Markdown file that states the plan.

Terms used here ([test oracle](../../CONTEXT.md#language-legacy-refactoring) and the rest) have one definition for this
repository. Follow the link before you use them in a report.

**Rule: never store output that a cell did not produce.** A notebook that is
marked as "not run" is acceptable. A notebook with invented output is not.
The same rule applies to the learned-environments file of a skill.

## Tier A — the session fails without these

| # | Task | Limit | Gate |
| --- | --- | --- | --- |
| A1 | Publish this directory. Send the URL to the audience before the session. | 20 min | The URL opens in a browser. |
| A2 | Choose the fo-dicom tag and the target member. Count the call sites. Find one call site that only reflection reaches. | 45 min | A member name, a count, and one invisible site. |
| A3 | Make the C# path work without a network. Vendor the packages. Add a local `nuget.config`. Run `dotnet build --no-restore`. | 45 min | A green build with the network switched off. |
| A4 | Run `05_refactoring`. Store the two counts and the missed call site. | 2 h | Two clean runs. The output is committed. |
| A5 | Write the `legacy-build-container` skill, with its learned-environments file. | 1.5 h | The skill validates. A notebook uses it. |
| A6 | Run `00_setup` and `01_precondition_checks`. | 1.5 h | Tier A is complete and pushed. |
| A7 | Write the `call-site-exhaustiveness` skill. | 1 h | The skill validates. |
| A8 | Write ADR 002 and ADR 003. | 45 min | Both files exist. The notebooks link to them. |
| A9 | Test the portability. Clone to the demonstration laptop. Run `00_setup` and `05_refactoring` with no network. Save the images with `docker save`. | 45 min | The laptop runs both notebooks offline. |

## Tier B — the session is better with these

| # | Task | Limit | Gate |
| --- | --- | --- | --- |
| B1 | Build the C++ image. Build the DCMTK `ofstd` and `dcmdata` targets. Check the package mirror first. | until 16:00, hard stop | A green subset build, or a screenshot and a note. |
| B2 | Write the `oracle-first-refactor` skill. | 1 h | The skill validates. It links to `call-site-exhaustiveness`. |
| B3 | Run `03_test_driven_development`. Show one pass and one deliberate failure. | 1.5 h | Both results are stored. |

Task B1 is the only task that can fail without damage to the session. Reduce it
in this order: a smaller subset; a newer compiler, with the difference stated
clearly; a stored build log; a screenshot.

## Tier C — ship as a plan

| # | Task | Gate |
| --- | --- | --- |
| C1 | `02_requirements_engineering` | Executed, or marked as not run. |
| C2 | `04_bug_investigation` | Executed, or marked as not run. |
| C3 | `06_transfer` | The pinned install command, with its verify output. |
| C4 | Verify the installation in a clean user profile. | The verify output lists the skills. |
| C5 | Add a minimal `.pre-commit-config.yaml`: whitespace and end-of-file hooks, plus the skills validation that CI already runs. Leave `nbstripout` commented out, with the reason beside it. | `pre-commit run --all-files` passes, and `grep -n nbstripout .pre-commit-config.yaml` shows only commented lines. |

## Known traps

| Trap | Action |
| --- | --- |
| `dotnet restore` needs a network. | Vendor the packages. Use `--no-restore`. Test with the network switched off, not merely idle. |
| Old Linux distributions moved their package servers. | Use `old-releases.ubuntu.com`, or Debian with `archive.debian.org`. Settle this in the first 20 minutes of task B1. |
| A tool that strips notebook output deletes the offline fallback. | `pre-commit` is fine; `nbstripout` is not. Keep it absent or excluded for `workshops/`. See [notebooks/README.md](notebooks/README.md) and task C5. |
| A USB port can be blocked by policy. | Keep the saved images on the laptop disk. |
| A new skill must pass CI. | Run `npx --yes skills-ref validate skills/<name>` before the commit. |
| A new skill must be registered twice. | Add it to `skills/SKILL_TREE.md` and to `.claude-plugin/marketplace.json`. |
