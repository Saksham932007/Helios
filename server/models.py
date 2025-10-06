from pydantic import BaseModel
from typing import Optional, Dict, Any
from dataclasses import dataclass

class CompletionRequest(BaseModel):
    code: str
    language: str
    position: Dict[str, int]  # {line: int, character: int}
    filename: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.1

class CompletionResponse(BaseModel):
    suggestion: str
    confidence: float
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    server_version: str
    uptime: float

@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    model_name: str = "codellama:7b-code"
    max_tokens: int = 100
    temperature: float = 0.1
    debug: bool = False