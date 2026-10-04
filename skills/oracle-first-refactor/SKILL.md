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

**Invoke:** `/oracle-first-refactor`
**Use when:** you plan a refactor **or a bug fix** in a large or legacy code
base, and you must be able to prove what changed and what did not.
**Status:** not yet exercised by a recorded run. See
[`workshops/legacy-refactor/`](../../workshops/legacy-refactor/README.md) for
the planned proof.

A [test oracle](../../CONTEXT.md#language-legacy-refactoring) is a tool that decides whether a result is correct. The
term is standard software-testing vocabulary, not invented here: see the
CONTEXT.md entry for the references. This skill uses it for two questions —
is the change complete, and did the behavior stay the same.

**The principle:** an AI agent writes code quickly. It is much more difficult
to know whether the new code is correct. So the slow part is proof, not writing.
The oracle gives the proof. Make the oracle first.

---

## Rule 0 — name the reason before you start

**Refuse to start a refactor that has no reason.** Nobody changes old code
because the code is old. A refactor costs money and it adds risk.

Ask the user which reason applies. Write the answer down.

| Reason | What the user wants | Which oracle the work needs |
| --- | --- | --- |
| 1. Fix a defect | The defect is gone, and no caller breaks. | Steps 1 and 3. Step 4 if the code produces data. |
| 2. Give a client one function | One function, usable on its own. | Steps 1 and 3. |
| 3. The platform forces it | An old interface is gone, or a framework is out of support. | Step 1, for every build setting. |
| 4. Nobody understands the code | Written rules, words, and decisions. | Step 2 first. The result is text, not a code change. |
| 5. There are no tests | Proof that a later change is safe. | Step 4 first. Record what the code produces now. |

Two things follow from the reason.

1. **The reason sets the smallest change.** Reason 2 does not permit a rewrite
   of the module. Say what is in scope and what is not.
2. **The reason sets the oracle.** A change that moves data needs step 4. A
   change that only moves types needs step 1.

If the user cannot name a reason, then the correct answer is **do not
refactor**. Say so. Offer reason 4 or reason 5 instead: better understanding
and a first test set are useful on their own, and they are cheaper.

## The oracle ladder

Name the oracle **before** the first edit.

| Step | Oracle | Question that it answers | Cost |
| --- | --- | --- | --- |
| 1 | Type system and compiler | Is the change complete? | Free, if a build exists |
| 2 | Semantic index | How much code does this change touch? | Low |
| 3 | Tests | Does the observable contract still hold? | Medium |
| 4 | Golden outputs | Is the produced data bit-identical? | Medium |

**The rule: if no oracle exists at the step that the change needs, then build
the oracle first.** That work is the first commit of the refactor. It is not a
detour from the refactor.

A change that moves data needs step 4. A change that only moves types needs
step 1. Match the oracle to the change, and say which step you chose.

---

## Refactor and bug fix need the same ladder, from a different rung

The two jobs look similar and they use opposite tests for success. Decide which
one you are doing before you choose the oracle.

| | Refactor | Bug fix |
| --- | --- | --- |
| What must happen to the behavior | Nothing changes. | Exactly one thing changes. |
| What the oracle must prove | Every stored output file is identical. | One stored output file changes on purpose. Every other file is identical. |
| A changed output file means | **Failure.** You broke something. | **Success**, for that one file only. Any second change is a defect. |
| Where you start on the ladder | Rung 1. The compiler proves that you reached every call site. | Rung 3. A defect is rarely a type error, so the compiler cannot see it. |
| What you write first | The stored output of the current behavior. | A test that fails because of the defect. |

### Worked example, both ways

Take a function that writes a DICOM tag, and say it writes the patient name
with the wrong character set.

**As a refactor** — you move that function to another class, and the defect
stays. Procedure: store the output of 200 files first. Break the old function
name so that the compiler lists every caller. Fix each caller. Compare the 200
files. All 200 must be identical, **including the wrong character set.** A
refactor that also fixes the defect is two changes in one commit, and a
reviewer then cannot see which change caused which effect.

**As a bug fix** — you correct the character set. Procedure: write the failing
test first, from the standard, not from the current output. Fix the function.
Compare the 200 files. Now exactly the files with a non-ASCII patient name must
differ, and you must look at each difference and accept it. The other files must
be identical. Then update those stored files in their own commit, with the
standard quoted in the message. That commit is the evidence of intent.

### The rule that follows

**Never put a refactor and a bug fix in the same commit.** The oracle cannot
tell you which change moved the output, so the evidence becomes useless. Do the
bug fix first if the defect blocks the refactor. Otherwise refactor first, prove
that nothing moved, and fix the defect after.

## The deliberate-breakage technique

Do not ask a text search to find every call site. Do not ask the model either.
**Break the old interface on purpose and let the build list the call sites.**

The roles change. The compiler does the search. The AI makes the changes. The
list is complete because of the method, not because somebody was careful.

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

1. **Name the reason and the oracle.** Why does this change happen? Which step
   of the ladder does it need?
2. **Build the missing oracle.** Commit it on its own.
3. **Measure how much code the change touches.** Use the semantic index,
   step 2.
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

## Where this comes from

Say this when you present the technique. Most of it is established work, and
claiming otherwise is the one thing that damages your credibility.

| Idea here | Established name and source |
| --- | --- |
| Test oracle, and "the oracle problem" | Standard testing vocabulary. Traced to William Howden's testing work of the late 1970s; Elaine Weyuker, _On Testing Non-testable Programs_ (1982); Barr, Harman, McMinn, Shahbaz and Yoo, _The Oracle Problem in Software Testing: A Survey_, IEEE TSE 41(5), 2015. |
| Deliberate breakage | **"Leaning on the Compiler"** — Michael Feathers, _Working Effectively with Legacy Code_ (2004), chapter 8. |
| Stored output files | **Characterization tests** (Feathers, same book). Also called golden-master or approval testing. |
| Sequencing a large refactor | The **Mikado Method** is the closest established treatment. |

**What this library adds.** Two things, and they are framing rather than
discovery. First, the four-rung ladder as a named order with the rule to build
the missing rung first. Second, using an oracle to judge **completeness** —
the compiler as the answer to "did I find every call site" — where the
literature uses an oracle to judge whether output is **correct**.

Present it as: Feathers' technique, with an agent doing the edits, and a named
ladder deciding when the compiler is not enough.

## Related skills

| Skill | Relation |
| --- | --- |
| [`call-site-exhaustiveness`](../call-site-exhaustiveness/SKILL.md) | Holds the method ladder and the recall-reporting rule. Do not repeat them here. |
| [`legacy-build-container`](../legacy-build-container/SKILL.md) | Produces oracle 1 when no build exists. |
| [`brutally-honest-code-review`](../brutally-honest-code-review/SKILL.md) | Reviews each reviewable step. |
| [`ai-factory`](../ai-factory/SKILL.md) | Decides whether the editing model runs locally or in the cloud. |
