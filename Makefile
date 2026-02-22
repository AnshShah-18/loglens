.PHONY: install run dev test demo-reset demo-seed clean

VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/python -m pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(VENV)/bin/uvicorn backend.app.main:app --reload --port 8000

dev:
	@echo "Backend starting on :8000"
	@echo "Frontend runs on :3000"
	@echo "In another terminal: cd frontend && npm run dev"
	$(VENV)/bin/uvicorn backend.app.main:app --reload --port 8000

test:
	$(PY) -m pytest -q

demo-reset:
	@if [ -f loglens.db ]; then \
		rm -f loglens.db; \
		echo "Demo DB reset (loglens.db removed)"; \
	else \
		echo "No demo DB found"; \
	fi

demo-seed: demo-reset
	@set -e; \
	BACKEND_URL="http://localhost:8000"; \
	FRONTEND_BASE="http://localhost:3000"; \
	STARTED_BACKEND=0; \
	if ! curl -sSf "$$BACKEND_URL/api/health" >/dev/null 2>&1; then \
		echo "Starting backend on :8000 in background..."; \
		nohup $(VENV)/bin/uvicorn backend.app.main:app --port 8000 >/tmp/loglens-demo-backend.log 2>&1 & \
		BG_PID=$$!; \
		STARTED_BACKEND=1; \
		for i in $$(seq 1 30); do \
			if curl -sSf "$$BACKEND_URL/api/health" >/dev/null 2>&1; then break; fi; \
			sleep 1; \
		done; \
		if ! curl -sSf "$$BACKEND_URL/api/health" >/dev/null 2>&1; then \
			echo "Backend failed to start. See /tmp/loglens-demo-backend.log"; \
			exit 1; \
		fi; \
		echo "Backend started (pid $$BG_PID). Logs: /tmp/loglens-demo-backend.log"; \
	fi; \
	UPLOAD1_JSON=$$(curl -sS -f -X POST "$$BACKEND_URL/api/upload" -F "file=@samples/demo.log"); \
	UPLOAD1_ID=$$(printf '%s' "$$UPLOAD1_JSON" | $(PY) -c 'import sys, json; print(json.load(sys.stdin)["id"])'); \
	UPLOAD2_JSON=$$(curl -sS -f -X POST "$$BACKEND_URL/api/upload" -F "file=@samples/demo_new.log"); \
	UPLOAD2_ID=$$(printf '%s' "$$UPLOAD2_JSON" | $(PY) -c 'import sys, json; print(json.load(sys.stdin)["id"])'); \
	echo "Seed complete (upload ids: $$UPLOAD1_ID, $$UPLOAD2_ID)"; \
	echo "Backend: $$BACKEND_URL"; \
	echo "Frontend: $$FRONTEND_BASE/uploads/$$UPLOAD2_ID"; \
	echo "API: curl $$BACKEND_URL/api/uploads/$$UPLOAD2_ID/patterns"; \
	if [ "$$STARTED_BACKEND" -eq 0 ]; then \
		echo "Using existing backend on :8000"; \
	fi

clean:
	rm -rf $(VENV)
