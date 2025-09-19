# Create MCP App

🚀 **The easiest way to create MCP (Model Context Protocol) servers**

Just like `create-next-app` for React, but for MCP servers! Generate production-ready MCP servers with FastMCP, Docker, tests, and CI/CD in seconds.

## ✨ Quick Start

```bash
# Install globally
pip install create-mcp-app

# Create your MCP server
create-mcp-app my-awesome-mcp

# That's it! 🎉
```

## 🎯 What You Get

- ✅ **FastMCP Framework** - Modern, fast MCP server
- ✅ **5 Example Tools** - Echo, calculator, HTTP client, system info, etc.
- ✅ **Docker Ready** - Dockerfile and deployment configs included
- ✅ **Type Hints** - Full TypeScript-style type safety
- ✅ **Error Handling** - Production-ready error handling
- ✅ **Test Suite** - Pytest tests included
- ✅ **CI/CD Pipeline** - GitHub Actions workflow
- ✅ **Professional Docs** - Complete README and documentation

## 🚀 Usage

### Interactive Mode
```bash
create-mcp-app my-project
```

### Quick Mode
```bash
create-mcp-app my-project --no-install --no-git
```

## 📦 Generated Project Structure

```
my-project/
├── my_project/
│   ├── __init__.py
│   └── app.py              # Main MCP server with example tools
├── tests/                  # Test suite
├── .github/workflows/      # CI/CD pipeline
├── Dockerfile             # Container configuration
├── requirements.txt       # Dependencies
├── setup.py              # Package configuration
├── README.md             # Project documentation
└── .gitignore           # Git ignore rules
```

## 🛠️ Example Tools Included

Every generated project includes these example tools:

1. **`echo_message`** - Echo messages with timestamps
2. **`calculate`** - Safe mathematical expression evaluation
3. **`fetch_url`** - HTTP client for external APIs
4. **`list_environment_variables`** - System environment access
5. **`get_server_info`** - Server metadata and health

Perfect starting points for building your own tools!

## 🏃‍♂️ Run Your MCP Server

```bash
cd my-project

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# Run with stdio (for Claude Desktop, etc.)
my_project-mcp --transport stdio

# Run with HTTP (for web integration)
my_project-mcp --transport streamable-http --port 8080

# Run with Docker
docker build -t my-project .
docker run -p 8080:8080 my-project
```

## 🌐 Integration Examples

### Claude Desktop
Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "my-project": {
      "command": "/path/to/my_project-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

### Web Integration
```bash
my_project-mcp --transport streamable-http --port 8080
# Server available at http://localhost:8080/mcp
```

## 🎨 Customization

The generated projects are fully customizable:

1. **Add new tools** - Just add `@mcp.tool()` decorated functions
2. **API integration** - Use the included HTTP client examples
3. **Database access** - Add your database libraries
4. **Custom logic** - Modify the example tools for your needs

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the MCP community**

*Get started in seconds, deploy in minutes!*
