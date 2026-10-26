# Repo facts: what the repo has, read in step 0

Steps 2, 3 and 6 change with the repo. Read these once in preflight and keep
the answers for the report.

```bash
# CI workflows, and whether any ran on this PR
ls .github/workflows 2>/dev/null
gh pr checks <pr>

# Local gate
test -f .pre-commit-config.yaml && echo "pre-commit: yes"

# Branch protection (404 = none)
gh api repos/{owner}/{repo}/branches/<base>/protection --jq '{
  approvals: .required_pull_request_reviews.required_approving_review_count,
  dismiss_stale: .required_pull_request_reviews.dismiss_stale_reviews,
  checks: .required_status_checks.contexts,
  up_to_date: .required_status_checks.strict,
  threads: .required_conversation_resolution.enabled}'

# Allowed merge methods
gh api repos/{owner}/{repo} --jq '{rebase: .allow_rebase_merge, squash: .allow_squash_merge, merge: .allow_merge_commit}'

# Merge queue (rulesets; an empty list = none)
gh api repos/{owner}/{repo}/rules/branches/<base> --jq '[.[] | select(.type == "merge_queue")]'
```

## How each answer changes the flow

| Fact | Effect |
|---|---|
| No workflows, or none ran on the PR | Say so. Step 2 becomes mandatory and goes in the report. |
| No `.pre-commit-config.yaml` | Run the test and lint commands directly. Do not add pre-commit. |
| No branch protection, or `approvals: 0` | The skill's gate still applies in full. `reviewDecision` will be empty, so use the reviews API check. |
| `dismiss_stale: false` | `reviewDecision` stays `APPROVED` after a push. Compare the review's `commit_id` with the head SHA. |
| `up_to_date: true` | GitHub blocks a `BEHIND` branch. Step 1 handles it. |
| Rebase-merge disallowed | Use squash. Never change the repo setting. |
| Merge queue present | `gh pr merge --auto`, then confirm `MERGED`. Do not set one up. |
| Dependabot PR | Hand off to the `dependabot` skill. |

Report what GitHub itself will block (from protection) next to what this skill
blocks on top of it, so the user can see where the two differ.
