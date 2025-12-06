PYTHON ?= python3
UVICORN ?= uvicorn
FRONTEND_PORT ?= 3000
BACKEND_PORT ?= 8000

.PHONY: help install run-backend run-frontend fmt lint clean

help:
	@echo "Common tasks:"
	@echo "  make install       # pip install -r requirements.txt"
	@echo "  make run-backend   # start FastAPI on $(BACKEND_PORT)"
	@echo "  make run-frontend  # serve static frontend on $(FRONTEND_PORT)"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run-backend:
	$(UVICORN) backend.app.api.main:app --host 0.0.0.0 --port $(BACKEND_PORT) --reload

run-frontend:
	$(PYTHON) -m http.server $(FRONTEND_PORT) --directory frontend

fmt:
	@echo "Add your formatter here if needed."

lint:
	@echo "Add your linter here if needed."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
