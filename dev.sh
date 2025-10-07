#!/bin/bash

# Helios Development Scripts
# Collection of useful development utilities

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}$1${NC}"
    echo "=========================="
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check dependencies
check_deps() {
    print_header "Checking Dependencies"
    
    # Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION"
    else
        print_error "Node.js not found"
        return 1
    fi
    
    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "$PYTHON_VERSION"
    else
        print_error "Python3 not found"
        return 1
    fi
    
    # VS Code
    if command -v code &> /dev/null; then
        print_success "VS Code found"
    else
        print_warning "VS Code not found in PATH"
    fi
    
    # Ollama
    if command -v ollama &> /dev/null; then
        print_success "Ollama found"
    else
        print_warning "Ollama not found"
    fi
}

# Build everything
build_all() {
    print_header "Building All Components"
    
    # Build extension
    echo "Building extension..."
    cd "$PROJECT_ROOT/extension"
    npm run compile
    print_success "Extension built"
    
    # Check server dependencies
    echo "Checking server dependencies..."
    cd "$PROJECT_ROOT/server"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python -c "import fastapi, ollama" 2>/dev/null
        print_success "Server dependencies OK"
    else
        print_warning "Server virtual environment not found"
    fi
    
    cd "$PROJECT_ROOT"
}

# Run tests
test_all() {
    print_header "Running Tests"
    
    # Extension tests
    echo "Running extension tests..."
    cd "$PROJECT_ROOT/extension"
    if npm test; then
        print_success "Extension tests passed"
    else
        print_error "Extension tests failed"
    fi
    
    # Server tests
    echo "Running server tests..."
    cd "$PROJECT_ROOT/server"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        if pytest; then
            print_success "Server tests passed"
        else
            print_error "Server tests failed"
        fi
    else
        print_warning "Server virtual environment not found"
    fi
    
    cd "$PROJECT_ROOT"
}

# Start development environment
start_dev() {
    print_header "Starting Development Environment"
    
    # Start server in background
    echo "Starting server..."
    cd "$PROJECT_ROOT/server"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python main.py &
        SERVER_PID=$!
        echo $SERVER_PID > /tmp/helios_server.pid
        print_success "Server started (PID: $SERVER_PID)"
    else
        print_error "Server virtual environment not found"
        return 1
    fi
    
    # Wait for server to start
    sleep 5
    
    # Test server health
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Server is healthy"
    else
        print_warning "Server health check failed"
    fi
    
    # Open VS Code
    echo "Opening VS Code..."
    cd "$PROJECT_ROOT"
    code .
    
    print_success "Development environment started"
    echo "Press Ctrl+C to stop the server"
    
    # Wait for interrupt
    trap "kill $SERVER_PID 2>/dev/null; rm -f /tmp/helios_server.pid; exit" INT
    wait $SERVER_PID
}

# Stop development environment
stop_dev() {
    print_header "Stopping Development Environment"
    
    if [ -f "/tmp/helios_server.pid" ]; then
        SERVER_PID=$(cat /tmp/helios_server.pid)
        if kill $SERVER_PID 2>/dev/null; then
            print_success "Server stopped"
        else
            print_warning "Server was not running"
        fi
        rm -f /tmp/helios_server.pid
    else
        print_warning "No server PID file found"
    fi
}

# Package extension
package_extension() {
    print_header "Packaging Extension"
    
    cd "$PROJECT_ROOT/extension"
    
    # Build first
    npm run compile
    
    # Package
    if vsce package; then
        print_success "Extension packaged successfully"
        ls -la *.vsix
    else
        print_error "Extension packaging failed"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
}

# Clean build artifacts
clean() {
    print_header "Cleaning Build Artifacts"
    
    # Extension
    if [ -d "$PROJECT_ROOT/extension/out" ]; then
        rm -rf "$PROJECT_ROOT/extension/out"
        print_success "Cleaned extension build"
    fi
    
    if [ -f "$PROJECT_ROOT/extension/*.vsix" ]; then
        rm -f "$PROJECT_ROOT/extension/*.vsix"
        print_success "Cleaned extension packages"
    fi
    
    # Server
    if [ -d "$PROJECT_ROOT/server/__pycache__" ]; then
        rm -rf "$PROJECT_ROOT/server/__pycache__"
        print_success "Cleaned Python cache"
    fi
    
    # Logs
    if [ -f "/tmp/helios_server.pid" ]; then
        rm -f /tmp/helios_server.pid
        print_success "Cleaned PID files"
    fi
}

# Show usage
show_usage() {
    echo "Helios Development Helper"
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  check      - Check system dependencies"
    echo "  build      - Build all components"
    echo "  test       - Run all tests"
    echo "  start      - Start development environment"
    echo "  stop       - Stop development environment"
    echo "  package    - Package VS Code extension"
    echo "  clean      - Clean build artifacts"
    echo "  validate   - Validate configuration"
    echo "  help       - Show this help"
}

# Validate configuration
validate_config() {
    print_header "Validating Configuration"
    
    if python3 "$PROJECT_ROOT/config_validator.py" "$PROJECT_ROOT"; then
        print_success "Configuration validation passed"
    else
        print_error "Configuration validation failed"
        echo "Run with --fix to apply automatic fixes"
    fi
}

# Main command dispatcher
main() {
    case "$1" in
        "check")
            check_deps
            ;;
        "build")
            build_all
            ;;
        "test")
            test_all
            ;;
        "start")
            start_dev
            ;;
        "stop")
            stop_dev
            ;;
        "package")
            package_extension
            ;;
        "clean")
            clean
            ;;
        "validate")
            validate_config
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            echo "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"