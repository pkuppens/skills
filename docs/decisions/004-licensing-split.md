# ADR 004: Licensing split — MIT skills, restricted workshops

**Status:** Accepted
**Date:** 2026-10-04
**Context:** The repository is public and MIT licensed since the first commit. The new [`workshops/`](../../workshops/) directory holds teaching material that has a different commercial value from the skills.

> **This ADR is not legal advice.** The author is an engineer, not a lawyer. If
> money, a contract, or an employer agreement depends on this split, then ask a
> lawyer to confirm it.

## Context

The root `LICENSE` file is the MIT licence. It is dated 2026 and it has not
changed since the bootstrap commit. The MIT licence covers "the Software and
associated documentation files". So it covers documentation, not only code.

Two facts follow from this.

1. **MIT cannot be taken back.** Every version that was published under MIT
   stays under MIT for the people who received it. A later change of licence
   works only for later versions.
2. **Therefore the licence must be decided before the first push.** After the
   push, the choice is made.

The new material has two parts with different value.

| Part | What it is | Value if a competitor copies it |
| --- | --- | --- |
| `skills/` | The method, as instructions that an agent reads. | Low harm. The skills are the public proof of ability. A skill that nobody may use is not proof of anything. |
| `workshops/` | The teaching material: the talk order, the notebooks, the stored output, the examples. | High harm. Another person could present this workshop as their own, or sell it as training. |

The author wants the skills to stay free, and wants to keep control of the
teaching material.

## Options considered

| Option | Result | Problem |
| --- | --- | --- |
| A. MIT for everything | Simple. One licence. | Gives away the teaching material. |
| B. Restrict everything | Protects everything. | Breaks the plugin marketplace promise and the mission of a public skills library. |
| C. MIT for `skills/`, a restricted licence for `workshops/` | Keeps the library open. Protects the teaching material. | Two licences in one repository. A reader can miss the split. |
| D. Move the workshop to a private repository | Strongest protection. | The audience cannot read it. The workshop then has no value as public proof. |

## Decision

**Option C.**

1. **The root `LICENSE` stays the MIT licence, unchanged.** Do not add text
   above or below it. Licence detection tools read that file, and extra text
   can stop them from recognising the MIT licence.
2. **`workshops/LICENSE` holds a second licence** for that directory and
   everything inside it: **CC BY-NC-ND 4.0**. People may read it and share it
   without change. They may not sell it and may not publish a changed version.
3. **Both READMEs state the split.** The root `README.md` has a Licence
   section. The workshop `README.md` has one too. A reader must not need to
   find a file to learn the rule.
4. **The skills stay MIT, including the new refactoring skills.** The method is
   the portfolio. It must be usable.
5. **Example code bases keep their own licences.** fo-dicom and DCMTK are not
   covered by either licence here.

### Why CC BY-NC-ND and not "all rights reserved"

"All rights reserved" would stop the audience from keeping a copy and from
showing it to a colleague. That removes the reason to publish it at all.

CC BY-NC-ND permits exactly what is wanted. The audience may read it, keep it,
and pass it on. Nobody may sell it or publish a changed version.

### Why NoDerivatives does not block the audience

The "NoDerivatives" term applies to the teaching material. It does not block
the audience from using the method on their own code, because the method lives
in `skills/`, which is MIT. Those files may be changed and used for commercial
work.

State this when somebody asks. The split is: **learn from the workshop, build
with the skills.**

## Consequences

**Good.** The skills library stays open, and the plugin marketplace keeps
working. The teaching material keeps its value. The audience can still read
everything.

**Bad.** Two licences in one repository need care. GitHub shows one licence for
the repository, which is MIT. A reader who looks only at the GitHub label will
believe that MIT covers everything. The README sections exist to correct that,
but a reader can miss them.

**Consequence for future work.** Any new directory needs a decision. Default:
new skills are MIT, new teaching material is CC BY-NC-ND. Write the choice in
the directory.

## Revisit when

- The workshop has served its purpose and the author wants to release it
  openly. Relaxing a licence is always possible. Restricting one is not.
- The repository gains a second author. Then the copyright holder is no longer
  one person, and both licences need review.
- A sponsor or an employer claims rights to the material. Then check the
  employment agreement before anything else.
