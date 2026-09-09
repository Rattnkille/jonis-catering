.PHONY: setup run test eval loop calibrate
PY ?= python3
setup:
	$(PY) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
run:
	$(PY) app.py
test:
	$(PY) -m pytest tests -q
eval:
	$(PY) eval/run_eval.py
calibrate:
	$(PY) -m forno_twin calibrate
loop:
	bash loop/improve.sh
