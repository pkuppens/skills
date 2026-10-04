# ADR 003: AI assistance, network, and confidentiality

**Status:** Accepted
**Date:** 2026-10-04
**Context:** [`workshops/legacy-refactor/`](../../workshops/legacy-refactor/README.md). The decision governs how a live demonstration reaches a model, and how a regulated team should do the same work. It extends the routing rules in the [`ai-factory`](../../skills/ai-factory/SKILL.md) skill.

## Context

AI-assisted refactoring sends source code to a model. The model can run in the
cloud or on-premises. The choice is a confidentiality decision, not a
performance decision.

A demonstration on a visitor site has a second problem. The site network may
block the model API. Three network options exist, and each option leaks
something.

| Option | What it exposes | Verdict for a demonstration | Verdict for daily work |
| --- | --- | --- | --- |
| A. The site network | The site proxy and the site logs see the traffic. The proxy may inspect TLS. | Acceptable for public example code only. | Not acceptable for product code without an agreement. |
| B. A phone hotspot | My own carrier sees the traffic. The source still goes to a cloud model. | Acceptable for public example code only. | Not acceptable for product code. |
| C. No network | Nothing leaves the machine. | **Preferred.** | Not applicable. |
| D. An on-premises model | Nothing leaves the site network. | Good, but it needs setup time. | **Preferred for confidential code.** |

The example code in the workshop is public, so option A and option B are
acceptable for the demonstration. The audience's own code is not public, so
neither option is acceptable for their daily work.

## Decision

1. **Design the demonstration for option C.** Store the output of each notebook
   cell in Git. The workshop then proves every claim with no network
   connection. Treat a network as an improvement, not as a requirement.
2. **Use a hotspot, not the site network, if a live run is wanted.** The
   example code is public, so the exposure is acceptable. A hotspot also avoids
   a request for site access and avoids a proxy that inspects TLS.
3. **Never send the audience's own source code to a cloud model during a
   session.** Not from a hotspot, and not from their network. There is no
   agreement that permits it.
4. **For a regulated team, route by sensitivity.** Confidential work runs on an
   on-premises model. Public work can run on a cloud model. This is the routing
   rule of the [`ai-factory`](../../skills/ai-factory/SKILL.md) skill.
5. **Say clearly what is exposed.** Name what leaves the machine, where it
   goes, and who can read it. Raise the subject before the audience raises it.

## Consequences

**Good.** The session works in a room with no network. The confidentiality
answer is part of the method, not an excuse. The routing rule gives the audience
a path that their own compliance process can accept.

**Bad.** An on-premises model is weaker than a current cloud model. The work
must be split, and the split costs effort. Some tasks become slower.

**Important.** The oracle ladder reduces this cost. The compiler, the semantic
index, the tests, and the golden outputs run locally. They need no model. The
model makes the edits, and the local oracles judge them. A weaker local model is
therefore acceptable for the edit step, because the verdict does not come from
the model.

That is the strongest argument for this way of working in a regulated setting.
The evidence is produced locally, by deterministic tools, and it is auditable.

## Revisit when

- The organisation signs an agreement with a cloud model provider. Then option A
  becomes available for product code, within the terms of the agreement.
- An on-premises model becomes strong enough for the edit step on complex code.
  Then the split becomes simpler.
- A regulator publishes guidance on AI assistance in IEC 62304 processes. Then
  check this ADR against it.
