# Project policy and major authorization

Disclosed reference for [`SKILL.md`](../SKILL.md) Step 0.

Do this once per repository, before Step 1. Where project rules and this
skill disagree, take the stricter one and say so in the report.

```bash
gh repo view <repo> --json squashMergeAllowed,rebaseMergeAllowed,mergeCommitAllowed,defaultBranchRef
gh api repos/<repo>/branches/<base>/protection --jq '.required_status_checks.contexts' 2>/dev/null   # 403/404 = unknown, not "none"
```

- **Merge strategy:** squash if allowed, else rebase, else merge commit. Step 8
  uses it. Never `--rebase` on a repo that disallows it.
- **Required CI check:** the branch-protection contexts. When none are set,
  look in the project policy for a named check. "Green" then means that check
  passed, not just any check.
- **Project policy files:** read `.github/dependabot.yml` (assignees, cooldown),
  and any dependency-update policy named in `AGENTS.md`, `CONTRIBUTING.md` or
  `.github/` (for example `.github/Dependency_Updates.md`). Apply extra holds it
  states (for example tool-dependency or runtime bumps need a human) and its
  required gates (for example a green base branch). A policy marked "proposed"
  is applied as a hold rule and cited as proposed. If policy and skill
  disagree, take the stricter rule and say so in the report.
- **Major authorization.** Read the user's invocation. Majors are merged only
  when it explicitly says so and names the scope, for example "dependabot
  update majors on green CI, I pre-checked" or "merge major bumps on #12 and
  #14". Record the exact words and the PRs they cover. "Run the daily check"
  is not authorization. When unsure, treat it as not authorized.
  - **Not authorization:** "go ahead", "clear the PRs", "do all of them",
    "run the daily check", or approval of the plan for patch and minor bumps.
  - **Scope:** the current invocation only, and only the PRs or the "majors"
    class it names. An earlier message or session does not carry over.
  - **"Names" for Docker, runtime, calver and policy-restricted bumps:** the
    invocation names the PR number, or says the word (for example "including
    runtime bumps"). "Majors" alone does not cover them.

