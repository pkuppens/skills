# Issues

The work that remains. File these issues after the interview, not before it.
Filing issues before the session has no value for the audience.

The full specifications are in `tmp/github/issue-descriptions/workshop-*.md`.
That directory is local only, because `tmp/` is in `.gitignore`.

## Label

Create the label one time:

```bash
gh label create workshop \
  --description "Workshop and teaching material" \
  --color 5319e7
```

Give each issue the `workshop` label. Give each issue one of `documentation` or
`enhancement`. Give the epic the `epic` label. Use `--assignee @me` on every
issue.

## The set

| Issue | Title | Priority | State |
| --- | --- | --- | --- |
| Epic | AI-assisted refactoring of large legacy code bases | P0 | To file |
| 1 | feat: skill `legacy-build-container` | P0 | **Done on this branch** |
| 2 | feat: skill `call-site-exhaustiveness` | P0 | **Done on this branch** |
| 3 | feat: skill `oracle-first-refactor` | P1 | **Done on this branch** |
| 4 | feat: skill `golden-output-regression` | P1 | Specification ready |
| 5 | feat: skill `intent-layer-reconstruction` | P1 | Specification ready |
| 6 | feat: skill `legacy-cpp-modernize` | P2 | Specification ready |
| 7 | docs: notebooks `00` and `01` | P0 | To do |
| 8 | docs: notebook `01a`, the call-site comparison | P0 | To do |
| 9 | docs: notebooks `02`, `03`, `04`, `06` | P1 | To do |
| 10 | build: C++ container and the DCMTK subset build | P1 | To do |
| 11 | fix: open the prepared pull request on fo-dicom | P2 | After the interview |
| 12 | docs: curated bundle `legacy-refactor` | P2 | After the interview |

## Rules for these issues

These rules come from the [root CLAUDE.md](../../CLAUDE.md).

- Keep each issue small. Each issue must close on its own merits.
- Write acceptance criteria that an inspection can verify. Name the command or
  the file.
- Do not repeat the scope of another issue. Link to it instead.
- Put a decision with a long effect in `docs/decisions/`, not in an issue.

## Filing order

1. Create the label.
2. File the epic.
3. File the children. Reference the epic in each child.
4. Replace each placeholder in the specifications with the real issue number.
5. Update the checklist in the epic.

## After the interview

- Open the pull request on fo-dicom.
- Promote the remaining specifications to skills.
- Decide whether `MISSION.md` must name migration work. It does not name it
  now.
- Consider a curated `legacy-refactor` bundle that holds the six skills.
