# Helios Extension Development Guide

## Architecture Overview

The Helios VS Code extension consists of several key components:

### Core Components

1. **Extension Entry Point** (`extension.ts`)
   - Manages extension lifecycle
   - Initializes all components
   - Registers commands and providers

2. **Server Communication** (`server.ts`)
   - Handles HTTP communication with local inference server
   - Manages connection health checks
   - Provides completion request/response handling

3. **Completion Provider** (`completion.ts`)
   - Implements VS Code's InlineCompletionItemProvider
   - Manages code completion logic
   - Handles context extraction and suggestion display

4. **Status Bar Integration** (`statusBar.ts`)
   - Shows current server status
   - Provides quick actions menu
   - Visual feedback for user

5. **Terminal Manager** (`terminal.ts`)
   - Handles file execution commands
   - Supports multiple programming languages
   - Manages VS Code integrated terminal

## Configuration System

The extension uses a comprehensive configuration system that allows users to customize:

- Server connection settings
- Model parameters (temperature, max tokens)
- Feature toggles (auto-complete, comment-to-code)
- Performance tuning (completion delay, debug mode)

## Development Setup

### Prerequisites

1. Node.js 16+ and npm
2. VS Code 1.74+
3. TypeScript 4.9+

### Installation

```bash
cd extension
npm install
```

### Build and Test

```bash
# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Package extension
npm run package
```

### Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## Extension API Integration

### Commands

- `helios.toggleAssistant` - Enable/disable the assistant
- `helios.runCurrentFile` - Execute the current file
- `helios.runSelectedCode` - Execute selected code
- `helios.restartServer` - Restart the inference server

### Keybindings

- `Ctrl+Shift+F5` - Run current file
- `Ctrl+Shift+F6` - Run selected code
- `Tab` - Accept completion (when available)
- `Esc` - Dismiss completion

### Settings

All settings are prefixed with `helios.` and include:

- `enabled` - Master enable/disable switch
- `serverUrl` - Local server URL
- `modelPath` - Path to model file
- `maxTokens` - Token generation limit
- `temperature` - Creativity parameter
- `autoComplete` - Auto-completion toggle
- `commentToCode` - Comment-to-code feature toggle

## Performance Considerations

### Debouncing

Completion requests are debounced to prevent overwhelming the server:
- Default delay: 300ms
- Configurable via `helios.completionDelay`

### Context Management

- Limited context window (10 lines before cursor by default)
- Intelligent truncation for large files
- Language-specific optimizations

### Error Handling

- Graceful degradation when server is unavailable
- Automatic retry with exponential backoff
- User-friendly error messages

## Debugging

### Debug Mode

Enable debug mode via `helios.debugMode` setting:
- Verbose logging to Output panel
- Network request/response logging
- Performance timing information

### Log Access

View logs via:
1. Command Palette → "View: Show Output"
2. Select "Helios" from dropdown
3. Or use `Ctrl+Shift+P` → "Helios: Show Logs"

## Contributing

### Code Style

- Use TypeScript strict mode
- Follow VS Code extension guidelines
- Maintain comprehensive error handling
- Write tests for new features

### Testing Guidelines

- Unit tests for core logic
- Integration tests for VS Code API usage
- Performance tests for completion timing
- Mock external dependencies (server calls)

### Pull Request Process

1. Fork and create feature branch
2. Write tests for new functionality
3. Update documentation
4. Ensure all tests pass
5. Submit PR with detailed description

## Troubleshooting

### Common Issues

1. **Server Connection Failed**
   - Check if inference server is running
   - Verify `helios.serverUrl` setting
   - Check firewall/network settings

2. **No Completions Showing**
   - Ensure `helios.enabled` is true
   - Check if model is loaded on server
   - Verify language is supported

3. **Slow Performance**
   - Increase `helios.completionDelay`
   - Check server hardware resources
   - Consider smaller model if available

### Diagnostic Commands

- `Helios: Show Status` - Display detailed status
- `Helios: Test Connection` - Test server connectivity
- `Helios: Show Metrics` - View performance metrics
- `Helios: Reset Configuration` - Reset to defaults