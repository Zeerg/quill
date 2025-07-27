#!/bin/bash
# Quill Development Setup Script
# This script sets up your local development environment for Quill

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Quill Development Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}Error: Python 3.10+ is required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version${NC}"

# Check if Ollama is installed
echo -e "${YELLOW}Checking for Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
    else
        echo -e "${YELLOW}⚠ Ollama is not running. Start it with: ollama serve${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Ollama not found. Install from: https://ollama.ai${NC}"
fi

# Create virtual environment
echo -e "${YELLOW}Setting up virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install package with development dependencies
echo -e "${YELLOW}Installing Quill and dependencies...${NC}"
pip install -e ".[dev]" > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Install additional development tools
echo -e "${YELLOW}Installing development tools...${NC}"
pip install black ruff mypy pytest pytest-cov pytest-asyncio > /dev/null 2>&1
pip install sphinx sphinx-rtd-theme > /dev/null 2>&1
pip install bandit safety > /dev/null 2>&1
echo -e "${GREEN}✓ Development tools installed${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating project directories...${NC}"
mkdir -p runs
mkdir -p docs
mkdir -p tests
echo -e "${GREEN}✓ Directories created${NC}"

# Set up git hooks
echo -e "${YELLOW}Setting up git hooks...${NC}"
if [ -d ".git" ]; then
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
# Run code quality checks before commit
echo "Running pre-commit checks..."
make check
EOF
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✓ Git hooks installed${NC}"
else
    echo -e "${YELLOW}⚠ Not a git repository, skipping hooks${NC}"
fi

# Download sample model for Ollama (if Ollama is installed)
if command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Checking for llama2 model...${NC}"
    if ollama list | grep -q "llama2"; then
        echo -e "${GREEN}✓ llama2 model already available${NC}"
    else
        echo -e "${YELLOW}Would you like to download llama2 model for testing? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Downloading llama2 model...${NC}"
            ollama pull llama2
            echo -e "${GREEN}✓ llama2 model downloaded${NC}"
        fi
    fi
fi

# Generate requirements files
echo -e "${YELLOW}Generating requirements files...${NC}"
pip freeze > requirements.txt
pip freeze | grep -E "(black|ruff|mypy|pytest|sphinx|bandit)" > requirements-dev.txt
echo -e "${GREEN}✓ Requirements files generated${NC}"

# Run initial checks
echo -e "${YELLOW}Running initial code checks...${NC}"
echo -e "  Formatting..."
black quill/ --quiet
echo -e "  Linting..."
ruff check quill/ --quiet || true
echo -e "${GREEN}✓ Initial checks complete${NC}"

# Display Claude agents info
echo ""
echo -e "${BLUE}Claude Sub-Agents Available:${NC}"
if [ -d ".claude/agents" ]; then
    for agent in .claude/agents/*.md; do
        if [ -f "$agent" ]; then
            name=$(basename "$agent" .md)
            echo -e "  - $name"
        fi
    done
else
    echo -e "${YELLOW}  No agents found${NC}"
fi

# Final instructions
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Setup Complete! 🎉${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Activate the virtual environment:"
echo -e "   ${BLUE}source .venv/bin/activate${NC}"
echo ""
echo -e "2. Run a test fuzzing session:"
echo -e "   ${BLUE}make fuzz-test${NC}"
echo ""
echo -e "3. See all available commands:"
echo -e "   ${BLUE}make help${NC}"
echo ""
echo -e "4. Start Ollama (if not running):"
echo -e "   ${BLUE}ollama serve${NC}"
echo ""
echo -e "${GREEN}Happy fuzzing! 🚀${NC}"