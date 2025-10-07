# Helios Server API Documentation

## Overview

The Helios inference server provides a RESTful API for code completion using CodeLlama models. It's designed to run locally and serve the VS Code extension with intelligent code suggestions.

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required for local usage. The server is designed to run on localhost only.

## Endpoints

### Health Check

Check if the server is running and healthy.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "server_version": "0.1.0",
  "uptime": 12345.67
}
```

**Status Codes:**
- `200` - Server is healthy
- `503` - Server is unhealthy or model not loaded

### Code Completion

Generate code completion suggestions.

```http
POST /complete
```

**Request Body:**
```json
{
  "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    ",
  "language": "python",
  "position": {
    "line": 3,
    "character": 4
  },
  "filename": "fibonacci.py",
  "max_tokens": 100,
  "temperature": 0.1
}
```

**Response:**
```json
{
  "suggestion": "return fibonacci(n-1) + fibonacci(n-2)",
  "confidence": 0.85,
  "processing_time": 0.245
}
```

**Status Codes:**
- `200` - Completion generated successfully
- `400` - Invalid request body
- `503` - Service unavailable (model not loaded)
- `500` - Internal server error

### Server Status

Get detailed server information.

```http
GET /status
```

**Response:**
```json
{
  "server_status": "running",
  "model_loaded": true,
  "model_name": "codellama:7b-code",
  "uptime": 12345.67,
  "config": {
    "max_tokens": 100,
    "temperature": 0.1,
    "host": "127.0.0.1",
    "port": 8000
  }
}
```

### Restart Server

Restart the inference server and reload the model.

```http
POST /restart
```

**Response:**
```json
{
  "message": "Server restart initiated"
}
```

**Status Codes:**
- `200` - Restart initiated successfully

## Request/Response Schemas

### CompletionRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | The code context before the cursor |
| `language` | string | Yes | Programming language identifier |
| `position` | object | Yes | Cursor position with `line` and `character` |
| `filename` | string | Yes | Name of the file being edited |
| `max_tokens` | integer | No | Maximum tokens to generate (default: 100) |
| `temperature` | float | No | Generation temperature 0-1 (default: 0.1) |

### CompletionResponse

| Field | Type | Description |
|-------|------|-------------|
| `suggestion` | string | The generated code completion |
| `confidence` | float | Confidence score 0-1 |
| `processing_time` | float | Time taken to generate in seconds |

### HealthResponse

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Server health status |
| `model_loaded` | boolean | Whether the model is loaded |
| `server_version` | string | Version of the server |
| `uptime` | float | Server uptime in seconds |

## Supported Languages

The server supports code completion for:

- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- Java (`.java`)
- C++ (`.cpp`, `.cc`, `.cxx`)
- C (`.c`)
- Go (`.go`)
- Rust (`.rs`)
- HTML (`.html`)
- CSS (`.css`)
- JSON (`.json`)

## Error Handling

### Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2023-10-07T12:00:00Z"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `MODEL_NOT_LOADED` | Model is not initialized | 503 |
| `INVALID_REQUEST` | Request body validation failed | 400 |
| `COMPLETION_FAILED` | Error during code generation | 500 |
| `SERVER_OVERLOADED` | Too many concurrent requests | 429 |

## Rate Limiting

- Maximum 10 requests per second per client
- Burst allowance of 20 requests
- Concurrent request limit: 5

## Performance Notes

### Response Times

Typical response times based on completion length:
- Short completions (1-20 tokens): 100-300ms
- Medium completions (20-50 tokens): 300-800ms
- Long completions (50+ tokens): 800ms-2s

### Hardware Requirements

**Minimum:**
- 8GB RAM
- 4 CPU cores
- 5GB disk space

**Recommended:**
- 16GB+ RAM
- 8+ CPU cores or GPU with 6GB+ VRAM
- 10GB+ disk space

### Model Information

The server uses quantized CodeLlama models for efficiency:

- **7B model**: ~4GB RAM, fastest inference
- **13B model**: ~8GB RAM, better quality
- **34B model**: ~20GB RAM, highest quality

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
python main.py

# Run with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Testing

```bash
# Run tests
pytest test_main.py

# Test with coverage
pytest --cov=main test_main.py

# Load testing
locust -f locustfile.py --host=http://localhost:8000
```

### Configuration

Environment variables:
- `HELIOS_HOST`: Server host (default: 127.0.0.1)
- `HELIOS_PORT`: Server port (default: 8000)
- `HELIOS_MODEL`: Model name (default: codellama:7b-code)
- `HELIOS_DEBUG`: Enable debug mode (default: false)

## Examples

### Python Completion

```bash
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        ",
    "language": "python",
    "position": {"line": 4, "character": 8},
    "filename": "math_utils.py"
  }'
```

### JavaScript Completion

```bash
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{
    "code": "function calculateSum(arr) {\n    let total = 0;\n    for (let i = 0; i < arr.length; i++) {\n        ",
    "language": "javascript",
    "position": {"line": 3, "character": 8},
    "filename": "utils.js"
  }'
```