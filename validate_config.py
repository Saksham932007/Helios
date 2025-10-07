#!/usr/bin/env python3
"""
Helios Configuration Validator

Validates Helios configuration files, VS Code settings, and server configuration.
Provides detailed feedback on configuration issues and suggestions for optimization.
"""

import json
import os
import sys
import argparse
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a configuration validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class HeliosConfigValidator:
    """Main configuration validator for Helios."""
    
    def __init__(self):
        self.vscode_schema = self._get_vscode_settings_schema()
        self.server_schema = self._get_server_config_schema()
    
    def _validate_dict_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Simple schema validation without external dependencies."""
        if schema.get("type") == "object" and "properties" in schema:
            for key, value in data.items():
                if key in schema["properties"]:
                    prop_schema = schema["properties"][key]
                    self._validate_value_against_schema(value, prop_schema, key)
    
    def _validate_value_against_schema(self, value: Any, schema: Dict[str, Any], field_name: str) -> None:
        """Validate a single value against its schema."""
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "string" and not isinstance(value, str):
                raise ValueError(f"Field '{field_name}' must be a string")
            elif expected_type == "integer" and not isinstance(value, int):
                raise ValueError(f"Field '{field_name}' must be an integer")
            elif expected_type == "number" and not isinstance(value, (int, float)):
                raise ValueError(f"Field '{field_name}' must be a number")
            elif expected_type == "boolean" and not isinstance(value, bool):
                raise ValueError(f"Field '{field_name}' must be a boolean")
            elif expected_type == "array" and not isinstance(value, list):
                raise ValueError(f"Field '{field_name}' must be an array")
        
        if "minimum" in schema and isinstance(value, (int, float)):
            if value < schema["minimum"]:
                raise ValueError(f"Field '{field_name}' must be >= {schema['minimum']}")
        
        if "maximum" in schema and isinstance(value, (int, float)):
            if value > schema["maximum"]:
                raise ValueError(f"Field '{field_name}' must be <= {schema['maximum']}")
        
        if "enum" in schema and value not in schema["enum"]:
            raise ValueError(f"Field '{field_name}' must be one of {schema['enum']}")
        
        if "pattern" in schema and isinstance(value, str):
            import re
            if not re.match(schema["pattern"], value):
                raise ValueError(f"Field '{field_name}' does not match required pattern")

    def _get_vscode_settings_schema(self) -> Dict[str, Any]:
        """Get JSON schema for VS Code settings validation."""
        return {
            "type": "object",
            "properties": {
                "helios.enabled": {
                    "type": "boolean",
                    "description": "Enable/disable Helios extension"
                },
                "helios.serverUrl": {
                    "type": "string",
                    "pattern": "^https?://.*",
                    "description": "Helios server URL"
                },
                "helios.autoComplete": {
                    "type": "boolean",
                    "description": "Enable automatic code completion"
                },
                "helios.maxCompletionLength": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 1000,
                    "description": "Maximum completion length in characters"
                },
                "helios.completionDelay": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 5000,
                    "description": "Delay before showing completion in milliseconds"
                },
                "helios.temperature": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "description": "Model temperature for completion"
                },
                "helios.enableMetrics": {
                    "type": "boolean",
                    "description": "Enable metrics collection"
                },
                "helios.logLevel": {
                    "type": "string",
                    "enum": ["debug", "info", "warn", "error"],
                    "description": "Logging level"
                },
                "helios.excludePatterns": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "File patterns to exclude from completion"
                },
                "helios.includedLanguages": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Programming languages to enable completion for"
                }
            },
            "additionalProperties": True
        }
    
    def _get_server_config_schema(self) -> Dict[str, Any]:
        """Get JSON schema for server configuration validation."""
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Server host address"
                },
                "port": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 65535,
                    "description": "Server port number"
                },
                "model": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Model name"
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 2.0
                        },
                        "max_tokens": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4096
                        },
                        "context_length": {
                            "type": "integer",
                            "minimum": 512,
                            "maximum": 32768
                        }
                    },
                    "required": ["name"]
                },
                "ollama": {
                    "type": "object",
                    "properties": {
                        "base_url": {
                            "type": "string",
                            "pattern": "^https?://.*"
                        },
                        "timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300
                        }
                    }
                },
                "logging": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]
                        },
                        "file": {
                            "type": "string"
                        }
                    }
                },
                "metrics": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        },
                        "port": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 65535
                        }
                    }
                }
            },
            "required": ["host", "port", "model"]
        }
    
    def validate_vscode_settings(self, settings: Dict[str, Any]) -> ValidationResult:
        """Validate VS Code settings for Helios."""
        errors = []
        warnings = []
        suggestions = []
        
        # Extract Helios-specific settings
        helios_settings = {k: v for k, v in settings.items() if k.startswith('helios.')}
        
        try:
            # Basic validation without jsonschema
            self._validate_dict_against_schema(helios_settings, self.vscode_schema)
        except ValueError as e:
            errors.append(f"Schema validation error: {e.message}")
        
        # Custom validation rules
        if 'helios.serverUrl' in helios_settings:
            url = helios_settings['helios.serverUrl']
            if not url.startswith(('http://', 'https://')):
                errors.append("helios.serverUrl must start with http:// or https://")
            if url.endswith('/'):
                warnings.append("helios.serverUrl should not end with a trailing slash")
        
        if 'helios.temperature' in helios_settings:
            temp = helios_settings['helios.temperature']
            if temp < 0.1:
                warnings.append("Very low temperature may result in repetitive completions")
            elif temp > 1.5:
                warnings.append("High temperature may result in inconsistent completions")
        
        if 'helios.completionDelay' in helios_settings:
            delay = helios_settings['helios.completionDelay']
            if delay > 1000:
                warnings.append("High completion delay may impact user experience")
        
        # Performance suggestions
        if helios_settings.get('helios.enableMetrics', True):
            suggestions.append("Consider disabling metrics in production for better performance")
        
        if not helios_settings.get('helios.excludePatterns'):
            suggestions.append("Consider adding exclude patterns for large files or binary files")
        
        # Check for required settings
        required_settings = ['helios.serverUrl']
        for setting in required_settings:
            if setting not in helios_settings:
                warnings.append(f"Missing recommended setting: {setting}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def validate_server_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate server configuration."""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Basic validation without jsonschema
            self._validate_dict_against_schema(config, self.server_schema)
        except ValueError as e:
            errors.append(f"Schema validation error: {e.message}")
        
        # Custom validation rules
        if 'port' in config:
            port = config['port']
            if port < 1024 and os.getuid() != 0:
                warnings.append("Port < 1024 requires root privileges on most systems")
        
        if 'model' in config:
            model_config = config['model']
            if 'context_length' in model_config and 'max_tokens' in model_config:
                if model_config['max_tokens'] > model_config['context_length']:
                    errors.append("max_tokens cannot exceed context_length")
            
            if model_config.get('temperature', 0.7) > 1.0:
                warnings.append("High model temperature may reduce code quality")
        
        if 'ollama' in config:
            ollama_config = config['ollama']
            if 'timeout' in ollama_config and ollama_config['timeout'] < 30:
                warnings.append("Short Ollama timeout may cause completion failures")
        
        # Performance suggestions
        if config.get('metrics', {}).get('enabled', False):
            suggestions.append("Metrics collection may impact performance in high-load scenarios")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def validate_extension_manifest(self, manifest: Dict[str, Any]) -> ValidationResult:
        """Validate VS Code extension package.json."""
        errors = []
        warnings = []
        suggestions = []
        
        # Check required fields
        required_fields = ['name', 'version', 'engines', 'main', 'contributes']
        for field in required_fields:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")
        
        # Check VS Code engine version
        if 'engines' in manifest and 'vscode' in manifest['engines']:
            engine_version = manifest['engines']['vscode']
            if not engine_version.startswith('^'):
                warnings.append("VS Code engine version should use caret notation (^)")
        
        # Check activation events
        if 'activationEvents' in manifest:
            events = manifest['activationEvents']
            if '*' in events:
                warnings.append("Activation event '*' may impact VS Code startup performance")
        
        # Check contribution points
        if 'contributes' in manifest:
            contributes = manifest['contributes']
            
            if 'commands' in contributes:
                for cmd in contributes['commands']:
                    if 'title' not in cmd or 'command' not in cmd:
                        errors.append("Command missing required 'title' or 'command' field")
            
            if 'configuration' in contributes:
                config = contributes['configuration']
                if 'properties' not in config:
                    warnings.append("Configuration contribution should have properties")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def check_file_permissions(self, file_path: str) -> ValidationResult:
        """Check file permissions and accessibility."""
        errors = []
        warnings = []
        suggestions = []
        
        path = Path(file_path)
        
        if not path.exists():
            errors.append(f"File does not exist: {file_path}")
            return ValidationResult(False, errors, warnings, suggestions)
        
        if not path.is_file():
            errors.append(f"Path is not a file: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            errors.append(f"File is not readable: {file_path}")
        
        # Check for common issues
        if path.suffix == '.json':
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON syntax: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


def print_validation_result(result: ValidationResult, title: str) -> None:
    """Print validation result in a formatted way."""
    print(f"\n{title}")
    print("=" * len(title))
    
    if result.is_valid:
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  ✗ {error}")
    
    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")
    
    if result.suggestions:
        print(f"\nSuggestions ({len(result.suggestions)}):")
        for suggestion in result.suggestions:
            print(f"  💡 {suggestion}")


def main():
    """Main entry point for configuration validator."""
    parser = argparse.ArgumentParser(description="Helios Configuration Validator")
    parser.add_argument("--vscode-settings", help="Path to VS Code settings.json")
    parser.add_argument("--server-config", help="Path to server configuration file")
    parser.add_argument("--extension-manifest", help="Path to extension package.json")
    parser.add_argument("--workspace", help="Validate entire workspace configuration")
    
    args = parser.parse_args()
    
    if not any([args.vscode_settings, args.server_config, args.extension_manifest, args.workspace]):
        parser.print_help()
        sys.exit(1)
    
    validator = HeliosConfigValidator()
    all_valid = True
    
    try:
        if args.vscode_settings:
            # Validate VS Code settings
            result = validator.check_file_permissions(args.vscode_settings)
            if result.is_valid:
                with open(args.vscode_settings, 'r') as f:
                    settings = json.load(f)
                result = validator.validate_vscode_settings(settings)
            print_validation_result(result, "VS Code Settings Validation")
            all_valid = all_valid and result.is_valid
        
        if args.server_config:
            # Validate server configuration
            result = validator.check_file_permissions(args.server_config)
            if result.is_valid:
                with open(args.server_config, 'r') as f:
                    config = json.load(f)
                result = validator.validate_server_config(config)
            print_validation_result(result, "Server Configuration Validation")
            all_valid = all_valid and result.is_valid
        
        if args.extension_manifest:
            # Validate extension manifest
            result = validator.check_file_permissions(args.extension_manifest)
            if result.is_valid:
                with open(args.extension_manifest, 'r') as f:
                    manifest = json.load(f)
                result = validator.validate_extension_manifest(manifest)
            print_validation_result(result, "Extension Manifest Validation")
            all_valid = all_valid and result.is_valid
        
        if args.workspace:
            # Validate entire workspace
            workspace_path = Path(args.workspace)
            
            # Check VS Code settings
            settings_path = workspace_path / ".vscode" / "settings.json"
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                result = validator.validate_vscode_settings(settings)
                print_validation_result(result, "Workspace VS Code Settings")
                all_valid = all_valid and result.is_valid
            
            # Check extension manifest
            manifest_path = workspace_path / "extension" / "package.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                result = validator.validate_extension_manifest(manifest)
                print_validation_result(result, "Extension Package.json")
                all_valid = all_valid and result.is_valid
            
            # Check server config if exists
            server_config_path = workspace_path / "server" / "config.json"
            if server_config_path.exists():
                with open(server_config_path, 'r') as f:
                    config = json.load(f)
                result = validator.validate_server_config(config)
                print_validation_result(result, "Server Configuration")
                all_valid = all_valid and result.is_valid
        
        print(f"\n{'='*50}")
        if all_valid:
            print("✓ All configurations are valid!")
            sys.exit(0)
        else:
            print("✗ Some configurations have issues that need attention")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()