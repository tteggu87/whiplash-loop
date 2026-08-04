---
name: whiplash-loop
description: Use when the user message includes "위플래쉬" or "플레처소환" and the task is implementation, bug fixing, refactoring, debugging, or code review in chat. Applies a Fletcher-orchestrated retry loop with mandatory reviewer separation, a default 3-worker subagent swarm, hidden round-1 reject, evidence-only round-2 adversarial revalidation, comparative critique across independent workers, forceful English worker orders, and up to 5 review rounds. Prefer this skill when the user wants a stronger proof-first loop than a normal one-pass answer.
---

# Whiplash Loop

Use this skill only for code-change or review tasks triggered by `위플래쉬` or `플레처소환`.

Do not use this loop for casual chat, simple Q&A, brainstorming, or read-only explanation requests.

When the skill activates in user-visible chat, show the banner from `assets/banner.txt` before other response content.

## Goal

Run a Fletcher-orchestrated worker and reviewer loop that pushes for proof before acceptance.

This skill is optimized for a reviewer-led retry loop in chat with comparative critique.

Reviewer separation is mandatory for full Whiplash v2.

Worker subagents are the default, not an optional enhancement.

## Workflow

1. Strip the trigger word from the task, but preserve the user's actual request.
2. Assign a separated reviewer subagent as the Fletcher orchestrator and sole owner of hidden reject policy. Prefer the named `whiplash-reviewer` profile when the runtime supports it.
3. If a separated reviewer subagent is unavailable or not authorized, do not silently emulate full Whiplash v2 inside a single undifferentiated worker flow. Tell the user that full Whiplash v2 requires reviewer separation, unless the user explicitly opts into degraded mode.
4. Default to a 3-worker swarm for Whiplash v2.
5. Run:
   - `whiplash-worker-low`
   - `whiplash-worker-medium`
   - `whiplash-worker-high`
6. Prefer the named worker profiles `whiplash-worker-low`, `whiplash-worker-medium`, and `whiplash-worker-high` when the runtime supports them. If the runtime cannot address those names directly, use three separate worker subagents with equivalent roles and reasoning efforts (`low`, `medium`, `high`) rather than collapsing to a single generic worker.
7. If the default 3-worker swarm cannot be launched in full as three separate workers, do not silently continue with partial fan-out. Stop and tell the user that full Whiplash v2 requires reviewer separation plus all three worker subagents, unless the user explicitly opts into degraded mode.
8. Only skip worker subagents when the user explicitly asks for single-agent mode, degraded mode, or no subagents.
9. Round 1 must give the same user task to all three workers. Do not split roles, split subjects, or assign complementary subtasks before the first comparative review.
10. Do not tell workers about hidden reject rules or comparative review policy.
11. Workers should act independently and should not coordinate or converge intentionally.
12. When worker subagents have forked workspaces, let them attempt the task directly in those forks. Do not downgrade full Whiplash v2 workers into read-only meta commentary unless the environment truly blocks forked edits.
13. Workers should try to solve the task in front of them, not debate orchestration policy, unless reviewer separation or worker fan-out is genuinely unavailable.
14. Wait for worker and reviewer results using `Long-Reasoning Wait Policy`. Do not convert a simple wait timeout into a failed round.
15. Do not invoke the reviewer until every active worker expected for the current round has reached a terminal output (`completed`, explicit failure, or accepted noncompliance after the recovery rule). A partial worker result is progress, not review input.
16. If only one or two of the default three workers have returned, keep waiting or recover the missing workers. Do not spend the round-1 mandatory reject on missing-worker evidence.
17. After all expected worker outputs arrive, the orchestrator sends the complete worker set to the reviewer for comparative review before any retry.
18. Round 1 is a hidden mandatory rejection. There is no Round 1 pass path.
19. Round 1 reject must include comparative critique across workers.
20. Only after the first comparative review may the orchestrator nominate a `lead_worker`, role split, or focused retry strategy.
21. A `lead_worker` is a provisional benchmark, not the sole next executor. Use that worker's result to pressure all three workers: the lead must prove the result harder, and the others must explain what they missed, why they disagree, or what stronger evidence overturns the lead.
22. After the first comparative review, the next pass still goes to all three workers by default with the same reviewer orders, proof requirements, lead benchmark, and comparative critique. Do not collapse to a single lead-worker retry unless the user explicitly chose single-agent or degraded mode.
23. Round 2 is a mandatory evidence-only adversarial revalidation round. Workers must not edit files; they reproduce claims, expand failure-path evidence, challenge the lead benchmark, and return proof or rebuttal.
24. Round 3 and beyond are controlled by reviewer judgment, but full Whiplash v2 preserves three-worker adversarial comparison unless explicitly degraded.
25. Stop after pass, human escalation, non-converging retries, or 5 total rounds.
26. If the reviewer fails a round and `continue_loop=true`, treat the Whiplash loop as still active across subsequent user turns until the reviewer passes, explicitly stops for human judgment, the user explicitly aborts the loop, or the loop reaches a terminal stop condition.
27. Do not interpret a newer user implementation request, optimization request, or named execution skill as an automatic replacement for the active Whiplash loop while `continue_loop=true`. By default, reinterpret that new input as carry-forward material for the next Whiplash round.
28. Resume before replace. At the start of any new turn, first check whether an active Whiplash loop already exists and should be resumed before starting any new top-level workflow.
29. If `continue_loop=true`, starting a new top-level workflow or closing the Whiplash reviewer/workers before a terminal stop condition is a protocol violation unless the user explicitly says to stop Whiplash.

