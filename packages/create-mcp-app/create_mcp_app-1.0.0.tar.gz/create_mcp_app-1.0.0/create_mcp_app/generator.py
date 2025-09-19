#!/usr/bin/env python3
"""
Project generator for MCP server projects
"""

import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any

class ProjectGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def create_project(self, project_name: str, project_info: Dict[str, Any]):
        """Create a new MCP project from template"""
        project_path = Path(project_name)
        project_path.mkdir(exist_ok=True)
        
        template_name = project_info['template']
        
        # Copy and render template files
        self._copy_template(template_name, project_path, project_info)
        
        # Create package directory
        package_name = project_info['package_name']
        package_dir = project_path / package_name
        package_dir.mkdir(exist_ok=True)
        
        # Generate package files
        self._generate_package_files(package_dir, project_info)
        
        # Generate additional files based on options
        if project_info.get('include_tests'):
            self._generate_test_files(project_path, project_info)
        
        if project_info.get('include_github_actions'):
            self._generate_github_actions(project_path, project_info)
    
    def _copy_template(self, template_name: str, dest_path: Path, context: Dict[str, Any]):
        """Copy template files to destination"""
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise ValueError(f"Template '{template_name}' not found")
        
        for root, dirs, files in os.walk(template_path):
            rel_root = Path(root).relative_to(template_path)
            dest_root = dest_path / rel_root
            dest_root.mkdir(exist_ok=True)
            
            for file in files:
                src_file = Path(root) / file
                dest_file = dest_root / file
                
                # Render template files
                if file.endswith('.j2'):
                    dest_file = dest_root / file[:-3]  # Remove .j2 extension
                    self._render_template_file(src_file, dest_file, context)
                else:
                    shutil.copy2(src_file, dest_file)
    
    def _render_template_file(self, src_file: Path, dest_file: Path, context: Dict[str, Any]):
        """Render a Jinja2 template file"""
        rel_path = src_file.relative_to(self.template_dir)
        template = self.jinja_env.get_template(str(rel_path))
        content = template.render(**context)
        
        with open(dest_file, 'w') as f:
            f.write(content)
    
    def _generate_package_files(self, package_dir: Path, context: Dict[str, Any]):
        """Generate package-specific files"""
        # __init__.py
        init_content = f'"""\n{context["name"]} - {context.get("description", "MCP Server")}\n"""\n\n__version__ = "1.0.0"\n'
        with open(package_dir / "__init__.py", 'w') as f:
            f.write(init_content)
        
        # Generate main app file (only one template now)
        self._generate_fastmcp_app(package_dir, context)
    
    def _generate_fastmcp_app(self, package_dir: Path, context: Dict[str, Any]):
        """Generate comprehensive FastMCP app.py with examples"""
        app_content = f'''#!/usr/bin/env python3
"""
{context["name"]} MCP Server

{context.get("description", "MCP Server using FastMCP framework")}
"""

import argparse
import asyncio
import logging
import os
from typing import Dict, Any, List, Optional

import httpx
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("{context["name"]} MCP Server")


@mcp.tool()
async def echo_message(message: str) -> Dict[str, Any]:
    """
    Echo a message back with a timestamp.
    
    Args:
        message: The message to echo
    
    Returns:
        Dictionary with the echoed message and timestamp
    """
    import datetime
    
    logger.info(f"Echoing message: {{message}}")
    
    return {{
        "success": True,
        "echo": message,
        "timestamp": datetime.datetime.now().isoformat(),
        "message": f"Hello from {context['name']}! You said: {{message}}"
    }}


@mcp.tool()
async def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)")
    
    Returns:
        Dictionary with the calculation result
    """
    import math
    import re
    
    # Only allow safe mathematical operations
    safe_dict = {{
        "__builtins__": {{}},
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "sqrt": math.sqrt, "sin": math.sin,
        "cos": math.cos, "tan": math.tan, "log": math.log, "pi": math.pi,
        "e": math.e
    }}
    
    try:
        # Basic validation
        if not re.match(r'^[0-9+\-*/().,\s\w]+$', expression):
            raise ValueError("Invalid characters in expression")
        
        result = eval(expression, safe_dict)
        
        return {{
            "success": True,
            "expression": expression,
            "result": result,
            "type": type(result).__name__
        }}
        
    except Exception as e:
        logger.error(f"Calculation failed for '{{expression}}': {{e}}")
        return {{
            "success": False,
            "expression": expression,
            "error": str(e)
        }}


@mcp.tool()
async def fetch_url(url: str, method: str = "GET") -> Dict[str, Any]:
    """
    Fetch content from a URL (example of HTTP client usage).
    
    Args:
        url: The URL to fetch
        method: HTTP method to use (GET or POST)
    
    Returns:
        Dictionary with the response data
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                response = await client.post(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {{method}}")
            
            response.raise_for_status()
            
            return {{
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_type": response.headers.get("content-type", "unknown"),
                "content_length": len(response.content),
                # Only include text content if it's not too large
                "content": response.text[:1000] if len(response.content) < 1000 else "Content too large to display"
            }}
            
    except Exception as e:
        logger.error(f"Failed to fetch {{url}}: {{e}}")
        return {{
            "success": False,
            "url": url,
            "error": str(e)
        }}


@mcp.tool()
async def list_environment_variables() -> Dict[str, Any]:
    """
    List environment variables (example of system integration).
    
    Returns:
        Dictionary with environment variables
    """
    # Only show non-sensitive environment variables
    safe_vars = {{}}
    sensitive_patterns = ['key', 'secret', 'password', 'token', 'auth']
    
    for key, value in os.environ.items():
        if not any(pattern.lower() in key.lower() for pattern in sensitive_patterns):
            safe_vars[key] = value
        else:
            safe_vars[key] = "***HIDDEN***"
    
    return {{
        "success": True,
        "environment_variables": safe_vars,
        "total_variables": len(os.environ)
    }}


@mcp.tool()
async def get_server_info() -> Dict[str, Any]:
    """
    Get information about this MCP server.
    
    Returns:
        Server information including name and available tools
    """
    return {{
        "name": "{context['name']}",
        "version": "1.0.0",
        "description": "{context.get('description', '')}",
        "author": "{context.get('author', '')}",
        "framework": "FastMCP",
        "tools": [
            "echo_message",
            "calculate", 
            "fetch_url",
            "list_environment_variables",
            "get_server_info"
        ],
        "features": [
            "HTTP and stdio transport support",
            "Async/await support", 
            "Type hints",
            "Error handling",
            "Logging"
        ]
    }}


def main():
    """Main entry point for the MCP server"""
    parser = argparse.ArgumentParser(description="{context['name']} MCP Server")
    parser.add_argument("--transport", default="stdio", help="Transport type (stdio, streamable-http)")
    parser.add_argument("--host", default="localhost", help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP transport")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting {context['name']} MCP Server...")
    logger.info(f"📡 Transport: {{args.transport}}")
    
    if args.transport == "streamable-http":
        logger.info(f"🌐 Host: {{args.host}}")
        logger.info(f"🔌 Port: {{args.port}}")
        logger.info(f"🔗 Server URL: http://{{args.host}}:{{args.port}}/mcp")
        mcp.run(transport=args.transport, host=args.host, port=args.port)
    else:
        logger.info(f"📝 Using stdio transport for direct integration")
        mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
'''
        
        with open(package_dir / "app.py", 'w') as f:
            f.write(app_content)
    
    
    def _generate_test_files(self, project_path: Path, context: Dict[str, Any]):
        """Generate test files"""
        tests_dir = project_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # __init__.py
        (tests_dir / "__init__.py").touch()
        
        # test_mcp_server.py
        test_content = f'''#!/usr/bin/env python3
"""
Tests for {context["name"]} MCP Server
"""

import pytest
import asyncio
from {context["package_name"]}.app import example_tool, get_server_info


@pytest.mark.asyncio
async def test_example_tool():
    """Test the example tool"""
    result = await example_tool("Hello, world!")
    
    assert result["success"] is True
    assert "Hello, world!" in result["echo"]
    assert "Hello from {context['name']}" in result["message"]


@pytest.mark.asyncio
async def test_get_server_info():
    """Test the server info tool"""
    result = await get_server_info()
    
    assert result["name"] == "{context['name']}"
    assert result["version"] == "1.0.0"
    assert isinstance(result["tools"], list)
    assert len(result["tools"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])
'''
        
        with open(tests_dir / "test_mcp_server.py", 'w') as f:
            f.write(test_content)
    
    def _generate_github_actions(self, project_path: Path, context: Dict[str, Any]):
        """Generate GitHub Actions workflow"""
        workflows_dir = project_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_content = f'''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e .
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: pytest tests/
    
    - name: Test MCP server can start
      run: |
        timeout 10s {context["package_name"]}-mcp --transport stdio || true

  docker:
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: docker build -t {context["name"].lower()} .
    
    - name: Test Docker image
      run: |
        docker run --rm -d --name test-container -p 8080:8080 {context["name"].lower()}
        sleep 5
        curl -f http://localhost:8080/mcp || true
        docker stop test-container
'''
        
        with open(workflows_dir / "ci.yml", 'w') as f:
            f.write(workflow_content)
