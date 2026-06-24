from __future__ import annotations

import sys

from common import ROOT, load_backlog, task_map


def exists(path: str | None) -> bool:
    return bool(path) and (ROOT / path).is_file()


def main(task_id: str) -> int:
    backlog = load_backlog()
    task = task_map(backlog).get(task_id)
    if task is None:
        print(f"Unknown task: {task_id}")
        return 2

    errors: list[str] = []
    state = task["state"]
    if not exists(task.get("task_packet")):
        errors.append("missing task packet")
    if state in {"dev_complete", "qa_failed", "qa_passed", "review_failed", "accepted", "done"}:
        if not exists(task.get("handoff")):
            errors.append("missing developer handoff")
    if state in {"qa_passed", "review_failed", "accepted", "done"}:
        if not exists(task.get("qa_report")):
            errors.append("missing QA report")
    if state in {"accepted", "done"}:
        if not exists(task.get("review_report")):
            errors.append("missing review report")
    if state == "done" and task.get("docs_impact") == "pending":
        errors.append("documentation impact is unresolved")

    if errors:
        print(f"{task_id} failed task checks:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"{task_id} task checks passed in state {state}.")
    print(f"Task packet: {task['task_packet']}")
    if task.get("handoff"):
        print(f"Handoff: {task['handoff']}")
    if task.get("qa_report"):
        print(f"QA: {task['qa_report']}")
    if task.get("review_report"):
        print(f"Review: {task['review_report']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: task_check.py <task-id>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
