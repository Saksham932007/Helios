#!/usr/bin/env python3
"""
Helios Server Startup Script
"""
import subprocess
import sys
import os
import logging

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ollama():
    """Install Ollama"""
    print("Ollama not found. Installing...")
    try:
        # Install ollama using the official installer
        subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh'], shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("Failed to install Ollama automatically.")
        print("Please install Ollama manually from https://ollama.com")
        return False

def pull_model(model_name="codellama:7b-code"):
    """Pull the CodeLlama model"""
    print(f"Pulling model {model_name}...")
    try:
        subprocess.run(['ollama', 'pull', model_name], check=True)
        print(f"Model {model_name} pulled successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to pull model {model_name}")
        return False

def start_server():
    """Start the Helios server"""
    print("Starting Helios inference server...")
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to start server")
        return False
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return True

def main():
    """Main setup and startup function"""
    print("🌟 Helios - Local CodeLlama Assistant Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: Please run this script from the server directory")
        sys.exit(1)
    
    # Check Ollama installation
    if not check_ollama_installed():
        if not install_ollama():
            sys.exit(1)
    
    print("✓ Ollama is installed")
    
    # Pull model if needed
    model_name = "codellama:7b-code"
    print(f"Checking for model {model_name}...")
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if model_name not in result.stdout:
            if not pull_model(model_name):
                print("Warning: Failed to pull model. Server may not work properly.")
        else:
            print(f"✓ Model {model_name} is available")
    except subprocess.CalledProcessError:
        print("Warning: Could not check model availability")
    
    # Start the server
    print("\n🚀 Starting server...")
    start_server()

if __name__ == "__main__":
    main()