#!/bin/bash
# MultiBrain Test Runner

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=================================="
echo "MultiBrain Test Suite"
echo "=================================="
echo

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${YELLOW}Running: ${test_name}${NC}"
    if eval "$test_command"; then
        echo -e "${GREEN}✓ ${test_name} passed${NC}\n"
        return 0
    else
        echo -e "${RED}✗ ${test_name} failed${NC}\n"
        return 1
    fi
}

# Check Python environment
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo "Please create a virtual environment first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -e ."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install test dependencies if needed
echo "Installing test dependencies..."
pip install -q pytest pytest-asyncio httpx

# Run unit tests
echo -e "\n${YELLOW}=== Unit Tests ===${NC}\n"
run_test "API Unit Tests" "pytest src/multibrain/api/tests/ -v" || true

# Run integration tests
echo -e "\n${YELLOW}=== Integration Tests ===${NC}\n"

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}API server is running${NC}"
    run_test "Frontend Integration Tests" "python tests/integration_frontend.py" || true
else
    echo -e "${RED}API server is not running!${NC}"
    echo "Skipping integration tests. Start the API with: multibrain-api"
fi

# Run LLM provider tests (optional)
echo -e "\n${YELLOW}=== LLM Provider Tests ===${NC}\n"
echo "These tests require API keys to be set in environment variables."
echo "Running with available keys..."
run_test "LLM Provider Compatibility" "python tests/integration_llm_providers.py" || true

# Summary
echo -e "\n${YELLOW}=================================="
echo "Test Summary"
echo -e "==================================${NC}\n"

echo "Test suite completed!"
echo
echo "For more detailed testing:"
echo "  - Set API keys: export OPENAI_API_KEY=sk-..."
echo "  - Run specific tests: pytest tests/test_specific.py"
echo "  - Check coverage: pytest --cov=multibrain"