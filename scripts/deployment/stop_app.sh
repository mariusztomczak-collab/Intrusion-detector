#!/bin/bash

# Intrusion-detector Application Shutdown Script
# This script safely stops all services using Docker Compose or local development mode

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
DOCKER_MODE=${DOCKER_MODE:-"auto"}

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

# Function to kill process gracefully
kill_process_gracefully() {
    local pid=$1
    local service_name=$2
    local timeout=10
    
    if [ -z "$pid" ]; then
        print_warning "No PID found for $service_name"
        return
    fi
    
    if is_process_running "$pid"; then
        print_step "Stopping $service_name (PID: $pid)..."
        
        # Try graceful shutdown first
        kill "$pid" 2>/dev/null || true
        
        # Wait for graceful shutdown
        local count=0
        while is_process_running "$pid" && [ $count -lt $timeout ]; do
            sleep 1
            ((count++))
        done
        
        # Force kill if still running
        if is_process_running "$pid"; then
            print_warning "Force killing $service_name..."
            kill -9 "$pid" 2>/dev/null || true
            sleep 1
        fi
        
        if is_process_running "$pid"; then
            print_error "Failed to stop $service_name"
        else
            print_success "$service_name stopped successfully"
        fi
    else
        print_warning "$service_name is not running"
    fi
}

# Function to stop service by pattern
stop_service_by_pattern() {
    local pattern=$1
    local service_name=$2
    
    print_step "Stopping $service_name processes..."
    
    # Find and kill processes by pattern
    local pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        # Convert to array and process each PID
        local pid_array=($pids)
        for pid in "${pid_array[@]}"; do
            if [ -n "$pid" ] && [ "$pid" -gt 0 ]; then
                kill_process_gracefully "$pid" "$service_name"
            fi
        done
    else
        print_warning "No $service_name processes found"
    fi
}

# Function to check if port is still in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to stop Docker services
stop_docker_services() {
    print_header "Stopping Docker Services"
    
    if [ ! -f "docker-compose.prod.yml" ]; then
        print_error "docker-compose.prod.yml not found!"
        return 1
    fi
    
    print_step "Stopping Docker Compose services..."
    docker-compose -f docker-compose.prod.yml down
    
    if [ $? -eq 0 ]; then
        print_success "Docker services stopped successfully!"
    else
        print_error "Failed to stop Docker services!"
        return 1
    fi
    
    # Wait a moment for cleanup
    sleep 3
    
    # Check if containers are still running
    local running_containers=$(docker ps --filter "name=intrusion-detector" --format "{{.Names}}" 2>/dev/null || true)
    
    if [ -n "$running_containers" ]; then
        print_warning "Some containers are still running:"
        echo "$running_containers" | while read -r container; do
            echo "  - $container"
        done
        print_step "Force stopping remaining containers..."
        docker stop $running_containers 2>/dev/null || true
    fi
}

