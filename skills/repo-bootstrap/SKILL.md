---
name: repo-bootstrap
description: Explains that pkuppens/skills is bootstrapping until migration from pkuppens/pkuppens completes. Use when you need a placeholder skill so Skills CLI list and CI smoke tests succeed before full SKILL_TREE migration.
---

# Repository bootstrap

This skill exists so **Skills CLI** discovery (`npx skills add pkuppens/skills --list`) and **validate-skills** CI succeed before the full tree from [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens) lands.

**Remove or replace** this directory when real migrated skills cover discovery and validation (see migration issues; parent epic [#90](https://github.com/pkuppens/pkuppens/issues/90)).