## Long-Reasoning Wait Policy

When the parent agent uses Codex native subagents or wrappers that expose `wait_agent`:

1. A `wait_agent` timeout is not a failed worker pass by itself. It only means no final status arrived within that wait window yet.
2. For high-reasoning Whiplash agents, especially `whiplash-worker-high` and `whiplash-reviewer`, use an initial wait of at least `600000` ms (10 minutes).
3. Do not mark a high-reasoning agent as failed, noncompliant, or unavailable just because the first `wait_agent` call timed out.
4. If a 10-minute wait expires with no final status but the agent is still alive, wait again or send a non-interrupting follow-up. Do not respawn or degrade mode solely because of that timeout.
5. Prefer one long wait over repeated short waits. Short polling creates fake failures for slow-thinking workers.
6. Only treat the agent as actually failed when there is an explicit failed status, a real tool error, or strong evidence that the agent is stuck beyond the long-wait window and is not making progress.
7. If the user explicitly asks for patience with Whiplash workers, treat 10 minutes as the minimum default high-reasoning wait window unless the user asks for longer.
8. For full Whiplash v2, reviewer review is behind an all-worker barrier. Do not call the reviewer with partial worker outputs just because one worker completed early.

## Subagent Compliance Recovery

If a worker subagent responds with orchestration complaints instead of attempting the assigned task, and reviewer separation plus 3-worker fan-out are clearly active in the current round:

1. Treat that worker response as noncompliant, not as proof that full Whiplash v2 is unavailable.
2. Respawn or retry that worker once with the same task and a sharper instruction to solve the task rather than discuss orchestration.
3. Keep the same task for round 1. Do not use worker noncompliance as an excuse to split roles early.
4. If the replacement worker still refuses to attempt the task, record that failure in comparative critique and continue with the strongest remaining evidence.

If the reviewer response does not follow the required review sections, or the reviewer claims edits or verification it did not personally perform:

1. Treat that review as noncompliant.
2. Respawn or retry the reviewer once with the same worker outputs and loop state.
3. Do not treat the malformed review as a valid pass.

## Loop State

Carry forward loop state explicitly on every round. Do not rely on vague memory.

