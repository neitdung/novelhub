from __future__ import annotations

import sys
import unittest
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_DIR))

from check_state import (  # noqa: E402
    ASSISTANT_WORKFLOW_FILES,
    OPENCODE_REQUIRED_AGENTS,
    REQUIRED_ROLE_PROMPTS,
    REQUIRED_SKILLS,
    TRANSITIONS,
    paths_overlap,
)
from common import next_valid_action, progress_for  # noqa: E402


class HarnessRulesTest(unittest.TestCase):
    def test_nested_owned_paths_overlap(self) -> None:
        self.assertTrue(paths_overlap("backend/src", "backend/src/api/routes"))

    def test_sibling_owned_paths_do_not_overlap(self) -> None:
        self.assertFalse(paths_overlap("backend/src/api", "frontend/src/api"))

    def test_illegal_completion_shortcut_is_not_allowed(self) -> None:
        self.assertNotIn("done", TRANSITIONS["in_progress"])

    def test_rework_loop_is_allowed(self) -> None:
        self.assertIn("in_progress", TRANSITIONS["qa_failed"])
        self.assertIn("in_progress", TRANSITIONS["review_failed"])

    def test_progress_counts_only_accepted_scope(self) -> None:
        tasks = [
            {"milestone": "m1", "weight": 3, "state": "done"},
            {"milestone": "m1", "weight": 2, "state": "dev_complete"},
            {"milestone": "m2", "weight": 9, "state": "done"},
        ]
        accepted, total, percentage = progress_for(tasks, "m1")
        self.assertEqual((accepted, total), (3, 5))
        self.assertEqual(percentage, 60.0)

    def test_next_action_does_not_assign_done_task(self) -> None:
        tasks = [
            {
                "id": "NH-FOUND-001",
                "milestone": "foundation",
                "priority": "P1",
                "weight": 5,
                "state": "done",
            }
        ]

        action = next_valid_action(tasks, "foundation")

        self.assertIn("No active or queued tasks remain", action)
        self.assertNotIn("Assign `NH-FOUND-001`", action)

    def test_next_action_assigns_ready_task_with_satisfied_dependencies(self) -> None:
        tasks = [
            {
                "id": "NH-FOUND-001",
                "milestone": "foundation",
                "priority": "P1",
                "weight": 5,
                "state": "done",
            },
            {
                "id": "NH-FOUND-002",
                "milestone": "foundation",
                "priority": "P0",
                "weight": 3,
                "state": "ready",
                "depends_on": ["NH-FOUND-001"],
            },
        ]

        action = next_valid_action(tasks, "foundation")

        self.assertEqual(
            action,
            "Assign `NH-FOUND-002` to a Developer and record its branch and owned paths.",
        )

    def test_every_agent_workflow_has_a_skill(self) -> None:
        self.assertEqual(
            REQUIRED_SKILLS,
            {
                "manage-project",
                "plan-task",
                "implement-task",
                "qa-task",
                "review-task",
                "document-task",
            },
        )

    def test_every_agent_role_has_a_prompt(self) -> None:
        self.assertEqual(
            REQUIRED_ROLE_PROMPTS,
            {
                "manager.md",
                "planner.md",
                "developer.md",
                "qa.md",
                "reviewer.md",
                "docs.md",
            },
        )

    def test_opencode_injects_project_setup_for_all_agents(self) -> None:
        self.assertIn("novelhub", OPENCODE_REQUIRED_AGENTS)
        for role in ("manager", "planner", "developer", "qa", "reviewer", "docs"):
            self.assertIn(f"novelhub-{role}", OPENCODE_REQUIRED_AGENTS)
        for builtin in ("general", "build", "explore", "plan"):
            self.assertIn(builtin, OPENCODE_REQUIRED_AGENTS)

    def test_common_assistant_workflow_entrypoints_exist(self) -> None:
        self.assertEqual(
            ASSISTANT_WORKFLOW_FILES,
            {
                "AGENTS.md",
                "CLAUDE.md",
                "GEMINI.md",
                ".github/copilot-instructions.md",
            },
        )


if __name__ == "__main__":
    unittest.main()
