# Skills transfer — examples

## Derivative skill: grill-with-autoaccept (sketch)

**Goal:** Same grilling discipline as a base `grill-with-docs` skill, but the agent states a recommended answer per question and proceeds without waiting for the user on each step (policy defined by the author).

**Layout:**

```text
grill-with-autoaccept/
├── SKILL.md
└── references/
    └── base-skill.md   # optional: link or short pointer to base
```

**SKILL.md frontmatter (example):**

```yaml
---
name: grill-with-autoaccept
description: >-
  Stress-tests plans using grill-style questions with a stated recommendation each
  step and no per-question user wait. Use when the user wants grill-with-docs rigor
  but prefers auto-accept of recommended answers.
---
```

**Body essentials:**

1. On activation, read the base skill instructions (from installed `grill-with-docs` or linked path).
2. For each question: state the question, give **Recommendation:** …, then apply that choice and continue (unless the user interrupts).
3. Update project `CONTEXT.md` when terms are resolved (same as base grill skill).

**Do not** copy the entire base `SKILL.md` into the derivative unless license and maintenance require a fork; prefer reference + delta.

## Install one skill from this library

```bash
npx skills add https://github.com/pkuppens/skills --skill skills-transfer -y
```

Project scope (default) installs under the current repo’s agent skills path; add `-g` for user-global. See [references/install-modes.md](references/install-modes.md).

## List discoverable skills in a remote repo

```bash
npx skills add https://github.com/pkuppens/skills --list -y
```