# Function to stop local services
stop_local_services() {
    print_header "Stopping Local Services"
    
    # Stop services using PID files first (graceful shutdown)
    print_step "Attempting graceful shutdown using PID files..."
    
    # Stop FastAPI
    if [ -f "$LOG_DIR/fastapi.pid" ]; then
        FASTAPI_PID=$(cat "$LOG_DIR/fastapi.pid")
        kill_process_gracefully "$FASTAPI_PID" "FastAPI"
        rm -f "$LOG_DIR/fastapi.pid"
    fi
    
    # Stop Gradio
    if [ -f "$LOG_DIR/gradio.pid" ]; then
        GRADIO_PID=$(cat "$LOG_DIR/gradio.pid")
        kill_process_gracefully "$GRADIO_PID" "Gradio UI"
        rm -f "$LOG_DIR/gradio.pid"
    fi
    
    # Stop MLflow (if running)
    if [ -f "$LOG_DIR/mlflow.pid" ]; then
        MLFLOW_PID=$(cat "$LOG_DIR/mlflow.pid")
        kill_process_gracefully "$MLFLOW_PID" "MLflow"
        rm -f "$LOG_DIR/mlflow.pid"
    fi
    
    # Force stop any remaining processes by pattern
    print_step "Force stopping any remaining processes..."
    
    # Stop FastAPI processes
    stop_service_by_pattern "uvicorn.*src.api.main" "FastAPI"
    
    # Stop Gradio processes
    stop_service_by_pattern "run_unified_app.py" "Gradio UI"
    
    # Stop MLflow processes
    stop_service_by_pattern "mlflow server" "MLflow"
    stop_service_by_pattern "gunicorn.*mlflow" "MLflow Worker"
    
    # Additional aggressive cleanup for stubborn processes
    print_step "Performing aggressive cleanup..."
    
    # Kill any remaining Python processes that might be related
    local python_pids=$(pgrep -f "python.*(uvicorn|gradio|mlflow|run_unified)" 2>/dev/null || true)
    if [ -n "$python_pids" ]; then
        local pid_array=($python_pids)
        for pid in "${pid_array[@]}"; do
            if [ -n "$pid" ] && [ "$pid" -gt 0 ]; then
                print_warning "Force killing remaining Python process PID: $pid"
                kill -9 "$pid" 2>/dev/null || true
            fi
        done
    fi
    
    # Wait a moment for processes to fully terminate
    sleep 3
}

