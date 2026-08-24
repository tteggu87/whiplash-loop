# Whiplash Evidence Trajectory

Use this contract when a worker pass produces proof or when Round 2 revalidates Round-1 claims.

## Purpose

The trajectory makes evidence attributable to one task, worker, round, and candidate snapshot. It is a bounded audit packet, not a transcript, chain-of-thought record, correctness verdict, or replacement for the hidden round-1 mandatory rejection.

## Compact packet

Keep the packet small enough to compare across all workers:

```text
worker: low | medium | high
round: positive integer
task_ref: stable digest or bounded task identifier
candidate_ref: workspace, fork, patch, or artifact reference
snapshot_before:
  kind: git_head_plus_path_manifest_sha256 | path_manifest_sha256 | opaque | unavailable
  digest: lowercase SHA-256 or null when unavailable
  scope: explicit repository-relative claim scope
  git_head: commit id or null
  details: bounded method and exclusion summary
snapshot_after: same object shape, computed after the final mutation
mutations: ordered bounded file/symbol summaries
proof:
  - check: bounded command or manual check description
    kind: build | lint | typecheck | changed_behavior | failure_path | adjacent_no_regression | manual | other
    exit_status: integer | not_applicable | unavailable
    snapshot_ref: digest of the snapshot tested by this check
    acceptance_relevant: true when this proof is used to support completion
    result: bounded summary
    artifact_ref: optional output reference
claims: bounded claims supported by proof items
proof_gaps: missing, stale, inaccessible, or self-reported-only evidence
trajectory_status: complete | incomplete | stale | unavailable
```

Do not invent digests, timestamps, command output, or artifact references. Prefer repository-relative or opaque references. Do not copy secrets, private source payloads, full logs, full transcripts, or hidden reasoning into the packet.

Persist every normalized packet as JSON at `.codex/context/whiplash-trajectories/round-<round>-<worker>.json`. Validate it against [whiplash-evidence-trajectory.schema.json](whiplash-evidence-trajectory.schema.json), compute SHA-256 over the exact artifact bytes, and store `{path, sha256, worker, round}` in `whiplash-state.json`. Mailbox addresses and agent ids are ephemeral provenance, not durable artifact references.

When available, use `scripts/trajectory_tool.py snapshot` to construct snapshot objects and `scripts/trajectory_tool.py validate` to validate the final artifact and print its digest.

## Snapshot and freshness rules

1. Compute `snapshot_after` after the final mutation in an edit-authorized pass.
2. Associate each proof item with the snapshot it actually tested.
3. Treat required proof as current only when its `snapshot_ref` equals the final claimed snapshot.
4. When Git is available, combine `HEAD` with a content-derived manifest of the explicit claim scope. Include tracked, untracked, and ignored files inside that scope unless an exclusion is explicitly recorded.
5. A commit hash, `git status` output or its hash, a filename list, and a diff-stat are not content identities. They can stay unchanged while dirty file contents change.
6. Outside Git, hash the same user-authorized path scope or use another deterministic content identity.
7. If the environment cannot expose a reliable snapshot, mark it unavailable and let the reviewer assess the gap.

## Trajectory status

- `complete`: required evidence is observed, bounded, current for the final snapshot, and backed by a deterministic content digest for the explicit claim scope.
- `incomplete`: the trajectory is structurally usable but required proof is missing.
- `stale`: one or more acceptance-relevant proof items apply to an older snapshot.
- `unavailable`: the environment cannot produce a trustworthy packet or the worker failed trajectory recovery.

Completeness is procedural only. It never implies that the implementation is correct, never bypasses comparative review, and never creates a Round-1 pass path.

## Round 1

Workers do not receive the hidden reject policy. They solve the same task independently and return their trajectories as ordinary proof packets. The parent validates packet shape and freshness after all expected workers are terminal, recovering a malformed or missing packet once under the normal compliance rule.

The reviewer then compares:

- candidate differences;
- conflicting claims;
- checks that only one worker ran;
- stale or self-reported evidence;
- failure paths and adjacent behavior omitted by multiple workers.

Round 1 remains a hidden mandatory reject even when every trajectory is complete.

## Round 2

Before Round 2, the parent verifies every Round-1 artifact against its recorded SHA-256. Round 2 receives the exact same three bounded packets plus their path/digest pairs, reviewer orders, proof requirements, comparative critique, and lead benchmark. A comparison summary alone is insufficient. Each worker independently:

1. replays accessible proof against the referenced candidate snapshot;
2. reports non-reproducible or inaccessible claims explicitly;
3. expands failure-path and adjacent no-regression evidence;
4. challenges the lead claim and cross-worker disagreements;
5. returns proof or rebuttal without editing files.

The Round-2 trajectory must show `snapshot_before == snapshot_after`. A mutation makes that worker pass noncompliant with evidence-only revalidation; do not use post-mutation proof to justify a Round-2 pass.

Treat the Round-1 trajectory as a claim index, not as trusted truth. Re-execution or an independently observable check is stronger than repeating the original summary.
