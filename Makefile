.PHONY: all clean install test lint build dist bump-patch bump-minor bump-major version help venv \
        setup dev check format typecheck security docs serve-docs fuzz-test quick-test \
        corpus-check mutator-list agent-test clean-cache clean-all requirements update-deps \
        pre-commit install-hooks benchmark profile

# Variables
PYTHON := python3
UV := uv
PACKAGE := quill
VERSION_FILE := pyproject.toml
DIST_DIR := dist
TEST_DIR := tests
SRC_DIR := quill
VENV_DIR := .venv
DOCS_DIR := docs
RUNS_DIR := runs
CACHE_DIR := .cache
OLLAMA_MODEL := llama2
TEST_CORPUS := test_corpus/test_prompts.txt

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
all: setup test lint typecheck

# Help - default target when just typing 'make'
help:
	@echo "$(BLUE)Quill - LLM Fuzzing Tool$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@echo "  make setup          - Complete development setup (venv, deps, hooks)"
	@echo "  make install        - Install package in development mode"
	@echo "  make dev            - Setup development environment with all tools"
	@echo "  make requirements   - Generate requirements files"
	@echo ""
	@echo "$(GREEN)Testing & Quality:$(NC)"
	@echo "  make test           - Run full test suite"
	@echo "  make quick-test     - Run quick smoke tests"
	@echo "  make fuzz-test      - Run sample fuzzing test"
	@echo "  make lint           - Run all linters (ruff, black)"
	@echo "  make format         - Auto-format code"
	@echo "  make typecheck      - Run type checking with mypy"
	@echo "  make security       - Run security checks"
	@echo "  make check          - Run all checks (lint, type, security)"
	@echo ""
	@echo "$(GREEN)Fuzzing Operations:$(NC)"
	@echo "  make fuzz           - Run fuzzing with default settings"
	@echo "  make fuzz-ollama    - Fuzz local Ollama model"
	@echo "  make corpus-check   - Validate corpus files"
	@echo "  make mutator-list   - List available mutators"
	@echo ""
	@echo "$(GREEN)Claude Agents:$(NC)"
	@echo "  make agent-test     - Test Claude sub-agents"
	@echo "  make agent-list     - List available sub-agents"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make docs           - Build documentation"
	@echo "  make serve-docs     - Serve docs locally"
	@echo "  make benchmark      - Run performance benchmarks"
	@echo "  make profile        - Profile code execution"
	@echo ""
	@echo "$(GREEN)Maintenance:$(NC)"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make clean-cache    - Clean cache files"
	@echo "  make clean-all      - Clean everything"
	@echo "  make update-deps    - Update dependencies"
	@echo ""
	@echo "$(GREEN)Release:$(NC)"
	@echo "  make build          - Build package"
	@echo "  make dist           - Create distribution"
	@echo "  make bump-patch     - Bump patch version"
	@echo "  make bump-minor     - Bump minor version"
	@echo "  make bump-major     - Bump major version"
	@echo "  make version        - Show current version"

# Setup & Installation
setup: venv install-deps install-hooks
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV_DIR)/bin/activate$(NC)"

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

install-deps: venv
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -e ".[dev]"

install: install-deps
	@echo "$(GREEN)✓ Package installed in development mode$(NC)"

dev: setup
	@echo "$(BLUE)Installing additional development tools...$(NC)"
	$(VENV_DIR)/bin/pip install black ruff mypy pytest pytest-cov pytest-asyncio
	$(VENV_DIR)/bin/pip install sphinx sphinx-rtd-theme
	$(VENV_DIR)/bin/pip install bandit safety
	@echo "$(GREEN)✓ Development environment complete$(NC)"

requirements:
	@echo "$(BLUE)Generating requirements files...$(NC)"
	$(VENV_DIR)/bin/pip freeze > requirements.txt
	$(VENV_DIR)/bin/pip freeze | grep -E "(black|ruff|mypy|pytest|sphinx|bandit)" > requirements-dev.txt
	@echo "$(GREEN)✓ Requirements files generated$(NC)"

# Testing
test: venv
	@echo "$(BLUE)Running tests...$(NC)"
	$(VENV_DIR)/bin/pytest $(TEST_DIR) -v --color=yes

quick-test: venv
	@echo "$(BLUE)Running quick tests...$(NC)"
	$(VENV_DIR)/bin/pytest $(TEST_DIR) -v -m "not slow" --color=yes

fuzz-test: venv
	@echo "$(BLUE)Running sample fuzzing test...$(NC)"
	$(VENV_DIR)/bin/python -m quill fuzz -c $(TEST_CORPUS) -o $(RUNS_DIR)/test_run \
		--max-prompts 10 --verbose ollama --model $(OLLAMA_MODEL)

