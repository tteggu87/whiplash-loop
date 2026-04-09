# Whiplash Loop

![Whiplash Loop Logo](./logo.png)

`whiplash-loop` is a Codex skill for Fletcher-style, proof-first retry orchestration triggered by `위플래쉬` or `플레처소환`.

## What It Does

- shows the PR2-style Whiplash ASCII banner at activation time
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
- rotates retry strategy across rounds instead of repeating the same failed move
- tracks recurrence plus a prevention note for defect classes that keep returning
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
    A["User prompt includes trigger"] --> B["Show Whiplash banner"]
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
    O --> P["Comparative critique + recurrence tracking"]
    P --> Q{"Reviewer compliant?"}
    Q -->|No| R["Respawn reviewer once with same state"]
    Q -->|Yes| S["Verbatim Orders to worker + Proof required"]
    R --> S
    S --> T{"Retry strategy for this round?"}
    T -->|Round 2| U["Direct fix retry"]
    T -->|Round 3| V["Structural change retry"]
    T -->|Round 4| W["Reset approach retry"]
    T -->|Round 5| X["Last chance retry"]
    U --> Y["Use non-git evidence when git metadata is unavailable"]
    V --> Y
    W --> Y
    X --> Y
    Y --> Z{"Pass / ask human / continue?"}
    Z -->|Continue| N
    Z -->|Pass| AA["Finish"]
    Z -->|Ask human| AB["Stop"]
```

## Runtime Notes

- Activation currently includes the PR2-style banner before the loop begins.
- Full Whiplash v2 requires reviewer separation and the full 3-worker swarm. If either is unavailable, the loop should stop and ask for degraded mode instead of silently collapsing.
- Round 1 is always the same task to all workers. Early topic split is not part of the design.
- Worker or reviewer noncompliance is retried once before the loop accepts that failure mode as real.
- On fail rounds, `Orders to worker` should be shown verbatim before any higher-level explanation.
- Active fail rounds should persist through `.codex/context/whiplash-state.json` so the next user turn resumes the same loop before any new top-level workflow starts.
- New execution requests that arrive during an active fail round should be queued into the next Whiplash round unless the user explicitly stops or replaces Whiplash.
- Outside Git repositories, verification should rely on file contents, hashes, byte checks, listings, or targeted command output rather than failing `git diff` as core evidence.
- Retry strategy rotates across rounds: direct fix, structural change, reset approach, then last chance.
- Evidence must cover build-or-equivalent output, changed behavior, at least one failure path, and no-regression confidence.
- Repeated defect classes should be surfaced through `recurrence` and `prevention_note`.

## Note On The Logo

This repository now uses the supplied reference image directly as the logo asset.
