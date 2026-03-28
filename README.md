# Whiplash Loop

![Whiplash Loop Logo](./logo.png)

`whiplash-loop` is a Codex skill for high-pressure worker and reviewer loops triggered by `위플래쉬` or `플레처소환`.

## What It Does

- runs a strong worker -> reviewer retry loop
- forces a round-1 calibration reject
- lets the reviewer decide continue or stop from round 2 onward
- pushes short, forceful English worker orders
- supports a named `whiplash-reviewer` agent plus structured verdict schema

## Main Files

- `.codex/skills/whiplash-loop/SKILL.md`
- `.codex/skills/whiplash-loop/agents/openai.yaml`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-profile.md`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-verdict.schema.json`
- `.codex/agents/whiplash-reviewer.toml`
- `.codex/agents/whiplash-reviewer-verdict.schema.json`

## Note On The Logo

This repository now uses the supplied reference image directly as the logo asset.