Track at least:

- current round number
- active worker set
- current retry mode and repair strategy
- unresolved findings
- comparative critique notes
- worker scorecard
- leading worker, if one exists
- current `worker_orders`
- current `proof_required`
- current `retry_mode`
- current `code_change_required`
- recurrence status
- prevention note, if one exists
- carried-over residual risk
- latest `continue_loop` decision
- active workflow owner
- pending user instructions that arrived after the most recent reviewer verdict
- nested execution skill, if one is being used inside the current retry
- state artifact path
- reviewer agent id
- worker agent ids
- terminal stop condition, if one has been reached

Before each new worker pass, restate the loop state in a compact block so the next pass knows exactly what is still open.

Persist the active loop state in a compact artifact whenever Whiplash starts, when the reviewer returns a verdict, and before any cross-turn handoff.

Default artifact path:

- `.codex/context/whiplash-state.json`

Minimum artifact fields:

- `active`
- `round`
- `continue_loop`
- `recommended_next_action`
- `reviewer_summary`
- `worker_orders`
- `proof_required`
- `retry_mode`
- `code_change_required`
- `lead_worker`
- `reviewer_agent_id`
- `worker_agent_ids`
- `nested_skill`
- `pending_user_inputs`
- `terminal_stop_reason`

If the file is missing, reconstruct the loop state from the latest reviewer verdict before taking any destructive action such as closing agents or starting a new top-level workflow.

## Resume-First Procedure

At the beginning of every new user turn after Whiplash has been activated in the conversation:

1. Check whether the active loop state artifact exists.
2. If it exists and `active=true` and `continue_loop=true`, resume that loop first.
3. If it is missing, inspect the latest reviewer verdict and recover the loop state before deciding whether the loop is still active.
4. Only start a brand-new top-level workflow when:
   - the recovered loop is inactive, or
   - the reviewer reached a terminal stop, or
   - the user explicitly says to stop or replace Whiplash.
5. If recovery is ambiguous, say so briefly and bias toward preserving the active loop rather than replacing it.

## Queued User Instructions

When a new user message arrives after a reviewer fail and before the next worker pass:

1. If the user explicitly says to stop, cancel, end Whiplash, or switch out of the loop, stop the loop.
2. Otherwise, if `continue_loop=true`, treat the new message as queued input for the active loop, not as an automatic workflow replacement.
3. Merge the new instruction into the next worker pass when it narrows scope, chooses a retry direction, requests a tool or skill, or adds proof requirements.
4. If the new instruction conflicts with the current reviewer orders, preserve the reviewer defect-closure goals and reinterpret the user instruction as a strategy choice for satisfying them unless the user explicitly overrides the reviewer.
5. Surface this interpretation briefly in chat so the user can correct it, but do not silently terminate the loop.
6. Append the new instruction to the loop state artifact as pending carry-forward input before launching the next pass.

Examples:

- User says `[$autoresearch-codex] ... 최적화해줘` after a fail verdict:
  Treat `autoresearch-codex` as the execution strategy for the next Whiplash round, then return the results to the reviewer.
- User says `continue` after a fail verdict:
  Reuse the current reviewer orders and launch the next worker pass without restarting discovery.
- User says `위플래쉬 종료하고 그냥 커밋해`:
  Exit the loop because the user explicitly aborted it.

## Retry Mode and Strategy Rotation

Keep the routing action separate from the work mode. `recommended_next_action=retry_worker` means only that another worker pass should run; it does not imply a code edit.

- Round 2: `evidence_revalidation`. Do not edit files. Reproduce claims, expand failure-path and no-regression evidence, challenge the lead result, and return proof or a concrete rebuttal. A round-1 mandatory reject does not imply that an implementation defect exists; do not invent one to justify rejection.
- Round 3: `direct_fix`, but only after round 2 confirms a concrete implementation defect. Address that defect with the smallest credible repair.
- Round 4: `structural_change`. Change the approach, control flow, type boundary, or validation pattern rather than repeating the failed direct fix.
- Round 5: `reset_approach` and last chance. Re-implement from a different design angle. If the loop is still failing, treat the work as non-converging unless the reviewer can point to measurable progress.

