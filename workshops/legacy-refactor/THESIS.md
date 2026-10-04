# The thesis

Six claims. One command proves each claim.

## 1. It is an oracle problem, not a retrieval problem

The context window is the wrong bottleneck. Generation is cheap. A trustworthy
verdict is scarce. The verdict must tell you two things. The change is
complete. The change does not change the behavior.

Therefore you must invest in the oracle. The oracle ladder has four steps:

| Step | Oracle | Question that it answers |
| --- | --- | --- |
| 1 | Compiler | Is the change complete? |
| 2 | Semantic index | What is the blast radius, before I choose an approach? |
| 3 | Tests | Does the observable contract still hold? |
| 4 | Golden outputs | Is the produced data bit-identical? |

If the code base has no oracle at the step that the change needs, then build
the oracle first. That work is the first commit of the refactor. It is not a
detour.

## 2. Let the compiler find the call sites

Do not ask a text search to find every call site. Do not ask the model either.

Instead, break the old interface on purpose, on a branch. Delete the member,
rename it, or mark it as an error.

| Language | How to break it |
| --- | --- |
| C++ | Delete the member, or mark it `[[deprecated]]` and compile with `-Werror=deprecated-declarations`. |
| C# | Mark it `[Obsolete("message", error: true)]`. |

The build then lists every call site. The list includes the sites that a text
search cannot see.

The roles change. **The compiler is the search. The AI makes the edits.** The
recall is 100% by construction, not by diligence.

State the limits before somebody asks:

- Code behind a build condition appears only in the configurations that you
  build. Full recall needs the full build matrix.
- A C++ template that is not instantiated is not type-checked.
- Reflection and string keys reach past the compiler in both languages.

## 3. Static types are an asset

A legacy C++ or C# code base is the best case for AI-assisted refactoring. The
compiler is a free, sound, and exhaustive oracle.

A Python or JavaScript team must write that oracle themselves.

## 4. A green test run is not proof

The code compiles. The unit tests pass. This is still not proof.

In DICOM and in imaging, a refactor can move a pixel. It can change the window
and the level. It can drop a private tag. Only a bit-exact comparison of the
output answers the question.

Under IEC 62304, that set of oracles **is** the evidence. The same artifact
that makes the refactor safe also makes it auditable. This is the reason why
AI-assisted refactoring is acceptable in a regulated product.

## 5. Reconstruct the intent first

Legacy code often has no documentation. The first AI deliverable is not a
refactor. It is the reconstructed intent: decision records, invariants, and a
glossary.

A reviewer cannot approve a diff if the reviewer cannot tell whether the old
behavior was intentional. Reconstruction makes the later diff reviewable.
Reviewability is the real limit on speed, not generation.

## 6. Keep the context discipline auditable

The rule: do not open a file until a tool tells you which lines to open.

The transcript shows whether you obeyed the rule. This is the falsifiable form
of the claim "this method scales".

The transcript is a committed file. Therefore this claim is provable without a
network connection.
