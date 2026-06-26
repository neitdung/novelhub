from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / ".agents"
BACKLOG_PATH = AGENTS_DIR / "BACKLOG.yaml"
STATUS_PATH = AGENTS_DIR / "STATUS.md"


def load_backlog() -> dict[str, Any]:
    try:
        data = json.loads(BACKLOG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing backlog: {BACKLOG_PATH.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{BACKLOG_PATH.relative_to(ROOT)} must remain JSON-compatible YAML: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError("backlog root must be an object")
    return data


def task_map(backlog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = backlog.get("tasks", [])
    return {task["id"]: task for task in tasks if isinstance(task, dict) and "id" in task}


def progress_for(tasks: list[dict[str, Any]], milestone: str) -> tuple[int, int, float]:
    milestone_tasks = [task for task in tasks if task.get("milestone") == milestone]
    total = sum(int(task.get("weight", 0)) for task in milestone_tasks)
    accepted = sum(
        int(task.get("weight", 0))
        for task in milestone_tasks
        if task.get("state") in {"accepted", "done"}
    )
    percentage = 100.0 if total == 0 else accepted * 100.0 / total
    return accepted, total, percentage


def task_sort_key(task: dict[str, Any]) -> tuple[int, int, str]:
    priority_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return (
        priority_rank.get(str(task.get("priority")), 99),
        -int(task.get("weight", 0)),
        str(task.get("id", "")),
    )


def dependencies_satisfied(
    task: dict[str, Any],
    tasks_by_id: dict[str, dict[str, Any]],
) -> bool:
    for dependency in task.get("depends_on", []):
        if tasks_by_id.get(dependency, {}).get("state") not in {"accepted", "done"}:
            return False
    return True


def next_valid_action(tasks: list[dict[str, Any]], milestone: str) -> str:
    tasks_by_id = {
        task["id"]: task
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    }
    ordered = sorted(
        [task for task in tasks if isinstance(task, dict)],
        key=task_sort_key,
    )

    for state, message in [
        (
            "blocked",
            "Resolve blockers for `{id}` or move it back to `in_progress` when unblocked.",
        ),
        ("needs_decision", "Record the required decision for `{id}` before planning continues."),
        ("qa_failed", "Reassign `{id}` to a Developer for QA rework."),
        ("review_failed", "Reassign `{id}` to a Developer for review rework."),
        ("dev_complete", "Assign `{id}` to QA and require a `<!-- qa-report -->` verdict."),
        (
            "qa_passed",
            "Assign `{id}` to Reviewer and require a `<!-- review-report -->` verdict.",
        ),
    ]:
        for task in ordered:
            if task.get("state") == state:
                return message.format(id=task["id"])

    for task in ordered:
        if task.get("state") == "accepted":
            if task.get("docs_impact") == "pending":
                return f"Resolve documentation impact for `{task['id']}` before closing it."
            return f"Move `{task['id']}` to `done` and close its GitHub Issue."

    for task in ordered:
        if task.get("state") == "in_progress":
            return f"Wait for Developer handoff on `{task['id']}` or record a blocker."

    ready = [
        task
        for task in ordered
        if task.get("state") == "ready" and dependencies_satisfied(task, tasks_by_id)
    ]
    if ready:
        task = ready[0]
        return f"Assign `{task['id']}` to a Developer and record its branch and owned paths."

    waiting = [
        task
        for task in ordered
        if task.get("state") == "ready" and not dependencies_satisfied(task, tasks_by_id)
    ]
    if waiting:
        task = waiting[0]
        return f"Wait for dependencies before assigning ready task `{task['id']}`."

    for task in ordered:
        if task.get("state") == "planning":
            return f"Complete the task packet for `{task['id']}` and move it to `ready`."

    for task in ordered:
        if task.get("state") == "proposed":
            return f"Move `{task['id']}` to `planning` and create its GitHub Issue packet."

    milestone_tasks = [task for task in ordered if task.get("milestone") == milestone]
    if milestone_tasks and all(task.get("state") in {"done", "superseded"} for task in milestone_tasks):
        return (
            f"No active or queued tasks remain for `{milestone}`. "
            "Select the next approved milestone or create the next task packet."
        )

    return "No active or queued tasks remain. Create the next approved task packet before assigning work."


def render_status(backlog: dict[str, Any]) -> str:
    tasks = backlog.get("tasks", [])
    milestone = backlog.get("current_milestone", "unknown")
    accepted, total, percentage = progress_for(tasks, milestone)
    groups = [
        ("Ready", {"ready"}),
        ("In progress", {"in_progress", "dev_complete", "qa_passed", "accepted"}),
        ("Blocked / rework", {"blocked", "needs_decision", "qa_failed", "review_failed"}),
        ("Done", {"done"}),
        ("Queued / proposed", {"proposed", "planning", "superseded"}),
    ]

    repo = "neitdung/novelhub"
    lines = [
        "# NovelHub Status",
        "",
        "<!-- GENERATED: scripts/harness/render_status.py --write -->",
        "",
        f"- Current milestone: `{milestone}`",
        f"- Milestone accepted weight: {accepted}/{total} ({percentage:.1f}%)",
        f"- Backlog updated: `{backlog.get('updated_at', 'unknown')}`",
        f"- GitHub Project: https://github.com/{repo}/projects",
        "",
    ]

    for heading, states in groups:
        matching = [task for task in tasks if task.get("state") in states]
        lines.extend([f"## {heading}", ""])
        if not matching:
            lines.extend(["None.", ""])
            continue
        lines.extend(
            [
                "| Task | State | Owner | Milestone | Dependencies |",
                "|------|-------|-------|-----------|--------------|",
            ]
        )
        for task in sorted(matching, key=lambda item: item["id"]):
            owner = task.get("owner") or "unassigned"
            dependencies = ", ".join(task.get("depends_on", [])) or "none"
            lines.append(
                f"| `{task['id']}` {task['title']} | `{task['state']}` | "
                f"{owner} | `{task['milestone']}` | {dependencies} |"
            )
        lines.append("")

    active = [
        task
        for task in tasks
        if task.get("state")
        in {"in_progress", "blocked", "dev_complete", "qa_failed", "qa_passed", "review_failed", "accepted"}
    ]
    lines.extend(["## Active ownership", ""])
    if not active:
        lines.extend(["No active path ownership.", ""])
    else:
        lines.extend(
            [
                "| Task | Branch | Owned paths |",
                "|------|--------|-------------|",
            ]
        )
        for task in sorted(active, key=lambda item: item["id"]):
            paths = "<br>".join(f"`{path}`" for path in task.get("owned_paths", [])) or "none"
            lines.append(f"| `{task['id']}` | `{task.get('branch')}` | {paths} |")
        lines.append("")

    blocked = [
        task
        for task in tasks
        if task.get("state") in {"blocked", "needs_decision"}
    ]
    lines.extend(["## Decisions and blockers", ""])
    if not blocked:
        lines.extend(["None recorded.", ""])
    else:
        for task in blocked:
            reasons = ", ".join(task.get("blocked_by", [])) or "reason not recorded"
            lines.append(f"- `{task['id']}`: {reasons}")
        lines.append("")

    lines.extend(
        [
            "## Next valid action",
            "",
            next_valid_action(tasks, milestone),
            "",
        ]
    )
    return "\n".join(lines)
