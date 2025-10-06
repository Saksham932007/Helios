import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "server_version" in data
    assert "uptime" in data

def test_status_endpoint():
    """Test the status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "server_status" in data
    assert "uptime" in data
    assert "config" in data

def test_completion_endpoint_without_model():
    """Test completion endpoint when model is not loaded"""
    completion_request = {
        "code": "def hello():",
        "language": "python",
        "position": {"line": 0, "character": 12},
        "filename": "test.py"
    }
    
    response = client.post("/complete", json=completion_request)
    # Should return 503 if model is not loaded
    assert response.status_code in [200, 503]

def test_restart_endpoint():
    """Test the restart endpoint"""
    response = client.post("/restart")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data