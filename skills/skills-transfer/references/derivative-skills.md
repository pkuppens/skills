# Derivative skills

A **derivative skill** is a new `skills/<name>/` folder that depends on a **base skill** without modifying the base in place.

## When to create one

- Personal or team policy on top of a public skill (auto-accept recommendations, extra checklist, locale)
- Thin wrapper that points agents at canonical content plus local rules
- Experimentation before proposing an upstream PR to this library

## When not to

- One-line tweak → consider project rule or `CLAUDE.md` instead
- Full copy of a public skill with no delta → install via Skills CLI only

## Authoring rules

1. New `name` and `description` (third person; include triggers).
2. In the body: state which base skill to load first and what changes (order, defaults, output).
3. Use relative links only one level deep from `SKILL.md` into `references/` or `examples.md`.
4. Run `skills-ref validate` on the derivative folder before merge.

## Upstreaming

If the delta benefits everyone, open a PR to `pkuppens/skills` or to the upstream package repo. Remove the derivative when the base skill absorbs the behaviour.

## Example

See [examples.md](../examples.md) (grill-with-autoaccept sketch).
