#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="create-mcp-app",
    version="1.0.0",
    description="CLI tool to bootstrap MCP (Model Context Protocol) server projects",
    author="MCP Deploy",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "jinja2>=3.1.0",
        "rich>=13.0.0",
        "inquirer>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "create-mcp-app=create_mcp_app.cli:main",
        ],
    },
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "create_mcp_app": ["templates/**/*"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
