---
name: oracle-first-refactor
description: >
  Establish the oracle before you edit, then let the oracle drive the refactor.
  Holds the deliberate-breakage technique that makes the compiler list every
  call site, and the four-step oracle ladder with the rule to build the missing
  oracle first. Use before any refactor of a code base that is too large to
  read, and whenever an agent must prove that a change is complete and does not
  change the behavior.
---

# Oracle-first refactor

**Use when:** you plan a refactor in a large or legacy code base, and you must
be able to prove two things. The change is complete. The change does not change
the behavior.

**The principle:** generation is cheap, and a trustworthy verdict is scarce.
Therefore the oracle, not the context window, is the bottleneck.

---

## The oracle ladder

Name the oracle **before** the first edit.

| Step | Oracle | Question that it answers | Cost |
| --- | --- | --- | --- |
| 1 | Type system and compiler | Is the change complete? | Free, if a build exists |
| 2 | Semantic index | What is the blast radius, before I choose an approach? | Low |
| 3 | Tests | Does the observable contract still hold? | Medium |
| 4 | Golden outputs | Is the produced data bit-identical? | Medium |

**The rule: if no oracle exists at the step that the change needs, then build
the oracle first.** That work is the first commit of the refactor. It is not a
detour from the refactor.

A change that moves data needs step 4. A change that only moves types needs
step 1. Match the oracle to the change, and say which step you chose.

---

## The deliberate-breakage technique

Do not ask a text search to find every call site. Do not ask the model either.
**Break the old interface on purpose and let the build list the call sites.**

The roles change. The compiler is the search. The AI makes the edits. The
recall is then 100% by construction, not by diligence.

### Procedure

1. **Create a branch.** This technique only works on a branch. Never do it on
   a shared branch.

   ```bash
   git switch -c refactor/enumerate-oldapi
   ```

2. **Break the member.** Choose the method for the language.

   | Language | Method | Flag or attribute |
   | --- | --- | --- |
   | C++ | Mark it deprecated and make the warning an error. | `[[deprecated]]` with `-Werror=deprecated-declarations` |
   | C++ | Or delete the member. | None needed |
   | C++ | Or change the parameter type to an incompatible type. | None needed |
   | C# | Mark it as an error. | `[Obsolete("message", error: true)]` |
   | C# | Or make every warning an error. | `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` |

3. **Build every configuration that you intend to claim.**

   ```bash
   cmake --build build 2>&1 | tee /tmp/diagnostics.txt
   dotnet build --no-restore 2>&1 | tee /tmp/diagnostics.txt
   ```

4. **Count the diagnostics.** Each diagnostic is one call site. Record the
   count.

5. **Fix one diagnostic at a time.** Each fix must be reviewable. Do not write
   an automatic fixer. A sweep that nobody can review is not a refactor; it is
   a risk.

6. **Rebuild until the count is zero.**

7. **Revert the breakage, or keep it as the deprecation.** Decide explicitly.
   A deprecation that stays is a release decision, not a refactor decision.

8. **Report with the rule in
   [`call-site-exhaustiveness`](../call-site-exhaustiveness/SKILL.md).** State
   the method, the count, the configurations, and the blind spots.

### Caveats — state these, do not bury them

1. **A build condition hides call sites.** Code behind `#ifdef`, or behind a
   build configuration, appears only in what you build. Full recall needs the
   full build matrix. Say which configurations you built.
2. **An uninstantiated C++ template is not type-checked.** The compiler never
   sees the call. Force an instantiation, or add a `static_assert` probe.
3. **C# reaches past the compiler.** Reflection, `nameof`, string-keyed
   dependency registration, serialization contracts, and source generators
   produce call sites that the compiler cannot see. The compiler oracle is
   necessary there, but it is not sufficient. Climb to step 3 or step 4.
4. **This is a branch technique.** The obvious objection is that deliberate
   breakage is reckless. It is not reckless on a branch that nobody shares, and
   the revert is one command. Say this before somebody asks.

---

## Order of work

Work in this order. Each step produces evidence for the next step.

1. **Name the oracle.** Which step of the ladder does this change need?
2. **Build the missing oracle.** Commit it on its own.
3. **Measure the blast radius.** Use the semantic index, step 2.
4. **Reconstruct the intent**, if the code has no documentation. A reviewer
   cannot approve a diff when nobody knows whether the old behavior was
   intentional.
5. **Enumerate the call sites.** Use the deliberate breakage.
6. **Edit, one diagnostic at a time.**
7. **Prove that the behavior did not change.** The build and the unit tests are
   not enough for data-processing code. Compare the output.
8. **Report.** Method, counts, configurations, blind spots.

## Why this is acceptable in a regulated product

Under IEC 62304 and similar rules, a change needs evidence. This set of oracles
**is** the evidence:

- The pinned toolchain shows a controlled build environment.
- The diagnostic list shows which call sites existed.
- The diff shows what changed, one reviewable step at a time.
- The output comparison shows that the behavior did not change.

The same artifacts that make the refactor safe also make it auditable. That is
the reason why AI-assisted refactoring is acceptable here at all. The verdict
comes from deterministic local tools, not from the model.

## Rules for the agent

1. Name the oracle before the first edit. Write it down.
2. Build the oracle first when it is missing.
3. Never claim complete recall from a text search.
4. Report the configurations that you compiled.
5. Fix one diagnostic at a time. Keep each step reviewable.
6. State the caveats in the same report as the result.

## Related skills

| Skill | Relation |
| --- | --- |
| [`call-site-exhaustiveness`](../call-site-exhaustiveness/SKILL.md) | Holds the method ladder and the recall-reporting rule. Do not repeat them here. |
| [`legacy-build-container`](../legacy-build-container/SKILL.md) | Produces oracle 1 when no build exists. |
| [`brutally-honest-code-review`](../brutally-honest-code-review/SKILL.md) | Reviews each reviewable step. |
| [`ai-factory`](../ai-factory/SKILL.md) | Decides whether the editing model runs locally or in the cloud. |
