# Preparation tasks

Two events, not one. Plan for both.

| When | What | Travel |
| --- | --- | --- |
| Tuesday 2026-10-06, 13:00 | Preparation meeting, in person | 30 to 45 minutes each way |
| Wednesday 2026-10-07, 14:00 | Final interview and workshop, in person | 30 to 45 minutes each way |

Neither event is remote. There is no screen share, and there is no second
attempt from home. Everything must work from the laptop that goes in the bag.

## The time that really exists

| Day | Usable hours | Use it for |
| --- | --- | --- |
| Sunday 10-04 (today) | about 4 | The two tasks that remove risk: the offline proof, and `01`. |
| Monday 10-05 | about 8 | New content. This is the only full day. |
| Tuesday 10-06, morning | about 4 | Rehearse once. Prepare the questions. Then stop. |
| Tuesday 10-06, evening | about 4 | **Only** what the preparation meeting asked for. |
| Wednesday 10-07, morning | about 4 | Dry run and equipment. No new content. |

About 20 hours. That is more than the earlier plan assumed, because the earlier
plan read "2 days of effort" as "the interview is tomorrow". So
`03_test_driven_development` and the DCMTK build move from "cut first" to
"planned".

**Freeze: Tuesday 22:00.** After that, no new cells, no new skills, no new
claims. Wednesday morning is rehearsal and cables.

## The preparation meeting is a gate, not a rehearsal

This is the most valuable hour of the week, and the earlier plan ignored it.
Tuesday answers the questions that decide Wednesday. Do not arrive with a
finished workshop and no questions.

Bring: the two executed notebooks, on the laptop, working with no network.

Ask these, and write the answers down.

| Question | Why it changes the work |
| --- | --- |
| How long is my slot, and how much of it is questions? | The talk track assumes about 90 minutes of content. |
| Who is in the room, and how many? | C++ people, C# people, managers, or a mix. It sets which half leads. |
| What do you project onto, and which cable? | HDMI, USB-C, DisplayPort. Bring all three. |
| Is there a guest network, and does it allow outbound HTTPS? | Decides whether anything runs live, or everything is replayed. |
| May I run commands from my own laptop? | Some sites do not allow an unmanaged laptop on the projector. |
| Which half of your code base hurts more today, C++ or C#? | Decides the running order. |
| **May we run the precondition check against one of your own modules?** | The strongest possible close. It makes the workshop about them, not about fo-dicom. |

The last question is the one to prepare for. If they say yes, Tuesday evening
goes on making `01_precondition_checks` run against a path they name.

## Tier A — the workshop fails without these

| # | Task | State |
| --- | --- | --- |
| A1 | Publish the branch and open the pull request. | **Done.** PR #39. |
| A2 | Choose the target and count the call sites. | **Done.** fo-dicom 4.0.8, `AsyncManualResetEvent`, counts 62 / 8 / 6. No reflective call site exists for this target, and the notebook says so instead of inventing one. |
| A3 | Prove the C# build works with no network. | **Done.** Proved by configuration rather than by network state: a local feed with `<clear />` removes nuget.org, and the restore still succeeds into a cold package folder in under half a second, then builds green in about two seconds. A negative control with no feed fails with 6 × `NU1101`, so the pass was not an accident. See `00_setup`, step 6. **Still to do on the demo laptop:** the same run with the adapter physically off (task A9/A11). |
| A4 | Run `05_refactoring`. | **Done.** 9 of 9 cells, no errors. |
| A5 | Write `legacy-build-container` with its learned-environments file. | **Done.** Two verified rows, both from real runs. |
| A6 | Run `00_setup`. | **Done.** 8 of 8 cells. g++ 4.9.4, pinned by digest. |
| A7 | Write `call-site-exhaustiveness`. | **Done.** Validates. |
| A8 | Write the ADRs. | **Done.** 002, 003, and 004 for licensing. |
| A9 | Write and run `01_precondition_checks`: which rungs does a code base already have? | **To do. Sunday, 2 h.** The most reusable artifact for the audience. |
| A10 | Merge PR #39 into `main` and tag it. Both events then show one clean URL, and `/plugin install` resolves with no branch reference. | **To do. Tuesday morning, before the meeting.** |
| A11 | Full dry run, timed, with the network off. | **To do. Wednesday morning.** |
| A12 | Equipment check. See the list below. | **To do. Tuesday evening.** |

