# Contributing to Helios

Thank you for your interest in contributing to Helios! This document provides guidelines and information for contributors.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** - Search the issue tracker to see if the bug has already been reported
2. **Create a detailed report** - Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, VS Code version, Python version)
   - Relevant logs or error messages

### Suggesting Features

1. **Check existing feature requests** - Avoid duplicates
2. **Provide detailed description** - Include:
   - Use case and motivation
   - Proposed implementation approach
   - Any relevant examples or mockups

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Make your changes** following our coding standards
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Node.js 16+
- Python 3.8+
- VS Code 1.74+
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/your-username/helios.git
cd helios

# Run the installation script
./install.sh

# Or manual setup:
cd extension && npm install
cd ../server && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Running Tests

```bash
# Extension tests
cd extension
npm test

# Server tests
cd server
source venv/bin/activate
pytest
```

### Building

```bash
# Build extension
cd extension
npm run compile

# Package extension
npm run package
```

## Coding Standards

### TypeScript/JavaScript

- Use TypeScript strict mode
- Follow ESLint configuration
- Write comprehensive JSDoc comments
- Use meaningful variable and function names
- Handle errors gracefully

### Python

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions and classes
- Use meaningful variable names
- Handle exceptions properly

### Git Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(completion): add multi-line code generation
fix(server): resolve memory leak in model loading
docs(api): update endpoint documentation
```

## Project Structure

```
helios/
├── extension/          # VS Code extension
│   ├── src/           # TypeScript source code
│   ├── package.json   # Extension manifest
│   └── tsconfig.json  # TypeScript configuration
├── server/            # Python inference server
│   ├── main.py        # FastAPI application
│   ├── inference.py   # Model inference logic
│   ├── models.py      # Pydantic models
│   └── requirements.txt
├── docs/              # Additional documentation
├── install.sh         # Setup script
└── README.md          # Main documentation
```

## Testing Guidelines

### Extension Tests

- Unit tests for core logic
- Integration tests for VS Code API usage
- Mock external dependencies (server calls)
- Test error handling paths

### Server Tests

- Unit tests for API endpoints
- Integration tests with model inference
- Performance tests for completion timing
- Load tests for concurrent requests

### Manual Testing

Before submitting a PR:

1. Test basic code completion in Python and JavaScript
2. Verify status bar functionality
3. Test terminal execution features
4. Check configuration changes take effect
5. Test with and without server running

## Documentation

- Update relevant documentation for changes
- Add JSDoc/docstring comments for new functions
- Update API documentation for server changes
- Include examples in documentation

## Performance Considerations

- Minimize API calls to the server
- Implement proper debouncing for user input
- Use efficient data structures
- Profile performance-critical code paths
- Consider memory usage implications

## Security Guidelines

- Never commit sensitive information
- Validate all user inputs
- Use secure communication protocols
- Follow least privilege principle
- Regularly update dependencies

## Release Process

1. **Version bumping** - Update version in package.json and pyproject.toml
2. **Testing** - Run full test suite on multiple platforms
3. **Documentation** - Update CHANGELOG.md and release notes
4. **Tagging** - Create git tag with version number
5. **Distribution** - Package and distribute extension

## Getting Help

- **Questions** - Open a GitHub discussion
- **Bugs** - Create a GitHub issue
- **Chat** - Join our Discord/Slack channel (if available)
- **Email** - Contact maintainers directly for sensitive issues

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Extension credits

Thank you for contributing to Helios!