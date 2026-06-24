from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from common import AGENTS_DIR, ROOT, STATUS_PATH, load_backlog, render_status

TASK_ID = re.compile(r"^NH-[A-Z]+-[0-9]{3}$")
STATES = {
    "proposed",
    "planning",
    "needs_decision",
    "ready",
    "in_progress",
    "blocked",
    "dev_complete",
    "qa_failed",
    "qa_passed",
    "review_failed",
    "accepted",
    "done",
    "superseded",
}
TRANSITIONS = {
    "proposed": {"planning", "superseded"},
    "planning": {"ready", "needs_decision", "superseded"},
    "needs_decision": {"planning", "superseded"},
    "ready": {"in_progress", "blocked", "superseded"},
    "in_progress": {"blocked", "dev_complete", "superseded"},
    "blocked": {"in_progress", "superseded"},
    "dev_complete": {"qa_failed", "qa_passed", "in_progress"},
    "qa_failed": {"in_progress", "superseded"},
    "qa_passed": {"review_failed", "accepted", "in_progress"},
    "review_failed": {"in_progress", "superseded"},
    "accepted": {"done", "in_progress"},
    "done": set(),
    "superseded": set(),
}
ACTIVE_STATES = {
    "in_progress",
    "blocked",
    "dev_complete",
    "qa_failed",
    "qa_passed",
    "review_failed",
    "accepted",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def valid_time(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def path_exists(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and (ROOT / value).is_file()


def path_contains(value: Any, expected: str) -> bool:
    if not path_exists(value):
        return False
    return expected.lower() in (ROOT / value).read_text(encoding="utf-8").lower()


def paths_overlap(left: str, right: str) -> bool:
    left_path = Path(left)
    right_path = Path(right)
    return left_path == right_path or left_path in right_path.parents or right_path in left_path.parents


def validate_task(
    task: dict[str, Any],
    all_ids: set[str],
    errors: list[str],
) -> None:
    required = {
        "id",
        "title",
        "milestone",
        "priority",
        "weight",
        "state",
        "owner",
        "branch",
        "depends_on",
        "owned_paths",
        "task_packet",
        "handoff",
        "qa_report",
        "review_report",
        "docs_impact",
        "blocked_by",
        "history",
        "updated_at",
    }
    task_id = task.get("id", "<missing>")
    missing = sorted(required - task.keys())
    if missing:
        fail(errors, f"{task_id}: missing fields: {', '.join(missing)}")
        return
    if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
        fail(errors, f"{task_id}: invalid task ID")
    if task["state"] not in STATES:
        fail(errors, f"{task_id}: invalid state {task['state']!r}")
    if task["priority"] not in {"P0", "P1", "P2", "P3"}:
        fail(errors, f"{task_id}: invalid priority")
    if not isinstance(task["weight"], int) or task["weight"] < 1:
        fail(errors, f"{task_id}: weight must be a positive integer")
    if task["docs_impact"] not in {"pending", "none", "resolved"}:
        fail(errors, f"{task_id}: invalid docs_impact")
    if not valid_time(task["updated_at"]):
        fail(errors, f"{task_id}: invalid updated_at")

    dependencies = task["depends_on"]
    if not isinstance(dependencies, list):
        fail(errors, f"{task_id}: depends_on must be a list")
    else:
        for dependency in dependencies:
            if dependency == task_id:
                fail(errors, f"{task_id}: cannot depend on itself")
            elif dependency not in all_ids:
                fail(errors, f"{task_id}: unknown dependency {dependency}")

    if not path_exists(task["task_packet"]):
        fail(errors, f"{task_id}: missing task packet {task['task_packet']!r}")

    history = task["history"]
    if not isinstance(history, list) or not history:
        fail(errors, f"{task_id}: history must be non-empty")
    else:
        states: list[str] = []
        for index, event in enumerate(history):
            if not isinstance(event, dict):
                fail(errors, f"{task_id}: history event {index} must be an object")
                continue
            event_state = event.get("state")
            states.append(event_state)
            if event_state not in STATES:
                fail(errors, f"{task_id}: invalid history state {event_state!r}")
            if not valid_time(event.get("at")):
                fail(errors, f"{task_id}: invalid history timestamp at event {index}")
            if not event.get("by"):
                fail(errors, f"{task_id}: history event {index} has no actor")
        for previous, current in zip(states, states[1:]):
            if current not in TRANSITIONS.get(previous, set()):
                fail(errors, f"{task_id}: illegal transition {previous} -> {current}")
        if states and task["state"] != states[-1]:
            fail(errors, f"{task_id}: current state does not match history")

    state = task["state"]
    if state in ACTIVE_STATES:
        if not task["owner"]:
            fail(errors, f"{task_id}: active task requires owner")
        if not task["branch"]:
            fail(errors, f"{task_id}: active task requires branch")
        if not task["owned_paths"]:
            fail(errors, f"{task_id}: active task requires owned_paths")
    if state in {"blocked", "needs_decision"} and not task["blocked_by"]:
        fail(errors, f"{task_id}: blocked state requires blocked_by")
    if state in {"dev_complete", "qa_failed", "qa_passed", "review_failed", "accepted", "done"}:
        if not path_exists(task["handoff"]):
            fail(errors, f"{task_id}: state {state} requires a handoff")
    if state in {"qa_passed", "review_failed", "accepted", "done"}:
        if not path_exists(task["qa_report"]):
            fail(errors, f"{task_id}: state {state} requires a QA report")
        elif not path_contains(task["qa_report"], "verdict: `pass`"):
            fail(errors, f"{task_id}: QA report does not record a pass verdict")
    if state in {"accepted", "done"}:
        if not path_exists(task["review_report"]):
            fail(errors, f"{task_id}: state {state} requires a review report")
        elif not path_contains(task["review_report"], "verdict: `approve`"):
            fail(errors, f"{task_id}: review report does not record approval")
    if state == "done" and task["docs_impact"] == "pending":
        fail(errors, f"{task_id}: done task has unresolved documentation impact")


def main() -> int:
    errors: list[str] = []
    try:
        backlog = load_backlog()
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    required_root = {"schema_version", "project", "current_milestone", "updated_at", "tasks"}
    missing_root = sorted(required_root - backlog.keys())
    if missing_root:
        fail(errors, f"backlog missing root fields: {', '.join(missing_root)}")
    if backlog.get("schema_version") != 1:
        fail(errors, "unsupported schema_version")
    if backlog.get("project") != "novelhub":
        fail(errors, "project must be novelhub")
    if not valid_time(backlog.get("updated_at")):
        fail(errors, "invalid backlog updated_at")

    tasks = backlog.get("tasks")
    if not isinstance(tasks, list):
        fail(errors, "tasks must be a list")
        tasks = []
    ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    duplicate_ids = sorted({task_id for task_id in ids if ids.count(task_id) > 1})
    if duplicate_ids:
        fail(errors, f"duplicate task IDs: {', '.join(duplicate_ids)}")
    all_ids = {task_id for task_id in ids if isinstance(task_id, str)}

    for task in tasks:
        if not isinstance(task, dict):
            fail(errors, "every task must be an object")
            continue
        validate_task(task, all_ids, errors)

    by_id = {task["id"]: task for task in tasks if isinstance(task, dict) and "id" in task}
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("state") in {"ready"} | ACTIVE_STATES | {"done", "accepted"}:
            for dependency in task.get("depends_on", []):
                dependency_state = by_id.get(dependency, {}).get("state")
                if dependency_state not in {"accepted", "done"}:
                    fail(
                        errors,
                        f"{task['id']}: dependency {dependency} is {dependency_state}, not accepted/done",
                    )

    active = [task for task in tasks if isinstance(task, dict) and task.get("state") in ACTIVE_STATES]
    for index, task in enumerate(active):
        for other in active[index + 1 :]:
            for left in task.get("owned_paths", []):
                for right in other.get("owned_paths", []):
                    if paths_overlap(left, right):
                        fail(
                            errors,
                            f"ownership conflict: {task['id']}:{left} overlaps {other['id']}:{right}",
                        )

    required_files = [
        "AGENTS.md",
        "PLAN.md",
        ".agents/PROJECT.md",
        ".agents/ROADMAP.md",
        ".agents/schemas/backlog.schema.json",
        ".agents/schemas/agent-result.schema.json",
        ".agents/schemas/report.schema.json",
        "docs/plans/README.md",
    ]
    for relative in required_files:
        if not (ROOT / relative).is_file():
            fail(errors, f"missing required harness file: {relative}")

    for schema_path in (AGENTS_DIR / "schemas").glob("*.json"):
        try:
            json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(errors, f"invalid JSON schema {schema_path.relative_to(ROOT)}: {exc}")

    expected_status = render_status(backlog)
    actual_status = STATUS_PATH.read_text(encoding="utf-8") if STATUS_PATH.is_file() else ""
    if actual_status != expected_status:
        fail(errors, "STATUS.md is stale; run `make status-write`")

    if errors:
        print("Harness validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Harness validation passed: {len(tasks)} tasks, {len(active)} active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
