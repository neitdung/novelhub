from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / ".agents"
TASKS_DIR = AGENTS_DIR / "tasks"
HANDOFFS_DIR = AGENTS_DIR / "handoffs"
REPORTS_DIR = AGENTS_DIR / "reports"
BACKLOG_PATH = AGENTS_DIR / "BACKLOG.yaml"

TASK_ID_RE = re.compile(r"^\[(NH-[A-Z]+-\d{3})\]\s*(.+)$")
ADR_ID_RE = re.compile(r"^\[(ADR-\d{4})\]\s*(.+)$")

MARKER_HANDOFF = "<!-- handoff -->"
MARKER_QA = "<!-- qa-report -->"
MARKER_REVIEW = "<!-- review-report -->"

ACTION_OWNER: dict[str, str] = {
    "proposed": "manager-agent",
    "planning": "manager-agent",
    "ready": "manager-agent",
    "in_progress": "manager-agent",
    "blocked": "manager-agent",
    "dev_complete": "developer-agent",
    "qa_failed": "qa-agent",
    "qa_passed": "qa-agent",
    "review_failed": "reviewer-agent",
    "accepted": "reviewer-agent",
    "done": "manager-agent",
}

STATE_LABEL_MAP: dict[str, str] = {
    "Proposed": "proposed",
    "Planning": "planning",
    "Needs Decision": "needs_decision",
    "Ready": "ready",
    "In Progress": "in_progress",
    "Blocked": "blocked",
    "Dev Complete": "dev_complete",
    "QA Failed": "qa_failed",
    "QA Passed": "qa_passed",
    "Review Failed": "review_failed",
    "Accepted": "accepted",
    "Done": "done",
    "Superseded": "superseded",
}
STATE_LABEL_INV = {v: k for k, v in STATE_LABEL_MAP.items()}


def _load_env() -> None:
    env_path = ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


def gh(*args: str, input_data: str | None = None) -> dict[str, Any]:
    _load_env()
    cmd = ["gh"]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    env = {**os.environ, "GH_TOKEN": token, "NO_COLOR": "1"}
    result = subprocess.run(
        cmd + list(args),
        capture_output=True,
        text=True,
        env=env,
        input=input_data,
    )
    if result.returncode != 0:
        print(f"gh command failed: {' '.join(cmd + list(args))}", file=sys.stderr)
        err = result.stderr.strip()
        if err:
            print(err, file=sys.stderr)
        result.check_returncode()
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"stdout": stdout}


def gh_list(*args: str) -> list[dict[str, Any]]:
    result = gh(*args)
    if isinstance(result, list):
        return result
    return result.get("stdout", [])


def gh_mutation(mutation: str, variables: dict[str, Any]) -> dict[str, Any]:
    """Run a GraphQL mutation with variables via gh api graphql."""
    q = mutation.replace("\n", " ").strip()
    args = ["api", "graphql", "-f", f"query={q}"]
    for key, val in variables.items():
        if isinstance(val, (dict, list)):
            args.extend(["-F", f"{key}={json.dumps(val)}"])
        elif isinstance(val, bool):
            args.extend(["-F", f"{key}={str(val).lower()}"])
        elif isinstance(val, (int, float)):
            args.extend(["-F", f"{key}={val}"])
        else:
            args.extend(["-f", f"{key}={val}"])
    return gh(*args)


