from __future__ import annotations

import sys
import unittest
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_DIR))

from check_state import TRANSITIONS, paths_overlap  # noqa: E402
from common import progress_for  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
