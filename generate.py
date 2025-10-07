#!/usr/bin/env python3
"""
Helios Code Generator

A utility for generating boilerplate code, configuration files, and project scaffolding
for Helios development. Helps maintain consistency and speeds up development.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess


class HeliosCodeGenerator:
    """Main code generator for Helios project scaffolding."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        
    def generate_extension_command(self, command_name: str, title: str, category: str = "Helios") -> None:
        """Generate a new VS Code command for the extension."""
        # Generate command implementation
        command_file = f"""import * as vscode from 'vscode';
import {{ logger }} from './logger';

export async function {self._to_camel_case(command_name)}(): Promise<void> {{
    try {{
        logger.info('Executing command: {command_name}');
        
        // TODO: Implement command logic
        vscode.window.showInformationMessage('{title} executed successfully!');
        
    }} catch (error) {{
        logger.error('Command {command_name} failed:', error);
        vscode.window.showErrorMessage(`{title} failed: ${{error}}`);
    }}
}}
"""
        
        command_path = self.project_root / "extension" / "src" / "commands" / f"{command_name.replace('-', '_')}.ts"
        command_path.parent.mkdir(exist_ok=True)
        
        with open(command_path, 'w') as f:
            f.write(command_file)
        
        print(f"Generated command file: {command_path}")
        
        # Update package.json
        self._add_command_to_package_json(command_name, title, category)
        
    def generate_server_endpoint(self, endpoint_name: str, method: str = "POST") -> None:
        """Generate a new FastAPI endpoint for the server."""
        endpoint_file = f"""from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from .models import BaseResponse
from .auth import get_current_user  # If authentication is needed

logger = logging.getLogger(__name__)
router = APIRouter()


class {self._to_pascal_case(endpoint_name)}Request(BaseModel):
    \"\"\"Request model for {endpoint_name} endpoint.\"\"\"
    # TODO: Add request fields
    data: str


class {self._to_pascal_case(endpoint_name)}Response(BaseResponse):
    \"\"\"Response model for {endpoint_name} endpoint.\"\"\"
    # TODO: Add response fields
    result: str


@router.{method.lower()}("/{endpoint_name.replace('_', '-')}")
async def {endpoint_name}(
    request: {self._to_pascal_case(endpoint_name)}Request,
    # current_user = Depends(get_current_user)  # Uncomment if auth needed
) -> {self._to_pascal_case(endpoint_name)}Response:
    \"\"\"
    {endpoint_name.replace('_', ' ').title()} endpoint.
    
    Args:
        request: The request data
        
    Returns:
        The response data
        
    Raises:
        HTTPException: If the operation fails
    \"\"\"
    try:
        logger.info(f"Processing {endpoint_name} request")
        
        # TODO: Implement endpoint logic
        result = f"Processed: {{request.data}}"
        
        return {self._to_pascal_case(endpoint_name)}Response(
            success=True,
            message="{endpoint_name.replace('_', ' ').title()} completed successfully",
            result=result
        )
        
    except Exception as e:
        logger.error(f"{endpoint_name} endpoint error: {{e}}")
        raise HTTPException(
            status_code=500,
            detail=f"{endpoint_name.replace('_', ' ').title()} failed: {{str(e)}}"
        )
"""
        
        endpoint_path = self.project_root / "server" / "endpoints" / f"{endpoint_name}.py"
        endpoint_path.parent.mkdir(exist_ok=True)
        
        with open(endpoint_path, 'w') as f:
            f.write(endpoint_file)
        
        print(f"Generated endpoint file: {endpoint_path}")
        
        # Update main.py to include the router
        self._add_router_to_main(endpoint_name)
    
    def generate_test_file(self, module_name: str, test_type: str = "unit") -> None:
        """Generate a test file for a module."""
        if test_type == "unit":
            test_file = f"""import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Import the module being tested
# from {module_name} import YourClass


class Test{self._to_pascal_case(module_name)}:
    \"\"\"Unit tests for {module_name} module.\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures before each test method.\"\"\"
        # TODO: Initialize test fixtures
        pass
    
    def teardown_method(self):
        \"\"\"Clean up after each test method.\"\"\"
        # TODO: Clean up test fixtures
        pass
    
    def test_{module_name}_basic_functionality(self):
        \"\"\"Test basic functionality of {module_name}.\"\"\"
        # TODO: Implement test
        assert True  # Replace with actual test
    
    @pytest.mark.asyncio
    async def test_{module_name}_async_functionality(self):
        \"\"\"Test async functionality of {module_name}.\"\"\"
        # TODO: Implement async test
        assert True  # Replace with actual test
    
    def test_{module_name}_error_handling(self):
        \"\"\"Test error handling in {module_name}.\"\"\"
        # TODO: Test error conditions
        with pytest.raises(Exception):
            pass  # Replace with code that should raise exception
    
    @patch('{module_name}.external_dependency')
    def test_{module_name}_with_mocked_dependency(self, mock_dependency):
        \"\"\"Test {module_name} with mocked external dependency.\"\"\"
        # TODO: Configure mock and test
        mock_dependency.return_value = "mocked_result"
        assert True  # Replace with actual test
"""
        elif test_type == "integration":
            test_file = f"""import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient

# Import the application
from main import app


class TestIntegration{self._to_pascal_case(module_name)}:
    \"\"\"Integration tests for {module_name}.\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures before each test method.\"\"\"
        self.client = TestClient(app)
    
    def teardown_method(self):
        \"\"\"Clean up after each test method.\"\"\"
        pass
    
    def test_{module_name}_endpoint_success(self):
        \"\"\"Test successful API call to {module_name} endpoint.\"\"\"
        response = self.client.post(
            f"/{module_name.replace('_', '-')}",
            json={{"data": "test_input"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_{module_name}_endpoint_error_handling(self):
        \"\"\"Test error handling in {module_name} endpoint.\"\"\"
        response = self.client.post(
            f"/{module_name.replace('_', '-')}",
            json={{"invalid": "data"}}
        )
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_{module_name}_with_async_client(self):
        \"\"\"Test {module_name} with async HTTP client.\"\"\"
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/{module_name.replace('_', '-')}",
                json={{"data": "async_test"}}
            )
            assert response.status_code == 200
"""
        
        test_dir = "tests/unit" if test_type == "unit" else "tests/integration"
        test_path = self.project_root / test_dir / f"test_{module_name}.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_path, 'w') as f:
            f.write(test_file)
        
        print(f"Generated {test_type} test file: {test_path}")
    
    def generate_config_schema(self, config_name: str) -> None:
        """Generate a configuration schema file."""
        schema_file = f"""{{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "{config_name.replace('_', ' ').title()} Configuration",
  "description": "Configuration schema for {config_name}",
  "type": "object",
  "properties": {{
    "enabled": {{
      "type": "boolean",
      "description": "Enable/disable {config_name}",
      "default": true
    }},
    "settings": {{
      "type": "object",
      "description": "{config_name.replace('_', ' ').title()} specific settings",
      "properties": {{
        "example_setting": {{
          "type": "string",
          "description": "Example configuration setting",
          "default": "default_value"
        }}
      }},
      "additionalProperties": false
    }}
  }},
  "required": ["enabled"],
  "additionalProperties": false
}}
"""
        
        schema_path = self.project_root / "schemas" / f"{config_name}_config.json"
        schema_path.parent.mkdir(exist_ok=True)
        
        with open(schema_path, 'w') as f:
            f.write(schema_file)
        
        print(f"Generated config schema: {schema_path}")
    
    def generate_documentation(self, doc_type: str, topic: str) -> None:
        """Generate documentation files."""
        if doc_type == "api":
            doc_content = f"""# {topic.replace('_', ' ').title()} API Documentation

## Overview

This document describes the {topic} API endpoints and their usage.

## Authentication

<!-- Describe authentication requirements -->

## Endpoints

### GET /{topic}

Retrieve {topic} information.

**Parameters:**
- `id` (optional): Specific {topic} ID

**Response:**
```json
{{
  "success": true,
  "data": {{
    "id": "string",
    "name": "string"
  }}
}}
```

### POST /{topic}

Create new {topic}.

**Request Body:**
```json
{{
  "name": "string",
  "description": "string"
}}
```

**Response:**
```json
{{
  "success": true,
  "message": "{topic.replace('_', ' ').title()} created successfully",
  "data": {{
    "id": "string",
    "name": "string"
  }}
}}
```

## Error Responses

All endpoints may return the following error responses:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Examples

<!-- Add usage examples -->
"""
        elif doc_type == "user":
            doc_content = f"""# {topic.replace('_', ' ').title()} User Guide

## Introduction

This guide explains how to use the {topic} feature in Helios.

## Getting Started

### Prerequisites

- Helios installed and configured
- Access to the feature

### Basic Usage

1. **Step 1**: Description of first step
2. **Step 2**: Description of second step
3. **Step 3**: Description of third step

## Advanced Features

### Feature 1

Detailed explanation of advanced feature.

### Feature 2

Another advanced feature explanation.

## Troubleshooting

### Common Issues

**Issue**: Problem description
**Solution**: How to resolve the issue

**Issue**: Another problem
**Solution**: Another solution

## FAQ

**Q**: Common question?
**A**: Answer to the question.

## See Also

- [Related Documentation](link)
- [API Reference](link)
"""
        
        doc_path = self.project_root / "docs" / f"{topic}_{doc_type}.md"
        doc_path.parent.mkdir(exist_ok=True)
        
        with open(doc_path, 'w') as f:
            f.write(doc_content)
        
        print(f"Generated {doc_type} documentation: {doc_path}")
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in snake_str.split('_'))
    
    def _add_command_to_package_json(self, command_name: str, title: str, category: str) -> None:
        """Add command to package.json contributes section."""
        package_json_path = self.project_root / "extension" / "package.json"
        
        if not package_json_path.exists():
            print(f"Warning: {package_json_path} not found")
            return
        
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        # Add to contributes.commands
        if "contributes" not in package_data:
            package_data["contributes"] = {}
        if "commands" not in package_data["contributes"]:
            package_data["contributes"]["commands"] = []
        
        new_command = {
            "command": f"helios.{command_name}",
            "title": title,
            "category": category
        }
        
        package_data["contributes"]["commands"].append(new_command)
        
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        print(f"Added command to package.json: helios.{command_name}")
    
    def _add_router_to_main(self, endpoint_name: str) -> None:
        """Add router import and include to main.py."""
        main_py_path = self.project_root / "server" / "main.py"
        
        if not main_py_path.exists():
            print(f"Warning: {main_py_path} not found")
            return
        
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Add import
        import_line = f"from .endpoints.{endpoint_name} import router as {endpoint_name}_router"
        if import_line not in content:
            # Find a good place to add the import
            lines = content.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_index = i + 1
            
            lines.insert(insert_index, import_line)
            content = '\n'.join(lines)
        
        # Add router include
        include_line = f'app.include_router({endpoint_name}_router, prefix="/api", tags=["{endpoint_name}"])'
        if include_line not in content:
            # Find app creation and add router after it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'app = FastAPI(' in line:
                    # Find the end of app creation
                    j = i
                    while j < len(lines) and not lines[j].strip().endswith(')'):
                        j += 1
                    lines.insert(j + 1, '')
                    lines.insert(j + 2, include_line)
                    break
            
            content = '\n'.join(lines)
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print(f"Added router to main.py: {endpoint_name}_router")


