#!/bin/bash
# cleanup-branches.sh
#
# Tidies a repo's branches:
#   1. git fetch --all --prune         (drop remote-tracking refs for deleted branches)
#   2. Fast-forward local branches from their upstreams (never touches the working tree)
#   3. Delete local + remote branches fully merged into the main branch
#   4. Report anything it can't safely resolve (permissions, diverged branches,
#      protected branches) instead of forcing past it
#
# Usage:
#   ./cleanup-branches.sh              # Dry-run (show what would happen)
#   ./cleanup-branches.sh --execute    # Perform the cleanup
#   ./cleanup-branches.sh --local-only # Skip remote branch deletion
#   ./cleanup-branches.sh --help
#
# Requirements: git; gh CLI recommended (fallback path for remote deletion
# when a plain `git push --delete` is rejected for auth reasons).
# Works from Git Bash on Windows, and bash/zsh elsewhere.

set -u

DRY_RUN=true
CLEAN_REMOTE=true

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

Fetches/prunes, fast-forwards local branches from their upstreams, then
deletes local and remote branches fully merged into the main branch.

Protected branches (never deleted): main, master, develop, development,
staging, production, release/*, hotfix/*

Usage:
  $0                  Dry-run (default) - report only, no changes
  $0 --execute        Perform the cleanup
  $0 --local-only     Skip remote branch deletion
  $0 --help           Show this help
EOF
  exit 0
}

for arg in "$@"; do
  case $arg in
    --execute) DRY_RUN=false ;;
    --local-only) CLEAN_REMOTE=false ;;
    --help|-h) show_help ;;
    *) print_error "Unknown argument: $arg"; exit 1 ;;
  esac
done

git rev-parse --git-dir >/dev/null 2>&1 || { print_error "Not in a git repository"; exit 1; }

UNRESOLVED=()

if [ "$DRY_RUN" = true ]; then
  print_warning "DRY-RUN MODE - no changes will be made (use --execute to apply)"
  echo ""
fi

# ---------------------------------------------------------------------------
# STEP 1: fetch --all --prune
# ---------------------------------------------------------------------------
print_info "STEP 1: git fetch --all --prune"
if ! git fetch --all --prune 2>&1 | sed 's/^/  /'; then
  print_warning "fetch --all --prune reported errors (see above)"
  UNRESOLVED+=("git fetch --all --prune failed or was incomplete")
fi
echo ""

# Determine main branch
if git show-ref --verify --quiet refs/heads/main; then
  MAIN_BRANCH="main"
elif git show-ref --verify --quiet refs/heads/master; then
  MAIN_BRANCH="master"
elif git show-ref --verify --quiet refs/remotes/origin/main; then
  MAIN_BRANCH="main"
elif git show-ref --verify --quiet refs/remotes/origin/master; then
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
print_info "Main branch: $MAIN_BRANCH (comparing against $MAIN_REF)"
echo ""

is_protected_branch() {
  case "$1" in
    main|master|develop|development|staging|production) return 0 ;;
    release/*|hotfix/*) return 0 ;;
    *) return 1 ;;
  esac
}

CURRENT_BRANCH=$(git branch --show-current)

# ---------------------------------------------------------------------------
# STEP 2: fast-forward local branches from their upstream
# ---------------------------------------------------------------------------
print_info "STEP 2: Fast-forwarding local branches from their upstreams..."
FF_COUNT=0
while IFS= read -r branch; do
  [ -z "$branch" ] && continue
  upstream=$(git for-each-ref --format='%(upstream:short)' "refs/heads/$branch")
  [ -z "$upstream" ] && continue

  remote=${upstream%%/*}
  remote_branch=${upstream#*/}

  if [ "$branch" = "$CURRENT_BRANCH" ]; then
    # Never touch the checked-out branch's worktree; merge --ff-only is safe here.
    if [ "$DRY_RUN" = false ]; then
      if git merge --ff-only "$upstream" >/dev/null 2>&1; then
        FF_COUNT=$((FF_COUNT + 1))
        print_success "Fast-forwarded (checked out): $branch -> $upstream"
      fi
    else
      ahead_behind=$(git rev-list --left-right --count "$branch...$upstream" 2>/dev/null || echo "0 0")
      behind=$(echo "$ahead_behind" | awk '{print $2}')
      [ "$behind" != "0" ] && print_warning "Would fast-forward (checked out): $branch -> $upstream ($behind behind)"
    fi
    continue
  fi

  if [ "$DRY_RUN" = false ]; then
    if git fetch "$remote" "$remote_branch:$branch" 2>/dev/null; then
      FF_COUNT=$((FF_COUNT + 1))
      print_success "Fast-forwarded: $branch -> $upstream"
    else
      # Non-fast-forward (local commits diverged from upstream) - leave it alone.
      :
    fi
  else
    ahead_behind=$(git rev-list --left-right --count "$branch...$upstream" 2>/dev/null || echo "0 0")
    behind=$(echo "$ahead_behind" | awk '{print $2}')
    [ "$behind" != "0" ] && print_warning "Would fast-forward: $branch -> $upstream ($behind behind)"
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/heads/)

[ "$DRY_RUN" = false ] && print_success "Fast-forwarded $FF_COUNT branch(es)"
echo ""

