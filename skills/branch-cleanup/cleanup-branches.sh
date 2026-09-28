#!/bin/bash
# cleanup-branches.sh
#
# Tidies a repo's branches, in this order:
#   0. Preflight - record current branch, working-tree changes, other worktrees
#   1. Fetch     - git fetch --all --prune (the only network step; drops
#                  remote-tracking refs for branches deleted upstream)
#   2. Refresh   - fast-forward every local branch, main included, from its
#                  upstream - without checking anything out
#   3. Verify    - classify every branch by *content*: merged (ancestor),
#                  squash-merged (its changes are already in main), pr-merged
#                  (its tip went through a merged GitHub PR, even if main has
#                  changed the same files since), or unmerged (kept). Local
#                  branches with uncommitted changes or checked out in another
#                  worktree are never deleted.
#   4. Switch    - check out the freshly fast-forwarded main (skipped when the
#                  working tree has changes, or with --stay)
#   5. Delete    - verified-merged local branches, then remote branches
#   6. Report    - actions taken (with restore commands), unresolved items,
#                  final state
#
# Usage:
#   ./cleanup-branches.sh              # Dry-run (show what would happen)
#   ./cleanup-branches.sh --execute    # Perform the cleanup
#   ./cleanup-branches.sh --local-only # Skip remote branch deletion
#   ./cleanup-branches.sh --stay       # Don't switch to main at the end
#   ./cleanup-branches.sh --help
#
# Requirements: git (2.38+ for the fast squash-merge check; older versions
# fall back to a patch-id check); gh CLI recommended (merged-PR lookup for
# squash-merged branches that main has edited since, and fallback path for
# remote deletion when a plain `git push --delete` is rejected for auth).
# Works from Git Bash on Windows, and bash/zsh elsewhere.

set -u

DRY_RUN=true
CLEAN_REMOTE=true
SWITCH_TO_MAIN=true

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
  cat << EOF
Branch Cleanup Script

Fetches/prunes, fast-forwards local branches (main included), verifies each
branch's content against main, switches to main, then deletes local and
remote branches whose content is fully in main. Reports actions and final
state.

