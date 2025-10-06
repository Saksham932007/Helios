from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import time
import asyncio
from contextlib import asynccontextmanager

from models import CompletionRequest, CompletionResponse, HealthResponse, ServerConfig
from inference import CodeLlamaInference

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
config = ServerConfig()
inference_engine: CodeLlamaInference = None
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global inference_engine
    
    # Startup
    logger.info("Starting Helios Inference Server...")
    inference_engine = CodeLlamaInference(config)
    
    # Initialize model in background
    asyncio.create_task(initialize_model())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Helios Inference Server...")

async def initialize_model():
    """Initialize the model asynchronously"""
    global inference_engine
    try:
        success = await inference_engine.initialize()
        if success:
            logger.info("Model initialized successfully")
        else:
            logger.error("Failed to initialize model")
    except Exception as e:
        logger.error(f"Error during model initialization: {e}")

# Create FastAPI app
app = FastAPI(
    title="Helios Inference Server",
    description="Local CodeLlama inference server for VS Code extension",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        model_loaded=inference_engine.is_model_loaded() if inference_engine else False,
        server_version="0.1.0",
        uptime=uptime
    )

@app.post("/complete", response_model=CompletionResponse)
async def get_completion(request: CompletionRequest):
    """Generate code completion"""
    if not inference_engine:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    if not inference_engine.is_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        completion, processing_time = await inference_engine.generate_completion(request)
        
        # Calculate confidence based on completion length and processing time
        confidence = min(0.95, len(completion) / 100.0 * 0.8 + (1.0 / max(processing_time, 0.1)) * 0.2)
        
        return CompletionResponse(
            suggestion=completion,
            confidence=confidence,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating completion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate completion: {str(e)}")

@app.post("/restart")
async def restart_server(background_tasks: BackgroundTasks):
    """Restart the inference server"""
    background_tasks.add_task(restart_model)
    return {"message": "Server restart initiated"}

async def restart_model():
    """Restart the model"""
    global inference_engine
    try:
        logger.info("Restarting model...")
        inference_engine = CodeLlamaInference(config)
        await inference_engine.initialize()
        logger.info("Model restarted successfully")
    except Exception as e:
        logger.error(f"Error restarting model: {e}")

@app.get("/status")
async def get_status():
    """Get detailed server status"""
    return {
        "server_status": "running",
        "model_loaded": inference_engine.is_model_loaded() if inference_engine else False,
        "model_name": config.model_name,
        "uptime": time.time() - start_time,
        "config": {
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "host": config.host,
            "port": config.port
        }
    }

if __name__ == "__main__":
    logger.info(f"Starting server on {config.host}:{config.port}")
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info"
    )