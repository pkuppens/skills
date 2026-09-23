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
#   wiplive     unmerged work, upstream exists               -> kept
#   behind      unmerged, behind its upstream                -> fast-forwarded, kept
#   main        behind origin/main                           -> fast-forwarded

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
  for b in merged squashed squashlive wipgone wiplive behind; do
    git switch -qc "$b" main
    c "$b.txt" "$b 1" "$b 1"; c "$b.txt" "$b 2" "$b 2"
    git push -q -u origin "$b"
  done
  git switch -q main
  git merge -q --no-ff merged -m "merge merged"
  for b in squashed squashlive wipgone; do git merge -q --squash "$b" >/dev/null; git commit -qm "squash $b"; done
  git push -q origin main
  git push -q origin --delete merged squashed wipgone
  git switch -q wipgone; c wipgone.txt "unpushed extra" "extra after merge"
  # a collaborator advances main and 'behind' on origin
  cd ..; git clone -q -c core.autocrlf=false origin.git other; cd other
  git config user.email o@o; git config user.name o
  git switch -q behind; echo more >> behind.txt; git commit -qam "behind 3"; git push -q
  git switch -q main; echo x >> a.txt; git commit -qam "main moves"; git push -q
  cd ../dev
  git switch -q squashed; echo dirty >> squashed.txt
) >/dev/null 2>&1
# Checked separately: `( ... ) || exit` would disable set -e inside the subshell.
[ $? -eq 0 ] || { echo "fixture setup failed"; exit 1; }
cd "$T/dev"

# --- run 1: dry-run changes nothing ---------------------------------------
echo "Run 1: dry-run"
before=$(git for-each-ref refs/heads/; git branch --show-current)
bash "$SCRIPT" >/dev/null 2>&1
after=$(git for-each-ref refs/heads/; git branch --show-current)
check "dry-run leaves local branches and checkout unchanged" '[ "$before" = "$after" ]'
check "dry-run leaves remote squashlive in place" 'has_remote squashlive'

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
check "wiplive kept" 'has_local wiplive && has_remote wiplive'
check "behind fast-forwarded" '[ "$(git rev-parse behind)" = "$(git rev-parse origin/behind)" ]'
check "main fast-forwarded" '[ "$(git rev-parse main)" = "$(git rev-parse origin/main)" ]'
check "report lists restore command" 'printf "%s" "$out" | grep -q "restore: git branch merged"'
check "report shows final state" 'printf "%s" "$out" | grep -q "^Final state:"'

# --- run 3: execute after stashing -----------------------------------------
echo "Run 3: --execute after 'git stash'"
git stash -q
out=$(bash "$SCRIPT" --execute 2>&1)
check "switched to main" '[ "$(git branch --show-current)" = main ]'
check "squashed deleted once clean" '! has_local squashed'
check "stash survives and is reported" '[ "$(git stash list | wc -l | tr -d " ")" = 1 ] && printf "%s" "$out" | grep -q "made on '"'"'squashed'"'"'"'
check "protected main kept" 'has_local main && has_remote main'

echo ""
if [ $FAILS -eq 0 ]; then echo "ALL CHECKS PASSED"; else echo "$FAILS CHECK(S) FAILED"; fi
exit $FAILS
