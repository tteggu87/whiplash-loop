---
name: whiplash-loop
description: Run a Whiplash v2 coding or code-review loop in Claude Code when the user invokes /whiplash-loop or requests 위플래쉬 or 플레처소환. Three independent workers return snapshot-bound evidence to a separate reviewer for replay and evaluation.
---

# Whiplash Loop for Claude Code

Run this skill as the parent in the main conversation. Use `$ARGUMENTS` as the task when supplied, or use the current user request. An explicit slash invocation is equivalent to the shared trigger.

Read the [shared loop contract](../../../.codex/skills/whiplash-loop/SKILL.md) and the [evidence packet contract](../../../.codex/skills/whiplash-loop/references/whiplash-evidence-trajectory.md) before dispatch. Resolve these files from `${CLAUDE_SKILL_DIR}`, including when this skill was loaded from another checkout with `--add-dir`. Write loop state and evidence under `${CLAUDE_PROJECT_DIR}`, the project being worked on.

Use Claude Code's Agent tool with the named `whiplash-worker-low`, `whiplash-worker-medium`, `whiplash-worker-high`, and `whiplash-reviewer` profiles. Wait for all expected worker outputs using Claude's agent completion mechanism. Give workers the task, candidate reference, retry instructions, and worker-facing evidence contract. Keep parent and reviewer policy out of worker prompts. For edit-authorized passes, use isolated candidates where available and check that they start from the intended task baseline. Retain candidate references for replay. If a candidate cannot be accessed later, record the proof gap.

## Store evidence before review

1. Ask each worker for the shared packet, with its worker tier and round, task and candidate references, before/after snapshots, ordered mutations and checks, claims, proof gaps, and trajectory status. Wait for the expected worker set to finish. Validate packet identity, required fields, and whether the proof matches the claimed snapshot. Retry a missing or malformed packet once under the shared recovery rule.
2. The parent normalizes each usable packet into `.codex/context/whiplash-trajectories/round-<round>-<worker>.json`. Compute SHA-256 from the bytes written with a local hashing tool such as `shasum -a 256 "$packet_path"`. Record each repository-relative `{path, sha256, worker, round}` in `.codex/context/whiplash-state.json`. Record unresolved gaps explicitly. If writes are unavailable, report the affected trajectory as unavailable.
3. Only then send the reviewer the complete expected worker set, with the normalized packets, persisted references, and any unresolved gaps. Use the reviewer's verdict to control the next pass.

## Check file integrity before Round 2

After the reviewer returns a verdict directing an `evidence_revalidation` retry, load the Round-1 packets for all three expected workers as one dispatch set. For each stored reference, parse and hash the same bytes. Confirm that the JSON identifies the expected worker and round and that its SHA-256 matches the digest already in loop state. A new digest must never silently replace a mismatched recorded digest. Try to recover missing references and missing, unreadable, or mismatched packets before dispatch. If recovery cannot restore a packet, record a replay gap for that worker and exclude the unverified bytes.

Send each of the three workers the same complete packet contents from that verified set and the exact path/digest pairs, with the reviewer orders, proof requirements, comparative critique, and lead benchmark. When a gap remains, send every worker the same verified subset and the same gap list. A summary alone is insufficient.

## Replay proof during Round 2

Workers independently reproduce or challenge the received claims and record inaccessible or stale proof. They must leave task files unchanged and return a fresh packet with matching before/after snapshots and no mutations. The parent persists those packets after the pass and hands them to the reviewer. These file checks confirm which evidence was received. The workers test the claims and report what they can reproduce, refute, or cannot verify.
