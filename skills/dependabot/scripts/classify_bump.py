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

That omission has a real consequence on group PRs: when a package's
existing range already covers the new version (`^5.0.2` covering 5.0.3),
dependabot updates only the lock file and the manifest diff shows nothing,
so the package goes unreported. Pass `--body <file>` with the PR body
(`gh pr view <n> --json body --jq .body`) to reconcile against dependabot's
own authoritative "Updates `pkg` from X to Y" lines — this recovers the
lock-only bumps without parsing the lock file, and flags any disagreement
between the two sources rather than silently preferring one.

Usage:
    gh pr diff 109 | python classify_bump.py
    python classify_bump.py pr109.diff
    python classify_bump.py pr109.diff --body pr109-body.md
    python classify_bump.py --self-test   # verify the gate rule itself
"""
import re
import sys

FILE_HEADER = re.compile(r'^\+\+\+ b/(.*)$')
VERSION_LINE = re.compile(
    r'^([+-])\s*"([^"]+)"\s*:\s*"[\^~]?([0-9]+(?:\.[0-9]+){0,2}[^"]*)"'
)

# Dependabot writes one of these per package in every PR body it opens,
# for single and group PRs alike. It is generated from the update metadata
# rather than from the diff, which is what makes it a usable cross-check.
BODY_UPDATE_LINE = re.compile(
    r'Updates\s+`([^`]+)`\s+from\s+([0-9][^\s]*)\s+to\s+([0-9][^\s]*)'
)
# The "with N updates" claim in a group PR's opening sentence.
BODY_GROUP_COUNT = re.compile(r'with\s+(\d+)\s+updates?')

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


def parse_diff(text: str) -> dict[str, tuple[str, str]]:
    """Extract {package: (old, new)} from manifest hunks of a unified diff."""
    removed: dict[str, str] = {}
    found: dict[str, tuple[str, str]] = {}
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
            found[pkg] = (removed.pop(pkg), ver)
    return found


def parse_body(text: str) -> tuple[dict[str, tuple[str, str]], int | None]:
    """Extract {package: (old, new)} and the claimed update count from a PR body."""
    found = {m.group(1): (m.group(2), m.group(3)) for m in BODY_UPDATE_LINE.finditer(text)}
    claim = BODY_GROUP_COUNT.search(text)
    return found, int(claim.group(1)) if claim else None


def reconcile(
    diff_pkgs: dict[str, tuple[str, str]],
    body_pkgs: dict[str, tuple[str, str]],
) -> tuple[list[tuple[str, str, str, str, str]], list[str]]:
    """Merge diff and body findings into one package list, plus any warnings.

    Returns (rows, warnings) where each row is
    (package, old, new, severity, source). Disagreement between the two
    sources is reported as a warning and classified as "conflict" rather
    than resolved by preferring one — if the manifest and dependabot's own
    metadata disagree about a version, that is exactly the case a human
    should look at.
    """
    rows: list[tuple[str, str, str, str, str]] = []
    warnings: list[str] = []

    for pkg in sorted(set(diff_pkgs) | set(body_pkgs)):
        in_diff, in_body = diff_pkgs.get(pkg), body_pkgs.get(pkg)
        if in_diff and in_body and in_diff != in_body:
            warnings.append(
                f"{pkg}: manifest says {in_diff[0]} -> {in_diff[1]} but PR body says "
                f"{in_body[0]} -> {in_body[1]} -- sources disagree"
            )
            rows.append((pkg, in_diff[0], in_diff[1], "conflict", "diff/body"))
            continue
        old, new = in_diff or in_body  # type: ignore[misc]
        # Present in the manifest diff = an explicit range change. Present
        # only in the body = dependabot bumped the lock file because the
        # existing range already covered the new version.
        source = "manifest" if in_diff else "lock-only"
        rows.append((pkg, old, new, classify(parse_version(old), parse_version(new)), source))

    return rows, warnings


def self_test() -> int:
    """Verify the gate rule and the reconciliation against known cases.

    Executable so the rule in SKILL.md is checked by running it, not by
    re-reading prose. Covers each example in the rule, the two non-bump
    severities the classifier can emit, and the real group-PR case that
    motivated reconciliation (babblr#325: 3 packages claimed, 2 visible
    in the manifest).
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

    # Reconciliation: the babblr#325 shape -- vitest is bumped only in the
    # lock file because ^5.0.2 already covered 5.0.3, so the manifest diff
    # shows 2 of the 3 packages the body names.
    body = (
        "Bumps the monthly-updates group in /frontend with 3 updates: "
        "@vitest/ui, electron and vitest.\n"
        "Updates `@vitest/ui` from 5.0.2 to 5.0.3\n"
        "Updates `electron` from 44.5.0 to 44.5.1\n"
        "Updates `vitest` from 5.0.2 to 5.0.3\n"
    )
    body_pkgs, claim = parse_body(body)
    diff_pkgs = {"@vitest/ui": ("5.0.2", "5.0.3"), "electron": ("44.5.0", "44.5.1")}
    rows, warnings = reconcile(diff_pkgs, body_pkgs)
    recon_checks = [
        ("body names 3 packages", len(body_pkgs) == 3),
        ("claimed count parsed as 3", claim == 3),
        ("reconciled list has all 3", len(rows) == 3),
        ("vitest recovered as lock-only", any(r[0] == "vitest" and r[4] == "lock-only" for r in rows)),
        ("no false conflicts", not warnings),
        ("overall still patch", max(rows, key=lambda r: SEVERITY_ORDER.get(r[3], 99))[3] == "patch"),
    ]
    for label, ok in recon_checks:
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'} reconcile: {label}")

    # A genuine disagreement must surface as a conflict, not be smoothed over.
    rows, warnings = reconcile({"lodash": ("4.17.20", "5.0.0")}, {"lodash": ("4.17.20", "4.17.21")})
    conflict_ok = len(warnings) == 1 and rows[0][3] == "conflict"
    gate_ok = gate("conflict")[0] == "HOLD"
    failures += not conflict_ok
    failures += not gate_ok
    print(f"{'PASS' if conflict_ok else 'FAIL'} reconcile: source disagreement raises a conflict")
    print(f"{'PASS' if gate_ok else 'FAIL'} reconcile: a conflict gates to HOLD")

    total = len(cases) + len(recon_checks) + 2
    print(f"\n{total} checks, {failures} failure(s)")
    return 1 if failures else 0


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        sys.exit(self_test())

    body_path = None
    if "--body" in args:
        i = args.index("--body")
        try:
            body_path = args[i + 1]
        except IndexError:
            print("--body needs a file path", file=sys.stderr)
            sys.exit(2)
        del args[i : i + 2]

    text = open(args[0], encoding="utf-8").read() if args else sys.stdin.read()
    diff_pkgs = parse_diff(text)

    body_pkgs: dict[str, tuple[str, str]] = {}
    claimed: int | None = None
    if body_path:
        body_pkgs, claimed = parse_body(open(body_path, encoding="utf-8").read())

    if not diff_pkgs and not body_pkgs:
        print("NO_VERSION_CHANGES_FOUND")
        print("Neither the manifest diff nor the PR body yielded a version pair --", file=sys.stderr)
        print("fall back to parsing the PR title's 'from X to Y' wording by hand.", file=sys.stderr)
        return

    rows, warnings = reconcile(diff_pkgs, body_pkgs)
    overall = max(rows, key=lambda r: SEVERITY_ORDER.get(r[3], 99))[3]

    for pkg, old_v, new_v, level, source in rows:
        suffix = "" if source == "manifest" else f"  [{source}]"
        print(f"{level.upper():10s} {pkg}: {old_v} -> {new_v}{suffix}")

    # Only meaningful when a body was supplied; without one, a count
    # mismatch is expected rather than a finding, so stay quiet about it.
    if body_path and claimed is not None and claimed != len(rows):
        warnings.append(
            f"PR body claims {claimed} updates but {len(rows)} were resolved -- "
            "some package was named in neither the manifest nor an 'Updates' line"
        )
    if body_path and not body_pkgs:
        warnings.append(
            "PR body had no 'Updates `pkg` from X to Y' lines -- reconciliation "
            "contributed nothing, so lock-only bumps may still be missing"
        )
    if not body_path and len(diff_pkgs) > 1:
        warnings.append(
            "group PR classified from the manifest alone -- pass --body to catch "
            "packages bumped only in the lock file"
        )

    verdict, reason = gate(overall)
    print(f"\nOVERALL: {overall.upper()}")
    print(f"GATE:    {verdict} ({reason})")
    for w in warnings:
        print(f"WARN:    {w}")


if __name__ == "__main__":
    main()