# ---------------------------------------------------------------------------
# STEP 3a: delete local branches merged into main
#
# Two signals, since squash-merge workflows (e.g. `gh pr merge --squash`)
# leave no ancestor relationship for `git branch --merged` to find:
#   - true ancestor-merged (git branch --merged)
#   - upstream deleted ("gone") - the branch's remote counterpart no longer
#     exists, almost always because it was merged and auto-deleted
# ---------------------------------------------------------------------------
print_info "STEP 3a: Local branches merged into $MAIN_BRANCH..."
LOCAL_COUNT=0
LOCAL_DELETED=0
MERGED_LOCAL=$(git branch --merged "$MAIN_REF" | grep -v '^\*' | sed 's/^[ *]*//' || true)
GONE_LOCAL=$(git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads/ | grep '\[gone\]' | awk '{print $1}' || true)
CANDIDATES=$(printf '%s\n%s\n' "$MERGED_LOCAL" "$GONE_LOCAL" | sed '/^$/d' | sort -u || true)

if [ -n "$CANDIDATES" ]; then
  while IFS= read -r branch; do
    [ -z "$branch" ] && continue
    is_protected_branch "$branch" && { print_info "Skipping protected branch: $branch"; continue; }
    [ "$branch" = "$MAIN_BRANCH" ] && continue

    reason="merged"
    printf '%s\n' "$GONE_LOCAL" | grep -qx "$branch" && ! printf '%s\n' "$MERGED_LOCAL" | grep -qx "$branch" && reason="upstream gone (likely squash-merged)"

    LOCAL_COUNT=$((LOCAL_COUNT + 1))
    if [ "$DRY_RUN" = false ]; then
      if git branch -d "$branch" 2>/dev/null; then
        LOCAL_DELETED=$((LOCAL_DELETED + 1))
        print_success "Deleted local branch: $branch ($reason)"
      else
        print_warning "Could not delete local branch: $branch ($reason)"
        if [ "$reason" = "merged" ]; then
          UNRESOLVED+=("local branch '$branch' could not be deleted (checked out elsewhere, or git refused for another reason)")
        else
          UNRESOLVED+=("local branch '$branch' has a deleted upstream but git can't verify it's merged (no shared ancestor - likely squash-merged); re-run with 'git branch -D $branch' after confirming its PR merged")
        fi
      fi
    else
      print_warning "Would delete local branch: $branch ($reason)"
    fi
  done <<< "$CANDIDATES"
fi

if [ $LOCAL_COUNT -eq 0 ]; then
  print_success "No local merged branches to clean"
elif [ "$DRY_RUN" = false ]; then
  print_success "Deleted $LOCAL_DELETED of $LOCAL_COUNT local branches"
fi
echo ""

# ---------------------------------------------------------------------------
# STEP 3b: delete remote branches merged into main
# ---------------------------------------------------------------------------
REMOTE_COUNT=0
REMOTE_DELETED=0
if [ "$CLEAN_REMOTE" = true ]; then
  print_info "STEP 3b: Remote branches merged into $MAIN_REF..."

  MERGED_REMOTE=$(git branch -r --merged "$MAIN_REF" 2>/dev/null | grep 'origin/' | grep -v "origin/$MAIN_BRANCH$" | grep -v 'origin/HEAD' | sed 's/^[ ]*//' | sed 's|origin/||' || true)

  if [ -n "$MERGED_REMOTE" ]; then
    while IFS= read -r branch; do
      [ -z "$branch" ] && continue
      is_protected_branch "$branch" && { print_info "Skipping protected remote branch: $branch"; continue; }

      REMOTE_COUNT=$((REMOTE_COUNT + 1))
      if [ "$DRY_RUN" = false ]; then
        print_info "Deleting remote branch: origin/$branch"
        if git push origin --delete "$branch" 2>/dev/null; then
          REMOTE_DELETED=$((REMOTE_DELETED + 1))
          print_success "Deleted: origin/$branch"
        elif command -v gh >/dev/null 2>&1 && REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null) && [ -n "$REPO" ] && gh api --method DELETE "/repos/$REPO/git/refs/heads/$branch" >/dev/null 2>&1; then
          REMOTE_DELETED=$((REMOTE_DELETED + 1))
          print_success "Deleted: origin/$branch (via gh CLI)"
        else
          print_warning "Could not delete remote branch: origin/$branch (likely missing permission)"
          UNRESOLVED+=("remote branch 'origin/$branch' could not be deleted - check push/admin permissions")
        fi
      else
        print_warning "Would delete remote branch: origin/$branch"
      fi
    done <<< "$MERGED_REMOTE"
  fi

  if [ $REMOTE_COUNT -eq 0 ]; then
    print_success "No remote merged branches to clean"
  elif [ "$DRY_RUN" = false ]; then
    print_success "Deleted $REMOTE_DELETED of $REMOTE_COUNT remote branches"
  fi
  echo ""
fi

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
echo "========================================"
print_success "CLEANUP SUMMARY"
echo "========================================"
if [ "$DRY_RUN" = true ]; then
  echo "Would delete: $LOCAL_COUNT local, $REMOTE_COUNT remote branch(es)"
  print_info "Run with --execute to perform cleanup: $0 --execute"
else
  echo "Deleted: $LOCAL_DELETED of $LOCAL_COUNT local, $REMOTE_DELETED of $REMOTE_COUNT remote branch(es)"
fi

if [ ${#UNRESOLVED[@]} -gt 0 ]; then
  echo ""
  print_warning "Unresolved (reported, not force-fixed):"
  for item in "${UNRESOLVED[@]}"; do
    echo "  - $item"
  done
fi
echo ""
