# Reverting a Dependabot merge that turned the base branch red

Disclosed reference for [`SKILL.md`](../SKILL.md) Step 9. Run it as soon as
the base-branch run after a merge concludes `failure` — don't wait to be
asked. Every change goes through a PR; never push to the base branch.

1. **Rule out flake.** Rerun the failed jobs once (`gh run rerun <run-id>
   --failed`). Green on the rerun → transient; report it and stop.
2. **Confirm it is ours.** The baseline from Step 7 was green, so a failure
   now is attributable to this pass. If it wasn't (the blocker was waived),
   compare the failing job against the baseline run before reverting.
3. **Find the merge.** Each merge triggers its own base-branch run; match
   runs to merge commits by `headSha`. The first merge whose run failed is
   the culprit — revert it and every later merge from this pass whose run
   is red or was cancelled/superseded. If the runs can't separate them,
   revert every merge from this pass.
4. **Revert through a PR**, never a direct push. A rebase merge can put
   several commits on base, so revert each PR's full range (from the base
   SHA before it merged to its `mergeCommit`), newest PR first:

   ```bash
   git fetch origin && git switch -c revert/dependabot-<pr-numbers> origin/<base>
   git revert --no-edit <pre-merge-sha>..<merge-commit>   # per PR, newest first
   git push -u origin revert/dependabot-<pr-numbers>
   gh pr create --repo <repo> --base <base> --assignee @me \
     --title "Revert Dependabot #<n>: <base> CI red after merge" \
     --body "Reverts #<n>. Failing run: <run-url>. ..."
   ```

   Check `git log <pre-merge-sha>..<merge-commit>` first: if it contains
   commits that are not from the PR being reverted, revert that PR's own
   commits by SHA instead of the range.
5. **Merge the revert when its CI is green** (`gh pr checks <n> --watch`,
   then `gh pr merge <n>` with the Step 0 strategy and `--delete-branch`), and watch the base run
   it triggers, as above. If the revert PR is also red, the failure is not
   from these bumps: leave the revert PR open, and report it as a base-branch
   failure for a human.
6. **Tell the original PRs** with Template E, so the revert is traceable
   from the bump that caused it.
7. **Analyse and recommend.** A revert restores green but fixes nothing:
   Dependabot will offer the update again. Read the failing job log
   (`gh run view <run-id> --log-failed`) and the release notes of the bumped
   package, then classify the cause and recommend one next step. Never push a
   fix to the base branch. A fix is a separate PR, opened only when asked.

   | Cause (from the log) | Typical recommendation |
   |---|---|
   | Breaking API change the project uses | Fix-forward PR that adapts the code, then re-apply the bump. Or `ignore` that version in `dependabot.yml` until then. |
   | Peer-dependency or resolution conflict | Bump the conflicting package in the same PR, or pin and wait for its release. |
   | Lockfile or installer mismatch (CI installs differently than local) | Fix the lockfile or the CI install command, then `@dependabot rebase`. |
   | Test relied on old behaviour | Update the test in a separate PR, linked from the bump. |
   | Advisory database or other external change | Not the bump: report it as a base-branch failure. |
   | Cause unclear | Open an issue with the log excerpt. Assign it, and wait for the next patch release. |

   Put the cause, the evidence (log line, run URL) and the recommendation in
   Template E. If several causes fit, say which one the evidence favours.
