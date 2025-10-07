#!/bin/bash

# Helios Installation Script
# This script sets up the complete Helios development environment

set -e

echo "🌟 Helios - Local CodeLlama Assistant Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "extension" ] || [ ! -d "server" ]; then
    print_error "Please run this script from the Helios root directory"
    exit 1
fi

print_status "Found Helios project structure"

# Check Node.js installation
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    print_error "Node.js version 16+ is required (found: $NODE_VERSION)"
    exit 1
fi

print_status "Node.js $(node --version) is installed"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_error "Python 3.8+ is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_status "Python $PYTHON_VERSION is installed"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed"
    exit 1
fi

print_status "npm $(npm --version) is installed"

# Install extension dependencies
echo ""
echo "📦 Installing VS Code extension dependencies..."
cd extension

if [ -f "package-lock.json" ]; then
    npm ci
else
    npm install
fi

print_status "Extension dependencies installed"

# Install VSCE if not present
if ! command -v vsce &> /dev/null; then
    echo "Installing VS Code Extension CLI (vsce)..."
    npm install -g vsce
fi

# Build the extension
echo "🔨 Building extension..."
npm run compile
print_status "Extension compiled successfully"

# Go back to root and setup server
cd ..
echo ""
echo "🐍 Setting up Python server..."
cd server

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Python dependencies installed"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama is not installed"
    echo "Would you like to install Ollama now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        print_status "Ollama installed"
    else
        print_warning "You'll need to install Ollama manually later"
        echo "Visit: https://ollama.com"
    fi
else
    print_status "Ollama is already installed"
fi

# Go back to root
cd ..

# Create workspace settings for VS Code
mkdir -p .vscode
cat > .vscode/settings.json << EOF
{
    "typescript.preferences.includePackageJsonAutoImports": "on",
    "editor.codeActionsOnSave": {
        "source.fixAll.eslint": true
    },
    "eslint.workingDirectories": ["extension"],
    "python.defaultInterpreterPath": "./server/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "helios.enabled": true,
    "helios.serverUrl": "http://localhost:8000",
    "helios.debugMode": true
}
EOF

print_status "VS Code workspace settings created"

# Create launch configuration for debugging
cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Launch Extension",
            "type": "extensionHost",
            "request": "launch",
            "runtimeExecutable": "\${execPath}",
            "args": ["--extensionDevelopmentPath=\${workspaceFolder}/extension"],
            "outFiles": ["\${workspaceFolder}/extension/out/**/*.js"]
        },
        {
            "name": "Debug Server",
            "type": "python",
            "request": "launch",
            "program": "\${workspaceFolder}/server/main.py",
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}/server",
            "python": "\${workspaceFolder}/server/venv/bin/python"
        }
    ]
}
EOF

print_status "VS Code launch configuration created"

# Create tasks for building and running
cat > .vscode/tasks.json << EOF
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build Extension",
            "type": "shell",
            "command": "npm",
            "args": ["run", "compile"],
            "options": {
                "cwd": "\${workspaceFolder}/extension"
            },
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": "\$tsc"
        },
        {
            "label": "Watch Extension",
            "type": "shell",
            "command": "npm",
            "args": ["run", "watch"],
            "options": {
                "cwd": "\${workspaceFolder}/extension"
            },
            "isBackground": true,
            "problemMatcher": "\$tsc-watch"
        },
        {
            "label": "Start Server",
            "type": "shell",
            "command": "\${workspaceFolder}/server/venv/bin/python",
            "args": ["main.py"],
            "options": {
                "cwd": "\${workspaceFolder}/server"
            },
            "group": "build",
            "isBackground": true,
            "problemMatcher": []
        },
        {
            "label": "Package Extension",
            "type": "shell",
            "command": "vsce",
            "args": ["package"],
            "options": {
                "cwd": "\${workspaceFolder}/extension"
            },
            "group": "build"
        }
    ]
}
EOF

print_status "VS Code tasks configuration created"

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Open this project in VS Code"
echo "2. Install CodeLlama model: ollama pull codellama:7b-code"
echo "3. Start the server: cd server && source venv/bin/activate && python main.py"
echo "4. Press F5 in VS Code to launch the extension in debug mode"
echo ""
echo "For more information, see:"
echo "- Extension development: extension/DEVELOPMENT.md"
echo "- Server API documentation: server/API.md"
echo "- Main README: README.md"