def ensure_dirs() -> None:
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_project_fields(field_values: list[dict[str, Any]]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for fv in field_values:
        fname = ""
        if isinstance(fv, dict):
            field_info = fv.get("field", {})
            fname = field_info.get("name", "") if isinstance(field_info, dict) else ""
        if not fname:
            continue
        raw = fv.get("value") or fv.get("text") or fv.get("name")
        if fv.get("type") == "NUMBER":
            try:
                raw = int(fv.get("number") or 0)
            except (ValueError, TypeError):
                raw = 0
        if isinstance(fv.get("iteration"), dict):
            raw = fv["iteration"].get("title", "")
        fields[fname] = raw
    return fields


def find_comment_by_marker(comments: list[dict[str, Any]], marker: str) -> dict[str, Any] | None:
    for comment in comments:
        body = comment.get("body", "")
        if marker in body:
            return comment
    return None


def escape_gh_title(title: str) -> str:
    return title.replace("'", "\\'")


def _strip_marker(body: str, marker: str) -> str:
    """Remove the marker line from a comment body, returning clean content."""
    lines = body.split("\n")
    cleaned = [line for line in lines if marker not in line]
    return "\n".join(cleaned).strip()


def _fetch_issue_full(repo: str, issue_num: int) -> dict[str, Any]:
    """Fetch a single issue's body and comments (only when needed)."""
    result = gh("issue", "view", str(issue_num), "--repo", repo,
                "--json", "body,comments")
    return result if isinstance(result, dict) else {}


def _prefetch_comments(
    repo: str,
    owner: str,
    issue_nums: list[int],
    cache: dict[int, list[str]],
) -> None:
    """Batch-fetch comments for multiple issues in a single GraphQL query."""

    if not issue_nums:
        return

    # Build a GraphQL query with aliases for each issue number
    alias_parts: list[str] = []
    for num in issue_nums:
        alias_parts.append(
            f'  i{num}: issue(number: {num}) {{ number comments(first: 10) {{ nodes {{ body }} }} }}'
        )

    query = f"query {{ repository(owner: \"{owner}\", name: \"{repo.split('/')[-1]}\") {{\n" + "\n".join(alias_parts) + "\n}} }}"

    result = gh("api", "graphql", "-f", f"query={query}")
    repo_data = result.get("data", {}).get("repository", {})

    for num in issue_nums:
        issue_data = repo_data.get(f"i{num}", {})
        comment_nodes = issue_data.get("comments", {}).get("nodes", [])
        cache[num] = [c.get("body", "") for c in comment_nodes if isinstance(c, dict)]


def pull(task_filter: str = "") -> int:
    """Pull Issues → local files (BACKLOG.yaml, task packets, handoffs, reports).

    If task_filter is set, only pull data for that specific task ID.
    """
    project_number = os.environ.get("GH_PROJECT_NUMBER")
    owner = os.environ.get("GH_OWNER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or ""

    if not project_number or not owner:
        print("ERROR: GH_PROJECT_NUMBER and GH_OWNER env vars required", file=sys.stderr)
        return 1

    repo = f"{owner}/novelhub"

    # Load existing backlog so we can preserve fields GitHub doesn't store well
    existing_backlog: dict[str, Any] = {"tasks": []}
    existing_by_id: dict[str, dict[str, Any]] = {}
    if BACKLOG_PATH.is_file():
        try:
            existing_backlog = json.loads(BACKLOG_PATH.read_text(encoding="utf-8"))
            for t in existing_backlog.get("tasks", []):
                if isinstance(t, dict) and t.get("id"):
                    existing_by_id[t["id"]] = t
        except (json.JSONDecodeError, Exception):
            existing_backlog = {"tasks": []}

    # Step 1: Lightweight issue list — just number, title, state
    # No body or comments — those are fetched on-demand only for tasks that need them
    list_args: list[str] = [
        "issue", "list", "--repo", repo, "--state", "all",
        "--json", "number,title,state,updatedAt",
        "--limit", "1000",
    ]
    if task_filter:
        list_args.extend(["--search", f"[{task_filter}] in:title"])
        print(f"Pulling single task: {task_filter}")
    issues = gh_list(*list_args)

    if not isinstance(issues, list):
        print(f"ERROR: unexpected issues response: {issues}", file=sys.stderr)
        return 1

    project_fields_raw = gh_list("project", "field-list", project_number, "--owner", owner, "--format", "json")
    proj_fields_list = project_fields_raw if isinstance(project_fields_raw, list) else project_fields_raw.get("fields", [])

    task_id_field_name = "Task ID"

    # Step 2: GraphQL query for project fields — reduced from first:30 to first:15
    items_gql = gh("api", "graphql", "-f", f"query={{user(login:\"{owner}\"){{projectV2(number:{project_number}){{items(first:100){{nodes{{id fieldValues(first:15){{nodes{{__typename ...on ProjectV2ItemFieldTextValue{{text field{{...on ProjectV2Field{{id name}}}}}} ...on ProjectV2ItemFieldNumberValue{{number field{{...on ProjectV2Field{{id name}}}}}} ...on ProjectV2ItemFieldSingleSelectValue{{name field{{...on ProjectV2SingleSelectField{{id name}}}}}}}}}} content{{...on Issue{{number title}}}}}}}}}}}}}}")
    items_list = (items_gql or {}).get("data", {}).get("user", {}).get("projectV2", {}).get("items", {}).get("nodes", [])

    issue_by_task_id: dict[str, dict[str, Any]] = {}

    for item in items_list:
        if not isinstance(item, dict):
            continue
        content = item.get("content", {})
        if not isinstance(content, dict):
            continue
        issue_number = content.get("number")
        issue_title = content.get("title", "")
        match = TASK_ID_RE.match(issue_title or "")
        task_id = match.group(1) if match else ""
        if not task_id:
            field_values = item.get("fieldValues", {}).get("nodes", [])
            fields = parse_project_fields(field_values)
            task_id = fields.get("Task ID", "") or fields.get("task_id", "")
        if task_id:
            issue_by_task_id[task_id] = {"item": item, "fields": parse_project_fields(
                item.get("fieldValues", {}).get("nodes", [])
            )}

    known_states = {
        "proposed", "planning", "needs_decision", "ready", "in_progress",
        "blocked", "dev_complete", "qa_failed", "qa_passed", "review_failed",
        "accepted", "done", "superseded",
    }
    known_priorities = {"P0", "P1", "P2", "P3"}
    known_impacts = {"pending", "none", "resolved"}

    tasks_out: list[dict[str, Any]] = []

    # Build a map from issue number to task info for on-demand fetching
    issue_num_to_task: dict[int, str] = {}
    for issue in issues:
        title = issue.get("title", "")
        match = TASK_ID_RE.match(title)
        if not match:
            continue
        task_id = match.group(1)
        issue_num = issue.get("number")
        if issue_num:
            issue_num_to_task[issue_num] = task_id

    for issue in issues:
        title = issue.get("title", "")
        match = TASK_ID_RE.match(title)
        if not match:
            continue
        task_id = match.group(1)
        issue_title = match.group(2)

        issue_num = issue.get("number")

        # Step 3: Fetch body and comments ON-DEMAND only if local files are missing
        body = ""
        comments_list: list[dict[str, Any]] = []
        tp_path = ROOT / f".agents/tasks/{task_id}.md"
        hf_path = ROOT / f".agents/handoffs/{task_id}.md"
        qa_path = ROOT / f".agents/reports/{task_id}-qa.md"
        rv_path = ROOT / f".agents/reports/{task_id}-review.md"

        need_body = not tp_path.is_file()
        need_comments = not (hf_path.is_file() and qa_path.is_file() and rv_path.is_file())
        if need_body or need_comments:
            full = _fetch_issue_full(repo, issue_num)
            if need_body:
                body = full.get("body") or ""
            if need_comments:
                comments_list = full.get("comments", []) or []

        handoff_comment = find_comment_by_marker(comments_list, MARKER_HANDOFF)
        qa_comment = find_comment_by_marker(comments_list, MARKER_QA)
        review_comment = find_comment_by_marker(comments_list, MARKER_REVIEW)

        issue_state = (issue.get("state") or "open").lower()
        gh_state = "done" if issue_state == "closed" else "proposed"

        fields: dict[str, Any] = {}
        if task_id in issue_by_task_id:
            fields = issue_by_task_id[task_id].get("fields", {})

        state = str(fields.get("State", fields.get("Status", gh_state)))
        if state in STATE_LABEL_MAP:
            state = STATE_LABEL_MAP[state]
        if state not in known_states:
            state = gh_state

        milestone = str(fields.get("Milestone", "")) or "unknown"
        priority = str(fields.get("Priority", "P2"))
        if priority not in known_priorities:
            priority = "P2"
        weight_raw = fields.get("Weight", 0)
        weight = int(weight_raw) if str(weight_raw).isdigit() else 0

        owner = str(fields.get("Owner", "") or "")
        deps_raw = str(fields.get("Dependencies", "") or "")
        depends_on = [d.strip() for d in deps_raw.split(",") if d.strip()] if deps_raw else []
        blocked_raw = str(fields.get("Blocked by", "") or "")
        blocked_by = [b.strip() for b in blocked_raw.split(",") if b.strip()] if blocked_raw else []
        docs_impact = str(fields.get("Docs Impact", "pending")).lower()
        if docs_impact not in known_impacts:
            docs_impact = "pending"

        # Parse owned_paths from body (or existing backlog if body was skipped)
        owned_paths: list[str] = []
        if body:
            for line in body.split("\n"):
                if "owned paths" in line.lower() or "owned_paths" in line.lower():
                    parts = line.split(":")
                    if len(parts) > 1:
                        raw = parts[1].strip()
                        owned_paths = [p.strip().strip("`",).strip() for p in raw.split(",") if p.strip()]
                    break
        # Fall back to preserved value if body wasn't fetched
        if not owned_paths and task_id in existing_by_id:
            owned_paths = existing_by_id[task_id].get("owned_paths", [])

        # Preserve existing values when GitHub returns empty/zero/invalid
        existing = existing_by_id.get(task_id, {})
        if weight == 0 and existing.get("weight", 0) > 0:
            weight = existing["weight"]
        if docs_impact in ("pending",) and existing.get("docs_impact") in ("none", "resolved"):
            docs_impact = existing["docs_impact"]

        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        history: list[dict[str, str]] = [{
            "state": state,
            "at": issue.get("updatedAt", now_iso),
            "by": "github-mcp",
        }]

        # Compute artifact paths based on task_id and state
        task_packet_path = f".agents/tasks/{task_id}.md"
        handoff_path = f".agents/handoffs/{task_id}.md"
        qa_path = f".agents/reports/{task_id}-qa.md"
        review_path = f".agents/reports/{task_id}-review.md"

        # Write task packet from Issue body (only if file doesn't exist yet)
        if body and not body.startswith("Task packet not available"):
            tp_file = ROOT / task_packet_path
            if not tp_file.is_file():
                tp_file.parent.mkdir(parents=True, exist_ok=True)
                tp_file.write_text(body, encoding="utf-8")
                print(f"  Wrote {task_packet_path}")

        # Write handoff/QA/review files from Issue comments (only if files don't exist yet)
        if handoff_comment:
            hf_file = ROOT / handoff_path
            if not hf_file.is_file():
                hf_file.parent.mkdir(parents=True, exist_ok=True)
                hf_file.write_text(_strip_marker(handoff_comment["body"], MARKER_HANDOFF), encoding="utf-8")
                print(f"  Wrote {handoff_path}")

        if qa_comment:
            qa_file = ROOT / qa_path
            if not qa_file.is_file():
                qa_file.parent.mkdir(parents=True, exist_ok=True)
                qa_file.write_text(_strip_marker(qa_comment["body"], MARKER_QA), encoding="utf-8")
                print(f"  Wrote {qa_path}")

        if review_comment:
            rv_file = ROOT / review_path
            if not rv_file.is_file():
                rv_file.parent.mkdir(parents=True, exist_ok=True)
                rv_file.write_text(_strip_marker(review_comment["body"], MARKER_REVIEW), encoding="utf-8")
                print(f"  Wrote {review_path}")

        # Build the new task entry — preserve existing updated_at if nothing changed
        new_entry: dict[str, Any] = {
            "id": task_id,
            "title": issue_title,
            "milestone": milestone,
            "priority": priority,
            "weight": weight if weight else 0,
            "state": state,
            "owner": owner,
            "branch": None,
            "depends_on": depends_on,
            "owned_paths": owned_paths,
            "task_packet": task_packet_path if (ROOT / task_packet_path).is_file() else "",
            "handoff": handoff_path if (ROOT / handoff_path).is_file() else "",
            "qa_report": qa_path if (ROOT / qa_path).is_file() else "",
            "review_report": review_path if (ROOT / review_path).is_file() else "",
            "docs_impact": docs_impact,
            "blocked_by": blocked_by,
            "history": history,
            "updated_at": now_iso,
        }

        # Detect whether the task actually changed vs the previous snapshot
        prev_task = existing_by_id.get(task_id, {})
        if prev_task:
            # Compare only meaningful task data fields (exclude metadata)
            compare_keys = {"id", "title", "milestone", "priority", "weight", "state",
                            "owner", "depends_on", "owned_paths", "docs_impact",
                            "blocked_by", "task_packet", "handoff", "qa_report",
                            "review_report"}
            prev_flat = {k: prev_task.get(k) for k in compare_keys}
            new_flat = {k: new_entry.get(k) for k in compare_keys}
            if prev_flat == new_flat:
                # No meaningful change — preserve the previous updated_at
                new_entry["updated_at"] = prev_task.get("updated_at", now_iso)

        task_entry = new_entry

        tasks_out.append(task_entry)

    # If task_filter was set, also preserve backlog entries for other tasks
    # so the backlog doesn't lose all other tasks
    if task_filter:
        for tid, tdata in existing_by_id.items():
            if tid != task_filter and not any(t.get("id") == tid for t in tasks_out):
                tasks_out.append(tdata)

    backlog = {
        "schema_version": 1,
        "project": "novelhub",
        "current_milestone": existing_backlog.get("current_milestone", "external-ingestion"),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tasks": tasks_out,
    }

    BACKLOG_PATH.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    print(f"Pulled {len(tasks_out)} tasks from GitHub Issues.")

    from common import render_status
    rendered = render_status(backlog)
    status_path = AGENTS_DIR / "STATUS.md"
    status_path.write_text(rendered, encoding="utf-8")
    print(f"Generated {status_path.relative_to(ROOT)}")

    return 0


def push(task_filter: str = "", since: str = "", push_all: bool = False, dry_run: bool = False) -> int:
    """Push local files → GitHub Issues (bootstrap)."""
    project_number = os.environ.get("GH_PROJECT_NUMBER")
    owner = os.environ.get("GH_OWNER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or ""

    if not project_number or not owner:
        print("ERROR: GH_PROJECT_NUMBER and GH_OWNER env vars required", file=sys.stderr)
        return 1

    proj_result = gh("api", "graphql", "-f",
                     f"query={{user(login:\"{owner}\"){{projectV2(number:{project_number}){{id}}}}}}")
    PROJECT_ID = proj_result.get("data", {}).get("user", {}).get("projectV2", {}).get("id", "")

    repo = f"{owner}/novelhub"
    backlog_raw = BACKLOG_PATH.read_text(encoding="utf-8")
    backlog = json.loads(backlog_raw)
    all_tasks: list[dict[str, Any]] = backlog.get("tasks", [])

    # Filter tasks to push
    if task_filter:
        tasks = [t for t in all_tasks if t.get("id") == task_filter]
        if not tasks:
            print(f"No task found with ID '{task_filter}'", file=sys.stderr)
            return 1
        if dry_run:
            print(f"[dry-run] Would push 1 task: {task_filter}")
            return 0
    elif push_all:
        tasks = all_tasks
        if dry_run:
            print(f"[dry-run] Would push all {len(tasks)} tasks")
            return 0
    else:
        # Default: only push active (non-done) tasks
        tasks = [t for t in all_tasks if t.get("state") not in ("done", "accepted")]
        if dry_run:
            print(f"[dry-run] Would push {len(tasks)} active tasks (skipping {len(all_tasks) - len(tasks)} done/accepted)")
            return 0

    print(f"Pushing {len(tasks)} tasks to GitHub Issues...")

    # When task_filter is set, only search for that specific issue
    existing_issues_args: list[str] = [
        "issue", "list", "--repo", repo, "--state", "all",
        "--json", "number,title,state", "--limit", "1000",
    ]
    if task_filter:
        existing_issues_args.extend(["--search", f"[{task_filter}] in:title"])
    existing_issues = gh_list(*existing_issues_args)

    existing_by_id: dict[str, int] = {}
    for issue in existing_issues:
        if not isinstance(issue, dict):
            continue
        title = issue.get("title", "")
        match = TASK_ID_RE.match(title)
        if match:
            existing_by_id[match.group(1)] = issue["number"]

    fields_info = gh_list("project", "field-list", project_number, "--owner", owner, "--format", "json")
    proj_fields_list = fields_info if isinstance(fields_info, list) else fields_info.get("fields", [])
    field_map: dict[str, Any] = {}
    for f in proj_fields_list:
        if isinstance(f, dict):
            field_map[f.get("name", "")] = f

    sid = field_map.get("State", {}).get("id", "")
    pid = field_map.get("Priority", {}).get("id", "")
    wid = field_map.get("Weight", {}).get("id", "")
    oid = field_map.get("Owner", {}).get("id", "")
    tid_fid = field_map.get("Task ID", {}).get("id", "")
    did = field_map.get("Dependencies", {}).get("id", "")
    bid = field_map.get("Blocked by", {}).get("id", "")
    dimp = field_map.get("Docs Impact", {}).get("id", "")

    state_opts = {o["name"]: o["id"] for o in field_map.get("State", {}).get("options", [])}
    priority_opts = {o["name"]: o["id"] for o in field_map.get("Priority", {}).get("options", [])}
    impact_opts = {o["name"]: o["id"] for o in field_map.get("Docs Impact", {}).get("options", [])}

    # Cache project item list once (reduces GraphQL calls from N to 1)
    item_cmd = gh("project", "item-list", project_number, "--owner", owner, "--format", "json", "--limit", "100")
    items_raw = item_cmd if isinstance(item_cmd, list) else item_cmd.get("items", [])
    item_by_issue: dict[int, str] = {}
    for item in items_raw:
        if not isinstance(item, dict):
            continue
        content = item.get("content", {})
        issue_num = content.get("number")
        item_id = item.get("id", "")
        if issue_num and item_id:
            item_by_issue[issue_num] = item_id

    created = 0
    updated = 0
    skipped = 0

    # Pre-fetch comments for all existing issues in a single GraphQL query
    # to avoid N individual REST calls
    comments_cache: dict[int, list[str]] = {}
    existing_issue_nums = [
        existing_by_id[t["id"]] for t in tasks
        if t["id"] in existing_by_id
    ]
    _prefetch_comments(repo, owner, existing_issue_nums, comments_cache)

    for task in tasks:
        task_id = task.get("id", "")
        title = task.get("title", "")
        issue_title = f"[{task_id}] {title}"

        task_packet = ""
        tp = task.get("task_packet", "")
        if tp:
            tp_path = ROOT / tp
            if tp_path.is_file():
                task_packet = tp_path.read_text(encoding="utf-8")

        handoff_body = ""
        hf = task.get("handoff", "")
        if hf:
            hf_path = ROOT / hf
            if hf_path.is_file():
                handoff_body = hf_path.read_text(encoding="utf-8")

        qa_body = ""
        qa = task.get("qa_report", "")
        if qa:
            qa_path = ROOT / qa
            if qa_path.is_file():
                qa_body = qa_path.read_text(encoding="utf-8")

        review_body = ""
        rv = task.get("review_report", "")
        if rv:
            rv_path = ROOT / rv
            if rv_path.is_file():
                review_body = rv_path.read_text(encoding="utf-8")

        labels = "task"

        created_new = False
        if task_id in existing_by_id:
            issue_num = existing_by_id[task_id]
            if task_packet:
                gh("issue", "edit", str(issue_num), "--repo", repo,
                   "--title", issue_title, "--body", task_packet)
            else:
                gh("issue", "edit", str(issue_num), "--repo", repo,
                   "--title", issue_title)
            updated += 1
        else:
            if not task_packet:
                task_packet = f"# {task_id} — {title}\n\nTask packet not available."
            result = gh("issue", "create", "--repo", repo,
                        "--title", issue_title, "--body", task_packet,
                        "--label", labels)
            url = result.get("stdout", "")
            m = re.search(r'/(\d+)$', url)
            issue_num = int(m.group(1)) if m else 0
            existing_by_id[task_id] = issue_num
            created += 1
            created_new = True

        # Use cached comments when available; freshly created issues have none
        existing_bodies = comments_cache.get(issue_num, [])
        if created_new or not existing_bodies:
            existing_bodies = []

        def _has_marker(marker: str) -> bool:
            return any(marker in body for body in existing_bodies)

        if handoff_body and not _has_marker(MARKER_HANDOFF):
            gh("issue", "comment", str(issue_num), "--repo", repo,
               "--body", f"{MARKER_HANDOFF}\n\n{handoff_body}")
        if qa_body and not _has_marker(MARKER_QA):
            gh("issue", "comment", str(issue_num), "--repo", repo,
               "--body", f"{MARKER_QA}\n\n{qa_body}")
        if review_body and not _has_marker(MARKER_REVIEW):
            gh("issue", "comment", str(issue_num), "--repo", repo,
               "--body", f"{MARKER_REVIEW}\n\n{review_body}")

        # Batch all project field updates into a single GraphQL mutation per task
        state_label = STATE_LABEL_INV.get(task.get("state", ""), "Proposed")
        try:
            item_id = item_by_issue.get(issue_num)
            if item_id:
                updates: list[tuple[str, str, str | int]] = []
                if tid_fid:
                    updates.append((tid_fid, "text", task_id))
                if sid and state_label in state_opts:
                    updates.append((sid, "singleSelectOptionId", state_opts[state_label]))
                if pid and task.get("priority") in priority_opts:
                    updates.append((pid, "singleSelectOptionId", priority_opts[task["priority"]]))
                if wid:
                    updates.append((wid, "number", task.get("weight", 0)))
                if oid and task.get("owner"):
                    updates.append((oid, "text", str(task["owner"])))
                if did:
                    deps = ", ".join(task.get("depends_on", []))
                    if deps:
                        updates.append((did, "text", deps))
                if bid:
                    blocked = ", ".join(task.get("blocked_by", []))
                    if blocked:
                        updates.append((bid, "text", blocked))
                if dimp:
                    impact = task.get("docs_impact", "pending")
                    impact_label = {"pending": "Pending", "none": "None", "resolved": "Resolved"}.get(impact, "Pending")
                    if impact_label in impact_opts:
                        updates.append((dimp, "singleSelectOptionId", impact_opts[impact_label]))

                if updates:
                    # Send all field updates in a single batched GraphQL mutation
                    parts: list[str] = []
                    for i, (fid, vtype, val) in enumerate(updates):
                        val_json = json.dumps(val)
                        parts.append(
                            f'  f{i}: updateProjectV2ItemFieldValue(input: {{'
                            f'projectId: $pid, itemId: $iid, fieldId: "{fid}", '
                            f'value: {{ {vtype}: {val_json} }}'
                            f'}}) {{ projectV2Item {{ id }} }}'
                        )
                    mutation = "mutation($pid: ID!, $iid: ID!) {\n" + "\n".join(parts) + "\n}"
                    gh_mutation(mutation, {"pid": PROJECT_ID, "iid": item_id})
            else:
                print(f"  Warning: item #{issue_num} ({task_id}) not found in project", file=sys.stderr)
        except Exception as exc:
            print(f"  Warning: could not update project fields for {task_id}: {exc}", file=sys.stderr)

    print(f"Pushed {len(tasks)} tasks to GitHub Issues:")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync local harness files with GitHub Issues")
    parser.add_argument("direction", nargs="?", choices=["pull", "push"], default="pull",
                        help="Sync direction (default: pull)")
    parser.add_argument("--task", type=str, default="",
                        help="Only sync a specific task ID (e.g., NH-FOUND-001)")
    parser.add_argument("--since", type=str, default="",
                        help="Only sync tasks updated after this ISO timestamp")
    parser.add_argument("--all", action="store_true", default=False,
                        help="Push ALL tasks, not just active (non-done) ones")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Show what would be synced without making changes")
    args = parser.parse_args()
    ensure_dirs()
    if args.direction == "push":
        return push(task_filter=args.task, since=args.since, push_all=args.all, dry_run=args.dry_run)
    return pull(task_filter=args.task)


if __name__ == "__main__":
    raise SystemExit(main())