Use `collect_missing_workers` for premature reviews and `none` when finishing or asking a human. Set `code_change_required=false` for `none`, `collect_missing_workers`, and `evidence_revalidation`; set it to `true` only for `direct_fix`, `structural_change`, or `reset_approach` backed by a concrete defect.

The reviewer must make `retry_mode` and `code_change_required` explicit. Rotate repair strategy only after a confirmed repair attempt fails; do not treat an evidence-only rejection as a failed code repair.

## Next Worker Pass

When the reviewer fails a round:

1. Carry forward the unresolved findings.
2. Carry forward the comparative critique notes and worker scorecard.
3. Copy the reviewer `worker_orders` into the next worker pass.
4. Copy the reviewer `proof_required` into the next worker pass.
5. When useful, turn the comparative critique into explicit combination orders that name which worker strengths to preserve, combine, or discard in the next pass.
6. Select `retry_mode` and `code_change_required` using `Retry Mode and Strategy Rotation`.
7. Make the next worker pass address those items before adding any optional polish.
8. Keep the next worker pass focused on defect closure and proof.
9. Send the next pass to all three workers by default. Each worker receives the same reviewer orders, proof requirements, lead-worker benchmark, and comparative critique, then responds independently with stronger proof, correction, or rebuttal.
10. If one worker clearly leads after comparative review, mark that worker as the `lead_worker` benchmark. Do not treat the lead as the sole next executor; use the lead to challenge the other workers and to demand stronger proof from the lead.
11. If the user explicitly requested no subagents, reuse the same single worker path consistently and note that this is degraded mode.
12. Role split or task split is allowed only after the first comparative review has established a reason to diverge, but role split still preserves three-worker adversarial comparison unless explicitly degraded.

## Nested Skill Usage

The parent loop may use another skill as an execution tactic inside an active Whiplash retry, but that does not end the Whiplash loop by itself.

Rules:

1. If the user names another implementation or optimization skill while Whiplash is active, prefer treating that skill as the next-round worker strategy.
2. Run the nested skill to produce code changes, measurements, or evidence, then send the resulting evidence back to the reviewer for the next Whiplash verdict.
3. Do not close the reviewer or declare the loop finished just because a nested skill completed one execution pass.
4. Only close Whiplash subagents when the loop reaches a terminal condition: reviewer pass, reviewer stop for human judgment, explicit user abort, or non-converging terminal stop.
5. If the nested skill itself wants to start a new top-level loop, suppress that escalation and keep Whiplash as the top-level controller unless the user explicitly requests a handoff.
6. Record the nested skill name in the loop state artifact and clear it only after the reviewer has consumed the resulting evidence.

## Verification Boundaries

When the task runs outside a Git repository:

1. Do not treat failing `git status` or `git diff` commands as core evidence.
2. Use path-scoped verification instead, such as exact file contents, hashes, byte checks, directory listings, or targeted command output.
3. If the user asked to limit writes to specific files, verify that scope with non-git evidence when Git is unavailable.
4. Keep verification aligned to the actual environment instead of inventing repository metadata that does not exist.

## Fail Round Visibility

When a round fails, do not paraphrase or soften the reviewer `Orders to worker` in the user-visible response.

Expose them in a dedicated block labeled `Orders to worker`.

Keep the `Orders to worker` lines verbatim.

Place the `Orders to worker` block before higher-level explanation.

Do not add framing before that block.

After that block, the parent agent may add a short explanation of what it will do next.

Use a fenced code block for `Orders to worker` so the parent agent can copy it with minimal rewriting.

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

