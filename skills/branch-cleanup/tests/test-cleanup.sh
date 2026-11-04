#!/bin/bash
# test-cleanup.sh - end-to-end check of cleanup-branches.sh against a
# throwaway repo with a local bare "origin". Touches nothing outside a
# temp directory. Exit code 0 = all checks passed.
#
# Usage: bash skills/branch-cleanup/tests/test-cleanup.sh [path/to/cleanup-branches.sh]
#
# Fixture branches:
#   merged      merge-commit merged, upstream deleted        -> deleted
#   squashed    squash-merged, upstream deleted, CURRENT + dirty
#                                                            -> kept (run 1), deleted (run 2)
#   squashlive  squash-merged, upstream still exists         -> deleted local + remote
#   wipgone     squash-merged, then an extra unpushed commit, upstream deleted
#                                                            -> kept + unresolved
#   wiplive     unmerged work, upstream exists, up to date   -> kept, never reported
#                                                               as fast-forwarded
#   squashedit  squash-merged via PR, then main edited the same file,
#               upstream deleted                             -> deleted (PR evidence)
#   rewritten   local commits rewritten after pushing; the PR merged a rebased
#               copy, main edited the file since, upstream deleted
#                                                            -> deleted (same changes as PR)
#   stacked     PR merged into another branch (stacked PR), not main,
#               upstream deleted                             -> kept (not in main)
#   stale       at main's base, but its upstream has new work -> kept; dry-run
#                                                               must not plan a delete
#   behind      unmerged, behind its upstream                -> fast-forwarded, kept
#   main        behind origin/main                           -> fast-forwarded
#   mylive      merge-commit merged via my PR, remote only   -> remote deleted (PR evidence)
#   env/qa      at main, matches git config branch-cleanup.protect
#                                                            -> kept, even with --remote-scope=all
# Remote-only branches of a colleague ('o@o', not the gh user):
#   colleague-fresh  pushed at main, no commits yet         -> kept; deleted only with
#                                                               --remote-scope=all
#   colleague-done   squash-merged into main                -> kept (not mine)

set -u
SCRIPT=${1:-"$(cd "$(dirname "$0")/.." && pwd)/cleanup-branches.sh"}
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
FAILS=0
check() { if eval "$2"; then echo "  PASS: $1"; else echo "  FAIL: $1"; FAILS=$((FAILS + 1)); fi; }
has_local() { git show-ref --verify --quiet "refs/heads/$1"; }
has_remote() { git ls-remote --exit-code --heads origin "$1" >/dev/null; }