# Code Quality
lint: venv
	@echo "$(BLUE)Running linters...$(NC)"
	$(VENV_DIR)/bin/ruff check $(SRC_DIR)
	$(VENV_DIR)/bin/black --check $(SRC_DIR)

format: venv
	@echo "$(BLUE)Formatting code...$(NC)"
	$(VENV_DIR)/bin/black $(SRC_DIR)
	$(VENV_DIR)/bin/ruff check --fix $(SRC_DIR)
	@echo "$(GREEN)✓ Code formatted$(NC)"

typecheck: venv
	@echo "$(BLUE)Running type checks...$(NC)"
	$(VENV_DIR)/bin/mypy $(SRC_DIR) --ignore-missing-imports

security: venv
	@echo "$(BLUE)Running security checks...$(NC)"
	$(VENV_DIR)/bin/bandit -r $(SRC_DIR)
	$(VENV_DIR)/bin/safety check

check: lint typecheck security
	@echo "$(GREEN)✓ All checks passed$(NC)"

# Fuzzing Operations
fuzz: venv
	@echo "$(YELLOW)Starting fuzzing with default settings...$(NC)"
	$(VENV_DIR)/bin/python -m quill fuzz -c $(TEST_CORPUS) -o $(RUNS_DIR)/manual_run \
		--max-prompts 100 ollama --model $(OLLAMA_MODEL)

fuzz-ollama: venv
	@echo "$(YELLOW)Checking if Ollama is running...$(NC)"
	@curl -s http://localhost:11434/api/tags > /dev/null || \
		(echo "$(RED)Error: Ollama not running. Start with: ollama serve$(NC)" && exit 1)
	@echo "$(GREEN)✓ Ollama is running$(NC)"
	$(MAKE) fuzz

