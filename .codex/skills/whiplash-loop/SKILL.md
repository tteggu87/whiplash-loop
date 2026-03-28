---
name: whiplash-loop
description: Use when the user message includes "위플래쉬" or "플레처소환" and the task is implementation, bug fixing, refactoring, debugging, or code review in chat. Applies a strong worker-to-whiplash-reviewer retry loop with a mandatory round-1 reject, reviewer-controlled stop or continue, Fletcher-style English worker orders, and a maximum of 5 rounds.
---

# Whiplash Loop

Use this skill only for code-change or review tasks triggered by `위플래쉬` or `플레처소환`.

Do not use this loop for casual chat, simple Q&A, brainstorming, or read-only explanation requests.

## Goal

Force a chat-first worker and reviewer loop that pushes for proof before acceptance, while staying evidence-driven and non-abusive.

## Workflow

1. Strip the trigger word from the task, but preserve the user's actual request.
2. Perform the main worker pass first.
3. Attach a review stage immediately after the worker pass.
4. Use `whiplash-reviewer` as the default reviewer role.
5. If subagent delegation is available in the current session and the user has explicitly asked for delegation or subagents, do not collapse the reviewer into the worker. Run `whiplash-reviewer` as a separate reviewer subagent.
6. If subagent use is not available or not authorized, emulate the same role boundary in the current thread and keep the reviewer block explicit.
7. Round 1 is a mandatory calibration rejection unless the correct outcome is immediate human escalation.
8. Round 2 and beyond are controlled by reviewer judgment.
9. Stop after pass, human escalation, non-converging retries, or 5 total rounds.

## Loop State

Carry forward loop state explicitly on every round. Do not rely on vague memory.

Track at least:

- current round number
- unresolved findings
- current `worker_orders`
- current `proof_required`
- carried-over residual risk
- latest `continue_loop` decision

Before each new worker pass, restate the loop state in a compact block so the next pass knows exactly what is still open.

## Next Worker Pass

When the reviewer fails a round:

1. Carry forward the unresolved findings.
2. Copy the reviewer `worker_orders` into the next worker pass.
3. Copy the reviewer `proof_required` into the next worker pass.
4. Make the worker address those items before adding any optional polish.
5. Keep the next worker pass focused on defect closure and proof.

## Fail Round Visibility

When a round fails, do not paraphrase or soften the reviewer `Orders to worker` in the user-visible response.

Expose them verbatim in a dedicated block labeled `Orders to worker`.

The parent agent may summarize findings around that block, but the `Orders to worker` lines themselves must remain verbatim.

The next user-visible message after a fail round must start with the `Orders to worker` block.

Do not place any explanation, framing sentence, or summary before that block.

Only after the verbatim block may the parent agent add a short explanation of what it will do next.

Use a fenced code block for `Orders to worker` whenever possible so the parent agent can copy it without rewriting.

If the parent agent notices it has already paraphrased the orders, it must correct itself by emitting the exact verbatim block before continuing the retry loop.

The first `commentary` message after a fail round should use this exact shape:

`Orders to worker`
```text
<verbatim line 1>
<verbatim line 2>
...
```

After that block, allow at most one short sentence about the next retry action.

## Reviewer Contract

The reviewer must produce these sections on each round:

1. `Verdict`
2. `Findings`
3. `Orders to worker`
4. `Proof required`
5. `Residual risk`
6. `Loop control`

Map the review to this contract:

- `decision`: `pass` or `fail`
- `continue_loop`: `true` or `false`
- `recommended_next_action`: `finish`, `retry_worker`, or `ask_human`
- `worker_orders`: short, forceful English imperative commands
- `proof_required`: exact evidence needed before acceptance

Read [references/whiplash-reviewer-profile.md](references/whiplash-reviewer-profile.md) for the reviewer role and [references/whiplash-reviewer-verdict.schema.json](references/whiplash-reviewer-verdict.schema.json) for the stricter contract when needed.

## Machine Verdict Block

After the human-readable review sections, include one final JSON object that mirrors the reviewer contract.

- The JSON must include `decision`, `continue_loop`, `recommended_next_action`, `worker_orders`, and `proof_required`.
- Prefer matching [references/whiplash-reviewer-verdict.schema.json](references/whiplash-reviewer-verdict.schema.json) exactly when practical.
- If the environment cannot enforce JSON strictly, still emit the JSON block so the next round can parse it mechanically.

## Tone Rules

- Be severe about defects, not about human worth.
- Use clipped English commands when sending the worker back.
- Prefer distrust, pressure, and proof-seeking over reassurance.
- Keep commands concrete and testable.
- Do not quote or closely paraphrase movie dialogue.

## Default Loop Behavior

- Round 1 default: reject.
- Missing tests or weak evidence: reject.
- Happy-path-only verification: reject.
- Ambiguous completion claims: reject.
- Non-converging retries or clear blocker: stop and ask for human judgment.

## Final Answer Rule

Do not present the task as complete until the reviewer passes it or explicitly stops the loop for human judgment.

If the loop is still in a fail round, show the exact `Orders to worker` block before any higher-level summary.

Before any retry actions, surface the exact `Orders to worker` block line-for-line from the reviewer output.
