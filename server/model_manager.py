#!/usr/bin/env python3
"""
Helios Model Management Utility
Handles downloading, caching, and switching between different CodeLlama models
"""

import os
import sys
import subprocess
import json
import time
from typing import List, Dict, Optional
from pathlib import Path

class ModelManager:
    def __init__(self):
        self.available_models = {
            "codellama:7b-code": {
                "size": "~4GB",
                "description": "Fastest, good for basic completion",
                "recommended_ram": "8GB"
            },
            "codellama:13b-code": {
                "size": "~8GB", 
                "description": "Balanced speed and quality",
                "recommended_ram": "16GB"
            },
            "codellama:34b-code": {
                "size": "~20GB",
                "description": "Highest quality, slower inference",
                "recommended_ram": "32GB"
            },
            "codellama:7b-instruct": {
                "size": "~4GB",
                "description": "Instruction-tuned for better code understanding",
                "recommended_ram": "8GB"
            }
        }
        
    def list_available_models(self) -> None:
        """List all available CodeLlama models"""
        print("Available CodeLlama Models:")
        print("=" * 50)
        
        for model_name, info in self.available_models.items():
            print(f"\n📦 {model_name}")
            print(f"   Size: {info['size']}")
            print(f"   Description: {info['description']}")
            print(f"   Recommended RAM: {info['recommended_ram']}")
    
    def list_installed_models(self) -> List[str]:
        """Get list of locally installed models"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, check=True)
            
            installed = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    if model_name.startswith('codellama'):
                        installed.append(model_name)
            
            return installed
            
        except subprocess.CalledProcessError:
            print("❌ Error: Could not list models. Is Ollama running?")
            return []
    
    def install_model(self, model_name: str) -> bool:
        """Install a specific model"""
        if model_name not in self.available_models:
            print(f"❌ Error: Unknown model '{model_name}'")
            print("Use 'list' command to see available models")
            return False
        
        print(f"📥 Installing {model_name}...")
        print(f"📊 Size: {self.available_models[model_name]['size']}")
        print("⏳ This may take several minutes depending on your internet connection...")
        
        try:
            # Start the pull process
            process = subprocess.Popen(['ollama', 'pull', model_name],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True, bufsize=1)
            
            # Show progress
            for line in process.stdout:
                print(f"   {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"✅ Successfully installed {model_name}")
                return True
            else:
                print(f"❌ Failed to install {model_name}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {model_name}: {e}")
            return False
    
    def remove_model(self, model_name: str) -> bool:
        """Remove a locally installed model"""
        installed = self.list_installed_models()
        
        if model_name not in installed:
            print(f"❌ Model '{model_name}' is not installed")
            return False
        
        try:
            subprocess.run(['ollama', 'rm', model_name], check=True)
            print(f"✅ Successfully removed {model_name}")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to remove {model_name}")
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a model"""
        try:
            result = subprocess.run(['ollama', 'show', model_name],
                                  capture_output=True, text=True, check=True)
            
            # Parse the output (this is a simplified version)
            info = {
                "name": model_name,
                "status": "installed",
                "details": result.stdout
            }
            
            return info
            
        except subprocess.CalledProcessError:
            return None
    
    def test_model(self, model_name: str) -> bool:
        """Test if a model is working correctly"""
        print(f"🧪 Testing {model_name}...")
        
        test_prompt = "def fibonacci(n):"
        
        try:
            result = subprocess.run(['ollama', 'generate', model_name, test_prompt],
                                  capture_output=True, text=True, 
                                  timeout=30, check=True)
            
            if result.stdout.strip():
                print("✅ Model test successful")
                print(f"   Test completion: {result.stdout.strip()[:50]}...")
                return True
            else:
                print("❌ Model test failed - no output generated")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Model test failed - timeout")
            return False
        except subprocess.CalledProcessError:
            print("❌ Model test failed - execution error")
            return False

def main():
    manager = ModelManager()
    
    if len(sys.argv) < 2:
        print("Helios Model Manager")
        print("Usage: python model_manager.py <command> [args]")
        print("\nCommands:")
        print("  list                 - List available models")
        print("  installed           - List installed models")
        print("  install <model>     - Install a model")
        print("  remove <model>      - Remove a model")
        print("  info <model>        - Show model information")
        print("  test <model>        - Test model functionality")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        manager.list_available_models()
    
    elif command == "installed":
        installed = manager.list_installed_models()
        if installed:
            print("Installed Models:")
            for model in installed:
                print(f"  ✅ {model}")
        else:
            print("No CodeLlama models installed")
    
    elif command == "install":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a model to install")
            return
        
        model_name = sys.argv[2]
        manager.install_model(model_name)
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a model to remove")
            return
        
        model_name = sys.argv[2]
        manager.remove_model(model_name)
    
    elif command == "info":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a model")
            return
        
        model_name = sys.argv[2]
        info = manager.get_model_info(model_name)
        if info:
            print(f"Model Information for {model_name}:")
            print(info['details'])
        else:
            print(f"❌ Model '{model_name}' not found or not installed")
    
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a model to test")
            return
        
        model_name = sys.argv[2]
        manager.test_model(model_name)
    
    else:
        print(f"❌ Error: Unknown command '{command}'")

if __name__ == "__main__":
    main()