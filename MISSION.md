# Mission

`pkuppens/skills` is the canonical, curated library of Agent Skills for AI-assisted software delivery. Our mission is to collect, author, and curate high-quality skills that cover the entire Software Development Life Cycle (SDLC) — from ideation, requirements and architecture through implementation, testing, deployment, and operations — so agents can provide coherent, project‑specific assistance at every stage.

We are a virtual company offering SDLC services through composable skills: skills in this repo are either authored by the maintainer or selected and curated from external sources by reference. Curation emphasizes best practices, provenance metadata, explicit licensing, and practical examples so teams can safely adopt and adapt skills for their projects.

Adaptivity and project specificity are core requirements: skills should be composable and tunable for a project's constraints, and the library should support feedback-driven refinement so recommendations improve with real usage while preserving traceability.

The library follows the Agent Skills specification (https://agentskills.io/specification) so spec-compliant agents can install skills consistently. Curation and governance are the moat — we maintain a clear boundary between canonical skills (source-of-truth here) and vendor/derivative skills (installed or forked externally), and treat duplication or name-collisions as defects. See [skills/SKILL_TREE.md](skills/SKILL_TREE.md) for the strategy → skill pipeline and [CONTEXT.md](CONTEXT.md) and [CLAUDE.md](CLAUDE.md) for process fundamentals.
