.PHONY: all clean install test lint build dist bump-patch bump-minor bump-major version help venv

# Variables
PYTHON := python
UV := uv
VERSION_FILE := pyproject.toml
DIST_DIR := dist
TEST_DIR := tests
SRC_DIR := quill
VENV_DIR := .venv

# Default target
all: test lint build

# Create virtual environment
venv:
	$(UV) venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

# Install dependencies
install: venv
	$(UV) pip install -e .

# Run tests
test:
	$(UV) run pytest $(TEST_DIR)

# Run linting
lint:
	$(UV) run black $(SRC_DIR)

# Clean built artifacts
clean:
	rm -rf $(DIST_DIR) build *.egg-info .uv
	$(PYTHON) quill.py clean --all --confirm
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Build package
build: clean
	$(UV) pip build

# Create distribution packages
dist: build
	$(UV) pip build --sdist --wheel
	@echo "Distribution files created in $(DIST_DIR)"

# Version management commands
bump-patch:
	$(UV) run python -c "import re; \
		content = open('$(VERSION_FILE)').read(); \
		version_pattern = r'version = \"([0-9]+)\.([0-9]+)\.([0-9]+)\"'; \
		major, minor, patch = re.search(version_pattern, content).groups(); \
		new_version = f'{major}.{minor}.{int(patch)+1}'; \
		print(f'Bumping version: {major}.{minor}.{patch} -> {new_version}'); \
		open('$(VERSION_FILE)', 'w').write(re.sub(version_pattern, f'version = \"{new_version}\"', content))"

bump-minor:
	$(UV) run python -c "import re; \
		content = open('$(VERSION_FILE)').read(); \
		version_pattern = r'version = \"([0-9]+)\.([0-9]+)\.([0-9]+)\"'; \
		major, minor, patch = re.search(version_pattern, content).groups(); \
		new_version = f'{major}.{int(minor)+1}.0'; \
		print(f'Bumping version: {major}.{minor}.{patch} -> {new_version}'); \
		open('$(VERSION_FILE)', 'w').write(re.sub(version_pattern, f'version = \"{new_version}\"', content))"

bump-major:
	$(UV) run python -c "import re; \
		content = open('$(VERSION_FILE)').read(); \
		version_pattern = r'version = \"([0-9]+)\.([0-9]+)\.([0-9]+)\"'; \
		major, minor, patch = re.search(version_pattern, content).groups(); \
		new_version = f'{int(major)+1}.0.0'; \
		print(f'Bumping version: {major}.{minor}.{patch} -> {new_version}'); \
		open('$(VERSION_FILE)', 'w').write(re.sub(version_pattern, f'version = \"{new_version}\"', content))"

# Display current version
version:
	@grep "version" $(VERSION_FILE) | cut -d'"' -f2


# Help
help:
	@echo "Available targets:"
	@echo "  all         : Run tests, lint, and build"
	@echo "  venv        : Create virtual environment with uv"
	@echo "  install     : Create venv and install package in development mode"
	@echo "  test        : Run tests"
	@echo "  lint        : Run linting tools"
	@echo "  clean       : Remove build artifacts and cache files"
	@echo "  build       : Build the package"
	@echo "  dist        : Create distribution packages"
	@echo "  bump-patch  : Increment patch version (x.y.Z)"
	@echo "  bump-minor  : Increment minor version (x.Y.0)"
	@echo "  bump-major  : Increment major version (X.0.0)"
	@echo "  version     : Display current version"
	@echo "  help        : Show this help message"