# --- fixture ---------------------------------------------------------------
(
  set -e
  cd "$T"
  git init -q --bare -b main origin.git
  git clone -q -c core.autocrlf=false origin.git dev
  cd dev
  git config user.email t@t; git config user.name t
  c() { echo "$2" >> "$1"; git add -A; git commit -qm "$3"; }
  c a.txt base "base"; git push -q -u origin main
  for b in merged squashed squashlive wipgone wiplive behind squashedit stacked; do
    git switch -qc "$b" main
    c "$b.txt" "$b 1" "$b 1"; c "$b.txt" "$b 2" "$b 2"
    git push -q -u origin "$b"
  done
  git switch -qc mylive main; c mylive.txt "mylive 1" "mylive 1"; git push -q origin mylive
  git switch -q main; git branch -qD mylive
  git merge -q --no-ff origin/mylive -m "merge mylive (PR 105)"
  git merge -q --no-ff merged -m "merge merged"
  git switch -qc rewritten main; c rewritten.txt "rw 1" "rw 1"; git commit -q --amend -m "rw 1 (local rewrite)"
  git switch -q main
  for b in squashed squashlive wipgone squashedit; do git merge -q --squash "$b" >/dev/null; git commit -qm "squash $b"; done
  # PR for 'rewritten' was a rebased copy on the newer main (different SHAs)
  git switch -qc pr-rewritten main; git cherry-pick rewritten
  pr_rw=$(git rev-parse HEAD); git switch -q main
  git merge -q --squash pr-rewritten >/dev/null; git commit -qm "squash rewritten"; git branch -qD pr-rewritten
  echo "edited on main" > squashedit.txt; echo "edited on main" > rewritten.txt
  git commit -qam "main edits merged files afterwards"
  git push -q origin main
  # GitHub keeps refs/pull/<n>/head for merged PRs
  git push -q origin "$pr_rw:refs/pull/103/head" "wipgone:refs/pull/102/head"
  # fake GitHub: merged PRs as "headRefName<TAB>headRefOid<TAB>number<TAB>baseRefName<TAB>author"
  printf 'squashedit	%s	101	main	me
wipgone	%s	102	main	me
rewritten	%s	103	main	me
stacked	%s	104	wiplive	me
mylive	%s	105	main	me
'     "$(git rev-parse squashedit)" "$(git rev-parse wipgone)" "$pr_rw" "$(git rev-parse stacked)" "$(git rev-parse origin/mylive)" > ../merged-prs.tsv
  git push -q origin --delete merged squashed wipgone squashedit stacked
  git branch -q stale main; git push -q -u origin stale
  git branch -q env/qa main; git push -q -u origin env/qa
  git config --add branch-cleanup.protect 'env/*'
  git switch -q wipgone; c wipgone.txt "unpushed extra" "extra after merge"
  # a collaborator advances main and 'behind' on origin
  cd ..; git clone -q -c core.autocrlf=false origin.git other; cd other
  git config user.email o@o; git config user.name o
  git switch -q behind; echo more >> behind.txt; git commit -qam "behind 3"; git push -q
  git switch -q stale; echo new > stale.txt; git add stale.txt; git commit -qm "stale new work"; git push -q
  git switch -q main; echo x >> a.txt; git commit -qam "main moves"; git push -q
  git switch -qc colleague-fresh main; git push -q -u origin colleague-fresh
  git switch -qc colleague-done main; echo c > colleague.txt; git add colleague.txt
  git commit -qm "colleague work"; git push -q -u origin colleague-done
  git switch -q main; git merge -q --squash colleague-done >/dev/null
  git commit -qm "squash colleague-done"; git push -q
  cd ../dev
  git switch -q squashed; echo dirty >> squashed.txt
) >/dev/null 2>&1
# Checked separately: `( ... ) || exit` would disable set -e inside the subshell.
[ $? -eq 0 ] || { echo "fixture setup failed"; exit 1; }
cd "$T/dev"

# Fake `gh`: `gh pr list` returns the merged-PR fixture, `gh api user` the
# login 'me'; everything else fails.
mkdir -p "$T/bin"
cat > "$T/bin/gh" <<GH
#!/bin/bash
[ "\$1 \$2" = "pr list" ] && exec cat "$T/merged-prs.tsv"
[ "\$1 \$2" = "api user" ] && { echo me; exit 0; }
exit 1
GH
chmod +x "$T/bin/gh"
export PATH="$T/bin:$PATH"

# --- run 1: dry-run changes nothing ---------------------------------------
echo "Run 1: dry-run"
before=$(git for-each-ref refs/heads/; git branch --show-current)
out=$(bash "$SCRIPT" 2>&1)
after=$(git for-each-ref refs/heads/; git branch --show-current)
check "dry-run leaves local branches and checkout unchanged" '[ "$before" = "$after" ]'
check "dry-run leaves remote squashlive in place" 'has_remote squashlive'
check "dry-run does not plan deleting stale (its upstream has new work)" '! printf "%s" "$out" | grep -q "Would delete local: stale"'
check "dry-run plans deleting squashedit (merged PR)" 'printf "%s" "$out" | grep -q "Would delete local: squashedit"'
check "dry-run does not plan fast-forwarding up-to-date wiplive" '! printf "%s" "$out" | grep -Eq "[Ff]ast-forward(ed)?: wiplive"'

