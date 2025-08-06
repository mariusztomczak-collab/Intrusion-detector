#!/bin/bash

# Intrusion-detector Application Startup Script
# This script starts all services: MLflow, FastAPI, and Gradio UI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to kill existing processes
kill_existing_processes() {
    print_status "Checking for existing processes..."
    
    # Kill MLflow processes
    pkill -f "mlflow server" 2>/dev/null || true
    pkill -f "gunicorn.*mlflow" 2>/dev/null || true
    
    # Kill FastAPI processes
    pkill -f "uvicorn.*src.api.main" 2>/dev/null || true
    
    # Kill Gradio processes
    pkill -f "run_unified_app.py" 2>/dev/null || true
    pkill -f "gradio" 2>/dev/null || true
    
    sleep 2
}

# Main startup function
start_services() {
    print_status "Starting Intrusion-detector Application..."
    print_status "Project directory: $PROJECT_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        print_error "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    # Check if required packages are installed
    print_status "Checking required packages..."
    if ! python -c "import mlflow" 2>/dev/null; then
        print_error "MLflow not found. Installing requirements..."
        pip install -r requirements.txt
    fi
    
    if ! python -c "import uvicorn" 2>/dev/null; then
        print_error "Uvicorn not found. Installing requirements..."
        pip install -r requirements.txt
    fi
    
    if ! python -c "import gradio" 2>/dev/null; then
        print_error "Gradio not found. Installing requirements..."
        pip install -r requirements.txt
    fi
    
    # Kill existing processes
    kill_existing_processes
    
    # Start MLflow
    print_status "Starting MLflow server..."
    if check_port 5000; then
        print_warning "Port 5000 is already in use. Skipping MLflow startup."
    else
        nohup mlflow server \
            --host 0.0.0.0 \
            --port 5000 \
            --backend-store-uri sqlite:///mlflow.db \
            --default-artifact-root mlruns \
            > "$LOG_DIR/mlflow.log" 2>&1 &
        MLFLOW_PID=$!
        echo $MLFLOW_PID > "$LOG_DIR/mlflow.pid"
        print_success "MLflow started with PID: $MLFLOW_PID"
    fi
    
    # Wait for MLflow
    sleep 3
    if ! wait_for_service "http://localhost:5000" "MLflow"; then
        print_warning "MLflow may not be fully ready, continuing..."
    fi
    
    # Start FastAPI
    print_status "Starting FastAPI server..."
    if check_port 8000; then
        print_warning "Port 8000 is already in use. Skipping FastAPI startup."
    else
        nohup python -m uvicorn src.api.main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --reload \
            > "$LOG_DIR/fastapi.log" 2>&1 &
        FASTAPI_PID=$!
        echo $FASTAPI_PID > "$LOG_DIR/fastapi.pid"
        print_success "FastAPI started with PID: $FASTAPI_PID"
    fi
    
    # Wait for FastAPI
    sleep 5
    if ! wait_for_service "http://localhost:8000/health" "FastAPI"; then
        print_warning "FastAPI may not be fully ready, continuing..."
    fi
    
    # Start Gradio UI
    print_status "Starting Gradio UI..."
    if check_port 7860; then
        print_warning "Port 7860 is already in use. Skipping Gradio startup."
    else
        nohup python run_unified_app.py \
            > "$LOG_DIR/gradio.log" 2>&1 &
        GRADIO_PID=$!
        echo $GRADIO_PID > "$LOG_DIR/gradio.pid"
        print_success "Gradio UI started with PID: $GRADIO_PID"
    fi
    
    # Wait for Gradio
    sleep 5
    if ! wait_for_service "http://localhost:7860" "Gradio UI"; then
        print_warning "Gradio UI may not be fully ready, continuing..."
    fi
    
    # Final status check
    print_status "Performing final status check..."
    sleep 2
    
    echo ""
    print_success "=== APPLICATION STARTUP COMPLETE ==="
    echo ""
    print_status "Service URLs:"
    echo "  🌐 Gradio UI:     http://localhost:7860"
    echo "  🔧 FastAPI:       http://localhost:8000"
    echo "  📊 API Docs:      http://localhost:8000/docs"
    echo "  🧪 MLflow:        http://localhost:5000"
    echo "  ❤️  Health Check:  http://localhost:8000/health"
    echo ""
    print_status "Log files:"
    echo "  📝 MLflow:        $LOG_DIR/mlflow.log"
    echo "  📝 FastAPI:       $LOG_DIR/fastapi.log"
    echo "  📝 Gradio:        $LOG_DIR/gradio.log"
    echo ""
    print_status "PID files:"
    echo "  🔢 MLflow:        $LOG_DIR/mlflow.pid"
    echo "  🔢 FastAPI:       $LOG_DIR/fastapi.pid"
    echo "  🔢 Gradio:        $LOG_DIR/gradio.pid"
    echo ""
    print_success "All services are running! 🎉"
}

# Run the startup function
start_services 