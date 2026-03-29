---
name: whiplash-loop
description: Use when the user message includes "위플래쉬" or "플레처소환" and the task is implementation, bug fixing, refactoring, debugging, or code review in chat. Applies a Fletcher-orchestrated retry loop with mandatory reviewer separation, a default 3-worker subagent swarm, hidden round-1 reject, comparative critique across independent workers, forceful English worker orders, and up to 5 review rounds. Prefer this skill when the user wants a stronger proof-first loop than a normal one-pass answer.
---

# Whiplash Loop

Use this skill only for code-change or review tasks triggered by `위플래쉬` or `플레처소환`.

Do not use this loop for casual chat, simple Q&A, brainstorming, or read-only explanation requests.

## Goal

Run a Fletcher-orchestrated worker and reviewer loop that pushes for proof before acceptance.

This skill is optimized for a reviewer-led retry loop in chat with comparative critique.

Reviewer separation is mandatory for full Whiplash v2.

Worker subagents are the default, not an optional enhancement.

## Workflow

1. Strip the trigger word from the task, but preserve the user's actual request.
2. Assign `whiplash-reviewer` as the Fletcher orchestrator and sole owner of hidden reject policy.
3. If reviewer subagent separation is unavailable or not authorized, do not silently emulate full Whiplash v2. Tell the user that full Whiplash v2 requires subagents, unless the user explicitly opts into degraded mode.
4. Default to a 3-worker swarm for Whiplash v2.
5. Run:
   - `whiplash-worker-low`
   - `whiplash-worker-medium`
   - `whiplash-worker-high`
6. Only skip worker subagents when the user explicitly asks for single-agent mode, degraded mode, or no subagents.
7. Do not tell workers about hidden reject rules or comparative review policy.
8. Workers should act independently and should not coordinate or converge intentionally.
9. After worker outputs arrive, the orchestrator compares them before any retry.
10. Round 1 is a hidden mandatory rejection unless the correct outcome is immediate human escalation.
11. Round 1 reject must include comparative critique across workers.
12. Round 2 and beyond are controlled by reviewer judgment.
13. Stop after pass, human escalation, non-converging retries, or 5 total rounds.

## Loop State

Carry forward loop state explicitly on every round. Do not rely on vague memory.

Track at least:

- current round number
- active worker set
- unresolved findings
- comparative critique notes
- worker scorecard
- leading worker, if one exists
- current `worker_orders`
- current `proof_required`
- carried-over residual risk
- latest `continue_loop` decision

Before each new worker pass, restate the loop state in a compact block so the next pass knows exactly what is still open.

## Next Worker Pass

When the reviewer fails a round:

1. Carry forward the unresolved findings.
2. Carry forward the comparative critique notes and worker scorecard.
3. Copy the reviewer `worker_orders` into the next worker pass.
4. Copy the reviewer `proof_required` into the next worker pass.
5. Make the next worker pass address those items before adding any optional polish.
6. Keep the next worker pass focused on defect closure and proof.
7. If one worker clearly leads after comparative review, prefer sending the next pass through that worker while preserving the comparative notes from the other workers.
8. If the user explicitly requested no subagents, reuse the same single worker path consistently and note that this is degraded mode.

## Fail Round Visibility

When a round fails, prefer not to paraphrase or soften the reviewer `Orders to worker` in the user-visible response.

Expose them in a dedicated block labeled `Orders to worker`.

When the runtime supports it cleanly, keep the `Orders to worker` lines verbatim.

Prefer to place the `Orders to worker` block before higher-level explanation.

Avoid long framing before that block.

After that block, the parent agent may add a short explanation of what it will do next.

Use a fenced code block for `Orders to worker` whenever possible so the parent agent can copy it with minimal rewriting.

If the parent agent notices it has heavily softened the orders, it should restate them more directly before continuing the retry loop.

Preferred fail-round shape:

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
3. `Comparative critique`
4. `Orders to worker`
5. `Proof required`
6. `Residual risk`
7. `Loop control`

Map the review to this contract:

- `decision`: `pass` or `fail`
- `summary`: one concise rationale line
- `retryable`: whether another worker pass is still useful
- `needs_human`: whether external judgment is needed
- `continue_loop`: `true` or `false`
- `loop_exit_reason`: why the reviewer chose stop or continue
- `recommended_next_action`: `finish`, `retry_worker`, or `ask_human`
- `lead_worker`: `low`, `medium`, `high`, `all`, or `none`
- `worker_scorecard`: comparative assessment of the current worker outputs
- `issues`: concrete defects with severity and suggested fix
- `evidence`: proof already seen, missing, or unclear
- `worker_orders`: short, forceful English imperative commands
- `proof_required`: exact evidence needed before acceptance

Read [references/whiplash-reviewer-profile.md](references/whiplash-reviewer-profile.md) for the reviewer role and [references/whiplash-reviewer-verdict.schema.json](references/whiplash-reviewer-verdict.schema.json) for the stricter contract when needed.

## Internal Machine Verdict

Keep the machine-readable verdict available for loop control, but do not surface raw JSON or JSONL in normal user-visible chat unless the parent agent explicitly asks for it.

- Prefer matching [references/whiplash-reviewer-verdict.schema.json](references/whiplash-reviewer-verdict.schema.json) exactly when the parent agent or wrapper explicitly needs machine-parsable loop control.
- Include `decision`, `summary`, `retryable`, `needs_human`, `continue_loop`, `loop_exit_reason`, `recommended_next_action`, `lead_worker`, `worker_scorecard`, `issues`, `evidence`, `worker_orders`, and `proof_required`.
- In normal chat mode, keep the user-visible response human-readable and do not dump the machine object into the conversation.
- Never emit JSONL to the user-visible chat stream for this skill.
- If strict machine parsing is unavailable, preserve the contract in compact structured notes or internal carry-forward state rather than exposing raw machine output to the user.

## Tone Rules

- Be severe about defects, not about human worth.
- Use clipped English commands when sending the worker back.
- Prefer distrust, pressure, and proof-seeking over reassurance.
- Keep commands concrete and testable.
- Do not quote or closely paraphrase movie dialogue.

## Default Loop Behavior

- Round 1 default: reject.
- Round 1 reject is hidden from workers until the orchestrator delivers comparative critique.
- Missing tests or weak evidence: reject.
- Happy-path-only verification: reject.
- Ambiguous completion claims: reject.
- Non-converging retries or clear blocker: stop and ask for human judgment.

## Final Answer Rule

Do not present the task as complete until the reviewer passes it or explicitly stops the loop for human judgment.

If the loop is still in a fail round, show the `Orders to worker` block before any higher-level summary when practical.

Before any retry actions, surface the reviewer orders as directly as the runtime allows.