# Function to check final status
check_final_status() {
    print_step "Checking final status..."
    
    # Check if ports are free
    local ports=("8000:FastAPI" "7860:Gradio UI" "5000:MLflow")
    local all_ports_free=true
    
    for port_info in "${ports[@]}"; do
        IFS=':' read -r port name <<< "$port_info"
        
        if check_port "$port"; then
            print_warning "Port $port ($name) is still in use"
            all_ports_free=false
        else
            print_success "Port $port ($name) is free"
        fi
    done
    
    # Check for any remaining processes with more specific patterns
    print_step "Checking for remaining processes..."
    
    local remaining_patterns=(
        "uvicorn.*src.api.main"
        "run_unified_app.py"
        "mlflow server"
        "gunicorn.*mlflow"
        "python.*uvicorn"
        "python.*gradio"
    )
    
    local any_remaining=false
    
    for pattern in "${remaining_patterns[@]}"; do
        local pids=$(pgrep -f "$pattern" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            print_warning "Found remaining processes matching '$pattern':"
            local pid_array=($pids)
            for pid in "${pid_array[@]}"; do
                if [ -n "$pid" ] && [ "$pid" -gt 0 ]; then
                    local cmd=$(ps -p "$pid" -o command= 2>/dev/null || echo "Unknown")
                    echo "  PID $pid: $cmd"
                    any_remaining=true
                fi
            done
        fi
    done
    
    if [ "$any_remaining" = true ]; then
        print_warning "Some processes are still running - attempting final cleanup..."
        
        # Final aggressive cleanup
        for pattern in "${remaining_patterns[@]}"; do
            local pids=$(pgrep -f "$pattern" 2>/dev/null || true)
            if [ -n "$pids" ]; then
                local pid_array=($pids)
                for pid in "${pid_array[@]}"; do
                    if [ -n "$pid" ] && [ "$pid" -gt 0 ]; then
                        print_warning "Final force kill of PID $pid"
                        kill -9 "$pid" 2>/dev/null || true
                    fi
                done
            fi
        done
        
        # Wait and check again
        sleep 2
        local final_check=$(pgrep -f "(uvicorn|gradio|mlflow|run_unified)" 2>/dev/null || true)
        if [ -n "$final_check" ]; then
            print_error "Some processes still running after final cleanup"
            all_ports_free=false
        else
            print_success "All processes successfully terminated after final cleanup"
        fi
    fi
    
    if [ "$all_ports_free" = true ]; then
        print_success "All services have been stopped successfully!"
    else
        print_warning "Some services may still be running"
    fi
}

# Function to show current status
show_status() {
    print_header "Current Application Status"
    
    # Check Docker containers
    if check_docker && [ -f "docker-compose.prod.yml" ]; then
        print_step "Docker containers:"
        local containers=$(docker ps --filter "name=intrusion-detector" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true)
        
        if [ -n "$containers" ]; then
            echo "$containers"
        else
            print_warning "No Docker containers running"
        fi
    fi
    
    # Check local processes
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
    
    # Check ports
    print_step "Port status:"
    local ports=("8000:FastAPI" "7860:Gradio UI" "5000:MLflow")
    
    for port_info in "${ports[@]}"; do
        IFS=':' read -r port name <<< "$port_info"
        
        if check_port "$port"; then
            print_warning "Port $port ($name): In use"
        else
            print_success "Port $port ($name): Free"
        fi
    done
}

# Function to restart services
restart_services() {
    print_header "Restarting Application"
    
    print_step "Stopping services..."
    stop_services
    
    print_step "Waiting for cleanup..."
    sleep 3
    
    print_step "Starting services..."
    ./start.sh
}

# Main shutdown function
stop_services() {
    print_header "Intrusion Detector Shutdown"
    print_status "Project directory: $PROJECT_DIR"
    
    # Determine shutdown mode
    if [ "$DOCKER_MODE" = "docker" ] || ([ "$DOCKER_MODE" = "auto" ] && check_docker); then
        stop_docker_services
    else
        if [ "$DOCKER_MODE" = "auto" ]; then
            print_warning "Docker not available, stopping local services"
        fi
        stop_local_services
    fi
    
    # Check final status
    check_final_status
    
    # Final cleanup
    print_step "Performing final cleanup..."
    
    # Remove PID files if they still exist
    rm -f "$LOG_DIR/fastapi.pid"
    rm -f "$LOG_DIR/gradio.pid"
    rm -f "$LOG_DIR/mlflow.pid"
    
    echo ""
    print_success "🎉 Application shutdown complete!"
}

# Main function
main() {
    # Parse command line arguments
    case "${1:-stop}" in
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "restart")
            restart_services
            ;;
        "--docker")
            DOCKER_MODE="docker"
            stop_services
            ;;
        "--local")
            DOCKER_MODE="local"
            stop_services
            ;;
        "--help"|"-h")
            echo "Usage: $0 {stop|status|restart} [OPTIONS]"
            echo ""
            echo "🛑 Intrusion Detector - Service Management"
            echo ""
            echo "Commands:"
            echo "  stop     - Stop all services (default)"
            echo "  status   - Show current status of all services"
            echo "  restart  - Stop and restart all services"
            echo ""
            echo "Options:"
            echo "  --docker  - Force Docker mode (if you know you're using Docker)"
            echo "  --local   - Force local development mode (if you know you're using Python)"
            echo "  --help, -h - Show this help message"
            echo ""
            echo "🔧 Service Management:"
            echo "  $0                    # Stop all services (auto-detect mode)"
            echo "  $0 status             # Check what's currently running"
            echo "  $0 restart            # Restart the entire application"
            echo "  $0 --docker stop      # Force Docker shutdown"
            echo "  $0 --local stop       # Force local Python shutdown"
            echo ""
            echo "📊 What Gets Stopped:"
            echo "  - FastAPI server (port 8000)"
            echo "  - Gradio UI (port 7860)"
            echo "  - MLflow server (port 5000)"
            echo "  - All related background processes"
            echo ""
            echo "🌍 Environment Variables:"
            echo "  DOCKER_MODE  Set to 'docker' or 'local' to override auto-detection"
            echo ""
            echo "📚 Related Commands:"
            echo "  ./start.sh            # Start the application"
            echo "  ./status.sh           # Quick status check"
            echo "  ./manage.sh           # Advanced management"
            exit 0
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 