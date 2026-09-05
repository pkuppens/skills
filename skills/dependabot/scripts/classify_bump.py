#!/usr/bin/env python3
"""Classify dependabot version bumps in a PR diff by semver severity.

Reads a unified diff (e.g. `gh pr diff <number>`) from stdin or a file
argument, extracts every '"<package>": "<old>"' -> '"<package>": "<new>"'
pair changed in a package.json-style diff, and classifies each as
major/minor/patch/downgrade using numeric tuple comparison — never string
comparison, so "1.9.0" -> "1.11.0" is correctly seen as a minor bump, not
a downgrade.

Handles dependabot "group" PRs (multiple packages bumped in one PR) by
reporting every package plus the overall (worst) severity across all of
them.

Only reads `package.json` hunks — `package-lock.json` (and similar lock
files) record each resolved dependency's version under a bare "version"
key with no package name on that line, which would otherwise produce noisy,
mislabeled duplicate entries for every transitive dependency the lockfile
also bumped.

Usage:
    gh pr diff 109 | python classify_bump.py
    python classify_bump.py pr109.diff
"""
import re
import sys

FILE_HEADER = re.compile(r'^\+\+\+ b/(.*)$')
VERSION_LINE = re.compile(
    r'^([+-])\s*"([^"]+)"\s*:\s*"[\^~]?([0-9]+(?:\.[0-9]+){0,2}[^"]*)"'
)

SEVERITY_ORDER = {"major": 3, "minor": 2, "patch": 1, "unchanged": 0, "downgrade": -1}


def parse_version(v: str) -> tuple[int, int, int]:
    v = v.split("-")[0].split("+")[0]  # drop pre-release/build metadata
    parts = v.split(".")
    nums = []
    for p in parts[:3]:
        m = re.match(r"\d+", p)
        nums.append(int(m.group()) if m else 0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)  # type: ignore[return-value]


def classify(old: tuple[int, int, int], new: tuple[int, int, int]) -> str:
    if new > old:
        if new[0] != old[0]:
            return "major"
        if new[1] != old[1]:
            return "minor"
        return "patch"
    if new < old:
        return "downgrade"
    return "unchanged"


def main() -> None:
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()

    removed: dict[str, str] = {}
    results: list[tuple[str, str, str, str]] = []
    in_manifest = False

    for line in text.splitlines():
        header = FILE_HEADER.match(line)
        if header:
            in_manifest = header.group(1).endswith("package.json")
            removed.clear()
            continue
        if not in_manifest:
            continue
        m = VERSION_LINE.match(line)
        if not m:
            continue
        sign, pkg, ver = m.groups()
        if sign == "-":
            removed[pkg] = ver
        elif pkg in removed:
            old_v, new_v = removed.pop(pkg), ver
            level = classify(parse_version(old_v), parse_version(new_v))
            results.append((pkg, old_v, new_v, level))

    if not results:
        print("NO_VERSION_CHANGES_FOUND")
        print("Diff had no matching \"pkg\": \"version\" pairs — fall back to", file=sys.stderr)
        print("parsing the PR title's 'from X to Y' wording by hand.", file=sys.stderr)
        return

    overall = max(results, key=lambda r: SEVERITY_ORDER[r[3]])[3]

    for pkg, old_v, new_v, level in results:
        print(f"{level.upper():10s} {pkg}: {old_v} -> {new_v}")
    print(f"\nOVERALL: {overall.upper()}")


if __name__ == "__main__":
    main()
