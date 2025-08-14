#!/bin/bash

# Intrusion-detector Application Startup Script
# This script starts all services using Docker Compose or local development mode

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
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
DOCKER_MODE=${DOCKER_MODE:-"auto"}

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

# Function to check if Docker is available
check_docker() {
    if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if .env file exists and has required variables
check_env_file() {
    if [ ! -f ".env" ]; then
        print_error "No .env file found!"
        print_status "Creating .env template..."
        cat > .env.template << EOF
# Supabase Configuration (Required)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Application Configuration
MLFLOW_TRACKING_URI=local
APP_ENV=production
DEBUG=false

# Database Configuration (Optional - uses built-in PostgreSQL by default)
# DATABASE_URL=postgresql://user:password@host:port/database

# Redis Configuration (Optional - uses built-in Redis by default)
# REDIS_URL=redis://host:port
EOF
        print_warning "Please create a .env file with your Supabase credentials:"
        print_status "1. Copy .env.template to .env"
        print_status "2. Edit .env with your Supabase URL and API key"
        print_status "3. Run this script again"
        exit 1
    fi
    
    # Check for required variables
    if ! grep -q "SUPABASE_URL=" .env || ! grep -q "SUPABASE_KEY=" .env; then
        print_error "Missing required Supabase credentials in .env file!"
        print_status "Please add your SUPABASE_URL and SUPABASE_KEY to the .env file"
        exit 1
    fi
    
    # Check if values are not placeholder
    if grep -q "your_supabase_url_here" .env || grep -q "your_supabase_anon_key_here" .env; then
        print_error "Please replace placeholder values in .env with your actual Supabase credentials!"
        exit 1
    fi
}

# Function to check if model files exist
check_model_files() {
    print_step "Checking model files..."
    
    local model_files=("artifacts/model.joblib" "artifacts/preprocessor.joblib")
    local missing_files=()
    
    for file in "${model_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_warning "Some model files are missing:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        print_status "Creating sample model files..."
        
        if [ -f "scripts/create_sample_model.py" ]; then
            python scripts/create_sample_model.py
            print_success "Sample model files created!"
        else
            print_error "Cannot create sample models. Please ensure model files are present in artifacts/ directory"
            exit 1
        fi
    else
        print_success "All model files found!"
    fi
}

# Function to start services with Docker
start_docker_services() {
    print_header "Starting with Docker Compose"
    
    # Check if docker-compose.prod.yml exists
    if [ ! -f "docker-compose.prod.yml" ]; then
        print_error "docker-compose.prod.yml not found!"
        exit 1
    fi
    
    print_step "Starting Docker services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    if [ $? -eq 0 ]; then
        print_success "Docker services started successfully!"
    else
        print_error "Failed to start Docker services!"
        exit 1
    fi
    
    # Wait for services to be ready
    print_step "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_service_health
}

# Function to start services locally
start_local_services() {
    print_header "Starting in Local Development Mode"
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found!"
        print_status "Creating virtual environment..."
        python -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        pip install -r requirements.txt
    else
        source "$VENV_DIR/bin/activate"
    fi
    
    # Check required packages
    print_step "Checking required packages..."
    local missing_packages=()
    
    for package in "uvicorn" "fastapi" "gradio" "mlflow"; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        print_warning "Installing missing packages: ${missing_packages[*]}"
        pip install -r requirements.txt
    fi
    
    # Kill existing processes
    print_step "Stopping any existing processes..."
    pkill -f "uvicorn.*src.api.main" 2>/dev/null || true
    pkill -f "run_unified_app.py" 2>/dev/null || true
    pkill -f "mlflow server" 2>/dev/null || true
    sleep 2
    
    # Start services
    print_step "Starting FastAPI server..."
    nohup python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/fastapi.log" 2>&1 &
    echo $! > "$LOG_DIR/fastapi.pid"
    
    print_step "Starting Gradio UI..."
    nohup python run_unified_app.py > "$LOG_DIR/gradio.log" 2>&1 &
    echo $! > "$LOG_DIR/gradio.pid"
    
    print_success "Local services started!"
    sleep 5
}

# Function to check service health
check_service_health() {
    print_step "Checking service health..."
    
    local services=(
        "http://localhost:8000/health:FastAPI"
        "http://localhost:7860:Gradio UI"
    )
    
    local all_healthy=true
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$name is healthy"
        else
            print_warning "$name is not responding"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All services are healthy!"
    else
        print_warning "Some services may still be starting up..."
    fi
}

# Function to show service URLs
show_service_urls() {
    echo ""
    print_header "APPLICATION STARTED SUCCESSFULLY"
    echo ""
    print_status "Service URLs:"
    echo "  🌐 Web Interface:    http://localhost:7860"
    echo "  🔧 API Endpoint:     http://localhost:8000"
    echo "  📊 API Documentation: http://localhost:8000/docs"
    echo "  ❤️  Health Check:     http://localhost:8000/health"
    echo ""
    
    if [ "$DOCKER_MODE" = "docker" ] || [ "$DOCKER_MODE" = "auto" ]; then
        print_status "Docker Commands:"
        echo "  📊 View logs:       docker-compose -f docker-compose.prod.yml logs -f"
        echo "  🛑 Stop services:   docker-compose -f docker-compose.prod.yml down"
        echo "  🔄 Restart:         docker-compose -f docker-compose.prod.yml restart"
    else
        print_status "Local Commands:"
        echo "  📊 View logs:       tail -f logs/*.log"
        echo "  🛑 Stop services:   ./stop.sh"
        echo "  🔄 Restart:         ./stop.sh && ./start.sh"
    fi
    
    echo ""
    print_success "🎉 Intrusion Detector is ready to use!"
}

# Main function
main() {
    print_header "Intrusion Detector Startup"
    print_status "Project directory: $PROJECT_DIR"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                DOCKER_MODE="docker"
                shift
                ;;
            --local)
                DOCKER_MODE="local"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --docker    Force Docker mode"
                echo "  --local     Force local development mode"
                echo "  --help, -h  Show this help message"
                echo ""
                echo "Environment Variables:"
                echo "  DOCKER_MODE  Set to 'docker' or 'local' to override auto-detection"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    print_step "Checking prerequisites..."
    check_env_file
    check_model_files
    
    # Determine startup mode
    if [ "$DOCKER_MODE" = "docker" ] || ([ "$DOCKER_MODE" = "auto" ] && check_docker); then
        start_docker_services
    else
        if [ "$DOCKER_MODE" = "auto" ]; then
            print_warning "Docker not available, falling back to local mode"
        fi
        start_local_services
    fi
    
    # Show final status
    show_service_urls
}

# Run main function
main "$@" 