def main():
    """Main entry point for code generator."""
    parser = argparse.ArgumentParser(description="Helios Code Generator")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Extension command generator
    cmd_parser = subparsers.add_parser("command", help="Generate VS Code extension command")
    cmd_parser.add_argument("name", help="Command name (e.g., 'toggle-completion')")
    cmd_parser.add_argument("--title", required=True, help="Command title")
    cmd_parser.add_argument("--category", default="Helios", help="Command category")
    
    # Server endpoint generator
    endpoint_parser = subparsers.add_parser("endpoint", help="Generate FastAPI endpoint")
    endpoint_parser.add_argument("name", help="Endpoint name (e.g., 'analyze_code')")
    endpoint_parser.add_argument("--method", default="POST", choices=["GET", "POST", "PUT", "DELETE"])
    
    # Test generator
    test_parser = subparsers.add_parser("test", help="Generate test file")
    test_parser.add_argument("module", help="Module name to test")
    test_parser.add_argument("--type", default="unit", choices=["unit", "integration"])
    
    # Config schema generator
    config_parser = subparsers.add_parser("config", help="Generate configuration schema")
    config_parser.add_argument("name", help="Configuration name")
    
    # Documentation generator
    doc_parser = subparsers.add_parser("docs", help="Generate documentation")
    doc_parser.add_argument("topic", help="Documentation topic")
    doc_parser.add_argument("--type", default="user", choices=["api", "user"])
    
    # Project root option
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = HeliosCodeGenerator(args.project_root)
    
    try:
        if args.command == "command":
            generator.generate_extension_command(args.name, args.title, args.category)
        elif args.command == "endpoint":
            generator.generate_server_endpoint(args.name, args.method)
        elif args.command == "test":
            generator.generate_test_file(args.module, args.type)
        elif args.command == "config":
            generator.generate_config_schema(args.name)
        elif args.command == "docs":
            generator.generate_documentation(args.type, args.topic)
        
        print(f"\n✓ Successfully generated {args.command}")
        
    except Exception as e:
        print(f"Error generating {args.command}: {e}")


if __name__ == "__main__":
    main()