Protected branches (never deleted): main, master, develop, development,
staging, production, release/*, hotfix/*

Usage:
  $0                  Dry-run (default) - report only, no changes
  $0 --execute        Perform the cleanup
  $0 --local-only     Skip remote branch deletion
  $0 --stay           Don't switch to main at the end
  $0 --help           Show this help
EOF
  exit 0
}

for arg in "$@"; do
  case $arg in
    --execute) DRY_RUN=false ;;
    --local-only) CLEAN_REMOTE=false ;;
    --stay) SWITCH_TO_MAIN=false ;;
    --help|-h) show_help ;;
    *) print_error "Unknown argument: $arg"; exit 1 ;;
  esac
done

git rev-parse --git-dir >/dev/null 2>&1 || { print_error "Not in a git repository"; exit 1; }

ACTIONS=()     # what was (or would be) changed, with restore hints
UNRESOLVED=()  # things the script refused to force
KEPT=()        # branches intentionally left alone, with reason

# "${arr[@]}" on an empty array trips `set -u` in bash < 4.4 (macOS)
each() { eval "printf '%s\n' \${$1[@]+\"\${$1[@]}\"}"; }

if [ "$DRY_RUN" = true ]; then
  print_warning "DRY-RUN MODE - no branch changes (use --execute to apply)"
  print_info "The fetch/prune in step 1 still runs; it only updates remote-tracking refs"
  echo ""
fi

is_protected_branch() {
  case "$1" in
    main|master|develop|development|staging|production) return 0 ;;
    release/*|hotfix/*) return 0 ;;
    *) return 1 ;;
  esac
}

# ---------------------------------------------------------------------------
# STEP 0: preflight
# ---------------------------------------------------------------------------
print_info "STEP 0: Preflight"
START_BRANCH=$(git branch --show-current)
DIRTY=$(git status --porcelain)
if [ -n "$DIRTY" ]; then
  print_warning "Working tree on '${START_BRANCH:-detached HEAD}' has uncommitted/unstaged/untracked changes ($(printf '%s\n' "$DIRTY" | wc -l | tr -d ' ') path(s)) - that branch will not be deleted or switched away from"
else
  print_success "Working tree on '${START_BRANCH:-detached HEAD}' is clean"
fi

# Branches checked out in *other* worktrees: git won't delete them, and their
# uncommitted state is invisible from here, so never touch them.
TOPLEVEL=$(git rev-parse --show-toplevel)
OTHER_WORKTREES=""
wt=""
while IFS= read -r line; do
  case "$line" in
    "worktree "*) wt=${line#worktree } ;;
    "branch refs/heads/"*)
      [ "$wt" != "$TOPLEVEL" ] && OTHER_WORKTREES+="${line#branch refs/heads/}"$'\t'"$wt"$'\n' ;;
  esac
done < <(git worktree list --porcelain)
other_worktree_of() { printf '%s' "$OTHER_WORKTREES" | awk -F'\t' -v b="$1" '$1==b {print $2}'; }
echo ""

# ---------------------------------------------------------------------------
# STEP 1: fetch --all --prune
# ---------------------------------------------------------------------------
print_info "STEP 1: git fetch --all --prune"
git fetch --all --prune 2>&1 | sed 's/^/  /'
if [ "${PIPESTATUS[0]}" -ne 0 ]; then
  print_warning "fetch --all --prune reported errors (see above)"
  UNRESOLVED+=("git fetch --all --prune failed or was incomplete - results below may be stale")
fi
echo ""

if git show-ref --verify --quiet refs/heads/main || git show-ref --verify --quiet refs/remotes/origin/main; then
  MAIN_BRANCH="main"
elif git show-ref --verify --quiet refs/heads/master || git show-ref --verify --quiet refs/remotes/origin/master; then
  MAIN_BRANCH="master"
else
  print_error "Could not find a main or master branch"
  exit 1
fi
if git show-ref --verify --quiet "refs/remotes/origin/$MAIN_BRANCH"; then
  MAIN_REF="origin/$MAIN_BRANCH"
else
  MAIN_REF="$MAIN_BRANCH"
fi
MAIN_TREE=$(git rev-parse "$MAIN_REF^{tree}")
print_info "Main branch: $MAIN_BRANCH (verifying content against $MAIN_REF)"
echo ""

# ---------------------------------------------------------------------------
# STEP 2: fast-forward local branches (main included) from their upstream
# ---------------------------------------------------------------------------
print_info "STEP 2: Fast-forwarding local branches from their upstreams..."
FF_COUNT=0
WOULD_FF=""   # dry-run: "branch<TAB>upstream" lines, so step 3 plans against the post-refresh tip
while IFS=' ' read -r branch upstream track; do
  [ -z "$upstream" ] && continue
  [ "$track" = "[gone]" ] && continue

  counts=$(git rev-list --left-right --count "refs/heads/$branch...$upstream" 2>/dev/null) || continue
  ahead=${counts%%[[:space:]]*}
  behind=${counts##*[[:space:]]}
  [ "$behind" = "0" ] && continue

  if [ "$ahead" != "0" ]; then
    print_warning "Diverged, not fast-forwarded: $branch ($ahead ahead, $behind behind ${upstream#refs/remotes/})"
    UNRESOLVED+=("'$branch' has diverged from ${upstream#refs/remotes/} ($ahead ahead, $behind behind) - rebase or merge it yourself")
    continue
  fi

  wt_path=$(other_worktree_of "$branch")
  if [ -n "$wt_path" ]; then
    print_warning "Not fast-forwarded: $branch is checked out in worktree $wt_path"
    UNRESOLVED+=("'$branch' is $behind behind but checked out in worktree $wt_path - pull it there")
    continue
  fi

  old=$(git rev-parse --short "refs/heads/$branch")
  new=$(git rev-parse --short "$upstream")
  if [ "$DRY_RUN" = true ]; then
    print_warning "Would fast-forward: $branch $old..$new ($behind behind)"
    ACTIONS+=("would fast-forward $branch $old..$new")
    WOULD_FF+="$branch"$'	'"$upstream"$'
'
    continue
  fi

  if [ "$branch" = "$START_BRANCH" ]; then
    # Checked out here: merge --ff-only updates the worktree, refuses anything else.
    git merge --ff-only --quiet "$upstream" >/dev/null 2>&1
  else
    # Local fetch into the branch ref: fast-forward only, no checkout needed.
    git fetch --quiet . "$upstream:refs/heads/$branch" 2>/dev/null
  fi
  if [ $? -eq 0 ]; then
    FF_COUNT=$((FF_COUNT + 1))
    print_success "Fast-forwarded: $branch $old..$new"
    ACTIONS+=("fast-forwarded $branch $old..$new")
  else
    print_warning "Fast-forward failed: $branch"
    UNRESOLVED+=("fast-forward of '$branch' failed (for the checked-out branch: local changes likely overlap incoming ones)")
  fi
done < <(git for-each-ref --format='%(refname:short) %(upstream) %(upstream:track)' refs/heads/)
[ "$DRY_RUN" = false ] && print_success "Fast-forwarded $FF_COUNT branch(es)"
echo ""

# ---------------------------------------------------------------------------
# STEP 3: verify each branch's content against main
#
# content_status <ref> <branch-name> prints one of:
#   merged         - ref is an ancestor of main
#   squash-merged  - merging ref into main would change nothing: all of its
#                    changes are already in main (squash/rebase merges)
#   pr-merged #<n> - ref's tip went through merged GitHub PR <n> (catches
#                    squash merges whose files main has edited since)
#   unmerged:<n>   - ref carries changes main doesn't have (<n> commits ahead)
# ---------------------------------------------------------------------------
if git merge-tree --write-tree "$MAIN_REF" "$MAIN_REF" >/dev/null 2>&1; then
  HAS_MERGE_TREE=true
else
  HAS_MERGE_TREE=false
fi

# Merged GitHub PRs as "headRefName<TAB>headRefOid<TAB>number<TAB>baseRefName"
# lines. Empty without gh/auth/a GitHub remote - then only the git checks
# above apply.
MERGED_PRS=""
if command -v gh >/dev/null 2>&1; then
  MERGED_PRS=$(gh pr list --state merged --limit 1000 --json number,headRefName,headRefOid,baseRefName     --jq '.[] | [.headRefName, .headRefOid, (.number | tostring), .baseRefName] | @tsv' 2>/dev/null) || MERGED_PRS=""
fi

# changes_id <commit>: patch-id of the lines <commit> adds/removes relative to
# its merge base with main. Zero context lines, so the same change made on an
# older or newer base gives the same id.
changes_id() {
  local base
  base=$(git merge-base "$MAIN_REF" "$1" 2>/dev/null) || return
  git diff -U0 "$base" "$1" | git patch-id --stable | cut -d' ' -f1
}

# merged_pr_of <ref> <branch-name>: prints the number of a PR merged into the
# main branch whose head was <branch-name> and that carried everything on <ref>:
#   - the PR head contains <ref>'s tip (every commit went through the PR), or
#   - the PR was rebased/rewritten before merging, but makes exactly the same
#     line changes as <ref> (compared via refs/pull/<n>/head).
# A commit added after the merge fails both checks, so that work is kept.
# A PR merged into another branch (e.g. a stacked PR whose base was never
# retargeted to main) doesn't count: its content need not be in main.
merged_pr_of() {
  local tip head oid num base mine
  tip=$(git rev-parse "$1" 2>/dev/null) || return
  while IFS=$'	' read -r head oid num base; do
    [ "$head" = "$2" ] && [ "$base" = "$MAIN_BRANCH" ] || continue
    if [ "$oid" = "$tip" ] || git merge-base --is-ancestor "$tip" "$oid" 2>/dev/null; then
      echo "$num"; return
    fi
    [ -n "${mine:=$(changes_id "$tip")}" ] || continue
    if git fetch --quiet origin "refs/pull/$num/head" 2>/dev/null       && [ "$(changes_id "$oid")" = "$mine" ]; then
      echo "$num"; return
    fi
  done <<< "$MERGED_PRS"
}

content_status() {
  local ref=$1 name=$2 out base synth pr
  if git merge-base --is-ancestor "$ref" "$MAIN_REF" 2>/dev/null; then
    echo merged; return
  fi
  if [ "$HAS_MERGE_TREE" = true ]; then
    # Clean merge whose result is main's own tree => ref adds nothing.
    if out=$(git merge-tree --write-tree "$MAIN_REF" "$ref" 2>/dev/null) && [ "${out%%$'\n'*}" = "$MAIN_TREE" ]; then
      echo squash-merged; return
    fi
  else
    # git < 2.38: squash ref into one synthetic commit, ask if main has an
    # equivalent patch.
    if base=$(git merge-base "$MAIN_REF" "$ref" 2>/dev/null) \
      && synth=$(git commit-tree "$ref^{tree}" -p "$base" -m squash-check 2>/dev/null) \
      && [[ $(git cherry "$MAIN_REF" "$synth" 2>/dev/null) == -* ]]; then
      echo squash-merged; return
    fi
  fi
  # Squash-merged, but main has changed the same files since: git alone can't
  # prove it adds nothing, GitHub's record of the merge can.
  pr=$(merged_pr_of "$ref" "$name")
  [ -n "$pr" ] && { echo "pr-merged #$pr"; return; }
  echo "unmerged:$(git rev-list --count "$MAIN_REF..$ref")"
}

stash_count_for() {
  git stash list --format='%gs' 2>/dev/null \
    | awk -v b="$1" 'index($0, "WIP on " b ":") == 1 || index($0, "On " b ":") == 1' | wc -l | tr -d ' '
}

print_info "STEP 3a: Verifying local branches against $MAIN_REF..."
DEL_LOCAL=()   # "branch<TAB>reason"
while IFS=' ' read -r branch track; do
  [ -z "$branch" ] && continue
  if is_protected_branch "$branch"; then
    print_info "Protected, kept: $branch"
    continue
  fi

  # Dry-run skipped the fast-forward: plan against the tip --execute would see.
  ref="refs/heads/$branch"
  ff_to=$(printf '%s' "$WOULD_FF" | awk -F'	' -v b="$branch" '$1==b {print $2}')
  [ -n "$ff_to" ] && ref=$ff_to
  status=$(content_status "$ref" "$branch")
  gone=""
  [ "$track" = "[gone]" ] && gone=", upstream deleted"

  case "$status" in
    unmerged:*)
      n=${status#unmerged:}
      print_info "Kept: $branch - $n commit(s) with changes not in $MAIN_REF$gone"
      KEPT+=("$branch: $n commit(s) with changes not in $MAIN_REF$gone")
      [ -n "$gone" ] && UNRESOLVED+=("'$branch' lost its upstream but has changes not in $MAIN_REF - review it (git log -p $MAIN_REF..$branch) before deleting by hand")
      continue ;;
  esac

  wt_path=$(other_worktree_of "$branch")
  if [ -n "$wt_path" ]; then
    print_warning "Kept: $branch ($status) - checked out in worktree $wt_path"
    UNRESOLVED+=("'$branch' is $status but checked out in worktree $wt_path - remove that worktree first")
    continue
  fi
  if [ "$branch" = "$START_BRANCH" ] && [ -n "$DIRTY" ]; then
    print_warning "Kept: $branch ($status) - current branch has uncommitted/unstaged/untracked changes"
    UNRESOLVED+=("'$branch' is $status but has uncommitted/unstaged/untracked changes - commit, stash or discard them, then re-run")
    continue
  fi

  print_warning "Delete candidate: $branch ($status$gone)"
  DEL_LOCAL+=("$branch"$'\t'"$status$gone")
done < <(git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads/)
echo ""

DEL_REMOTE=()  # "branch<TAB>reason"
if [ "$CLEAN_REMOTE" = true ] && git remote | grep -qx origin; then
  print_info "STEP 3b: Verifying origin branches against $MAIN_REF..."
  while IFS= read -r ref; do
    branch=${ref#origin/}
    [ "$branch" = "HEAD" ] || [ "$branch" = "$ref" ] || [ "$branch" = "$MAIN_BRANCH" ] && continue
    if is_protected_branch "$branch"; then
      print_info "Protected, kept: origin/$branch"
      continue
    fi
    status=$(content_status "refs/remotes/$ref" "$branch")
    case "$status" in
      unmerged:*) continue ;;
    esac
    print_warning "Delete candidate: origin/$branch ($status)"
    DEL_REMOTE+=("$branch"$'\t'"$status")
  done < <(git for-each-ref --format='%(refname:short)' refs/remotes/origin/)
  echo ""
fi

# ---------------------------------------------------------------------------
# STEP 4: switch to the (now fresh) main branch
# ---------------------------------------------------------------------------
print_info "STEP 4: Switch to $MAIN_BRANCH"
start_is_candidate=false
each DEL_LOCAL | cut -f1 | grep -qxF "${START_BRANCH:-<detached>}" && start_is_candidate=true

if [ "$START_BRANCH" = "$MAIN_BRANCH" ]; then
  print_success "Already on $MAIN_BRANCH"
elif [ "$SWITCH_TO_MAIN" = false ] && [ "$start_is_candidate" = false ]; then
  print_info "Staying on '${START_BRANCH:-detached HEAD}' (--stay)"
elif [ -n "$DIRTY" ]; then
  print_warning "Staying on '${START_BRANCH:-detached HEAD}': working tree has changes"
elif [ "$DRY_RUN" = true ]; then
  print_warning "Would switch: ${START_BRANCH:-detached HEAD} -> $MAIN_BRANCH"
  ACTIONS+=("would switch ${START_BRANCH:-detached HEAD} -> $MAIN_BRANCH")
elif git switch --quiet "$MAIN_BRANCH" 2>/dev/null; then
  print_success "Switched: ${START_BRANCH:-detached HEAD} -> $MAIN_BRANCH"
  ACTIONS+=("switched ${START_BRANCH:-detached HEAD} -> $MAIN_BRANCH")
else
  print_warning "Could not switch to $MAIN_BRANCH"
  UNRESOLVED+=("could not switch from '${START_BRANCH:-detached HEAD}' to $MAIN_BRANCH")
  if [ "$start_is_candidate" = true ]; then
    # git refuses to delete the checked-out branch - drop it from the list
    remaining=()
    while IFS= read -r entry; do
      [ -n "$entry" ] && [ "${entry%%$'\t'*}" != "$START_BRANCH" ] && remaining+=("$entry")
    done < <(each DEL_LOCAL)
    DEL_LOCAL=(${remaining[@]+"${remaining[@]}"})
    UNRESOLVED+=("'$START_BRANCH' is merged but still checked out, so it was not deleted")
  fi
fi
echo ""

# ---------------------------------------------------------------------------
# STEP 5: delete verified-merged branches
#
# `git branch -d` only knows about ancestor merges into HEAD/upstream, so it
# refuses squash-merged branches. Step 3 already verified every candidate's
# content is in main, so -D is used - with the old tip logged for restore.
# ---------------------------------------------------------------------------
print_info "STEP 5a: Deleting local branches..."
LOCAL_DELETED=0
while IFS=$'\t' read -r branch reason; do
  [ -z "$branch" ] && continue
  sha=$(git rev-parse --short "refs/heads/$branch")
  stashes=$(stash_count_for "$branch")
  [ "$stashes" != "0" ] && KEPT+=("stash: $stashes entr(y/ies) made on '$branch' remain in 'git stash list' after its deletion")
  if [ "$DRY_RUN" = true ]; then
    print_warning "Would delete local: $branch @ $sha ($reason)"
    ACTIONS+=("would delete local $branch @ $sha ($reason)")
  elif git branch -D "$branch" >/dev/null 2>&1; then
    LOCAL_DELETED=$((LOCAL_DELETED + 1))
    print_success "Deleted local: $branch @ $sha ($reason)"
    ACTIONS+=("deleted local $branch @ $sha ($reason) - restore: git branch $branch $sha")
  else
    print_warning "Could not delete local: $branch"
    UNRESOLVED+=("local branch '$branch' could not be deleted")
  fi
done < <(each DEL_LOCAL)
[ ${#DEL_LOCAL[@]} -eq 0 ] && print_success "No local branches to delete"
echo ""

REMOTE_DELETED=0
if [ "$CLEAN_REMOTE" = true ]; then
  print_info "STEP 5b: Deleting origin branches..."
  REPO=""
  while IFS=$'\t' read -r branch reason; do
    [ -z "$branch" ] && continue
    sha=$(git rev-parse --short "refs/remotes/origin/$branch")
    if [ "$DRY_RUN" = true ]; then
      print_warning "Would delete remote: origin/$branch @ $sha ($reason)"
      ACTIONS+=("would delete remote origin/$branch @ $sha ($reason)")
      continue
    fi
    how=""
    if git push --quiet origin --delete "$branch" 2>/dev/null; then
      how="git push"
    elif command -v gh >/dev/null 2>&1 \
      && { [ -n "$REPO" ] || REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null); } \
      && [ -n "$REPO" ] && gh api --method DELETE "/repos/$REPO/git/refs/heads/$branch" >/dev/null 2>&1; then
      how="gh api"
      git update-ref -d "refs/remotes/origin/$branch" 2>/dev/null
    fi
    if [ -n "$how" ]; then
      REMOTE_DELETED=$((REMOTE_DELETED + 1))
      print_success "Deleted remote: origin/$branch @ $sha ($reason, via $how)"
      ACTIONS+=("deleted remote origin/$branch @ $sha ($reason) - restore: git push origin $sha:refs/heads/$branch")
    else
      print_warning "Could not delete remote: origin/$branch (likely missing permission)"
      UNRESOLVED+=("remote branch 'origin/$branch' could not be deleted - check push/admin permissions")
    fi
  done < <(each DEL_REMOTE)
  [ ${#DEL_REMOTE[@]} -eq 0 ] && print_success "No remote branches to delete"
  echo ""
fi

# ---------------------------------------------------------------------------
# STEP 6: report
# ---------------------------------------------------------------------------
echo "========================================"
if [ "$DRY_RUN" = true ]; then
  print_success "CLEANUP PLAN (dry-run)"
else
  print_success "CLEANUP REPORT"
fi
echo "========================================"

echo ""
echo "Actions:"
if [ ${#ACTIONS[@]} -eq 0 ]; then
  echo "  (none)"
else
  each ACTIONS | sed 's/^/  - /'
fi

if [ ${#KEPT[@]} -gt 0 ]; then
  echo ""
  echo "Kept / notes:"
  each KEPT | sed 's/^/  - /'
fi

if [ ${#UNRESOLVED[@]} -gt 0 ]; then
  echo ""
  print_warning "Unresolved (reported, not force-fixed):"
  each UNRESOLVED | sed 's/^/  - /'
fi

echo ""
if [ "$DRY_RUN" = true ]; then
  echo "Current state (unchanged - dry-run):"
else
  echo "Final state:"
fi
now=$(git branch --show-current)
changes=$(git status --porcelain | wc -l | tr -d ' ')
if [ "$changes" = "0" ]; then
  echo "  On: ${now:-detached HEAD} (working tree clean)"
else
  echo "  On: ${now:-detached HEAD} ($changes changed path(s))"
fi
echo "  Local branches:"
git branch -vv --no-color | sed 's/^/    /'
if git remote | grep -qx origin; then
  echo "  Remote branches (origin):"
  git for-each-ref --format='%(refname:short)' refs/remotes/origin/ | grep -v '^origin$' | grep -v '^origin/HEAD$' | sed 's/^/    /'
fi
echo "  Stash entries: $(git stash list | wc -l | tr -d ' ')"

if [ "$DRY_RUN" = true ]; then
  echo ""
  print_info "Run with --execute to apply: $0 --execute"
fi
echo ""