## Tier B — now realistic, no longer "cut first"

| # | Task | When | Gate |
| --- | --- | --- | --- |
| B1 | Build the DCMTK `ofstd` and `dcmdata` targets in the `gcc:4.9` container. This proves scale, where the fixture proves only the mechanism. | Monday, hard stop 16:00 | A green subset build, or a stored log and a note. |
| B2 | Write `oracle-first-refactor`. | — | **Done.** |
| B3 | Run `03_test_driven_development`: build the output comparison first, then show one pass and one deliberate failure. | Monday | Both results stored. **Claim 4 has no evidence without this.** |

B1 is still the only task that may fail without harming the session. Reduce it
in this order: a smaller target; a newer compiler with the difference stated
clearly; a stored build log; a screenshot.

## Tier C — if Monday goes well

| # | Task | Gate |
| --- | --- | --- |
| C1 | `02_requirements_engineering` | Executed, or marked `PLANNED`. |
| C2 | `04_bug_investigation` | Executed, or marked `PLANNED`. |
| C3 | `06_transfer`: the pinned install command with its verify output. | Cheap. Do it together with A10. |
| C4 | Verify the install in a clean user profile. | The verify output lists the skills. |
| C5 | Add a minimal `.pre-commit-config.yaml`: whitespace and end-of-file hooks, plus the skills validation that CI already runs. Leave `nbstripout` commented out, with the reason beside it. | `pre-commit run --all-files` passes, and `grep -n nbstripout .pre-commit-config.yaml` shows only comment lines. |

## Equipment, because both events are in person

| Item | Why |
| --- | --- |
| HDMI, USB-C and DisplayPort adapters | You do not know what is on the wall until you are in the room. |
| Charger, and a full battery | A 45-minute commute, then a 2-hour slot. |
| Images saved with `docker save`, on the laptop disk | Not on a USB stick. Their policy may block the port. |
| The repository cloned locally, on `main` | Not only on a branch. |
| Specimen cloned and packages restored | Tasks A3 and A9 make this safe offline. |
| A large terminal font, set in advance | Changing it live wastes a minute and looks unprepared. |
| A printed one-page command list | The last fallback if the projector refuses the laptop. |

If the projector fails completely, the room gathers around the laptop and reads
the notebooks. That still works, because the output is stored.

## Known traps

| Trap | Action |
| --- | --- |
| `dotnet restore` needs a network. | Vendor the packages, use `--no-restore`, and test with the adapter switched **off**, not merely idle. This is task A3. |
| Old Linux distributions moved their package servers. | Avoid the problem rather than working around it: use an image that already holds the compiler, such as `gcc:4.9`. Verified. |
| A tool that strips notebook output deletes the offline fallback. | `pre-commit` is fine; `nbstripout` is not. Keep it absent, or exclude `workshops/`. See [notebooks/README.md](notebooks/README.md) and task C5. |
| `error: true` under-reports call sites in C#. | Measured: 3 against 6. Promote the warning instead. See `05_refactoring`, step 4. |
| A new skill must pass CI. | Run `npx --yes skills-ref validate skills/<name>` before the commit. |
| A new skill must be registered twice. | In `skills/SKILL_TREE.md` and in `.claude-plugin/marketplace.json`. |

## The rule that outranks the schedule

**Never store output that a cell did not produce.** A notebook marked `PLANNED`
is acceptable. A notebook with invented output is a defect, and in a regulated
context it is worse, because the artifact becomes evidence.

Terms used here — [test oracle](../../CONTEXT.md#language-legacy-refactoring)
and the rest — have one definition for this repository. Follow the link before
you use them in a report.
