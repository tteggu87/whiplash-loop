# Whiplash Loop

![Whiplash Loop Logo](./logo.png)

`whiplash-loop` is a Codex skill for Fletcher-style, proof-first retry orchestration triggered by `위플래쉬` or `플레처소환`.

## What It Does

- uses `whiplash-reviewer` as a separated Fletcher orchestrator
- hides the round-1 mandatory reject from workers
- runs a 3-worker swarm (`low`, `medium`, `high`) for meaningful code tasks
- compares worker outputs before retrying
- pushes short, forceful English worker orders with proof requirements
- supports structured verdict data for internal loop control

## Main Files

- `.codex/skills/whiplash-loop/SKILL.md`
- `.codex/skills/whiplash-loop/agents/openai.yaml`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-profile.md`
- `.codex/skills/whiplash-loop/references/whiplash-reviewer-verdict.schema.json`
- `.codex/agents/whiplash-reviewer.toml`
- `.codex/agents/whiplash-worker-low.toml`
- `.codex/agents/whiplash-worker-medium.toml`
- `.codex/agents/whiplash-worker-high.toml`
- `.codex/agents/whiplash-reviewer-verdict.schema.json`

## Legacy Flow

This was the earlier reviewer-led loop before the orchestrated v2 redesign.

```mermaid
flowchart TD
    A["User prompt includes trigger"] --> B["whiplash-loop skill"]
    B --> C["Single worker pass"]
    C --> D["Review stage"]
    D --> E{"Round 1?"}
    E -->|Yes| F["Mandatory reject"]
    E -->|No| G["Reviewer decides pass or retry"]
    F --> H["Orders to worker + proof required"]
    G -->|Retry| H
    H --> I["Next worker pass"]
    I --> D
    G -->|Pass| J["Finish"]
    G -->|Ask human| K["Stop"]
```

## Current Flow

This is the current Whiplash v2 design.

```mermaid
flowchart TD
    A["User prompt includes trigger"] --> B["whiplash-loop skill"]
    B --> C["Fletcher orchestrator: whiplash-reviewer"]
    C --> D{"Subagent reviewer available?"}
    D -->|No| E["Stop or require degraded mode"]
    D -->|Yes| F["Launch worker swarm"]
    F --> G1["Worker low"]
    F --> G2["Worker medium"]
    F --> G3["Worker high"]
    G1 --> H["Comparative review"]
    G2 --> H
    G3 --> H
    H --> I["Hidden round-1 reject"]
    I --> J["Comparative critique"]
    J --> K["Orders to worker + proof required"]
    K --> L{"Lead worker chosen?"}
    L -->|All| M["Retry swarm"]
    L -->|One worker| N["Retry lead worker with comparative notes"]
    M --> H
    N --> H
    H --> O{"Pass / ask human / continue?"}
    O -->|Pass| P["Finish"]
    O -->|Ask human| Q["Stop"]
```

## Note On The Logo

This repository now uses the supplied reference image directly as the logo asset.
