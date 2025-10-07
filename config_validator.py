"""
Helios Configuration Validator
Validates and fixes common configuration issues
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

class ConfigValidator:
    def __init__(self):
        self.issues: List[Dict[str, str]] = []
        self.fixes_applied: List[str] = []
    
    def validate_vscode_config(self, workspace_path: str) -> bool:
        """Validate VS Code workspace configuration"""
        vscode_dir = Path(workspace_path) / ".vscode"
        
        # Check if .vscode directory exists
        if not vscode_dir.exists():
            self.issues.append({
                "type": "missing_directory",
                "message": ".vscode directory not found",
                "severity": "warning",
                "fix": "Create .vscode directory with default configuration"
            })
            return False
        
        # Check settings.json
        settings_file = vscode_dir / "settings.json"
        if not settings_file.exists():
            self.issues.append({
                "type": "missing_file",
                "message": "settings.json not found",
                "severity": "info",
                "fix": "Create default settings.json"
            })
        else:
            self._validate_settings_json(settings_file)
        
        # Check launch.json
        launch_file = vscode_dir / "launch.json"
        if not launch_file.exists():
            self.issues.append({
                "type": "missing_file",
                "message": "launch.json not found",
                "severity": "info",
                "fix": "Create default launch configuration"
            })
        
        return len([issue for issue in self.issues if issue["severity"] == "error"]) == 0
    
    def _validate_settings_json(self, settings_file: Path) -> None:
        """Validate VS Code settings.json content"""
        try:
            with open(settings_file) as f:
                settings = json.load(f)
            
            # Check Helios-specific settings
            helios_settings = {
                "helios.enabled": True,
                "helios.serverUrl": "http://localhost:8000",
                "helios.debugMode": False
            }
            
            for key, default_value in helios_settings.items():
                if key not in settings:
                    self.issues.append({
                        "type": "missing_setting",
                        "message": f"Missing Helios setting: {key}",
                        "severity": "info",
                        "fix": f"Add {key}: {default_value}"
                    })
            
        except json.JSONDecodeError:
            self.issues.append({
                "type": "invalid_json",
                "message": "settings.json contains invalid JSON",
                "severity": "error",
                "fix": "Fix JSON syntax errors"
            })
    
    def validate_python_environment(self, server_path: str) -> bool:
        """Validate Python environment setup"""
        server_dir = Path(server_path)
        
        # Check if server directory exists
        if not server_dir.exists():
            self.issues.append({
                "type": "missing_directory",
                "message": "Server directory not found",
                "severity": "error",
                "fix": "Ensure server directory exists"
            })
            return False
        
        # Check virtual environment
        venv_dir = server_dir / "venv"
        if not venv_dir.exists():
            self.issues.append({
                "type": "missing_venv",
                "message": "Python virtual environment not found",
                "severity": "warning",
                "fix": "Create virtual environment: python -m venv venv"
            })
        
        # Check requirements.txt
        requirements_file = server_dir / "requirements.txt"
        if not requirements_file.exists():
            self.issues.append({
                "type": "missing_file",
                "message": "requirements.txt not found",
                "severity": "error",
                "fix": "Create requirements.txt with necessary dependencies"
            })
        
        # Check if dependencies are installed
        if venv_dir.exists():
            python_path = venv_dir / "bin" / "python"
            if not python_path.exists():
                python_path = venv_dir / "Scripts" / "python.exe"  # Windows
            
            if python_path.exists():
                try:
                    result = subprocess.run([str(python_path), "-c", "import fastapi, ollama"],
                                          capture_output=True, text=True)
                    if result.returncode != 0:
                        self.issues.append({
                            "type": "missing_dependencies",
                            "message": "Required Python packages not installed",
                            "severity": "error",
                            "fix": "Install dependencies: pip install -r requirements.txt"
                        })
                except Exception:
                    self.issues.append({
                        "type": "environment_error",
                        "message": "Could not test Python environment",
                        "severity": "warning",
                        "fix": "Check virtual environment setup"
                    })
        
        return len([issue for issue in self.issues if issue["severity"] == "error"]) == 0
    
    def validate_ollama_installation(self) -> bool:
        """Validate Ollama installation and model availability"""
        # Check if Ollama is installed
        try:
            result = subprocess.run(["ollama", "version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.issues.append({
                    "type": "missing_ollama",
                    "message": "Ollama is not installed or not in PATH",
                    "severity": "error",
                    "fix": "Install Ollama from https://ollama.com"
                })
                return False
        except FileNotFoundError:
            self.issues.append({
                "type": "missing_ollama",
                "message": "Ollama command not found",
                "severity": "error",
                "fix": "Install Ollama and ensure it's in PATH"
            })
            return False
        
        # Check available models
        try:
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True)
            if "codellama" not in result.stdout:
                self.issues.append({
                    "type": "missing_model",
                    "message": "No CodeLlama models found",
                    "severity": "warning",
                    "fix": "Install a model: ollama pull codellama:7b-code"
                })
        except Exception:
            self.issues.append({
                "type": "ollama_error",
                "message": "Could not check available models",
                "severity": "warning",
                "fix": "Ensure Ollama service is running"
            })
        
        return True
    
    def validate_extension_setup(self, extension_path: str) -> bool:
        """Validate VS Code extension setup"""
        extension_dir = Path(extension_path)
        
        # Check package.json
        package_json = extension_dir / "package.json"
        if not package_json.exists():
            self.issues.append({
                "type": "missing_file",
                "message": "Extension package.json not found",
                "severity": "error",
                "fix": "Ensure you're in the correct extension directory"
            })
            return False
        
        # Check node_modules
        node_modules = extension_dir / "node_modules"
        if not node_modules.exists():
            self.issues.append({
                "type": "missing_dependencies",
                "message": "Node.js dependencies not installed",
                "severity": "error",
                "fix": "Run: npm install"
            })
        
        # Check compiled output
        out_dir = extension_dir / "out"
        if not out_dir.exists():
            self.issues.append({
                "type": "not_compiled",
                "message": "Extension not compiled",
                "severity": "warning",
                "fix": "Run: npm run compile"
            })
        
        return len([issue for issue in self.issues if issue["severity"] == "error"]) == 0
    
    def run_full_validation(self, workspace_path: str) -> Dict[str, Any]:
        """Run complete validation suite"""
        self.issues = []
        self.fixes_applied = []
        
        results = {
            "vscode_config": self.validate_vscode_config(workspace_path),
            "python_environment": self.validate_python_environment(
                os.path.join(workspace_path, "server")
            ),
            "ollama_installation": self.validate_ollama_installation(),
            "extension_setup": self.validate_extension_setup(
                os.path.join(workspace_path, "extension")
            )
        }
        
        results["overall_status"] = all(results.values())
        results["issues"] = self.issues
        results["issues_by_severity"] = {
            "error": [i for i in self.issues if i["severity"] == "error"],
            "warning": [i for i in self.issues if i["severity"] == "warning"],
            "info": [i for i in self.issues if i["severity"] == "info"]
        }
        
        return results
    
    def apply_automatic_fixes(self, workspace_path: str) -> List[str]:
        """Apply automatic fixes for common issues"""
        fixes_applied = []
        
        # Create .vscode directory if missing
        vscode_dir = Path(workspace_path) / ".vscode"
        if not vscode_dir.exists():
            vscode_dir.mkdir(parents=True)
            fixes_applied.append("Created .vscode directory")
        
        # Create default settings.json if missing
        settings_file = vscode_dir / "settings.json"
        if not settings_file.exists():
            default_settings = {
                "helios.enabled": True,
                "helios.serverUrl": "http://localhost:8000",
                "helios.debugMode": False,
                "python.defaultInterpreterPath": "./server/venv/bin/python"
            }
            with open(settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
            fixes_applied.append("Created default settings.json")
        
        return fixes_applied
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report"""
        report = "Helios Configuration Validation Report\n"
        report += "=" * 50 + "\n\n"
        
        # Overall status
        status_icon = "✅" if results["overall_status"] else "❌"
        report += f"Overall Status: {status_icon} {'PASS' if results['overall_status'] else 'FAIL'}\n\n"
        
        # Component status
        report += "Component Status:\n"
        for component, status in results.items():
            if component not in ["overall_status", "issues", "issues_by_severity"]:
                icon = "✅" if status else "❌"
                report += f"  {icon} {component.replace('_', ' ').title()}: {'OK' if status else 'Issues Found'}\n"
        
        # Issues by severity
        report += "\nIssues Found:\n"
        for severity in ["error", "warning", "info"]:
            issues = results["issues_by_severity"][severity]
            if issues:
                report += f"\n{severity.upper()}S ({len(issues)}):\n"
                for issue in issues:
                    report += f"  • {issue['message']}\n"
                    report += f"    Fix: {issue['fix']}\n"
        
        if not any(results["issues_by_severity"].values()):
            report += "  No issues found! 🎉\n"
        
        return report

def main():
    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <workspace_path>")
        print("Example: python config_validator.py /path/to/helios")
        return
    
    workspace_path = sys.argv[1]
    
    if not os.path.exists(workspace_path):
        print(f"Error: Workspace path '{workspace_path}' does not exist")
        return
    
    validator = ConfigValidator()
    
    print("🔍 Running Helios configuration validation...")
    results = validator.run_full_validation(workspace_path)
    
    # Apply automatic fixes if requested
    if "--fix" in sys.argv:
        print("\n🔧 Applying automatic fixes...")
        fixes = validator.apply_automatic_fixes(workspace_path)
        for fix in fixes:
            print(f"  ✅ {fix}")
    
    # Generate and display report
    report = validator.generate_report(results)
    print("\n" + report)
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] else 1)

if __name__ == "__main__":
    main()