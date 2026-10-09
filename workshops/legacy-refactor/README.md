# AI-assisted refactoring of legacy code

A 2-hour workshop. You need no preparation and no prior knowledge of this
repository. Start here.

## The idea in one sentence

**An AI agent can change code fast. The hard part is knowing the change is
right, so set up the thing that checks the change *before* you let the AI
change anything.**

## Why this matters

Nobody changes old code just because it is old. There is always a reason: a
bug, a new feature, an old library, code nobody understands, code without
tests.

Whatever the reason, you need two answers before you change anything:

1. **Where is this code used?** Did I find every place?
2. **Did I change the behavior?** Does it still do the same thing?

An AI agent does not answer these questions for you. It guesses quickly. You
need something that *knows*.

## Three things to remember

1. **First choose the checker, then let the AI change code.** The checker is
   any tool that gives a yes or no without your opinion: the compiler, the
   tests, or comparing output before and after the change. (The textbook name
   is *test oracle*.)
2. **Start with the cheapest checker: the compiler.** It already exists, it is
   fast, and it finds real uses of the code. A text search finds names, not
   uses.
3. **A green build is not proof that the behavior did not change.** The
   compiler shows that the change is complete. Only tests or output
   comparisons show that the behavior stayed the same.

## What we do in the session

We work on a real, public, open-source code base:
[fo-dicom](https://github.com/fo-dicom/fo-dicom), a C# library for medical
images (DICOM). Its old interface was moved out of the main package, so it has
to be migrated, just like legacy code at work.

| Notebook | The question | Status |
| --- | --- | --- |
| [`00_setup`](notebooks/00_setup.ipynb) | Can we build this old code, the same way on every machine? An AI skill writes the build container. | Done |
| [`01_build_warnings`](notebooks/01_build_warnings.ipynb) | The build works but shows 11 warnings. Which ones matter? We fix them with the compiler as the checker. | Done |
| [`01a_find_obsolete_call_sites`](notebooks/01a_find_obsolete_call_sites.ipynb) | Optional deep dive into `01`: how many uses does a text search find, and how many does the compiler find? | Done |
| `02_test_driven_development` | Some fixes change behavior. Write a test first, then make the change. New to this? See the [TDD primer](../test-driven-development/README.md). | Planned |

Each notebook stands on its own and starts with a short summary. You can open
them in a browser on GitHub, with the results already shown. You do not need to
install anything.

## The results: what we checked

These numbers come from real runs that are saved in the notebooks. They are not
slides.

- **The old code builds the same way for everyone.** One container, every tool
  version pinned, no network needed. The next person gets the same build, so
  there is no "works on my PC".
  ([`00_setup`](notebooks/00_setup.ipynb), and the full session record in
  [`evidence/`](evidence/legacy-build-container/README.md))
- **11 warnings were really 4 decisions.** What mattered was not the warning
  code but whether the fix changes behavior. We fixed some warnings and kept
  three on purpose, with the reason written next to the code.
  ([`01_build_warnings`](notebooks/01_build_warnings.ipynb))
- **The compiler judged three fix attempts.** It accepted one, rejected one,
  and showed that the third would change the public interface. A text search
  could not have shown any of this.
- **A text search found 62 matches. The compiler found 6 real uses.** If you
  had trusted the search, you would have edited the wrong places.
  ([`01a_find_obsolete_call_sites`](notebooks/01a_find_obsolete_call_sites.ipynb))

**What is not proven yet:** that the behavior stayed the same. No tests ran.
That is `02`, which is still planned.

## Try it on your own code

The method is packaged as **skills**: instructions that an AI agent (for
example Claude Code) reads and follows. You install them in your own project
and run them there.

- [`legacy-build-container`](../../skills/legacy-build-container/SKILL.md):
  writes a build container for an old project.
- [`call-site-exhaustiveness`](../../skills/call-site-exhaustiveness/SKILL.md):
  uses the compiler to find every use of the code you want to change.
- [`oracle-first-refactor`](../../skills/oracle-first-refactor/SKILL.md):
  chooses the checker before any change.

How to install the skills, or run the notebooks yourself: [SETUP.md](SETUP.md).

## More detail (optional)

You do not need these files to follow the session.

| File | Contents |
| --- | --- |
| [CLAIMS.md](CLAIMS.md) | The reasons to refactor, and the six claims, each with a way to check it. |
| [notebooks/README.md](notebooks/README.md) | How the notebooks are built and run. |
| [VERIFICATION.md](VERIFICATION.md) | Acceptance checks, including the offline block. |

## Licence

**Learn from the workshop, build with the skills.** This directory is
[CC BY-NC-ND 4.0](../LICENSE): read it and share it unchanged, but do not sell
it or publish changed versions. The [`skills/`](../../skills/) are
[MIT](../../LICENSE): use them freely, including commercially. Reasons:
[ADR 004](../../docs/decisions/004-licensing-split.md).
