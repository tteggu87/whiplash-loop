# Claude Code Guide

This repository packages `whiplash-loop`, a Codex skill for Fletcher-style proof-first retry orchestration.

## Repository Purpose

- provide a reusable chat skill triggered by `위플래쉬` or `플레처소환`
- keep the Whiplash v2 loop contract explicit across skill text, reviewer prompt, schemas, and evals
- publish a self-contained skill repo that other Codex users can install

## Current Architecture

The repository has two layers:

1. Skill layer
- `.codex/skills/whiplash-loop/SKILL.md`
- `.codex/skills/whiplash-loop/agents/openai.yaml`
- `.codex/skills/whiplash-loop/references/*`
- `.codex/skills/whiplash-loop/evals/evals.json`
- `.codex/skills/whiplash-loop/assets/*`

2. Agent layer
- `.codex/agents/whiplash-reviewer.toml`
- `.codex/agents/whiplash-reviewer-verdict.schema.json`
- `.codex/agents/whiplash-worker-low.toml`
- `.codex/agents/whiplash-worker-medium.toml`
- `.codex/agents/whiplash-worker-high.toml`

## Whiplash v2 Contract

The current repo is not the old single-worker loop. The active contract is:

- separated reviewer required for full v2
- default 3-worker swarm
- round 1 gives the same task to all workers
- hidden round-1 reject owned by the reviewer/orchestrator
- comparative critique before role split
- fail rounds surface verbatim `Orders to worker`
- retry strategy rotation across later rounds
- evidence checklist for pass/fail
- non-convergence detection
- recurrence tracking with `recurrence` and `prevention_note`

## Editing Rules

When changing loop behavior, keep these files aligned:

- `.codex/skills/whiplash-loop/SKILL.md`
- `.codex/agents/whiplash-reviewer.toml`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-profile.md`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-verdict.schema.json`
- `.codex/agents/whiplash-reviewer-verdict.schema.json`
- `.codex/skills/whiplash-loop/evals/evals.json`
- `README.md` when public behavior or diagrams change

## Important Guardrails

- do not silently weaken mandatory reviewer separation or the default 3-worker swarm
- do not silently shrink eval coverage when adding features
- do not let schema, reviewer prompt, and skill text drift apart
- do not replace non-git verification rules with git-only assumptions
- do not quote or closely paraphrase movie dialogue in worker/reviewer copy

## Safe Change Checklist

Before considering a change complete:

1. check whether the change affects public README behavior
2. update both verdict schema copies together
3. update reviewer instructions and the skill text together
4. add or adjust eval coverage for the new rule
5. sanity-check JSON files after editing

## For Claude Code Users

This repo is still a Codex skill repo, but these notes exist so Claude Code users can navigate and edit it without guessing the loop contract from scattered files.