# --- run 2: execute with a dirty current branch ----------------------------
echo "Run 2: --execute, current branch 'squashed' is dirty"
out=$(bash "$SCRIPT" --execute 2>&1)
check "merged (ancestor) deleted" '! has_local merged'
check "squashlive deleted locally" '! has_local squashlive'
check "squashlive deleted on origin" '! has_remote squashlive'
check "dirty current branch kept" 'has_local squashed'
check "stayed on dirty branch" '[ "$(git branch --show-current)" = squashed ]'
check "dirty change preserved" 'git diff --quiet -- squashed.txt; [ $? -eq 1 ]'
check "wipgone (unmerged work, upstream gone) kept" 'has_local wipgone'
check "wipgone reported as unresolved" 'printf "%s" "$out" | grep -q "wipgone.*lost its upstream"'
check "squashedit (PR-merged, main edited it since) deleted" '! has_local squashedit'
check "rewritten (same changes as its merged PR) deleted" '! has_local rewritten'
check "stacked (PR merged into a non-main branch) kept" 'has_local stacked'
check "wipgone not matched to its PR (commit added after merge)" '! printf "%s" "$out" | grep -q "Deleted local: wipgone"'
check "stale fast-forwarded and kept" 'has_local stale && [ "$(git rev-parse stale)" = "$(git rev-parse origin/stale)" ]'
check "wiplive kept" 'has_local wiplive && has_remote wiplive'
check "up-to-date wiplive not reported as fast-forwarded" '! printf "%s" "$out" | grep -Eq "[Ff]ast-forward(ed)?: wiplive"'
check "behind fast-forwarded" '[ "$(git rev-parse behind)" = "$(git rev-parse origin/behind)" ]'
check "main fast-forwarded" '[ "$(git rev-parse main)" = "$(git rev-parse origin/main)" ]'
check "report lists restore command" 'printf "%s" "$out" | grep -q "restore: git branch merged"'
check "report shows final state" 'printf "%s" "$out" | grep -q "^Final state:"'
check "own PR-merged remote mylive deleted" '! has_remote mylive'
check "colleague-fresh (no commits, not mine) kept on origin" 'has_remote colleague-fresh'
check "colleague-done (squash-merged, not mine) kept on origin" 'has_remote colleague-done'
check "colleague branches reported as not verified as yours" 'printf "%s" "$out" | grep -q "origin/colleague-done.*not verified as yours"'
check "configured protected env/qa kept" 'has_local env/qa && has_remote env/qa'

# --- run 3: execute after stashing -----------------------------------------
echo "Run 3: --execute after 'git stash'"
git stash -q
out=$(bash "$SCRIPT" --execute 2>&1)
check "switched to main" '[ "$(git branch --show-current)" = main ]'
check "squashed deleted once clean" '! has_local squashed'
check "stash survives and is reported" '[ "$(git stash list | wc -l | tr -d " ")" = 1 ] && printf "%s" "$out" | grep -q "made on '"'"'squashed'"'"'"'
check "protected main kept" 'has_local main && has_remote main'

# --- run 4: --remote-scope=all includes branches of others -----------------
echo "Run 4: --execute --remote-scope=all"
bash "$SCRIPT" --execute --remote-scope=all >/dev/null 2>&1
check "remote-scope=all deletes colleague-fresh" '! has_remote colleague-fresh'
check "remote-scope=all deletes colleague-done" '! has_remote colleague-done'
check "configured protected env/qa still kept" 'has_local env/qa && has_remote env/qa'
check "unknown --remote-scope value rejected" '! bash "$SCRIPT" --remote-scope=everyone >/dev/null 2>&1'

echo ""
if [ $FAILS -eq 0 ]; then echo "ALL CHECKS PASSED"; else echo "$FAILS CHECK(S) FAILED"; fi
exit $FAILS
