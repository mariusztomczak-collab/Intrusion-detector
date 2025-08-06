#!/bin/bash

# Intrusion-detector Application Shutdown Script
# This script safely stops all services: MLflow, FastAPI, and Gradio UI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
        print_status "Stopping $service_name (PID: $pid)..."
        
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
    
    print_status "Stopping $service_name processes..."
    
    # Find and kill processes by pattern
    local pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        echo "$pids" | while read -r pid; do
            kill_process_gracefully "$pid" "$service_name"
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

# Main shutdown function
stop_services() {
    print_status "Shutting down Intrusion-detector Application..."
    print_status "Project directory: $PROJECT_DIR"
    
    # Stop services using PID files first (graceful shutdown)
    print_status "Attempting graceful shutdown using PID files..."
    
    # Stop MLflow
    if [ -f "$LOG_DIR/mlflow.pid" ]; then
        MLFLOW_PID=$(cat "$LOG_DIR/mlflow.pid")
        kill_process_gracefully "$MLFLOW_PID" "MLflow"
        rm -f "$LOG_DIR/mlflow.pid"
    fi
    
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
    
    # Force stop any remaining processes by pattern
    print_status "Force stopping any remaining processes..."
    
    # Stop MLflow processes
    stop_service_by_pattern "mlflow server" "MLflow"
    stop_service_by_pattern "gunicorn.*mlflow" "MLflow Worker"
    
    # Stop FastAPI processes
    stop_service_by_pattern "uvicorn.*src.api.main" "FastAPI"
    
    # Stop Gradio processes
    stop_service_by_pattern "run_unified_app.py" "Gradio UI"
    stop_service_by_pattern "gradio" "Gradio"
    
    # Wait a moment for processes to fully terminate
    sleep 3
    
    # Check if ports are free
    print_status "Checking if ports are free..."
    
    if check_port 5000; then
        print_warning "Port 5000 (MLflow) is still in use"
    else
        print_success "Port 5000 (MLflow) is free"
    fi
    
    if check_port 8000; then
        print_warning "Port 8000 (FastAPI) is still in use"
    else
        print_success "Port 8000 (FastAPI) is free"
    fi
    
    if check_port 7860; then
        print_warning "Port 7860 (Gradio) is still in use"
    else
        print_success "Port 7860 (Gradio) is free"
    fi
    
    # Final cleanup
    print_status "Performing final cleanup..."
    
    # Remove PID files if they still exist
    rm -f "$LOG_DIR/mlflow.pid"
    rm -f "$LOG_DIR/fastapi.pid"
    rm -f "$LOG_DIR/gradio.pid"
    
    # Show final status
    echo ""
    print_success "=== APPLICATION SHUTDOWN COMPLETE ==="
    echo ""
    print_status "Final status:"
    
    # Check for any remaining processes
    local remaining_processes=$(pgrep -f "(mlflow|uvicorn|gradio|run_unified)" 2>/dev/null || true)
    
    if [ -n "$remaining_processes" ]; then
        print_warning "Some processes may still be running:"
        echo "$remaining_processes" | while read -r pid; do
            local cmd=$(ps -p "$pid" -o command= 2>/dev/null || echo "Unknown")
            echo "  PID $pid: $cmd"
        done
    else
        print_success "All application processes have been stopped"
    fi
    
    echo ""
    print_success "Application shutdown complete! 🛑"
}

# Function to show current status
show_status() {
    print_status "Current application status:"
    echo ""
    
    # Check PID files
    if [ -f "$LOG_DIR/mlflow.pid" ]; then
        MLFLOW_PID=$(cat "$LOG_DIR/mlflow.pid")
        if is_process_running "$MLFLOW_PID"; then
            print_success "MLflow: Running (PID: $MLFLOW_PID)"
        else
            print_warning "MLflow: PID file exists but process not running"
        fi
    else
        print_warning "MLflow: Not running (no PID file)"
    fi
    
    if [ -f "$LOG_DIR/fastapi.pid" ]; then
        FASTAPI_PID=$(cat "$LOG_DIR/fastapi.pid")
        if is_process_running "$FASTAPI_PID"; then
            print_success "FastAPI: Running (PID: $FASTAPI_PID)"
        else
            print_warning "FastAPI: PID file exists but process not running"
        fi
    else
        print_warning "FastAPI: Not running (no PID file)"
    fi
    
    if [ -f "$LOG_DIR/gradio.pid" ]; then
        GRADIO_PID=$(cat "$LOG_DIR/gradio.pid")
        if is_process_running "$GRADIO_PID"; then
            print_success "Gradio UI: Running (PID: $GRADIO_PID)"
        else
            print_warning "Gradio UI: PID file exists but process not running"
        fi
    else
        print_warning "Gradio UI: Not running (no PID file)"
    fi
    
    echo ""
    print_status "Port status:"
    if check_port 5000; then
        print_warning "Port 5000 (MLflow): In use"
    else
        print_success "Port 5000 (MLflow): Free"
    fi
    
    if check_port 8000; then
        print_warning "Port 8000 (FastAPI): In use"
    else
        print_success "Port 8000 (FastAPI): Free"
    fi
    
    if check_port 7860; then
        print_warning "Port 7860 (Gradio): In use"
    else
        print_success "Port 7860 (Gradio): Free"
    fi
}

# Parse command line arguments
case "${1:-stop}" in
    "stop")
        stop_services
        ;;
    "status")
        show_status
        ;;
    "restart")
        print_status "Restarting application..."
        stop_services
        sleep 2
        print_status "Starting application..."
        ./start_app.sh
        ;;
    *)
        echo "Usage: $0 {stop|status|restart}"
        echo "  stop    - Stop all services (default)"
        echo "  status  - Show current status"
        echo "  restart - Stop and restart all services"
        exit 1
        ;;
esac 