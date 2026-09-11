"""Summarize exported AIDP job-run details without exposing logs or parameters.

Offline only. Accepts an OCI raw-request envelope or a JobRun object per file.
Task wall time is not Spark compute time; null timestamps stay unknown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


SIGNATURES = {
    "volume_transport_disconnected": "Transport endpoint is not connected",
    "volume_connection_aborted": "Software caused connection abort",
    "command_tracking_error": "WORKFLOW_0015",
    "command_missing": "not found in context",
    "cancel_execution_failed": "Failed to cancel task run execution",
    "task_timeout": "Task run timed out",
    "oom_killed": "OOMKilled",
    "jvm_out_of_memory": "OutOfMemoryError",
    "spark_wrong_base_path": "Wrong basePath",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def epoch_ms(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(value) and value > 0 else None


def elapsed_seconds(start, end):
    if epoch_ms(start) is None or epoch_ms(end) is None:
        return None
    return round((end - start) / 1000, 3) if end >= start else None


def summarize_task(key, task, selected):
    state = task.get("state") or {}
    if not isinstance(state, dict):
        raise ValueError("Invalid task state")
    message = str(state.get("stateMessage") or "")
    return {
        "attempt_ref": digest(key)[:12],
        "task": task.get("taskKey"),
        "scope": ("unknown" if selected is None else "current" if key in selected else "historical"),
        "status": state.get("status"),
        "start_epoch_ms": epoch_ms(task.get("startTime")),
        "end_epoch_ms": epoch_ms(task.get("endTime")),
        "wall_seconds": elapsed_seconds(task.get("startTime"), task.get("endTime")),
        "signatures": [name for name, text in SIGNATURES.items() if text in message],
    }


def unwrap_run(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JobRun object or OCI response envelope")
    if "data" in payload:
        if str(payload.get("status", "200")).split(" ", 1)[0] != "200":
            raise ValueError("Cannot summarize an unsuccessful API response")
        payload = payload["data"]
    if not isinstance(payload, dict) or not payload.get("key"):
        raise ValueError("JobRun detail requires key")
    return payload


def summarize_attempts(payload):
    summaries = payload.get("taskRunSummaryMap") or {}
    current = payload.get("taskToTaskRunMap")
    if not isinstance(summaries, dict) or not all(isinstance(t, dict) for t in summaries.values()):
        raise ValueError("Invalid taskRunSummaryMap")
    if current is not None and (not isinstance(current, dict)
                               or not all(isinstance(v, str) for v in current.values())):
        raise ValueError("Invalid taskToTaskRunMap")
    warnings = []
    if not current:
        warnings.append("CURRENT_ATTEMPT_MAP_UNAVAILABLE")
    elif any(k not in summaries or summaries[k].get("taskKey") != task
             for task, k in current.items()):
        warnings.append("CURRENT_ATTEMPT_MAP_INCONSISTENT")
    selected = set(current.values()) if not warnings else None
    return [summarize_task(key, task, selected) for key, task in summaries.items()], warnings


def summarize(payload):
    payload = unwrap_run(payload)
    tasks, warnings = summarize_attempts(payload)
    state = payload.get("state") or {}
    if not isinstance(state, dict):
        raise ValueError("Invalid job state")
    repairs = payload.get("repairHistory") or []
    if not isinstance(repairs, list) or not all(isinstance(r, dict) for r in repairs):
        raise ValueError("Invalid repairHistory")
    return {
        "run_ref": digest(payload["key"])[:12],
        "status": state.get("status"),
        "reported_wall_seconds": elapsed_seconds(payload.get("startTime"), payload.get("endTime")),
        "repair_count": len(repairs),
        "repair_attempt_wall_seconds": [elapsed_seconds(r.get("startTime"), r.get("endTime")) for r in repairs],
        "task_definition_sha256": digest(payload["tasks"]) if payload.get("tasks") else None,
        "parameters_sha256": digest(payload["parameters"]) if payload.get("parameters") is not None else None,
        "unrepaired_success": state.get("status") == "SUCCESS" and not repairs,
        "comparison_note": "Also verify input snapshot, code version and historical compute; these hashes alone do not prove comparable runs.",
        "warnings": warnings,
        "tasks": tasks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        summaries = [summarize(json.loads(p.read_text(encoding="utf-8-sig"))) for p in args.files]
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f"Invalid input ({type(error).__name__}); no output written.\n")
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # ponytail: bounded exports fit in memory; stream inputs for larger incident bundles.
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(summaries, indent=2, ensure_ascii=False) + "\n")
    except OSError as error:
        parser.exit(2, f"Output not completed ({type(error).__name__}); existing files were not overwritten.\n")
    print(f"Summarized {len(summaries)} job-run details")


if __name__ == "__main__":
    main()
