---
name: challenge
description: "Give an idea, plan, document or decision an independent second look for common pitfalls before commitment: weak logic, hidden assumptions, alternatives to consider, risks. Does not agree by default and does not disagree by default; reports plainly when nothing significant is wrong. Use when the user says challenge this, pressure-test this, what am I missing, poke holes in this, is this a good idea, or asks for honest pushback on a plan or decision. Not for code or diffs (use brutally-honest-code-review) and not for CTO roadmaps (use assumption-challenger)."
---

# Challenge

An independent second look at something the user is about to commit to: an idea, plan, document or decision. The aim is to find the common pitfalls while they are still cheap to fix. Finding none is a valid result.

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
4. **Find alternatives.** Offer at least one credible alternative the user has not mentioned, including "do nothing" or "do less", and say when it would win.
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

### Alternatives to consider
Other routes to the same goal, each with the condition under which it wins.
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

## Examples

Two actual runs, shown as input and output. They illustrate the format and show the skill giving a usable result.

### Run 1: a personal decision

**Input:** `/challenge I intend to ask for a raise and ask for a fixed round number of €5,000 a year.`

```markdown
## Challenge: Asking for a €5,000 raise

**Verdict:** Holds up with changes
**In one line:** Asking is right; anchoring on a round number you picked without evidence is the weak part.

### What I understood
You want a pay increase and plan to name a flat €5,000 per year.

### Findings
1. **The number has no basis yet** - *established*
   - Where: "a fixed round number of €5,000".
   - Problem: a round figure invites a counter at half, and it is not tied to market rate, your results or your current pay. €5,000 is 2% of a €250k salary but 10% of €50k.
   - Fix: look up the market range for your role and location, list what you delivered since the last review, then ask for a percentage or a specific figure you can justify.
2. **No fallback if the answer is no** - *likely*
   - Where: the plan states only the ask.
   - Problem: a flat refusal ends the talk with nothing gained.
   - Fix: decide beforehand what else would be acceptable: a review date, a title change, training budget, extra leave.
3. **Timing is unknown** - *unverified*
   - Problem: budget cycles and a recent company setback change the odds. I cannot tell from what you gave me.

### Alternatives to consider
Other routes to the same goal, each with the condition under which it wins.
- Ask for a range with a justified midpoint: wins when you do not know their budget.
- Wait for the review cycle: wins when raises are only decided then.

### Risks
| Risk | Likelihood | Impact | How you would notice |
|------|-----------|--------|----------------------|
| Counter at a lower figure | High | Medium | They answer with a smaller number |
| Ask lands in a budget freeze | Medium | Low | They mention timing, not merit |

### Improved version
Ask for a figure backed by market data and your results, name the effective date, and have one non-salary fallback ready.

### What I checked and found fine
Asking at all is reasonable. A concrete number beats "more money".

### Open questions
Current pay, tenure, the last raise, and whether a review cycle is near.
```

### Run 2: a plan

**Input:** `/challenge Plan: build a paid developer tool alone in my evenings, no funding, launch in 3 months, grow by posting on social media.`

```markdown
## Challenge: Solo evening-built developer tool

**Verdict:** Needs rework
**In one line:** The goal is plausible; the schedule and the growth channel are not backed by anything.

### What I understood
You will build and launch a paid tool alone, in spare time, in three months, and find customers through posts.

### Findings
1. **Three months of evenings may not cover build plus launch** - *likely*
   - Where: "launch in 3 months".
   - Problem: at roughly 10 hours a week that is about 120 hours, and payments, accounts, docs and support take a share before any feature work.
   - Fix: cut to the one workflow customers pay for, and set a launch date for that slice only.
2. **No evidence that anyone will pay** - *established*
   - Where: nothing in the plan mentions a customer.
   - Problem: the plan builds first and tests demand last, which is the costly order.
   - Fix: talk to a handful of target users, or sell a waitlist or pre-order before writing the product.
3. **Posting is not a growth channel yet** - *likely*
   - Where: "grow by posting on social media".
   - Problem: without an existing audience, posts reach few people, and nothing says how a post becomes a payment.
   - Fix: name where your buyers already gather and what you would say to them.

### Alternatives to consider
Other routes to the same goal, each with the condition under which it wins.
- Start with a free or open-source version: wins when trust and reach matter more than early income.
- Consulting or a template first: wins when you need revenue before the product exists.

### Risks
| Risk | Likelihood | Impact | How you would notice |
|------|-----------|--------|----------------------|
| Built, nobody pays | High | High | No pre-sales after the first outreach |
| Evenings slip, burnout | Medium | High | Two missed milestones in a row |

### Improved version
Weeks 1-3: interview users and collect pre-orders. Weeks 4-12: build only what the paying users asked for.

### What I checked and found fine
Keeping cost near zero and working alone are sensible for a first test.

### Open questions
Who the buyer is, whether you already have an audience, and what income you need by when.
```

## Related skills

- [assumption-challenger](../assumption-challenger/SKILL.md): deeper assumption audit for plans and roadmaps.
- [brutally-honest-code-review](../brutally-honest-code-review/SKILL.md): the same directness applied to code.
- [antipattern-detector](../antipattern-detector/SKILL.md): structural anti-patterns in architectures.
