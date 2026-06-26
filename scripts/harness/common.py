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
            "Assign `NH-FOUND-001` to a Developer and record its branch and owned paths.",
            "",
        ]
    )
    return "\n".join(lines)
