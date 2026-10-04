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

Beyond the severity, prints a GATE verdict applying the auto-merge rule:
a bump is auto-mergeable only when the major component is unchanged AND
the new version is an overall semver increase. Everything else -- major
bumps, any decrease, an unparseable pair -- is HOLD, for a human.

Only reads `package.json` hunks — `package-lock.json` (and similar lock
files) record each resolved dependency's version under a bare "version"
key with no package name on that line, which would otherwise produce noisy,
mislabeled duplicate entries for every transitive dependency the lockfile
also bumped.

Usage:
    gh pr diff 109 | python classify_bump.py
    python classify_bump.py pr109.diff
    python classify_bump.py --self-test   # verify the gate rule itself
"""
import re
import sys

FILE_HEADER = re.compile(r'^\+\+\+ b/(.*)$')
VERSION_LINE = re.compile(
    r'^([+-])\s*"([^"]+)"\s*:\s*"[\^~]?([0-9]+(?:\.[0-9]+){0,2}[^"]*)"'
)

SEVERITY_ORDER = {"major": 3, "minor": 2, "patch": 1, "unchanged": 0, "downgrade": -1}

# The only two severities that may be approved and merged without a human
# looking. Keep this in sync with the decision table in SKILL.md -- every
# key in SEVERITY_ORDER needs a row there, which is what makes "downgrade"
# and "unchanged" defined outcomes rather than silent fall-throughs.
AUTO_MERGEABLE = {"patch", "minor"}


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


def gate(severity: str) -> tuple[str, str]:
    """Apply the auto-merge rule to an overall severity.

    Returns (verdict, reason). The rule is deliberately stated in terms of
    the semver comparison rather than per-component arithmetic: a minor bump
    normally resets the patch component (1.2.3 -> 1.3.1), which is an
    increase overall even though the patch number went down. Comparing the
    tuples as a whole gets that right, where checking each component in
    isolation would wrongly read it as a decrease.
    """
    if severity in AUTO_MERGEABLE:
        return "AUTO", f"{severity} bump, major unchanged and version increased"
    if severity == "major":
        return "HOLD", "major bump -- can be breaking even with green CI"
    if severity == "downgrade":
        return "HOLD", "version decreases -- never an expected dependabot bump"
    if severity == "unchanged":
        return "HOLD", "no effective version change -- nothing to approve"
    return "HOLD", f"unclassifiable severity {severity!r}"


def self_test() -> int:
    """Verify the gate rule against the documented examples.

    Executable so the rule in SKILL.md is checked by running it, not by
    re-reading prose. Covers each example in the rule plus the two
    non-bump severities the classifier can emit.
    """
    cases = [
        # (old, new, expected_severity, expected_verdict)
        ("1.2.3", "1.3.0", "minor", "AUTO"),      # minor bump, patch reset
        ("1.2.3", "1.2.4", "patch", "AUTO"),      # plain patch bump
        ("1.2.3", "1.3.1", "minor", "AUTO"),      # minor up, patch lower: still an increase
        ("1.2.3", "1.1.0", "downgrade", "HOLD"),  # minor decrease
        ("1.2.3", "1.2.1", "downgrade", "HOLD"),  # patch decrease
        ("1.2.3", "2.0.0", "major", "HOLD"),      # major bump
        ("1.9.0", "1.11.0", "minor", "AUTO"),     # numeric, not lexicographic
        ("1.2.3", "1.2.3", "unchanged", "HOLD"),  # no-op
        ("0.9.0", "0.10.0", "minor", "AUTO"),     # 0.x still compares on major=0
    ]
    failures = 0
    for old, new, want_sev, want_verdict in cases:
        got_sev = classify(parse_version(old), parse_version(new))
        got_verdict, _ = gate(got_sev)
        ok = got_sev == want_sev and got_verdict == want_verdict
        failures += not ok
        print(
            f"{'PASS' if ok else 'FAIL'} {old:>8s} -> {new:<8s} "
            f"severity={got_sev} (want {want_sev}) "
            f"verdict={got_verdict} (want {want_verdict})"
        )

    # Every severity the classifier can produce must have a defined verdict.
    for severity in SEVERITY_ORDER:
        verdict, reason = gate(severity)
        if verdict not in {"AUTO", "HOLD"} or not reason:
            print(f"FAIL severity {severity!r} has no defined gate verdict")
            failures += 1

    print(f"\n{len(cases)} rule cases, {failures} failure(s)")
    return 1 if failures else 0


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())

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
    verdict, reason = gate(overall)
    print(f"\nOVERALL: {overall.upper()}")
    print(f"GATE:    {verdict} ({reason})")


if __name__ == "__main__":
    main()
