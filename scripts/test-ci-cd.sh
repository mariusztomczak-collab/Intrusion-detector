#!/bin/bash

# CI/CD Test Script for Intrusion Detector
# This script simulates the GitHub Actions workflow locally

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

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

print_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

print_step() {
    echo -e "${CYAN}➤ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run test with timeout
run_with_timeout() {
    local timeout=$1
    local command=$2
    local description=$3
    
    print_step "$description"
    
    if timeout "$timeout" bash -c "$command" > "$LOG_DIR/ci-cd-test.log" 2>&1; then
        print_success "$description completed"
        return 0
    else
        print_error "$description failed (timeout: ${timeout}s)"
        echo "Logs:"
        tail -20 "$LOG_DIR/ci-cd-test.log"
        return 1
    fi
}

# Main CI/CD test function
test_cicd() {
    print_header "CI/CD Pipeline Test"
    print_status "Testing GitHub Actions workflow locally..."
    
    local test_results=()
    local failed_tests=()
    
    # Test 1: Code Quality & Linting
    print_header "Job 1: Code Quality & Linting"
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && black --check --diff src/ tests/" "Black formatting check"; then
        test_results+=("✅ Black")
    else
        failed_tests+=("❌ Black")
    fi
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && isort --check-only --diff src/ tests/" "Import sorting check"; then
        test_results+=("✅ isort")
    else
        failed_tests+=("❌ isort")
    fi
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics" "Flake8 code quality check"; then
        test_results+=("✅ flake8")
    else
        failed_tests+=("❌ flake8")
    fi
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && mypy src/ --ignore-missing-imports" "Type checking"; then
        test_results+=("✅ mypy")
    else
        failed_tests+=("❌ mypy")
    fi
    
    # Test 2: Unit Tests
    print_header "Job 2: Unit Tests & Coverage"
    
    if run_with_timeout 600 "cd $PROJECT_DIR && source venv/bin/activate && pytest tests/unit/ -v --cov=src --cov-report=term-missing" "Unit tests with coverage"; then
        test_results+=("✅ Unit Tests")
    else
        failed_tests+=("❌ Unit Tests")
    fi
    
    # Test 3: Integration Tests
    print_header "Job 3: Integration Tests"
    
    if run_with_timeout 600 "cd $PROJECT_DIR && source venv/bin/activate && pytest tests/integration/ -v" "Integration tests"; then
        test_results+=("✅ Integration Tests")
    else
        failed_tests+=("❌ Integration Tests")
    fi
    
    # Test 4: Security Scan
    print_header "Job 4: Security Analysis"
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && bandit -r src/ -f json -o $LOG_DIR/bandit-report.json" "Bandit security scan"; then
        test_results+=("✅ Bandit")
    else
        failed_tests+=("❌ Bandit")
    fi
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && safety check --json --output $LOG_DIR/safety-report.json" "Safety dependency check"; then
        test_results+=("✅ Safety")
    else
        failed_tests+=("❌ Safety")
    fi
    
    # Test 5: Docker Build Test
    print_header "Job 5: Docker Build Test"
    
    if command_exists docker; then
        if run_with_timeout 600 "cd $PROJECT_DIR && docker build -f Dockerfile.prod -t intrusion-detector-api:test ." "API Docker build"; then
            test_results+=("✅ API Docker Build")
        else
            failed_tests+=("❌ API Docker Build")
        fi
        
        if run_with_timeout 600 "cd $PROJECT_DIR && docker build -f Dockerfile.ui -t intrusion-detector-ui:test ." "UI Docker build"; then
            test_results+=("✅ UI Docker Build")
        else
            failed_tests+=("❌ UI Docker Build")
        fi
    else
        print_warning "Docker not found, skipping Docker build tests"
        test_results+=("⚠️ Docker (not available)")
    fi
    
    # Test 6: Application Test
    print_header "Job 6: Application Test"
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && python -c \"import sys; sys.path.append('src'); from api.main import app; print('✅ Application imports successfully')\"" "Application startup test"; then
        test_results+=("✅ Application Startup")
    else
        failed_tests+=("❌ Application Startup")
    fi
    
    if run_with_timeout 300 "cd $PROJECT_DIR && source venv/bin/activate && python -c \"import joblib; model = joblib.load('artifacts/model.joblib'); print(f'✅ Model loaded: {type(model)}')\"" "Model loading test"; then
        test_results+=("✅ Model Loading")
    else
        failed_tests+=("❌ Model Loading")
    fi
    
    # Test 7: Transfer Simulation
    print_header "Job 7: Transfer Simulation"
    
    if run_with_timeout 60 "cd $PROJECT_DIR && git status --porcelain" "Git status check"; then
        test_results+=("✅ Git Status")
    else
        failed_tests+=("❌ Git Status")
    fi
    
    # Print results
    print_header "CI/CD Test Results"
    
    echo "✅ Passed Tests (${#test_results[@]}):"
    for test in "${test_results[@]}"; do
        echo "  $test"
    done
    
    if [ ${#failed_tests[@]} -gt 0 ]; then
        echo ""
        echo "❌ Failed Tests (${#failed_tests[@]}):"
        for test in "${failed_tests[@]}"; do
            echo "  $test"
        done
        echo ""
        print_error "CI/CD pipeline would fail! Fix the issues above."
        return 1
    else
        echo ""
        print_success "All CI/CD tests passed! Ready for GitHub Actions deployment."
        return 0
    fi
}

# Function to show help
show_help() {
    echo "CI/CD Test Script for Intrusion Detector"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Show detailed output"
    echo "  --clean        Clean up test artifacts"
    echo ""
    echo "This script simulates the GitHub Actions workflow locally to ensure"
    echo "that the CI/CD pipeline will pass when pushed to GitHub."
}

# Function to clean up
cleanup() {
    print_header "Cleaning up test artifacts"
    
    # Remove test Docker images
    if command_exists docker; then
        docker rmi intrusion-detector-api:test 2>/dev/null || true
        docker rmi intrusion-detector-ui:test 2>/dev/null || true
    fi
    
    # Remove test logs
    rm -f "$LOG_DIR/ci-cd-test.log"
    rm -f "$LOG_DIR/bandit-report.json"
    rm -f "$LOG_DIR/safety-report.json"
    
    print_success "Cleanup completed"
}

# Parse command line arguments
VERBOSE=false
CLEANUP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --clean)
            CLEANUP=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
if [ "$CLEANUP" = true ]; then
    cleanup
    exit 0
fi

# Check prerequisites
print_header "Checking Prerequisites"

if ! command_exists python3; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

if ! command_exists git; then
    print_error "Git is required but not installed"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install -e ".[dev]"
else
    print_success "Virtual environment found"
fi

# Run CI/CD tests
if test_cicd; then
    print_header "🎉 CI/CD Test Summary"
    print_success "All tests passed! Your code is ready for GitHub Actions deployment."
    echo ""
    echo "Next steps:"
    echo "1. Commit your changes: git add . && git commit -m 'Update CI/CD pipeline'"
    echo "2. Push to GitHub: git push origin main"
    echo "3. Check GitHub Actions: https://github.com/your-repo/actions"
    echo ""
    print_success "🚀 Ready to deploy!"
    exit 0
else
    print_header "❌ CI/CD Test Summary"
    print_error "Some tests failed. Fix the issues before deploying to GitHub Actions."
    echo ""
    echo "Check the logs in: $LOG_DIR/"
    echo "Fix the issues and run this script again."
    exit 1
fi
