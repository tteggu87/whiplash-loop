# Whiplash Loop

![Whiplash Loop Logo](./logo.png)

`whiplash-loop` is a Codex skill for Fletcher-style, proof-first retry orchestration triggered by `위플래쉬` or `플레처소환`.

## What It Does

- uses `whiplash-reviewer` as a separated Fletcher orchestrator
- hides the round-1 mandatory reject from workers
- runs a default 3-worker swarm (`low`, `medium`, `high`)
- gives the same initial task to all three workers in round 1
- compares worker outputs before retrying
- allows lead-worker or role-split retries only after the first comparative review
- pushes short, forceful English worker orders with proof requirements
- stops instead of silently degrading when full reviewer separation or full 3-worker fan-out is unavailable
- retries noncompliant workers or reviewers once before accepting malformed loop behavior
- uses non-git verification evidence when the task runs outside a Git repository
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
    B --> C["Require separated reviewer"]
    C --> D{"Reviewer separation available?"}
    D -->|No| E["Stop or ask for degraded mode"]
    D -->|Yes| F["Launch 3-worker swarm"]
    F --> G{"All 3 workers available?"}
    G -->|No| E
    G -->|Yes| H["Round 1: same initial task to all workers"]
    H --> I1["Worker low"]
    H --> I2["Worker medium"]
    H --> I3["Worker high"]
    I1 --> J{"Worker compliant?"}
    I2 --> K{"Worker compliant?"}
    I3 --> L{"Worker compliant?"}
    J -->|No| M1["Respawn once with sharper solve-the-task order"]
    K -->|No| M2["Respawn once with sharper solve-the-task order"]
    L -->|No| M3["Respawn once with sharper solve-the-task order"]
    J -->|Yes| N["Comparative review"]
    K -->|Yes| N
    L -->|Yes| N
    M1 --> N
    M2 --> N
    M3 --> N
    N --> O["Hidden round-1 reject"]
    O --> P["Comparative critique"]
    P --> Q{"Reviewer compliant?"}
    Q -->|No| R["Respawn reviewer once with same state"]
    R --> S["Verbatim Orders to worker + Proof required"]
    Q -->|Yes| S["Verbatim Orders to worker + Proof required"]
    S --> T{"Retry strategy after first critique?"}
    T -->|All| U["Retry swarm"]
    T -->|Lead worker| V["Retry lead worker with comparative notes"]
    T -->|Role split| W["Focused split retry"]
    U --> X["Use non-git evidence when git metadata is unavailable"]
    V --> X
    W --> X
    X --> N
    N --> Y{"Pass / ask human / continue?"}
    Y -->|Pass| Z["Finish"]
    Y -->|Ask human| AA["Stop"]
```

## Runtime Notes

- Full Whiplash v2 requires reviewer separation and the full 3-worker swarm. If either is unavailable, the loop should stop and ask for degraded mode instead of silently collapsing.
- Round 1 is always the same task to all workers. Early topic split is not part of the design.
- Worker or reviewer noncompliance is retried once before the loop accepts that failure mode as real.
- On fail rounds, `Orders to worker` should be shown verbatim before any higher-level explanation.
- Outside Git repositories, verification should rely on file contents, hashes, byte checks, listings, or targeted command output rather than failing `git diff` as core evidence.

## Note On The Logo

This repository now uses the supplied reference image directly as the logo asset.
