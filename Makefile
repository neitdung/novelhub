PYTHON ?= python3

.PHONY: bootstrap harness-check status status-write task-check check integration e2e ci

bootstrap:
	$(PYTHON) --version
	$(PYTHON) scripts/harness/check_state.py

harness-check:
	$(PYTHON) scripts/harness/check_state.py

status:
	$(PYTHON) scripts/harness/render_status.py

status-write:
	$(PYTHON) scripts/harness/render_status.py --write

task-check:
	@test -n "$(ID)" || (echo "ID is required: make task-check ID=<task-id>" && exit 2)
	$(PYTHON) scripts/harness/task_check.py "$(ID)"

check: harness-check
	$(PYTHON) -m compileall -q scripts/harness
	$(PYTHON) -m unittest discover -s scripts/harness/tests -p 'test_*.py'

integration: check
	@echo "No application integration suite exists before Phase 1."

e2e: check
	@echo "No browser end-to-end suite exists before Phase 1."

ci: harness-check check integration e2e
