#!/bin/bash

# Intrusion-detector Application Management Script
# Simple interface to manage the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                Intrusion-detector Application                ║"
    echo "║                        Management                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

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
    print_header
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start all application services"
    echo "  stop    - Stop all application services"
    echo "  restart - Restart all application services"
    echo "  status  - Show current application status"
    echo "  logs    - Show recent log files"
    echo "  help    - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the application"
    echo "  $0 status   # Check if services are running"
    echo "  $0 stop     # Stop the application"
    echo "  $0 logs     # View recent logs"
    echo ""
}

# Function to show logs
show_logs() {
    print_header
    print_status "Recent application logs:"
    echo ""
    
    LOG_DIR="logs"
    
    if [ ! -d "$LOG_DIR" ]; then
        print_warning "No logs directory found. Application may not have been started yet."
        return
    fi
    
    # Show MLflow logs
    if [ -f "$LOG_DIR/mlflow.log" ]; then
        echo -e "${YELLOW}=== MLflow Logs (last 10 lines) ===${NC}"
        tail -10 "$LOG_DIR/mlflow.log"
        echo ""
    else
        print_warning "No MLflow logs found"
    fi
    
    # Show FastAPI logs
    if [ -f "$LOG_DIR/fastapi.log" ]; then
        echo -e "${YELLOW}=== FastAPI Logs (last 10 lines) ===${NC}"
        tail -10 "$LOG_DIR/fastapi.log"
        echo ""
    else
        print_warning "No FastAPI logs found"
    fi
    
    # Show Gradio logs
    if [ -f "$LOG_DIR/gradio.log" ]; then
        echo -e "${YELLOW}=== Gradio Logs (last 10 lines) ===${NC}"
        tail -10 "$LOG_DIR/gradio.log"
        echo ""
    else
        print_warning "No Gradio logs found"
    fi
}

# Function to show service URLs
show_urls() {
    echo ""
    print_status "Service URLs:"
    echo "  🌐 Gradio UI:     http://localhost:7860"
    echo "  🔧 FastAPI:       http://localhost:8000"
    echo "  📊 API Docs:      http://localhost:8000/docs"
    echo "  🧪 MLflow:        http://localhost:5000"
    echo "  ❤️  Health Check:  http://localhost:8000/health"
    echo ""
}

# Main function
main() {
    case "${1:-help}" in
        "start")
            print_header
            print_status "Starting Intrusion-detector Application..."
            ./start_app.sh
            show_urls
            ;;
        "stop")
            print_header
            print_status "Stopping Intrusion-detector Application..."
            ./stop_app.sh
            ;;
        "restart")
            print_header
            print_status "Restarting Intrusion-detector Application..."
            ./stop_app.sh restart
            show_urls
            ;;
        "status")
            print_header
            ./stop_app.sh status
            show_urls
            ;;
        "logs")
            show_logs
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function
main "$@" 