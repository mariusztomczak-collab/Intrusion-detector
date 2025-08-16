#!/bin/bash

# Intrusion-detector Setup Script
# This script helps end users set up the application after downloading from GitHub

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

# Function to check if file exists
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        print_success "$description found: $file"
        return 0
    else
        print_error "$description missing: $file"
        return 1
    fi
}

# Function to setup environment file
setup_env_file() {
    print_step "Setting up environment configuration..."
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Keeping existing .env file"
            return 0
        fi
    fi
    
    if [ -f ".env.example" ]; then
        print_status "Creating .env from .env.example..."
        cp .env.example .env
        print_success ".env file created from template"
        print_warning "⚠️  IMPORTANT: You must edit .env and add your Supabase credentials!"
        print_status "   Required variables: SUPABASE_URL and SUPABASE_KEY"
    else
        print_error ".env.example not found! Creating basic .env template..."
        cat > .env << EOF
# Supabase Configuration (REQUIRED - Get these from your Supabase project)
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
        print_success "Basic .env template created"
        print_warning "⚠️  IMPORTANT: You must edit .env and add your Supabase credentials!"
    fi
}

# Function to check Python environment
check_python_environment() {
    print_step "Checking Python environment..."
    
    # Check Python version
    local python_version=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    local major_version=$(echo "$python_version" | cut -d. -f1)
    local minor_version=$(echo "$python_version" | cut -d. -f1)
    
    if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]); then
        print_error "Python 3.8+ is required. Current version: $python_version"
        print_status "Please upgrade Python and try again."
        return 1
    fi
    
    print_success "Python version: $python_version (✓ compatible)"
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        print_success "Virtual environment found: venv/"
    else
        print_status "Virtual environment not found. Will be created when you run ./start.sh"
    fi
    
    return 0
}

# Function to check Docker environment
check_docker_environment() {
    print_step "Checking Docker environment..."
    
    if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
        print_success "Docker and Docker Compose found"
        
        # Check if Docker is running
        if docker info >/dev/null 2>&1; then
            print_success "Docker daemon is running"
        else
            print_warning "Docker daemon is not running"
            print_status "Start Docker before running the application"
        fi
    else
        print_warning "Docker not found"
        print_status "You can still run the application in local Python mode"
    fi
}

# Function to check model files
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
        
        if [ -f "scripts/create_sample_model.py" ]; then
            print_status "Creating sample model files..."
            python scripts/create_sample_model.py
            print_success "Sample model files created!"
        else
            print_error "Cannot create sample models. Please ensure model files are present in artifacts/ directory"
            return 1
        fi
    else
        print_success "All model files found!"
    fi
    
    return 0
}

# Function to make scripts executable
make_scripts_executable() {
    print_step "Making scripts executable..."
    
    local scripts=("start.sh" "stop.sh" "status.sh" "manage.sh" "setup.sh")
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            print_success "Made $script executable"
        fi
    done
}

# Function to show next steps
show_next_steps() {
    echo ""
    print_header "🎉 SETUP COMPLETE!"
    echo ""
    print_success "Your Intrusion Detector is ready to use!"
    echo ""
    print_status "📋 Next Steps:"
    echo "  1. Edit .env file with your Supabase credentials"
    echo "  2. Run: ./start.sh"
    echo "  3. Open browser to: http://localhost:7860"
    echo ""
    print_status "🔧 Available Commands:"
    echo "  ./start.sh          # Start the application"
    echo "  ./stop.sh           # Stop the application"
    echo "  ./status.sh         # Check application status"
    echo "  ./manage.sh         # Advanced management"
    echo ""
    print_status "📚 Documentation:"
    echo "  - README.md for detailed information"
    echo "  - .env.example for configuration options"
    echo "  - docker-compose.prod.yml for Docker setup"
    echo ""
    print_warning "⚠️  IMPORTANT: You must add your Supabase credentials to .env before starting!"
}

# Main function
main() {
    print_header "Intrusion Detector Setup"
    print_status "Project directory: $PROJECT_DIR"
    echo ""
    
    # Check command line arguments
    case "${1:-setup}" in
        "setup"|"")
            # Continue with setup
            ;;
        "--help"|"-h")
            echo "Usage: $0 [setup|--help]"
            echo ""
            echo "🚀 Intrusion Detector - Setup Script"
            echo ""
            echo "This script helps you set up the application after downloading from GitHub."
            echo ""
            echo "Commands:"
            echo "  setup    - Run the setup process (default)"
            echo "  --help, -h - Show this help message"
            echo ""
            echo "What this script does:"
            echo "  ✓ Checks Python and Docker environments"
            echo "  ✓ Creates .env file from template"
            echo "  ✓ Verifies required files and models"
            echo "  ✓ Makes scripts executable"
            echo "  ✓ Provides next steps guidance"
            echo ""
            echo "Prerequisites:"
            echo "  - Python 3.8+ installed"
            echo "  - Git repository cloned"
            echo "  - Supabase account and API credentials"
            exit 0
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    
    # Run setup steps
    print_step "Starting setup process..."
    
    # Check required files
    print_step "Checking required files..."
    local all_files_ok=true
    
    check_file "src/api/main.py" "FastAPI application" || all_files_ok=false
    check_file "src/ui/unified_app.py" "Gradio UI application" || all_files_ok=false
    check_file "run_unified_app.py" "UI launcher script" || all_files_ok=false
    check_file "pyproject.toml" "Project configuration" || all_files_ok=false
    
    if [ "$all_files_ok" = false ]; then
        print_error "Some required files are missing. This may not be a complete repository."
        exit 1
    fi
    
    # Setup environment
    setup_env_file
    
    # Check environments
    check_python_environment || exit 1
    check_docker_environment
    
    # Check model files
    check_model_files || exit 1
    
    # Make scripts executable
    make_scripts_executable
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@"