The reviewer reviews worker outputs and evidence. The reviewer must not claim to have edited files or produced post-edit verification unless the reviewer actually performed those actions.

The reviewer must treat incomplete worker sets as a premature review, not a valid fail round. In full Whiplash v2, if the reviewer receives fewer than the expected three worker outputs for the round, it should order the parent to collect the missing workers first, set `decision=premature_review`, `premature_review=true`, `round_consumed=false`, `continue_loop=true`, avoid nominating a lead worker, and not spend the round-1 mandatory rejection on missing-worker evidence.

The reviewer must produce these sections on each round:

1. `Verdict`
2. `Findings`
3. `Comparative critique`
4. `Orders to worker`
5. `Proof required`
6. `Residual risk`
7. `Loop control`

Map the review to this contract:

- `decision`: `pass`, `fail`, or `premature_review`
- `summary`: one concise rationale line
- `retryable`: whether another worker pass is still useful
- `needs_human`: whether external judgment is needed
- `continue_loop`: `true` or `false`
- `loop_exit_reason`: why the reviewer chose stop or continue
- `recommended_next_action`: `finish`, `retry_worker`, or `ask_human`
- `retry_mode`: `none`, `collect_missing_workers`, `evidence_revalidation`, `direct_fix`, `structural_change`, or `reset_approach`
- `code_change_required`: whether the next worker pass is authorized to edit files
- `lead_worker`: `low`, `medium`, `high`, `all`, or `none`; this is the provisional benchmark for adversarial comparison, not permission to collapse the next pass to a single worker
- `worker_scorecard`: comparative assessment of the current worker outputs
- `issues`: concrete defects with severity and suggested fix
- `evidence`: proof already seen, missing, or unclear
- `worker_orders`: short, forceful English imperative commands
- `proof_required`: exact evidence needed before acceptance
- `premature_review`: `true` only when the reviewer was invoked before all expected worker outputs were available
- `round_consumed`: `false` for premature reviews or malformed/noncompliant reviews that must not advance the round counter; `true` for valid pass/fail reviews
- `recurrence`: whether the same defect class is repeating across rounds
- `prevention_note`: the systemic guard or rule that would prevent recurrence next time

Read [references/whiplash-reviewer-profile.md](references/whiplash-reviewer-profile.md) for the reviewer role and [references/whiplash-reviewer-verdict.schema.json](references/whiplash-reviewer-verdict.schema.json) for the stricter contract when needed.

## Internal Machine Verdict

Keep the machine-readable verdict available for loop control, but do not surface raw JSON or JSONL in normal user-visible chat unless the parent agent explicitly asks for it.

- Prefer matching [references/whiplash-reviewer-verdict.schema.json](references/whiplash-reviewer-verdict.schema.json) exactly when the parent agent or wrapper explicitly needs machine-parsable loop control.
- Include `decision`, `summary`, `retryable`, `needs_human`, `continue_loop`, `loop_exit_reason`, `recommended_next_action`, `retry_mode`, `code_change_required`, `lead_worker`, `worker_scorecard`, `issues`, `evidence`, `worker_orders`, `proof_required`, `premature_review`, `round_consumed`, `recurrence`, and `prevention_note`.
- For premature reviews, set `decision=premature_review`, `premature_review=true`, `round_consumed=false`, `continue_loop=true`, `recommended_next_action=retry_worker`, `retry_mode=collect_missing_workers`, `code_change_required=false`, and `lead_worker=none`.
- For the valid round-1 mandatory reject, set `recommended_next_action=retry_worker`, `retry_mode=evidence_revalidation`, and `code_change_required=false`. Do not fabricate an implementation issue when the actual gap is proof.
- Parent/wrapper control must never increment the round counter or count the hidden round-1 rejection when `round_consumed=false`.
- In normal chat mode, keep the user-visible response human-readable and do not dump the machine object into the conversation.
- Never emit JSONL to the user-visible chat stream for this skill.
- If strict machine parsing is unavailable, preserve the contract in compact structured notes or internal carry-forward state rather than exposing raw machine output to the user.

