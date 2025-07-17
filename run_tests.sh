#!/bin/bash

# Test runner script for Neurologix Smart Search POV
# Supports different test types and environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="unit"
VERBOSE=false
COVERAGE=false
PARALLEL=false
ENVIRONMENT="test"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE       Test type: unit, integration, e2e, all (default: unit)"
    echo "  -v, --verbose         Verbose output"
    echo "  -c, --coverage        Generate coverage report"
    echo "  -p, --parallel        Run tests in parallel"
    echo "  -e, --env ENV         Environment: test, local, ci (default: test)"
    echo "  -f, --filter PATTERN  Run only tests matching pattern"
    echo "  -m, --marker MARKER   Run only tests with specific marker"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -t unit -v -c                    # Unit tests with verbose output and coverage"
    echo "  $0 -t integration                   # Integration tests"
    echo "  $0 -t e2e -e local                  # E2E tests in local environment"
    echo "  $0 -m smoke                         # Run only smoke tests"
    echo "  $0 -f test_query_processor          # Run tests matching pattern"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--filter)
            TEST_FILTER="$2"
            shift 2
            ;;
        -m|--marker)
            TEST_MARKER="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate test type
case $TEST_TYPE in
    unit|integration|e2e|all)
        ;;
    *)
        print_error "Invalid test type: $TEST_TYPE"
        print_error "Valid types: unit, integration, e2e, all"
        exit 1
        ;;
esac

print_status "Starting Neurologix Smart Search tests..."
print_status "Test type: $TEST_TYPE"
print_status "Environment: $ENVIRONMENT"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "tests" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ] && [ ! -d "venv" ]; then
    print_warning "No virtual environment detected. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
elif [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
fi

# Install test dependencies
print_status "Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist pytest-timeout

# Set environment variables based on environment
case $ENVIRONMENT in
    test)
        export TESTING=true
        export DB_NAME=neurologix_test_db
        export LOG_LEVEL=WARNING
        ;;
    local)
        export TESTING=true
        export LOG_LEVEL=INFO
        ;;
    ci)
        export TESTING=true
        export LOG_LEVEL=ERROR
        export CI=true
        ;;
esac

# Build pytest command
PYTEST_CMD="pytest"

# Add test type filters
case $TEST_TYPE in
    unit)
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        ;;
    e2e)
        PYTEST_CMD="$PYTEST_CMD tests/e2e/"
        print_warning "E2E tests require running backend and frontend services"
        ;;
    all)
        PYTEST_CMD="$PYTEST_CMD tests/"
        ;;
esac

# Add options
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=backend --cov=config --cov-report=html --cov-report=term-missing"
fi

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

if [ ! -z "$TEST_FILTER" ]; then
    PYTEST_CMD="$PYTEST_CMD -k $TEST_FILTER"
fi

if [ ! -z "$TEST_MARKER" ]; then
    PYTEST_CMD="$PYTEST_CMD -m $TEST_MARKER"
fi

# Pre-test checks
print_status "Running pre-test checks..."

# Check if backend can be imported
python -c "
try:
    from backend.main import app
    print('✓ Backend imports successfully')
except ImportError as e:
    print(f'✗ Backend import failed: {e}')
    exit(1)
" || {
    print_error "Backend import failed. Please check your code."
    exit 1
}

# For E2E tests, check if services are running
if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
    print_status "Checking if services are running for E2E tests..."
    
    # Check backend
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend service is running"
    else
        print_warning "Backend service not running. E2E tests may fail."
        print_warning "Start backend with: cd backend && uvicorn main:app --reload"
    fi
    
    # Check frontend
    if curl -s -f http://localhost:8501 > /dev/null 2>&1; then
        print_success "Frontend service is running"
    else
        print_warning "Frontend service not running. Some E2E tests may fail."
        print_warning "Start frontend with: streamlit run frontend.py"
    fi
fi

# Run tests
print_status "Running tests with command: $PYTEST_CMD"
echo ""

# Execute pytest
if eval $PYTEST_CMD; then
    print_success "All tests completed successfully!"
    
    # Show coverage report location if generated
    if [ "$COVERAGE" = true ]; then
        print_status "Coverage report generated in: htmlcov/index.html"
    fi
    
    exit 0
else
    print_error "Some tests failed!"
    exit 1
fi
