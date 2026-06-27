PYTHON ?= python3
BACKEND_DIR := backend
FRONTEND_DIR := frontend

# Load .env if present (local GitHub token, project number)
-include .env
export

GH_PROJECT_NUMBER ?= 1
GH_OWNER ?= neitdung
GITHUB_TOKEN ?=

.PHONY: start stop clear
.PHONY: bootstrap harness-check status status-write task-check check integration e2e ci
.PHONY: sync-pull sync-push sync-project
.PHONY: backend-install backend-lint backend-typecheck backend-test backend-check
.PHONY: frontend-install frontend-lint frontend-typecheck frontend-test frontend-build frontend-check
.PHONY: contract-export contract-check contract-validate

# =============================================================================
# Developer quick-start commands
# =============================================================================

start:
	./scripts/start.sh $(ARGS)

stop:
	./scripts/stop.sh

clear:
	./scripts/clear_data.sh

# =============================================================================
# Harness & management commands
# =============================================================================

bootstrap:
	$(PYTHON) --version
	$(PYTHON) scripts/harness/check_state.py

harness-check:
	$(PYTHON) scripts/harness/check_state.py

status:
	$(PYTHON) scripts/harness/render_status.py

status-write:
	$(PYTHON) scripts/harness/render_status.py --write

sync-pull:
	$(PYTHON) scripts/harness/sync_issues.py pull

sync-push:
	$(PYTHON) scripts/harness/sync_issues.py push

sync-project: sync-push sync-pull
	@echo "Synced both directions."

task-check:
	@test -n "$(ID)" || (echo "ID is required: make task-check ID=<task-id>" && exit 2)
	$(PYTHON) scripts/harness/task_check.py "$(ID)"

# =============================================================================
# Backend commands
# =============================================================================

backend-install:
	cd $(BACKEND_DIR) && uv sync

backend-lint:
	cd $(BACKEND_DIR) && .venv/bin/ruff check .

backend-typecheck:
	cd $(BACKEND_DIR) && .venv/bin/mypy .

backend-test:
	cd $(BACKEND_DIR) && .venv/bin/pytest -v

backend-check: backend-lint backend-typecheck backend-test

# =============================================================================
# Frontend commands
# =============================================================================

frontend-install:
	cd $(FRONTEND_DIR) && npm ci

frontend-lint:
	cd $(FRONTEND_DIR) && npx oxlint src

frontend-typecheck:
	cd $(FRONTEND_DIR) && npx tsc -b

frontend-test:
	cd $(FRONTEND_DIR) && npx vitest run

frontend-build:
	cd $(FRONTEND_DIR) && npm run build

frontend-check: frontend-lint frontend-typecheck frontend-test

# =============================================================================
# Contract commands
# =============================================================================

contract-export:
	$(PYTHON) scripts/contracts/export_openapi.py

contract-check:
	$(PYTHON) scripts/contracts/check_contract.py

contract-validate: contract-export contract-check

# =============================================================================
# CI / Composite commands
# =============================================================================

check: harness-check backend-check frontend-check contract-validate
	$(PYTHON) -m compileall -q scripts/harness
	$(PYTHON) -m unittest discover -s scripts/harness/tests -p 'test_*.py'

integration: check
	@echo "No application integration suite exists before Phase 1."

e2e: check
	@echo "No browser end-to-end suite exists before Phase 1."

ci: harness-check check integration e2e