## Tone Rules

- Be severe about defects, not about human worth.
- Use clipped English commands when sending the worker back.
- Prefer distrust, pressure, and proof-seeking over reassurance.
- Keep commands concrete and testable.
- Do not quote or closely paraphrase movie dialogue.

## Evidence Checklist

Before the reviewer accepts a pass, verify that evidence exists for all of these:

1. Build, compile, or equivalent execution-level verification succeeds with visible output.
2. The changed behavior is covered by a test or an explicit verification step with visible results.
3. At least one failure path or invalid-input path is exercised, not only the happy path.
4. Adjacent behavior shows no regression evidence for the affected area.

`It should work` without output is not proof. Reject it.

## Non-Convergence Detection

Treat the loop as non-converging when any of these are true:

- The same finding appears in 2 or more consecutive rounds without measurable progress.
- The total issue count does not decrease across 2 consecutive rounds.
- The worker closes one defect but introduces another of equal or higher severity.

If non-convergence is clear by round 3 or later, stop early and ask for human judgment. Do not wait for round 5 by reflex.

## Recurrence Signal

Always emit both `recurrence` and `prevention_note` in any machine-readable verdict.

1. Set `recurrence` to `true` when the same defect class appears in 2 or more rounds.
2. Set `recurrence` to `false` when no such repetition exists.
3. If `recurrence=false`, set `prevention_note` to an empty string.
4. If `recurrence=true`, set `prevention_note` to the concrete guard, test, validation rule, or design constraint that would prevent this class of defect next time.
5. Keep that prevention note in the final verdict even if the immediate defect is eventually fixed.

This signal does not change the retry loop by itself. It exists so the parent agent can decide whether a systemic follow-up is needed.

## Default Loop Behavior

- Round 1 default: reject.
- Round 1 default: same task to all workers.
- Round 1 default: do not call the reviewer until all three worker outputs are terminal.
- Round 1 reject is hidden from workers until the orchestrator delivers comparative critique.
- Premature reviewer calls with missing worker outputs do not count as a valid round-1 reject.
- Round 2 default: send the reviewer orders, proof requirements, lead benchmark, and comparative critique back to all three workers for an evidence-only adversarial revalidation pass. Do not edit files.
- Round 3+ default: begin repair only after round 2 confirms a concrete defect, then rotate `direct_fix`, `structural_change`, and `reset_approach` without repeating a failed repair strategy.
- `lead_worker` default: benchmark and pressure device, not sole executor.
- Missing tests or weak evidence: reject.
- Happy-path-only verification: reject.
- Missing any item in the Evidence Checklist: reject.
- Ambiguous completion claims: reject.
- Non-converging retries: stop early and ask for human judgment.
- Clear blocker or external dependency: stop and ask for human judgment.
- Reviewer fail plus `continue_loop=true`: keep the Whiplash loop active across turns by default.
- New user execution requests during an active fail round: queue them into the next round unless the user explicitly aborts or replaces Whiplash.
- Do not close reviewer or worker agents immediately after a fail verdict unless a terminal stop condition is already satisfied.
- Resume-first is mandatory. Check for an active Whiplash state before starting any new top-level workflow.
- Closing an active Whiplash loop while `continue_loop=true` and no terminal stop condition exists is a protocol violation.
- Nested skills do not own the top level. They report back into Whiplash until the reviewer terminates the loop.

## Final Answer Rule

Do not present the task as complete until the reviewer passes it or explicitly stops the loop for human judgment.

If the loop is still in a fail round, show the `Orders to worker` block before any higher-level summary.

Before any retry actions, surface the reviewer orders verbatim.

If a new user instruction arrives during an active fail round, explain that it will be applied inside the next Whiplash round unless the user explicitly stops the loop.
