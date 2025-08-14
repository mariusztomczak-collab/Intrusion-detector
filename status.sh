#!/bin/bash

# Intrusion-detector Application Status Script
# This script shows the current status of all services

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
LOG_DIR="$PROJECT_DIR/logs"

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

# Function to check if a process is running
is_process_running() {
    local pid=$1
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0  # Process is running
    else
        return 1  # Process is not running
    fi
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to check service health via HTTP
check_service_health() {
    local url=$1
    local service_name=$2
    
    if curl -s "$url" >/dev/null 2>&1; then
        print_success "$service_name is healthy"
        return 0
    else
        print_warning "$service_name is not responding"
        return 1
    fi
}

# Function to show Docker status
show_docker_status() {
    if ! check_docker; then
        print_warning "Docker not available"
        return
    fi
    
    if [ ! -f "docker-compose.prod.yml" ]; then
        print_warning "docker-compose.prod.yml not found"
        return
    fi
    
    print_step "Docker containers:"
    
    # Check if containers are running
    local containers=$(docker ps --filter "name=intrusion-detector" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true)
    
    if [ -n "$containers" ]; then
        echo "$containers"
        
        # Check container health
        print_step "Container health:"
        local container_names=$(docker ps --filter "name=intrusion-detector" --format "{{.Names}}" 2>/dev/null || true)
        
        if [ -n "$container_names" ]; then
            echo "$container_names" | while read -r container; do
                local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
                case "$health" in
                    "healthy")
                        print_success "$container: Healthy"
                        ;;
                    "unhealthy")
                        print_error "$container: Unhealthy"
                        ;;
                    "starting")
                        print_warning "$container: Starting"
                        ;;
                    *)
                        print_warning "$container: $health"
                        ;;
                esac
            done
        fi
    else
        print_warning "No Docker containers running"
    fi
}

# Function to show local process status
show_local_status() {
    print_step "Local processes:"
    
    # Check PID files
    local services=("fastapi:FastAPI" "gradio:Gradio UI" "mlflow:MLflow")
    local any_running=false
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service name <<< "$service_info"
        
        if [ -f "$LOG_DIR/${service}.pid" ]; then
            local pid=$(cat "$LOG_DIR/${service}.pid")
            if is_process_running "$pid"; then
                print_success "$name: Running (PID: $pid)"
                any_running=true
            else
                print_warning "$name: PID file exists but process not running"
            fi
        else
            print_warning "$name: Not running (no PID file)"
        fi
    done
    
    if [ "$any_running" = false ]; then
        print_warning "No local services are running"
    fi
}

# Function to show port status
show_port_status() {
    print_step "Port status:"
    
    local ports=("8000:FastAPI" "7860:Gradio UI" "5000:MLflow")
    
    for port_info in "${ports[@]}"; do
        IFS=':' read -r port name <<< "$port_info"
        
        if check_port "$port"; then
            print_success "Port $port ($name): In use"
        else
            print_warning "Port $port ($name): Free"
        fi
    done
}

# Function to show service health
show_service_health() {
    print_step "Service health:"
    
    local services=(
        "http://localhost:8000/health:FastAPI"
        "http://localhost:7860:Gradio UI"
    )
    
    local all_healthy=true
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        
        if ! check_service_health "$url" "$name"; then
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All services are healthy!"
    else
        print_warning "Some services may not be fully ready"
    fi
}

# Function to show service URLs
show_service_urls() {
    print_step "Service URLs:"
    echo "  🌐 Web Interface:    http://localhost:7860"
    echo "  🔧 API Endpoint:     http://localhost:8000"
    echo "  📊 API Documentation: http://localhost:8000/docs"
    echo "  ❤️  Health Check:     http://localhost:8000/health"
}

# Function to show environment info
show_environment_info() {
    print_step "Environment information:"
    
    # Check .env file
    if [ -f ".env" ]; then
        print_success ".env file exists"
        
        # Check for required variables
        if grep -q "SUPABASE_URL=" .env && grep -q "SUPABASE_KEY=" .env; then
            print_success "Supabase credentials configured"
        else
            print_warning "Missing Supabase credentials in .env"
        fi
        
        # Check MLflow setting
        if grep -q "MLFLOW_TRACKING_URI=local" .env; then
            print_success "Using local model files (end-user mode)"
        else
            print_warning "Using MLflow (developer mode)"
        fi
    else
        print_error ".env file not found"
    fi
    
    # Check model files
    if [ -f "artifacts/model.joblib" ] && [ -f "artifacts/preprocessor.joblib" ]; then
        print_success "Model files found"
    else
        print_warning "Model files missing"
    fi
}

# Main function
main() {
    print_header "Intrusion Detector Status"
    print_status "Project directory: $PROJECT_DIR"
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            "--docker")
                show_docker_status
                exit 0
                ;;
            "--local")
                show_local_status
                exit 0
                ;;
            "--ports")
                show_port_status
                exit 0
                ;;
            "--health")
                show_service_health
                exit 0
                ;;
            "--urls")
                show_service_urls
                exit 0
                ;;
            "--env")
                show_environment_info
                exit 0
                ;;
            "--help"|"-h")
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --docker   - Show only Docker container status"
                echo "  --local    - Show only local process status"
                echo "  --ports    - Show only port status"
                echo "  --health   - Show only service health"
                echo "  --urls     - Show only service URLs"
                echo "  --env      - Show only environment information"
                echo "  --help, -h - Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0              # Show complete status"
                echo "  $0 --docker     # Show Docker status only"
                echo "  $0 --health     # Show service health only"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
        shift
    done
    
    # Show complete status
    show_docker_status
    echo ""
    show_local_status
    echo ""
    show_port_status
    echo ""
    show_service_health
    echo ""
    show_service_urls
    echo ""
    show_environment_info
    echo ""
    print_success "Status check complete!"
}

# Run main function
main "$@"
