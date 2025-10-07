# Helios Development Guide

A comprehensive guide for contributing to and developing Helios, the local-first VS Code code assistant.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Debugging](#debugging)
- [Release Process](#release-process)
- [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

- **Node.js** 18+ and npm (for VS Code extension)
- **Python** 3.9+ (for server)
- **Docker** and Docker Compose (recommended for server deployment)
- **Ollama** (for local LLM inference)
- **Git** (for version control)

### Initial Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/helios.git
   cd helios
   ```

2. **Run the installation script:**

   ```bash
   ./install.sh
   ```

3. **Install development dependencies:**

   ```bash
   # Extension dependencies
   cd extension
   npm install
   npm run build

   # Server dependencies
   cd ../server
   pip install -e ".[dev]"
   ```

### Setting up Ollama

1. **Install Ollama:**

   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull CodeLlama model:**

   ```bash
   ollama pull codellama:7b-code
   ```

3. **Start Ollama service:**
   ```bash
   ollama serve
   ```

## Project Architecture

### Directory Structure

```
helios/
├── extension/          # VS Code extension (TypeScript)
│   ├── src/           # Extension source code
│   ├── package.json   # Extension manifest
│   └── tsconfig.json  # TypeScript configuration
├── server/            # Python FastAPI server
│   ├── main.py       # Server entry point
│   ├── inference.py  # LLM inference logic
│   └── models.py     # Data models
├── .github/          # GitHub workflows and templates
├── docs/             # Documentation
└── scripts/          # Development scripts
```

### Component Overview

#### VS Code Extension (`extension/`)

- **Purpose**: Provides the VS Code interface for Helios
- **Technology**: TypeScript, VS Code Extension API
- **Key Files**:
  - `src/extension.ts` - Main extension entry point
  - `src/completion.ts` - Code completion provider
  - `src/server.ts` - Server communication
  - `src/statusBar.ts` - Status bar integration

#### Python Server (`server/`)

- **Purpose**: Handles LLM inference and API endpoints
- **Technology**: FastAPI, Ollama integration
- **Key Files**:
  - `main.py` - FastAPI application
  - `inference.py` - Model inference logic
  - `model_manager.py` - Model lifecycle management
  - `models.py` - Pydantic data models

## Development Workflow

### Extension Development

1. **Open extension in VS Code:**

   ```bash
   cd extension
   code .
   ```

2. **Start development build:**

   ```bash
   npm run watch
   ```

3. **Run extension in development:**

   - Press `F5` to launch Extension Development Host
   - Test your changes in the new VS Code window

4. **Package extension:**
   ```bash
   npm run package
   ```

### Server Development

1. **Start development server:**

   ```bash
   cd server
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run with Docker (recommended):**

   ```bash
   docker-compose up --build
   ```

3. **API documentation:**
   - Server: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Development Scripts

The project includes several development utilities:

- `./install.sh` - Complete project setup
- `./dev.py` - Development helper with common tasks
- `./monitor.py` - System monitoring and health checks
- `./validate_config.py` - Configuration validation
- `./profile.py` - Performance profiling
- `./backup.py` - Backup and recovery

## Testing

### Extension Testing

```bash
cd extension
npm test
```

### Server Testing

```bash
cd server
pytest
```

### Integration Testing

```bash
# Start server
docker-compose up -d

# Run integration tests
python -m pytest tests/integration/

# Cleanup
docker-compose down
```

### Performance Testing

```bash
# Run performance profiler
./profile.py --iterations 10 --output results.json
```

## Debugging

### Extension Debugging

1. **Enable Developer Tools:**

   - In Extension Development Host: `Help > Toggle Developer Tools`

2. **Check extension logs:**

   - Open Output panel: `View > Output`
   - Select "Helios" from dropdown

3. **Debug TypeScript:**
   - Set breakpoints in VS Code
   - Use `F5` to start debugging session

### Server Debugging

1. **Check server logs:**

   ```bash
   docker logs helios-server
   ```

2. **Debug with Python debugger:**

   ```bash
   cd server
   python -m pdb main.py
   ```

3. **Monitor API calls:**
   ```bash
   curl -X POST http://localhost:8000/completion \
     -H "Content-Type: application/json" \
     -d '{"prompt": "def hello", "max_tokens": 50}'
   ```

### Common Issues

#### Extension not activating

- Check `activationEvents` in `package.json`
- Verify server is running and accessible
- Check Output panel for error messages

#### Completion not working

- Verify Ollama is running: `ollama list`
- Check server health: `curl http://localhost:8000/health`
- Validate configuration: `./validate_config.py --workspace .`

#### Performance issues

- Run profiler: `./profile.py`
- Monitor resources: `./monitor.py`
- Check model size and hardware requirements

## Release Process

### Version Management

1. **Update version numbers:**

   ```bash
   # Extension
   cd extension
   npm version patch  # or minor/major

   # Server
   cd server
   python setup.py version patch
   ```

2. **Update CHANGELOG.md:**
   - Add new version section
   - List all changes since last version

### Building Release

1. **Build extension:**

   ```bash
   cd extension
   npm run build
   npm run package
   ```

2. **Build server Docker image:**
   ```bash
   cd server
   docker build -t helios-server:latest .
   ```

### Publishing

1. **Extension to VS Code Marketplace:**

   ```bash
   cd extension
   npx vsce publish
   ```

2. **Server to Docker Hub:**

   ```bash
   docker tag helios-server:latest username/helios-server:latest
   docker push username/helios-server:latest
   ```

3. **Create GitHub release:**
   - Tag version: `git tag v1.0.0`
   - Push tags: `git push --tags`
   - Create release on GitHub with changelog

## Code Style and Quality

### TypeScript (Extension)

- **Linting**: ESLint with TypeScript rules
- **Formatting**: Prettier
- **Type checking**: Strict TypeScript configuration

```bash
cd extension
npm run lint
npm run format
npm run type-check
```

### Python (Server)

- **Linting**: Ruff
- **Formatting**: Black
- **Type checking**: mypy

```bash
cd server
ruff check .
black .
mypy .
```

### Git Hooks

Pre-commit hooks automatically run:

- Code formatting
- Linting
- Type checking
- Tests

## Troubleshooting

### Common Development Issues

#### Port conflicts

```bash
# Check what's using port 8000
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

#### Docker issues

```bash
# Clean up containers
docker-compose down
docker system prune

# Rebuild from scratch
docker-compose build --no-cache
```

#### Extension not loading

1. Check VS Code version compatibility
2. Verify all dependencies are installed
3. Clear extension cache: `Ctrl+Shift+P > "Reload Window"`

#### Model inference errors

1. Verify Ollama is running: `ollama serve`
2. Check model is available: `ollama list`
3. Test model directly: `ollama run codellama:7b-code "def hello"`

### Performance Optimization

#### Extension Performance

- Minimize activation events
- Use lazy loading for heavy operations
- Debounce completion requests
- Cache completion results

#### Server Performance

- Use async/await for I/O operations
- Implement request queuing
- Monitor memory usage
- Use connection pooling

#### Model Performance

- Choose appropriate model size for hardware
- Adjust context length and max tokens
- Use quantized models (GGUF format)
- Consider GPU acceleration

### Getting Help

1. **Check existing issues**: GitHub Issues
2. **Read documentation**: `/docs` directory
3. **Run diagnostics**: `./monitor.py --diagnostics`
4. **Validate configuration**: `./validate_config.py --workspace .`
5. **Join community**: Discord/Slack channels

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
