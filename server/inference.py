import ollama
import asyncio
import logging
import time
from typing import Optional, Dict, Any
from models import CompletionRequest, ServerConfig

logger = logging.getLogger(__name__)

class CodeLlamaInference:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.model_name = config.model_name
        self.client = ollama.AsyncClient()
        self.model_loaded = False
        
    async def initialize(self) -> bool:
        """Initialize the model and check if it's available"""
        try:
            # Check if model exists locally
            models = await self.client.list()
            model_names = [model['name'] for model in models['models']]
            
            if self.model_name not in model_names:
                logger.info(f"Model {self.model_name} not found locally. Pulling...")
                await self.pull_model()
            
            # Test the model with a simple prompt
            test_response = await self.client.generate(
                model=self.model_name,
                prompt="def hello():",
                options={
                    'num_predict': 10,
                    'temperature': 0.1
                }
            )
            
            self.model_loaded = True
            logger.info(f"Model {self.model_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            self.model_loaded = False
            return False
    
    async def pull_model(self) -> bool:
        """Pull the model from Ollama registry"""
        try:
            logger.info(f"Pulling model {self.model_name}...")
            await self.client.pull(self.model_name)
            logger.info(f"Model {self.model_name} pulled successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return False
    
    async def generate_completion(self, request: CompletionRequest) -> tuple[str, float]:
        """Generate code completion using CodeLlama"""
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")
        
        start_time = time.time()
        
        try:
            # Prepare the prompt with context
            prompt = self._prepare_prompt(request)
            
            # Generate completion
            response = await self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'num_predict': request.max_tokens or self.config.max_tokens,
                    'temperature': request.temperature or self.config.temperature,
                    'top_p': 0.9,
                    'stop': ['\n\n', '```', '</code>']  # Stop tokens
                }
            )
            
            completion = response['response'].strip()
            processing_time = time.time() - start_time
            
            # Post-process the completion
            completion = self._post_process_completion(completion, request)
            
            logger.debug(f"Generated completion in {processing_time:.2f}s: {completion[:50]}...")
            
            return completion, processing_time
            
        except Exception as e:
            logger.error(f"Failed to generate completion: {e}")
            raise
    
    def _prepare_prompt(self, request: CompletionRequest) -> str:
        """Prepare the prompt for code completion"""
        language = request.language
        code = request.code
        filename = request.filename
        
        # Create a context-aware prompt
        prompt = f"""<PRE> {filename}
{code}<SUF><MID>"""
        
        return prompt
    
    def _post_process_completion(self, completion: str, request: CompletionRequest) -> str:
        """Clean up the generated completion"""
        # Remove any unwanted prefixes/suffixes
        completion = completion.strip()
        
        # Remove common artifacts
        artifacts = [
            '<MID>', '</MID>', '<SUF>', '</SUF>', '<PRE>', '</PRE>',
            '```python', '```javascript', '```typescript', '```',
            '<code>', '</code>'
        ]
        
        for artifact in artifacts:
            completion = completion.replace(artifact, '')
        
        # Clean up extra whitespace
        lines = completion.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip():  # Keep non-empty lines
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1].strip():  # Keep first empty line after content
                cleaned_lines.append('')
                break  # Stop at first significant gap
        
        return '\n'.join(cleaned_lines).strip()
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model_loaded