corpus-check: venv
	@echo "$(BLUE)Validating corpus files...$(NC)"
	@for file in $(TEST_CORPUS) test_corpus/*.txt; do \
		if [ -f "$$file" ]; then \
			echo "Checking $$file..."; \
			wc -l "$$file"; \
		fi; \
	done

mutator-list: venv
	@echo "$(BLUE)Available mutators:$(NC)"
	@$(VENV_DIR)/bin/python -c "from quill.core.mutators import list_mutators; list_mutators()"

# Claude Agents
agent-test: venv
	@echo "$(BLUE)Testing Claude sub-agents...$(NC)"
	@echo "$(YELLOW)Sub-agents available in .claude/agents/:$(NC)"
	@ls -la .claude/agents/ | grep -E "\.md$$" | awk '{print "  - " $$9}'

agent-list:
	@echo "$(BLUE)Available Claude sub-agents:$(NC)"
	@echo ""
	@cat .claude/agents/README.md | grep -E "^#### [0-9]+\." | sed 's/#### //'

# Documentation
docs: venv
	@echo "$(BLUE)Building documentation...$(NC)"
	$(VENV_DIR)/bin/sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build

serve-docs: docs
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(NC)"
	cd $(DOCS_DIR)/_build && $(PYTHON) -m http.server 8000

# Performance
benchmark: venv
	@echo "$(BLUE)Running benchmarks...$(NC)"
	$(VENV_DIR)/bin/python -m quill fuzz -c $(TEST_CORPUS) -o $(RUNS_DIR)/benchmark \
		--max-prompts 100 ollama --model $(OLLAMA_MODEL) | \
		grep -E "(Completed|prompts/sec|Average)"

profile: venv
	@echo "$(BLUE)Profiling code execution...$(NC)"
	$(VENV_DIR)/bin/python -m cProfile -o profile.stats \
		-m quill fuzz -c $(TEST_CORPUS) -o $(RUNS_DIR)/profile --max-prompts 50 \
		ollama --model $(OLLAMA_MODEL)
	@echo "$(GREEN)✓ Profile saved to profile.stats$(NC)"

# Cleaning
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf $(DIST_DIR) build *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Build artifacts cleaned$(NC)"

clean-cache: clean
	@echo "$(BLUE)Cleaning cache files...$(NC)"
	rm -rf $(CACHE_DIR)
	rm -rf .ruff_cache
	@echo "$(GREEN)✓ Cache cleaned$(NC)"

clean-all: clean-cache
	@echo "$(BLUE)Cleaning all generated files...$(NC)"
	rm -rf $(RUNS_DIR)/*
	rm -rf $(VENV_DIR)
	rm -f requirements*.txt
	rm -f profile.stats
	@echo "$(GREEN)✓ All files cleaned$(NC)"

cache-stats:
	@echo "$(BLUE)Cache statistics:$(NC)"
	@if [ -f "$(RUNS_DIR)/latest/summary.json" ]; then \
		python -c "import json; \
		data = json.load(open('$(RUNS_DIR)/latest/summary.json')); \
		if 'cache_stats' in data: \
			stats = data['cache_stats']; \
			print(f\"Hit Rate: {stats['hit_rate']:.1%}\"); \
			print(f\"Memory Hits: {stats['memory_hits']}\"); \
			print(f\"Disk Hits: {stats['disk_hits']}\"); \
			print(f\"Misses: {stats['misses']}\"); \
		else: \
			print('No cache statistics found')"; \
	else \
		echo "$(YELLOW)No run data found$(NC)"; \
	fi

# Dependency Management
update-deps: venv
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install --upgrade -e ".[dev]"
	$(MAKE) requirements
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

# Git Hooks
install-hooks:
	@echo "$(BLUE)Installing git hooks...$(NC)"
	@mkdir -p .git/hooks
	@echo '#!/bin/sh\nmake check' > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)✓ Git hooks installed$(NC)"

pre-commit: check
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

# Build & Distribution
build: clean
	@echo "$(BLUE)Building package...$(NC)"
	$(VENV_DIR)/bin/pip install build
	$(VENV_DIR)/bin/python -m build
	@echo "$(GREEN)✓ Package built$(NC)"

dist: build
	@echo "$(GREEN)✓ Distribution files created in $(DIST_DIR)$(NC)"

# Version Management
bump-patch:
	@$(VENV_DIR)/bin/python -c "import re; \
		content = open('$(VERSION_FILE)').read(); \
		version_pattern = r'version = \"([0-9]+)\.([0-9]+)\.([0-9]+)\"'; \
		major, minor, patch = re.search(version_pattern, content).groups(); \
		new_version = f'{major}.{minor}.{int(patch)+1}'; \
		print(f'$(YELLOW)Bumping version: {major}.{minor}.{patch} -> {new_version}$(NC)'); \
		open('$(VERSION_FILE)', 'w').write(re.sub(version_pattern, f'version = \"{new_version}\"', content))"

bump-minor:
	@$(VENV_DIR)/bin/python -c "import re; \
		content = open('$(VERSION_FILE)').read(); \
		version_pattern = r'version = \"([0-9]+)\.([0-9]+)\.([0-9]+)\"'; \
		major, minor, patch = re.search(version_pattern, content).groups(); \
		new_version = f'{major}.{int(minor)+1}.0'; \
		print(f'$(YELLOW)Bumping version: {major}.{minor}.{patch} -> {new_version}$(NC)'); \
		open('$(VERSION_FILE)', 'w').write(re.sub(version_pattern, f'version = \"{new_version}\"', content))"

bump-major:
	@$(VENV_DIR)/bin/python -c "import re; \
		content = open('$(VERSION_FILE)').read(); \
		version_pattern = r'version = \"([0-9]+)\.([0-9]+)\.([0-9]+)\"'; \
		major, minor, patch = re.search(version_pattern, content).groups(); \
		new_version = f'{int(major)+1}.0.0'; \
		print(f'$(YELLOW)Bumping version: {major}.{minor}.{patch} -> {new_version}$(NC)'); \
		open('$(VERSION_FILE)', 'w').write(re.sub(version_pattern, f'version = \"{new_version}\"', content))"

version:
	@echo "$(BLUE)Current version:$(NC)"
	@grep "version" $(VERSION_FILE) | cut -d'"' -f2

# Git Workflow Helpers
feature:
	@if [ -z "$(NAME)" ]; then \
		echo "$(RED)Error: NAME parameter required. Usage: make feature NAME=my-feature$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating feature branch: feature/$(NAME)$(NC)"
	git checkout -b feature/$(NAME)
	@echo "$(GREEN)✓ Feature branch created$(NC)"

finish-feature:
	@BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
	if [[ "$$BRANCH" != feature/* ]]; then \
		echo "$(RED)Error: Not on a feature branch. Current branch: $$BRANCH$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Finishing feature on branch: $$(git rev-parse --abbrev-ref HEAD)$(NC)"
	@make check
	@echo "$(BLUE)Creating pull request...$(NC)"
	git push -u origin $$(git rev-parse --abbrev-ref HEAD)
	gh pr create --fill
	@echo "$(GREEN)✓ Pull request created$(NC)"

sync-main:
	@echo "$(BLUE)Syncing with main branch...$(NC)"
	git checkout main
	git pull
	git checkout -
	git rebase main
	@echo "$(GREEN)✓ Synced with main$(NC)"

# Default to help if no target specified
.DEFAULT_GOAL := help