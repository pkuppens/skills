# The claims

First: why you refactor at all. Then six claims. One command proves each claim.

## Why refactor legacy code?

Nobody refactors legacy code because the code is old. A refactor costs money
and it adds risk. You need a reason.

There are five common reasons. Each reason is a real request from a real
person.

| Reason | Example in fo-dicom | What you must know first |
| --- | --- | --- |
| 1. You must fix a defect. | A tag is parsed incorrectly. Many places in the library call the same parsing code. | Every place that calls the code. If you miss one place, the defect stays. |
| 2. A client needs one function. | A client wants to read the pixel data without a read of the complete file. The function is inside a large class. | What the function uses, and what other callers expect from it. |
| 3. The platform forces a change. | The team uses the 1.x interface. That interface now lives in a separate `fo-dicom.Legacy` package. The team must move to a supported version. | Every use of the old interface. |
| 4. Nobody understands the code. | The legacy interface has no documentation. A new engineer cannot change it safely. | The intent of the code: the rules it keeps, the words it uses, and what it does now. |
| 5. There are no tests. | You cannot show that a change is safe. | What the code produces now, stored as a reference file. |

**The refactor is not the goal. The refactor is the cheapest way to reach the
goal.**

This is the important part: **the preparation is the same in all five cases.**
Whether you fix a defect, extract one function, or write the missing
documentation, you first need a tool that answers two questions. Where is this
code used? Did I change the behavior?

That tool is the subject of this workshop.

### Which reason this workshop uses

Reason 3, with reason 1 inside it. The team must leave the 1.x interface of
fo-dicom. To do that, they must find every use of it. One of those uses holds
a defect.

Reasons 4 and 5 are not extra work. They are the output of
`02_requirements_engineering` and `03_test_driven_development`. Better
understanding, better documentation, and a first test set are results of this
method, not costs of it.

---

## 1. The problem is proof, not search

An AI agent writes code quickly. It is much more difficult to know whether the
new code is correct.

So the slow part is not reading the code base. The slow part is proof. You need
proof of two things:

1. The change is complete. No place was missed.
2. The change does not change the behavior.

A tool that gives such proof is called a **[test oracle](../../CONTEXT.md#language-legacy-refactoring)**. The term comes
from software testing and is about 45 years old; it does not mean the database
vendor. Four oracles exist, and they differ in strength:

| Step | Oracle | Question that it answers |
| --- | --- | --- |
| 1 | Compiler | Is the change complete? |
| 2 | Semantic index | How much code does this change touch? |
| 3 | Tests | Does the code still do what it promised? |
| 4 | Reference output files | Is the produced data the same, byte for byte? |

If the code base has no oracle at the step that your change needs, then make
that oracle first. Do not see this work as a delay. It is the first part of the
refactor.

## 2. Let the compiler find the places to change

Do not use a text search to find every place that calls a function. Do not ask
the AI model either. Both methods miss places.

Instead, break the old function on purpose, on a separate branch. Delete it,
rename it, or mark it so that the compiler refuses it.

| Language | How to break it |
| --- | --- |
| C++ | Delete the member. Or mark it `[[deprecated]]` and compile with `-Werror=deprecated-declarations`. |
| C# | Build with `-warnaserror:CS0618`, which promotes the obsolete warning. |

In C#, do **not** use `[Obsolete("message", error: true)]` to make the list. It
reports fewer places, because the compiler stops reporting uses of a field once
the declaration of that field is an error. Measured on the example code: the
promoted warning found 6 places, the error attribute found 3. Use the error
attribute to stop new use, not to count existing use.

The build then stops at every place that calls the function. On the example
code the text search gave 62 matches in 11 files, and 8 after you remove the
files that are not built. The compiler gave 6. The 2 extra were a **different
class with the same name**, which is the replacement for the deprecated one. A
text search cannot tell them apart; the compiler can.

The compiler shows
you the complete list. The list also holds the places that a text search cannot
find.

The roles change. The compiler does the search. The AI makes the changes. The
list is complete because of the method, not because somebody was careful.

Say the limits before somebody asks:

- Code inside a build option appears only in the build settings that you use.
  For a complete list, you must build every setting.
- A C++ template that nothing uses is not checked by the compiler.
- Reflection and text keys go around the compiler in both languages.

## 3. Static types help you

A legacy C++ or C# code base is the best case for AI-assisted work. The
compiler is free, it never misses a real result, and it checks everything that
you build.

A Python or JavaScript team does not get this for free. That team must write
the same checks by hand.

## 4. Green tests are not proof

The code compiles. The unit tests pass. This is still not proof.

In DICOM and in medical images, a change can move one pixel. It can change the
brightness and the contrast. It can remove a private tag. The unit tests do not
see these changes, because they do not compare the produced image.

Only a comparison of the output, byte for byte, answers the question.

Under IEC 62304, this set of oracles **is** the record that an auditor checks.
The same files that make the change safe also make it possible to audit. This
is the reason why AI-assisted work is acceptable in a medical product.

### Where the method comes from

Say this out of honesty, and because it is stronger than claiming novelty.

| Idea | Established name |
| --- | --- |
| Test oracle, and "the oracle problem" | Standard testing vocabulary. Weyuker, _On Testing Non-testable Programs_ (1982); Barr et al., _The Oracle Problem in Software Testing: A Survey_ (IEEE TSE, 2015). |
| Breaking the old function on purpose | **"Leaning on the Compiler"** — Michael Feathers, _Working Effectively with Legacy Code_ (2004). |
| Stored output files | **Characterization tests** (Feathers). Also golden-master or approval testing. |

What is new here is the framing, not the technique: the four rungs as a named
order, and the use of an oracle to prove that a change is **complete** where
the literature uses one to prove that output is **correct**.

## 5. Write down the intent first

Legacy code often has no documentation. So the first AI result is not a change
to the code. It is the written intent: the rules that the code keeps, the words
it uses, and the decisions behind it.

A reviewer cannot approve a change if the reviewer does not know whether the
old behavior was wanted. Written intent makes the later change possible to
review.

Review speed, not writing speed, sets how fast a team can move.

## 6. You can check the discipline

The rule: do not open a file until a tool tells you which lines to open.

The record of the session shows whether you kept the rule. So the claim "this
method works on a large code base" can be checked. It is not only an opinion.

The record is a file in the repository. So this claim needs no network
connection.
