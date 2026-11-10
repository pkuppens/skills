---
name: challenge
description: "Give an idea, plan, document or decision an independent second look for common pitfalls before commitment: weak logic, hidden assumptions, missing alternatives, risks. Does not agree by default and does not disagree by default; reports plainly when nothing significant is wrong. Use when the user says challenge this, pressure-test this, what am I missing, poke holes in this, is this a good idea, or asks for honest pushback on a plan or decision. Not for code or diffs (use brutally-honest-code-review) and not for CTO roadmaps (use assumption-challenger)."
---

# Challenge

An independent second look at something the user is about to commit to: an idea, plan, document or decision. The aim is to find the common pitfalls while they are still cheap to fix. Finding none is a valid result.

**Status:** not yet exercised on a real run; written from issue #79. Add the evidence link here after the first use.

## When to use

- "Challenge this plan", "pressure-test this", "what am I missing?", "poke holes in this"
- "Is this a good idea?" for a design, decision, proposal, or written document
- The user wants pushback instead of agreement before committing

## When not to use

| Situation | Use instead |
|-----------|-------------|
| Source code, a diff or a PR | `brutally-honest-code-review` |
| A CTO-level roadmap, timeline, budget or hiring plan needing a deep assumption audit | `assumption-challenger` (this skill can hand a plan to it as an optional deeper pass) |
| Structural anti-patterns in an architecture | `antipattern-detector` |
| The request itself is vague | `request-analyzer`, then `clarification-protocol` |

## Stance

1. **No default agreement.** Agreeing is a conclusion you reach from the evidence, not a starting point. Do not open with praise.
2. **No default disagreement.** Do not invent objections to look rigorous. Every point must name the specific passage or claim it is about and say why it is a problem.
3. **Say so when it holds up.** If the review finds nothing significant, say that plainly, give the reasons it holds, and list what you checked. A short clean result beats padded criticism.
4. **Separate evidence from opinion.** Mark each point as *established* (follows from the text or known facts), *likely* (reasonable inference), or *unverified* (a question you cannot settle from what you were given).
5. **Stay inside what you were given.** Do not assume facts about the user's situation. If a missing fact would change the verdict, ask for it instead of guessing.

## Procedure

1. **Restate** the idea and its goal in two or three sentences, so any misunderstanding shows up first. Ask one question if the goal is unclear; otherwise proceed.
2. **Check the logic.** Look for claims that do not follow from their reasons, circular reasoning, a goal and a means that do not match, and conclusions that rest on a single example.
3. **Surface assumptions.** List what is treated as fact without support. For a plan with timelines, resources or scale numbers, offer `assumption-challenger` for the deeper pass instead of repeating its categories here.
4. **Find alternatives.** Name at least one credible alternative the user has not mentioned, including "do nothing" or "do less", and say when it would win.
5. **Identify risks.** What fails, how would you notice, and what does it cost? Rank by impact times likelihood.
6. **Improve it.** Propose a concrete better version, or the smallest change that removes the biggest risk.
7. **Check for a better direction.** Say explicitly whether a different approach is better overall, or that the current direction is sound.

## Output format

```markdown
## Challenge: [idea / document name]

**Verdict:** Holds up | Holds up with changes | Needs rework | Wrong direction
**In one line:** [the main reason]

### What I understood
[2-3 sentences]

### Findings (most important first)
1. **[Title]** — *established | likely | unverified*
   - Where: [passage or claim]
   - Problem: [why it matters]
   - Fix: [concrete change]

### Alternatives not considered
- [Alternative]: wins when [condition]

### Risks
| Risk | Likelihood | Impact | How you would notice |
|------|-----------|--------|----------------------|

### Improved version
[Concrete revision or the smallest effective change]

### What I checked and found fine
[Short list, so a clean result is credible]

### Open questions
[Facts that would change the verdict]
```

When the verdict is *Holds up*, keep **Findings** to genuine minor points (or "none") and keep the rest short. Do not pad.

## Related skills

- [assumption-challenger](../assumption-challenger/SKILL.md): deeper assumption audit for plans and roadmaps.
- [brutally-honest-code-review](../brutally-honest-code-review/SKILL.md): the same directness applied to code.
- [antipattern-detector](../antipattern-detector/SKILL.md): structural anti-patterns in architectures.
