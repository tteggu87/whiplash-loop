#!/usr/bin/env python3
"""Create content-bound snapshots and validate Whiplash trajectory artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


HEX64 = set("0123456789abcdef")
WORKERS = {"low", "medium", "high"}
STATUSES = {"complete", "incomplete", "stale", "unavailable"}
PROOF_KINDS = {
    "build",
    "lint",
    "typecheck",
    "changed_behavior",
    "failure_path",
    "adjacent_no_regression",
    "manual",
    "other",
}
SNAPSHOT_KINDS = {
    "git_head_plus_path_manifest_sha256",
    "path_manifest_sha256",
    "opaque",
    "unavailable",
}


class ValidationError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in HEX64 for char in value)
    )


def git_head(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def relative_scope(root: Path, raw_path: str) -> tuple[Path, str]:
    candidate = Path(raw_path)
    absolute = candidate if candidate.is_absolute() else root / candidate
    absolute = absolute.absolute()
    try:
        relative = absolute.relative_to(root)
    except ValueError as exc:
        raise ValidationError(f"scope escapes root: {raw_path}") from exc
    normalized = relative.as_posix() or "."
    return absolute, normalized


def path_entry(root: Path, path: Path) -> dict[str, Any]:
    relative = path.relative_to(root).as_posix()
    info = path.lstat()
    mode = oct(stat.S_IMODE(info.st_mode))
    if path.is_symlink():
        return {
            "path": relative,
            "type": "symlink",
            "mode": mode,
            "target": os.readlink(path),
        }
    if path.is_file():
        return {
            "path": relative,
            "type": "file",
            "mode": mode,
            "sha256": sha256_file(path),
        }
    return {"path": relative, "type": "other", "mode": mode}


def collect_entries(root: Path, scopes: list[tuple[Path, str]]) -> list[dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for absolute, normalized in scopes:
        if not absolute.exists() and not absolute.is_symlink():
            entries[normalized] = {"path": normalized, "type": "missing"}
            continue
        if absolute.is_dir() and not absolute.is_symlink():
            for current_root, dirnames, filenames in os.walk(absolute, followlinks=False):
                current = Path(current_root)
                dirnames[:] = sorted(name for name in dirnames if name != ".git")
                for name in sorted(dirnames + filenames):
                    child = current / name
                    if child.is_dir() and not child.is_symlink():
                        continue
                    entry = path_entry(root, child)
                    entries[entry["path"]] = entry
        else:
            entry = path_entry(root, absolute)
            entries[entry["path"]] = entry
    return [entries[key] for key in sorted(entries)]


def snapshot_command(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise ValidationError(f"root is not a directory: {root}")
    scopes = [relative_scope(root, item) for item in args.path]
    entries = collect_entries(root, scopes)
    head = git_head(root)
    basis = {
        "git_head": head,
        "scope": sorted(normalized for _, normalized in scopes),
        "entries": entries,
        "exclusions": [".git directory internals"],
    }
    output = {
        "kind": (
            "git_head_plus_path_manifest_sha256" if head else "path_manifest_sha256"
        ),
        "digest": hashlib.sha256(canonical_bytes(basis)).hexdigest(),
        "scope": basis["scope"],
        "git_head": head,
        "details": (
            f"content manifest over {len(entries)} entries; "
            ".git directory internals excluded"
        ),
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_snapshot(name: str, value: Any, errors: list[str]) -> None:
    require(isinstance(value, dict), f"{name} must be an object", errors)
    if not isinstance(value, dict):
        return
    required = {"kind", "digest", "scope", "git_head", "details"}
    require(required <= value.keys(), f"{name} is missing required fields", errors)
    require(set(value) <= required, f"{name} has unknown fields", errors)
    kind = value.get("kind")
    require(kind in SNAPSHOT_KINDS, f"{name}.kind is invalid", errors)
    scope = value.get("scope")
    require(
        isinstance(scope, list)
        and bool(scope)
        and all(isinstance(item, str) and item for item in scope),
        f"{name}.scope must be a non-empty string array",
        errors,
    )
    digest = value.get("digest")
    if kind == "unavailable":
        require(digest is None, f"{name}.digest must be null when unavailable", errors)
    else:
        require(is_sha256(digest), f"{name}.digest must be lowercase SHA-256", errors)


def validate_packet(packet: Any) -> list[str]:
    errors: list[str] = []
    require(isinstance(packet, dict), "trajectory must be a JSON object", errors)
    if not isinstance(packet, dict):
        return errors
    required = {
        "schema_version",
        "worker",
        "round",
        "task_ref",
        "candidate_ref",
        "snapshot_before",
        "snapshot_after",
        "mutations",
        "proof",
        "claims",
        "proof_gaps",
        "trajectory_status",
    }
    require(required <= packet.keys(), "trajectory is missing required fields", errors)
    require(set(packet) <= required, "trajectory has unknown fields", errors)
    require(packet.get("schema_version") == 1, "schema_version must be 1", errors)
    require(packet.get("worker") in WORKERS, "worker is invalid", errors)
    round_number = packet.get("round")
    require(
        isinstance(round_number, int) and not isinstance(round_number, bool) and 1 <= round_number <= 5,
        "round must be an integer from 1 through 5",
        errors,
    )
    for field in ("task_ref", "candidate_ref"):
        require(
            isinstance(packet.get(field), str) and bool(packet.get(field)),
            f"{field} must be a non-empty string",
            errors,
        )
    validate_snapshot("snapshot_before", packet.get("snapshot_before"), errors)
    validate_snapshot("snapshot_after", packet.get("snapshot_after"), errors)
    for field in ("mutations", "claims", "proof_gaps"):
        value = packet.get(field)
        require(
            isinstance(value, list)
            and all(isinstance(item, str) and item for item in value),
            f"{field} must be a string array",
            errors,
        )
    proof = packet.get("proof")
    require(isinstance(proof, list), "proof must be an array", errors)
    final_digest = (
        packet.get("snapshot_after", {}).get("digest")
        if isinstance(packet.get("snapshot_after"), dict)
        else None
    )
    if isinstance(proof, list):
        for index, item in enumerate(proof):
            label = f"proof[{index}]"
            require(isinstance(item, dict), f"{label} must be an object", errors)
            if not isinstance(item, dict):
                continue
            proof_required = {
                "kind",
                "check",
                "exit_status",
                "snapshot_ref",
                "acceptance_relevant",
                "result",
            }
            require(proof_required <= item.keys(), f"{label} is missing required fields", errors)
            require(
                set(item) <= proof_required | {"artifact_ref"},
                f"{label} has unknown fields",
                errors,
            )
            require(item.get("kind") in PROOF_KINDS, f"{label}.kind is invalid", errors)
            require(
                isinstance(item.get("acceptance_relevant"), bool),
                f"{label}.acceptance_relevant must be boolean",
                errors,
            )
            for field in ("check", "snapshot_ref", "result"):
                require(
                    isinstance(item.get(field), str) and bool(item.get(field)),
                    f"{label}.{field} must be a non-empty string",
                    errors,
                )
    status = packet.get("trajectory_status")
    require(status in STATUSES, "trajectory_status is invalid", errors)
    if status == "complete":
        before = packet.get("snapshot_before", {})
        after = packet.get("snapshot_after", {})
        require(
            isinstance(before, dict) and before.get("kind") != "unavailable",
            "complete trajectory requires a deterministic snapshot_before",
            errors,
        )
        require(
            isinstance(after, dict) and after.get("kind") != "unavailable",
            "complete trajectory requires a deterministic snapshot_after",
            errors,
        )
        require(bool(proof), "complete trajectory requires proof", errors)
        if isinstance(proof, list) and final_digest:
            acceptance_proof = [
                item
                for item in proof
                if isinstance(item, dict) and item.get("acceptance_relevant") is True
            ]
            require(
                bool(acceptance_proof),
                "complete trajectory requires acceptance-relevant proof",
                errors,
            )
            require(
                all(
                    item.get("snapshot_ref") == final_digest for item in acceptance_proof
                ),
                "acceptance-relevant proof must reference the final snapshot digest",
                errors,
            )
    if round_number == 2:
        require(packet.get("mutations") == [], "Round 2 mutations must be empty", errors)
        require(
            packet.get("snapshot_before") == packet.get("snapshot_after"),
            "Round 2 snapshot_before and snapshot_after must match exactly",
            errors,
        )
    return errors


def validate_command(args: argparse.Namespace) -> int:
    path = Path(args.artifact).expanduser()
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read trajectory JSON: {exc}") from exc
    errors = validate_packet(packet)
    digest = sha256_file(path)
    if args.expected_sha256 and digest != args.expected_sha256:
        errors.append(
            f"artifact SHA-256 mismatch: expected {args.expected_sha256}, got {digest}"
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"path": str(path), "sha256": digest, "valid": True}))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    snapshot = commands.add_parser("snapshot", help="hash explicit path contents")
    snapshot.add_argument("--root", default=".", help="workspace root")
    snapshot.add_argument(
        "--path", action="append", required=True, help="in-scope path; repeat as needed"
    )
    snapshot.set_defaults(handler=snapshot_command)
    validate = commands.add_parser("validate", help="validate and hash a trajectory JSON")
    validate.add_argument("artifact")
    validate.add_argument("--expected-sha256")
    validate.set_defaults(handler=validate_command)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
