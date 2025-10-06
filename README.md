# Helios - Local-First CodeLlama VS Code Assistant

🌟 **Your Code, Your Machine** - A privacy-focused, entirely local code completion assistant for Visual Studio Code.

## Overview

Helios is a powerful VS Code extension that provides intelligent code suggestions using CodeLlama, running entirely on your local machine. No data ever leaves your environment, ensuring maximum privacy and offline capability.

## Architecture

- **VS Code Extension** (`extension/`) - TypeScript-based frontend interface
- **Python Inference Server** (`server/`) - FastAPI backend with CodeLlama integration

## Features

- 🤖 Real-time, context-aware code completion
- 💬 Comment-to-code generation
- 🖥️ Integrated terminal execution
- 📊 Status bar integration
- ⚙️ Configurable settings

## Quick Start

1. **Install Dependencies**
   ```bash
   # Extension dependencies
   cd extension && npm install
   
   # Server dependencies
   cd ../server && pip install -r requirements.txt
   ```

2. **Start the Inference Server**
   ```bash
   cd server && python main.py
   ```

3. **Install Extension**
   ```bash
   cd extension && npm run package
   code --install-extension helios-*.vsix
   ```

## Development Status

🚧 **Currently in development** - Building towards MVP with core completion features.

## License

MIT License - See LICENSE file for details.