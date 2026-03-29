# Claude Local Notes

Use this file as the quick editing reference for Claude Code sessions working in this repository.

## What Matters Most

- `whiplash-loop` is a skill repo, not a general app repo
- the main source of truth is the current Whiplash v2 contract in `.codex/skills/whiplash-loop/SKILL.md`
- the reviewer prompt, schemas, and evals must move together

## Files That Must Stay In Sync

- `.codex/skills/whiplash-loop/SKILL.md`
- `.codex/agents/whiplash-reviewer.toml`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-profile.md`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-verdict.schema.json`
- `.codex/agents/whiplash-reviewer-verdict.schema.json`
- `.codex/skills/whiplash-loop/evals/evals.json`

## Current Expected Runtime Behavior

- banner is shown on Whiplash activation
- reviewer separation is mandatory for full v2
- three workers are the default path
- round 1 uses the same task for all workers
- hidden reject belongs to the Fletcher reviewer, not the workers
- comparative critique happens before specialization
- fail rounds surface verbatim `Orders to worker`

## When Editing Contracts

If you add or change a verdict field:

1. add it to the skill contract text
2. add it to the reviewer instructions
3. update both schema copies
4. add or update eval coverage

## When Editing Public Behavior

If you change trigger behavior, loop flow, or visible output:

1. update `README.md`
2. check Mermaid diagrams
3. keep public wording consistent with the actual skill contract

## Non-Goals

- do not simplify the repo back to the old best-effort reviewer model
- do not drop the 3-worker default without an explicit design decision
- do not merge stale documentation assumptions from older PRs without reconciling them against current `main`
