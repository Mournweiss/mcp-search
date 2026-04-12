#!/usr/bin/env bash

set -euo pipefail

# ANSI color codes for output formatting
COLOR_INFO="\033[0m"       # White (default)
COLOR_WARN="\033[1;33m"    # Yellow
COLOR_ERROR="\033[1;31m"   # Red
COLOR_SUCCESS="\033[1;32m" # Green
COLOR_RESET="\033[0m"

# Default values
RUN_COVERAGE=true
RUN_UNIT=true
RUN_INTEGRATION=false
VERBOSE=false
TEST_PATH="tests/"

# Function to print colored output
info()    { echo -e "${COLOR_INFO}$1${COLOR_RESET}" >&2; }
warn()    { echo -e "${COLOR_WARN}$1${COLOR_RESET}" >&2; }
error()   { echo -e "${COLOR_ERROR}$1${COLOR_RESET}" >&2; exit 1; }
success() { echo -e "${COLOR_SUCCESS}$1${COLOR_RESET}" >&2; }

# Function to show help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-coverage     Skip coverage reporting"
    echo "  --unit            Run only unit tests"
    echo "  --integration     Run only integration tests" 
    echo "  --verbose         Enable verbose output"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests with coverage"
    echo "  $0 --no-coverage      # Run tests without coverage"
    echo "  $0 --unit --verbose   # Run unit tests verbosely"
    echo ""
}

# Function to check if poetry is available
check_poetry() {
    if ! command -v poetry &> /dev/null; then
        error "Poetry is not installed. Please install Poetry first."
    fi
}

# Function to run tests with coverage
run_with_coverage() {
    info "Running tests with coverage..."
    
    poetry install --with dev
    
    # Run pytest with coverage
    if [ "$VERBOSE" = true ]; then
        poetry run pytest \
            --verbose \
            --cov=src/mcp_search \
            --cov-report=term-missing \
            --cov-report=html:coverage_html_report \
            --cov-report=xml:coverage.xml \
            $TEST_PATH
    else
        poetry run pytest \
            --cov=src/mcp_search \
            --cov-report=term-missing \
            --cov-report=html:coverage_html_report \
            --cov-report=xml:coverage.xml \
            $TEST_PATH
    fi
    
    success "Tests completed with coverage report generated"
}

# Function to run tests without coverage
run_without_coverage() {
    info "Running tests without coverage..."
    
    poetry install --with dev
    
    # Run pytest without coverage
    if [ "$VERBOSE" = true ]; then
        poetry run pytest --verbose $TEST_PATH
    else
        poetry run pytest $TEST_PATH
    fi
    
    success "Tests completed"
}

# Function to run only unit tests
run_unit_tests() {
    info "Running unit tests only..."
    
    poetry install --with dev
    
    if [ "$VERBOSE" = true ]; then
        poetry run pytest --verbose tests/unit/
    else
        poetry run pytest tests/unit/
    fi
    
    success "Unit tests completed"
}

# Function to run only integration tests
run_integration_tests() {
    info "Running integration tests only..."
    
    poetry install --with dev
    
    if [ "$VERBOSE" = true ]; then
        poetry run pytest --verbose tests/integration/
    else
        poetry run pytest tests/integration/
    fi
    
    success "Integration tests completed"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-coverage)
            RUN_COVERAGE=false
            shift
            ;;
        --unit)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            TEST_PATH="tests/unit/"
            shift
            ;;
        --integration)
            RUN_UNIT=false
            RUN_INTEGRATION=true
            TEST_PATH="tests/integration/"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Main execution logic
main() {
    info "Starting MCP Search Server tests..."
    
    check_poetry
    
    # Determine which tests to run based on flags
    if [ "$RUN_UNIT" = true ] && [ "$RUN_INTEGRATION" = true ]; then
        # Run all tests
        if [ "$RUN_COVERAGE" = true ]; then
            run_with_coverage
        else
            run_without_coverage
        fi
    elif [ "$RUN_UNIT" = true ] && [ "$RUN_INTEGRATION" = false ]; then
        # Run only unit tests
        run_unit_tests
    elif [ "$RUN_UNIT" = false ] && [ "$RUN_INTEGRATION" = true ]; then
        # Run only integration tests
        run_integration_tests
    else
        # Default to all tests without coverage
        run_without_coverage
    fi
    
    success "All tests completed successfully!"
}

main "$@"