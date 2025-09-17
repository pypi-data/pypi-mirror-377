# Revos

A Python library for Revos API authentication and LangChain-based LLM tools with support for multiple LLM models and robust configuration management.

## Features

- **🔐 Revos API Authentication**: Dual authentication methods with automatic fallback
- **🤖 LangChain Integration**: Structured data extraction using LLMs
- **⚙️ Multiple LLM Models**: Support for multiple models with different configurations
- **🔄 Token Management**: Automatic token refresh with configurable intervals
- **🛡️ Robust Error Handling**: Comprehensive retry logic and fallback mechanisms
- **🔧 Flexible Configuration**: Environment variables, YAML, JSON, and programmatic configuration
- **📊 OpenAI-Compatible**: Works with OpenAI-compatible APIs through Revos
- **🧪 Comprehensive Testing**: Full test suite with pytest
- **📚 Rich Examples**: Multiple usage examples and configuration patterns

## Installation

### From Source

```bash
git clone https://github.com/yourusername/revo.git
cd revo
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/revo.git
cd revo
pip install -e ".[dev]"
```

## Configuration

The Revos library uses `pydantic_settings` for robust configuration management. You can configure the library in several ways:

### 1. Environment Variables

Set the following environment variables:

```bash
# Required Revos credentials
export REVOS_CLIENT_ID="your_client_id"
export REVOS_CLIENT_SECRET="your_client_secret"

# Optional Revos settings
export REVOS_TOKEN_URL="https://your-site.com/revo/oauth/token"
export REVOS_BASE_URL="https://your-site.com/revo/llm-api"
export REVOS_TOKEN_BUFFER_MINUTES="5"
export REVOS_MAX_RETRIES="3"
export REVOS_REQUEST_TIMEOUT="30"

# LLM settings
export LLM_MODEL="gpt-3.5-turbo"
export LLM_TEMPERATURE="0.1"
export LLM_MAX_TOKENS="1024"
export LLM_TOP_P="1.0"
export LLM_FREQUENCY_PENALTY="0.0"
export LLM_PRESENCE_PENALTY="0.0"

# Logging settings
export LOG_LEVEL="INFO"
export LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
export LOG_FILE="/tmp/revo.log"

# Token manager settings
export TOKEN_REFRESH_INTERVAL_MINUTES="45"
export TOKEN_MAX_FAILURES_BEFORE_FALLBACK="1"
export TOKEN_ENABLE_PERIODIC_REFRESH="true"
export TOKEN_ENABLE_FALLBACK="true"

# Global settings
export DEBUG="false"
```

### 2. Configuration Files

#### YAML Configuration File

Create a `config.yaml` file:

```yaml
revo:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  token_url: "https://your-site.com/revo/oauth/token"
  base_url: "https://your-site.com/revo/llm-api"
  token_buffer_minutes: 5
  max_retries: 3
  request_timeout: 30

llm:
  model: "gpt-3.5-turbo"
  temperature: 0.1
  max_tokens: 1024
  top_p: 1.0
  frequency_penalty: 0.0
  presence_penalty: 0.0

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/tmp/revo.log"
  max_size: 10485760  # 10MB
  backup_count: 5

token_manager:
  refresh_interval_minutes: 45
  max_failures_before_fallback: 1
  enable_periodic_refresh: true
  enable_fallback: true

debug: false
```

#### JSON Configuration File

Create a `config.json` file:

```json
{
  "revo": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "token_url": "https://your-site.com/revo/oauth/token",
    "base_url": "https://your-site.com/revo/llm-api",
    "token_buffer_minutes": 5,
    "max_retries": 3,
    "request_timeout": 30
  },
  "llm": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.1,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "/tmp/revo.log",
    "max_size": 10485760,
    "backup_count": 5
  },
  "token_manager": {
    "refresh_interval_minutes": 45,
    "max_failures_before_fallback": 1,
    "enable_periodic_refresh": true,
    "enable_fallback": true
  },
  "debug": false
}
```

#### .env File

Create a `.env` file:

```env
REVOS_CLIENT_ID=your_client_id
REVOS_CLIENT_SECRET=your_client_secret
REVOS_TOKEN_URL=https://your-site.com/revo/oauth/token
REVOS_BASE_URL=https://your-site.com/revo/llm-api
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1
LOG_LEVEL=INFO
TOKEN_REFRESH_INTERVAL_MINUTES=45
DEBUG=false
```

### 3. Programmatic Configuration

```python
from revos import RevosMainConfig, RevosConfig, LLMConfig, LoggingConfig, TokenManagerConfig

# Create custom configuration
config = RevosMainConfig(
    revo=RevosConfig(
        client_id="your_client_id",
        client_secret="your_client_secret",
        token_url="https://your-site.com/revo/oauth/token",
        base_url="https://your-site.com/revo/llm-api",
        token_buffer_minutes=5,
        max_retries=3,
        request_timeout=30
    ),
    llm=LLMConfig(
        model="gpt-3.5-turbo",
        temperature=0.1,
        max_tokens=1024,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    ),
    logging=LoggingConfig(
        level="INFO",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        file="/tmp/revo.log",
        max_size=10485760,
        backup_count=5
    ),
    token_manager=TokenManagerConfig(
        refresh_interval_minutes=45,
        max_failures_before_fallback=1,
        enable_periodic_refresh=True,
        enable_fallback=True
    ),
    debug=False
)

# Use the configuration
from revos import RevosTokenManager, LangChainExtractor

token_manager = RevosTokenManager(settings_instance=config)
extractor = LangChainExtractor(settings_instance=config)
```

### 4. Custom Environment Variable Prefixes

If you need to use different environment variable prefixes (e.g., to avoid conflicts or follow your organization's naming conventions), you can use the `create_config_with_prefixes()` function:

```python
from revos import create_config_with_prefixes

# Create configuration with custom prefixes
config = create_config_with_prefixes(
    revo_prefix="MY_API_",      # Instead of "REVOS_"
    llm_prefix="AI_",           # Instead of "LLM_"
    logging_prefix="APP_",      # Instead of "LOG_"
    token_prefix="AUTH_",       # Instead of "TOKEN_"
)

# This will look for environment variables like:
# MY_API_CLIENT_ID, MY_API_CLIENT_SECRET
# AI_MODEL, AI_TEMPERATURE
# APP_LOG_LEVEL, APP_LOG_FORMAT
# AUTH_REFRESH_INTERVAL_MINUTES
```

**Use Cases for Custom Prefixes:**
- **Avoid Conflicts**: When you have existing environment variables with the default prefixes
- **Organization Standards**: Follow your company's naming conventions
- **Multiple Instances**: Run multiple Revos configurations in the same environment
- **Minimal Prefixes**: Use shorter prefixes for simplicity

**Example with Custom Environment Variables:**
```bash
# Set custom environment variables
export MY_API_CLIENT_ID="your-client-id"
export MY_API_CLIENT_SECRET="your-client-secret"
export AI_MODEL="gpt-4"
export AI_TEMPERATURE="0.7"
export APP_LOG_LEVEL="INFO"
```

## Quick Start

### Basic Authentication

```python
from revos import get_revo_token, RevosTokenManager

# Get a token using the global token manager
token = get_revo_token()

# Or create your own token manager
token_manager = RevosTokenManager()
token = token_manager.get_token()
```

### Structured Data Extraction

```python
from revos import LangChainExtractor
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

# Define your data model
class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str

# Create a prompt template
template = """
Extract person information from the following text:
{text}

{format_instructions}
"""
prompt = PromptTemplate(template=template, input_variables=["text"])

# Extract structured data
extractor = LangChainExtractor()
result = await extractor.extract(
    target=PersonInfo,
    prompt=prompt,
    text="John is 30 years old and works as a software engineer."
)

print(result.name)  # "John"
print(result.age)   # 30
```

### Token Management

```python
from revos import TokenManager
import asyncio

# Create a token manager with 45-minute refresh interval
token_manager = TokenManager(refresh_interval_minutes=45)

# Start periodic refresh in background
async def main():
    # Start the background refresh task
    refresh_task = asyncio.create_task(token_manager.periodic_refresh())
    
    # Your application logic here
    # ...
    
    # Cancel the refresh task when done
    refresh_task.cancel()

asyncio.run(main())
```

## Examples

### Basic Usage Examples

#### 1. Simple Authentication and Token Management

```python
from revos import get_revo_token, RevosTokenManager

# Get a token using the global token manager
token = get_revo_token()
print(f"Token: {token[:20]}...")

# Create your own token manager with custom settings
token_manager = RevosTokenManager()
token = token_manager.get_token(force_refresh=True)
print(f"Fresh token: {token[:20]}...")

# Invalidate token to force refresh on next request
token_manager.invalidate_token()
```

#### 2. Single Model Data Extraction

```python
from revos import get_langchain_extractor
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
import asyncio

# Define your data model
class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str
    location: str

# Create a prompt template
template = """
Extract person information from the following text:
{text}

{format_instructions}
"""
prompt = PromptTemplate(template=template, input_variables=["text"])

async def extract_person_info():
    # Get extractor for a specific model
    extractor = get_langchain_extractor("gpt-3.5-turbo")
    
    # Extract structured data
    result = await extractor.extract(
        target=PersonInfo,
        prompt=prompt,
        text="John is 30 years old and works as a software engineer in San Francisco."
    )
    
    print(f"Name: {result.name}")
    print(f"Age: {result.age}")
    print(f"Occupation: {result.occupation}")
    print(f"Location: {result.location}")

# Run the extraction
asyncio.run(extract_person_info())
```

#### 3. Multiple Models Configuration

```python
from revos import RevosMainConfig, list_available_extractors, get_langchain_extractor
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

# Define your data model
class ProductReview(BaseModel):
    product_name: str
    rating: int
    sentiment: str
    key_features: list[str]
    summary: str

# Create a prompt template
template = """
Analyze the following product review and extract structured information:
{review}

{format_instructions}
"""
prompt = PromptTemplate(template=template, input_variables=["review"])

# Load configuration with multiple models
config = RevosMainConfig.from_file('config_multiple_models.yaml')

# List available models
available_models = list_available_extractors(config)
print("Available models:", list(available_models.keys()))

# Use different models for different tasks
async def analyze_review():
    review_text = """
    I love this new smartphone! The camera quality is amazing, 
    the battery lasts all day, and the screen is crystal clear. 
    I'd give it 5 stars. The only downside is the price, but 
    it's worth it for the quality.
    """
    
    # Use GPT-4 for complex analysis
    gpt4_extractor = get_langchain_extractor("gpt-4", config)
    gpt4_result = await gpt4_extractor.extract(
        target=ProductReview,
        prompt=prompt,
        review=review_text
    )
    
    # Use GPT-3.5 for faster, simpler analysis
    gpt35_extractor = get_langchain_extractor("gpt-3.5-turbo", config)
    gpt35_result = await gpt35_extractor.extract(
        target=ProductReview,
        prompt=prompt,
        review=review_text
    )
    
    print("GPT-4 Analysis:", gpt4_result.summary)
    print("GPT-3.5 Analysis:", gpt35_result.summary)

asyncio.run(analyze_review())
```

#### 4. Custom Model Configurations

```python
from revos import RevosMainConfig, LLMModelConfig, LLMModelsConfig
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

# Define your data model
class CreativeStory(BaseModel):
    title: str
    genre: str
    characters: list[str]
    plot_summary: str
    tone: str

# Create a creative prompt
template = """
Create a creative story based on these elements:
{story_elements}

{format_instructions}
"""
prompt = PromptTemplate(template=template, input_variables=["story_elements"])

# Create custom configuration with specialized models
config = RevosMainConfig(
    revo=RevosConfig(
        client_id="your_client_id",
        client_secret="your_client_secret"
    ),
    llm_models=LLMModelsConfig(
        models={
            # Creative model with high temperature
            "creative": LLMModelConfig(
                model="gpt-4",
                temperature=0.8,
                max_tokens=2000,
                top_p=0.9,
                frequency_penalty=0.3,
                presence_penalty=0.3,
                description="Creative model for storytelling and ideation"
            ),
            # Analytical model with low temperature
            "analytical": LLMModelConfig(
                model="gpt-4",
                temperature=0.0,
                max_tokens=3000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                description="Analytical model for data analysis and reasoning"
            )
        }
    )
)

async def create_story():
    # Use creative model for storytelling
    creative_extractor = get_langchain_extractor("creative", config)
    
    result = await creative_extractor.extract(
        target=CreativeStory,
        prompt=prompt,
        story_elements="A detective, a mysterious library, and a missing book"
    )
    
    print(f"Title: {result.title}")
    print(f"Genre: {result.genre}")
    print(f"Characters: {', '.join(result.characters)}")
    print(f"Plot: {result.plot_summary}")
    print(f"Tone: {result.tone}")

asyncio.run(create_story())
```

#### 5. Error Handling and Fallbacks

```python
from revos import get_langchain_extractor, RevosAuthenticationError, RevosAPIError
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
import asyncio

class SimpleData(BaseModel):
    value: str
    confidence: float

template = "Extract data from: {text}\n\n{format_instructions}"
prompt = PromptTemplate(template=template, input_variables=["text"])

async def robust_extraction():
    try:
        # Try to get extractor
        extractor = get_langchain_extractor("gpt-4")
        
        # Attempt extraction
        result = await extractor.extract(
            target=SimpleData,
            prompt=prompt,
            text="The answer is 42"
        )
        
        print(f"Extracted: {result.value} (confidence: {result.confidence})")
        
    except RevosAuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Please check your credentials and try again.")
        
    except RevosAPIError as e:
        print(f"API error: {e}")
        print("The API might be temporarily unavailable.")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check your configuration and try again.")

asyncio.run(robust_extraction())
```

#### 6. Background Token Refresh

```python
from revos import BackgroundTokenManager
import asyncio
import signal
import sys

async def main():
    # Create background token manager
    bg_manager = BackgroundTokenManager()
    
    # Start background refresh
    await bg_manager.start_background_refresh()
    
    print("Background token refresh started. Press Ctrl+C to stop.")
    
    try:
        # Your application logic here
        while True:
            # Simulate some work
            await asyncio.sleep(10)
            print("Application running...")
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        await bg_manager.stop_background_refresh()
        print("Background refresh stopped.")

# Handle graceful shutdown
def signal_handler(sig, frame):
    print("\nReceived interrupt signal")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
asyncio.run(main())
```

#### 7. Configuration Management

```python
from revos import RevosMainConfig, create_config_with_prefixes
import os

# Example 1: Load from YAML file
config = RevosMainConfig.from_file('config.yaml')
print("Loaded from YAML:", config.llm_models.list_available_models())

# Example 2: Load from JSON file
config = RevosMainConfig.from_file('config.json')
print("Loaded from JSON:", config.llm_models.list_available_models())

# Example 3: Custom environment variable prefixes
config = create_config_with_prefixes(
    revo_prefix="MY_API_",
    llm_prefix="AI_",
    logging_prefix="APP_",
    token_prefix="AUTH_"
)

# Example 4: Save configuration to file
config.save_to_file('my_config.yaml', format='yaml')
config.save_to_file('my_config.json', format='json')

# Example 5: Environment-specific configuration
if os.getenv('ENVIRONMENT') == 'production':
    config = RevosMainConfig.from_file('config.prod.yaml')
else:
    config = RevosMainConfig.from_file('config.dev.yaml')
```

#### 8. Batch Processing with Multiple Models

```python
from revos import get_langchain_extractor, list_available_extractors
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
import asyncio

class TextAnalysis(BaseModel):
    sentiment: str
    topics: list[str]
    summary: str
    word_count: int

template = """
Analyze the following text:
{text}

{format_instructions}
"""
prompt = PromptTemplate(template=template, input_variables=["text"])

async def batch_analysis():
    # Load configuration
    config = RevosMainConfig.from_file('config_multiple_models.yaml')
    
    # Get available models
    available_models = list_available_extractors(config)
    
    # Sample texts to analyze
    texts = [
        "I love this product! It's amazing and works perfectly.",
        "This is okay, but could be better. Not terrible though.",
        "Absolutely horrible experience. Would not recommend to anyone."
    ]
    
    # Analyze each text with different models
    for i, text in enumerate(texts):
        print(f"\n--- Analysis {i+1} ---")
        print(f"Text: {text}")
        
        for model_name in available_models.keys():
            try:
                extractor = get_langchain_extractor(model_name, config)
                result = await extractor.extract(
                    target=TextAnalysis,
                    prompt=prompt,
                    text=text
                )
                
                print(f"{model_name}: {result.sentiment} - {result.summary}")
                
            except Exception as e:
                print(f"{model_name}: Error - {e}")

asyncio.run(batch_analysis())
```

### Advanced Configuration Examples

#### 1. Custom Environment Variable Prefixes

```python
from revos import create_config_with_prefixes

# Create configuration with custom prefixes
config = create_config_with_prefixes(
    revo_prefix="MY_API_",      # Instead of "REVOS_"
    llm_prefix="AI_",           # Instead of "LLM_"
    logging_prefix="APP_",      # Instead of "LOG_"
    token_prefix="AUTH_",       # Instead of "TOKEN_"
)

# This will look for environment variables like:
# MY_API_CLIENT_ID, MY_API_CLIENT_SECRET
# AI_MODEL, AI_TEMPERATURE
# APP_LOG_LEVEL, APP_LOG_FORMAT
# AUTH_REFRESH_INTERVAL_MINUTES
```

#### 2. Programmatic Configuration

```python
from revos import RevosMainConfig, RevosConfig, LLMConfig, LLMModelConfig, LLMModelsConfig

# Create configuration programmatically
config = RevosMainConfig(
    revo=RevosConfig(
        client_id="your_client_id",
        client_secret="your_client_secret",
        token_url="https://your-site.com/revo/oauth/token",
        base_url="https://your-site.com/revo/llm-api"
    ),
    llm_models=LLMModelsConfig(
        models={
            "fast": LLMModelConfig(
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=1000,
                description="Fast model for quick tasks"
            ),
            "accurate": LLMModelConfig(
                model="gpt-4",
                temperature=0.0,
                max_tokens=2000,
                description="Accurate model for complex tasks"
            )
        }
    )
)
```

## FastAPI Integration

The Revos library integrates seamlessly with FastAPI applications. Here are several patterns for integrating Revos into your FastAPI projects:

### Basic FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Depends
from revos import (
    RevosMainConfig, 
    get_revos_token, 
    LangChainExtractor,
    RevosTokenError
)
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager

# Global extractor instance
extractor: Optional[LangChainExtractor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Revos extractor on startup."""
    global extractor
    try:
        # Initialize with your preferred model
        extractor = LangChainExtractor(model_name="gpt-4")
        print("✅ Revos extractor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Revos extractor: {e}")
        raise
    
    yield
    
    # Cleanup (if needed)
    print("🔄 Revos extractor cleanup completed")

app = FastAPI(title="Revos FastAPI Integration", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Revos FastAPI Integration"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if extractor is None:
        raise HTTPException(status_code=503, detail="Revos extractor not initialized")
    
    try:
        # Test token availability
        token = get_revos_token()
        return {
            "status": "healthy",
            "revos_connected": True,
            "token_available": bool(token)
        }
    except RevosTokenError:
        return {
            "status": "degraded", 
            "revos_connected": False,
            "token_available": False
        }
```

### Dependency Injection Pattern

```python
from fastapi import FastAPI, Depends, HTTPException
from revos import LangChainExtractor, get_revos_token, RevosTokenError
from functools import lru_cache

app = FastAPI()

@lru_cache()
def get_extractor() -> LangChainExtractor:
    """Dependency to get the Revos extractor."""
    try:
        return LangChainExtractor(model_name="gpt-4")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to initialize Revos extractor: {e}"
        )

def get_valid_token():
    """Dependency to ensure we have a valid token."""
    try:
        token = get_revos_token()
        if not token:
            raise HTTPException(status_code=401, detail="No valid token available")
        return token
    except RevosTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token error: {e}")

@app.get("/extract")
async def extract_data(
    prompt: str,
    extractor: LangChainExtractor = Depends(get_extractor),
    token: str = Depends(get_valid_token)
):
    """Extract structured data using Revos."""
    from pydantic import BaseModel
    
    class ExtractedData(BaseModel):
        summary: str
        confidence: float
        key_points: list[str]
    
    try:
        result = extractor.extract_structured_data(
            prompt=prompt,
            target_class=ExtractedData
        )
        return {"extracted_data": result.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")
```

### Advanced Integration with Background Token Management

```python
from fastapi import FastAPI, BackgroundTasks
from revos import (
    RevosMainConfig,
    TokenManager,
    LangChainExtractor,
    get_revos_token
)
from contextlib import asynccontextmanager
from typing import Optional

# Global instances
token_manager: Optional[TokenManager] = None
extractor: Optional[LangChainExtractor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with proper cleanup."""
    global token_manager, extractor
    
    # Startup
    try:
        # Initialize token manager with background refresh
        token_manager = TokenManager(refresh_interval_minutes=30)
        
        # Start background token refresh service
        await token_manager.start_background_service()
        
        # Initialize extractor
        extractor = LangChainExtractor(model_name="gpt-4")
        
        print("✅ Revos services started successfully")
        
    except Exception as e:
        print(f"❌ Failed to start Revos services: {e}")
        raise
    
    yield
    
    # Shutdown
    if token_manager:
        await token_manager.stop_background_service()
        print("✅ Revos services stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/token-status")
async def get_token_status():
    """Get current token status and refresh information."""
    if not token_manager:
        raise HTTPException(status_code=503, detail="Token manager not initialized")
    
    return {
        "background_service_running": token_manager.is_background_service_running(),
        "last_refresh_time": token_manager.get_last_refresh_time(),
        "should_refresh": token_manager.should_refresh_token(),
        "current_token_available": bool(get_revos_token())
    }

@app.post("/force-refresh")
async def force_token_refresh():
    """Force a token refresh."""
    if not token_manager:
        raise HTTPException(status_code=503, detail="Token manager not initialized")
    
    success = token_manager.force_refresh()
    return {"refresh_successful": success}
```

### Error Handling and Middleware

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from revos import RevosTokenError, RevosAuthenticationError, RevosAPIError

app = FastAPI()

@app.exception_handler(RevosTokenError)
async def revos_token_error_handler(request: Request, exc: RevosTokenError):
    """Handle Revos token errors."""
    return JSONResponse(
        status_code=401,
        content={
            "error": "Token Error",
            "message": str(exc),
            "type": "REVOS_TOKEN_ERROR"
        }
    )

@app.exception_handler(RevosAuthenticationError)
async def revos_auth_error_handler(request: Request, exc: RevosAuthenticationError):
    """Handle Revos authentication errors."""
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication Error", 
            "message": str(exc),
            "type": "REVOS_AUTH_ERROR"
        }
    )

@app.exception_handler(RevosAPIError)
async def revos_api_error_handler(request: Request, exc: RevosAPIError):
    """Handle Revos API errors."""
    return JSONResponse(
        status_code=502,
        content={
            "error": "API Error",
            "message": str(exc), 
            "type": "REVOS_API_ERROR"
        }
    )
```

### Complete FastAPI Application Example

```python
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from revos import (
    RevosMainConfig,
    LangChainExtractor, 
    TokenManager,
    get_revos_token,
    RevosTokenError
)
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

# Data models
class DocumentSummary(BaseModel):
    title: str
    summary: str
    key_points: List[str]
    confidence: float

class SentimentAnalysis(BaseModel):
    sentiment: str  # positive, negative, neutral
    confidence: float
    reasoning: str

# Global instances
token_manager: Optional[TokenManager] = None
extractor: Optional[LangChainExtractor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global token_manager, extractor
    
    # Startup
    token_manager = TokenManager(refresh_interval_minutes=30)
    await token_manager.start_background_service()
    extractor = LangChainExtractor(model_name="gpt-4")
    
    yield
    
    # Shutdown
    if token_manager:
        await token_manager.stop_background_service()

app = FastAPI(
    title="Revos FastAPI Integration",
    description="FastAPI application with Revos LLM integration",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Revos FastAPI Integration", "status": "running"}

@app.post("/summarize")
async def summarize_document(
    text: str,
    background_tasks: BackgroundTasks
):
    """Summarize a document using Revos."""
    try:
        result = extractor.extract_structured_data(
            prompt=f"Summarize this document: {text}",
            target_class=DocumentSummary
        )
        
        # Log the operation in background
        background_tasks.add_task(log_operation, "summarize", len(text))
        
        return {"summary": result.dict()}
    except RevosTokenError:
        raise HTTPException(status_code=401, detail="Authentication failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

@app.post("/analyze-sentiment")
async def analyze_sentiment(text: str):
    """Analyze sentiment of text using Revos."""
    try:
        result = extractor.extract_structured_data(
            prompt=f"Analyze the sentiment of this text: {text}",
            target_class=SentimentAnalysis
        )
        return {"analysis": result.dict()}
    except RevosTokenError:
        raise HTTPException(status_code=401, detail="Authentication failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        token = get_revos_token()
        return {
            "status": "healthy",
            "revos_connected": True,
            "token_available": bool(token),
            "background_service_running": token_manager.is_background_service_running() if token_manager else False
        }
    except Exception:
        return {
            "status": "degraded",
            "revos_connected": False,
            "token_available": False
        }

async def log_operation(operation: str, data_size: int):
    """Background task to log operations."""
    print(f"Operation '{operation}' completed on {data_size} characters")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Environment Configuration for FastAPI

Create a `.env` file for your FastAPI app:

```bash
# .env
REVOS_CLIENT_ID=your_client_id
REVOS_CLIENT_SECRET=your_client_secret
REVOS_TOKEN_URL=https://your-site.com/revo/oauth/token
REVOS_BASE_URL=https://your-site.com/revo/llm-api

# LLM Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000

# Token Management
TOKEN_MANAGER_REFRESH_INTERVAL_MINUTES=30
TOKEN_MANAGER_MAX_FAILURES_BEFORE_FALLBACK=3
```

### Running the FastAPI Application

```bash
# Install dependencies
pip install fastapi uvicorn revos

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or with the Makefile
make run-fastapi
```

### Key Benefits of FastAPI Integration

1. **🔄 Automatic Token Management**: Background refresh keeps tokens valid
2. **🛡️ Error Handling**: Proper HTTP status codes for different error types
3. **💉 Dependency Injection**: Clean separation of concerns
4. **📊 Health Monitoring**: Endpoints to check system status
5. **⚡ Background Tasks**: Non-blocking operations
6. **⚙️ Configuration Management**: Environment-based configuration
7. **🔒 Thread Safety**: Safe for concurrent requests
8. **📚 Modern FastAPI**: Uses `lifespan` instead of deprecated `on_event`

## API Reference

### Configuration Classes

#### RevosMainConfig

Main configuration class for the Revos library.

**Methods:**
- `from_file(config_path)`: Load configuration from a file (YAML, JSON, or .env)
- `save_to_file(config_path, format)`: Save configuration to a file

**Functions:**
- `create_config_with_prefixes()`: Create configuration with custom environment variable prefixes

**Properties:**
- `revo`: RevosConfig instance
- `llm`: LLMConfig instance
- `logging`: LoggingConfig instance
- `token_manager`: TokenManagerConfig instance
- `debug`: Global debug flag

#### RevosConfig

Revos API configuration settings.

**Properties:**
- `client_id`: Revos API client identifier (required)
- `client_secret`: Revos API client secret (required)
- `token_url`: OAuth token endpoint URL
- `base_url`: Revos API base URL
- `token_buffer_minutes`: Buffer time before token expiration
- `max_retries`: Maximum retry attempts for requests
- `request_timeout`: Request timeout in seconds

#### LLMConfig

LLM configuration settings.

**Properties:**
- `model`: LLM model name
- `temperature`: LLM temperature setting
- `max_tokens`: Maximum tokens to generate
- `top_p`: Top-p sampling parameter
- `frequency_penalty`: Frequency penalty
- `presence_penalty`: Presence penalty

#### LoggingConfig

Logging configuration settings.

**Properties:**
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `format`: Log message format
- `file`: Log file path (optional)
- `max_size`: Maximum log file size in bytes
- `backup_count`: Number of backup log files to keep

#### TokenManagerConfig

Token manager configuration settings.

**Properties:**
- `refresh_interval_minutes`: Token refresh interval in minutes
- `max_failures_before_fallback`: Maximum failures before switching to fallback
- `enable_periodic_refresh`: Enable automatic periodic token refresh
- `enable_fallback`: Enable fallback authentication method

### RevosTokenManager

Manages Revos API authentication tokens with dual authentication methods.

#### Methods

- `get_token(force_refresh=False, use_fallback=False)`: Get a valid access token
- `invalidate_token()`: Invalidate current token to force refresh
- `_is_token_expired()`: Check if current token is expired

#### Properties

- `consecutive_failures`: Count of consecutive authentication failures
- `max_failures_before_fallback`: Threshold for switching to fallback method

### LangChainExtractor

Extracts structured data using LangChain and LLM.

#### Methods

- `extract(target, prompt, **kwargs)`: Extract structured data using LLM
- `_refresh_llm(use_fallback=False)`: Refresh LLM with new token

### TokenManager

Manages authentication tokens for LLM services with automatic refresh.

#### Methods

- `should_refresh_token()`: Check if token should be refreshed
- `refresh_extractor()`: Refresh the LLM extractor with new token
- `periodic_refresh()`: Background task for periodic token refresh

### RevosConfig

Configuration class for Revos API settings.

#### Properties

- `client_id`: Revos API client identifier
- `client_secret`: Revos API client secret
- `token_url`: OAuth token endpoint URL
- `base_url`: Revos API base URL
- `token_buffer_minutes`: Buffer time before token expiration
- `llm_model`: LLM model name
- `llm_temperature`: LLM temperature setting

## Authentication Methods

The library supports two authentication methods:

1. **Original OAuth2**: Standard client credentials flow using requests
2. **Fallback httpx**: httpx-based authentication for OpenShift compatibility

The system automatically switches to the fallback method when the original method fails.

## Error Handling

The library includes comprehensive error handling:

- **Retry Logic**: Exponential backoff for transient failures
- **Fallback Mechanisms**: Automatic switching between authentication methods
- **Token Validation**: Automatic token refresh when expired
- **Graceful Degradation**: Fallback data when LLM is unavailable

## Development

### Quick Start with Makefile

The project includes a comprehensive Makefile with 50+ commands for development:

```bash
# Set up development environment
make dev-setup

# Run all tests
make test

# Run specific test categories
make test-auth
make test-config
make test-llm
make test-tokens

# Format and lint code
make format
make lint

# Run all quality checks
make check

# Build the package
make build

# Show all available commands
make help
```

### Available Makefile Commands

#### Testing Commands
- `make test` - Run all tests
- `make test-verbose` - Run tests with verbose output
- `make test-coverage` - Run tests with coverage report
- `make test-auth` - Run only authentication tests
- `make test-config` - Run only configuration tests
- `make test-llm` - Run only LLM tests
- `make test-tokens` - Run only token management tests
- `make test-fast` - Run tests excluding slow tests
- `make quick-test` - Quick test run for development

#### Development Commands
- `make dev-setup` - Set up development environment
- `make install-dev` - Install with development dependencies
- `make format` - Format code with black and isort
- `make lint` - Run linting checks
- `make check` - Run all quality checks
- `make clean` - Clean build artifacts and cache files

#### Building & Publishing
- `make build` - Build the package
- `make build-wheel` - Build wheel distribution
- `make build-sdist` - Build source distribution
- `make publish` - Publish to PyPI
- `make publish-test` - Publish to test PyPI

#### Configuration & Utilities
- `make config-check` - Check configuration files
- `make version` - Show current version
- `make examples` - Run example scripts
- `make backup` - Backup important files

### Manual Development Commands

If you prefer not to use the Makefile:

#### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=revo --cov-report=html

# Run specific test files
uv run pytest tests/test_auth.py -v
uv run pytest tests/test_config.py -v
uv run pytest tests/test_llm.py -v
uv run pytest tests/test_tokens.py -v
```

#### Code Formatting

```bash
# Format code
uv run black revo/ tests/
uv run isort revo/ tests/

# Check formatting
uv run black --check revo/ tests/
uv run isort --check-only revo/ tests/
```

#### Type Checking

```bash
# Run type checking
uv run mypy revo/
```

#### Building

```bash
# Build the package
uv build

# Build specific formats
uv build --wheel
uv build --sdist
```

### Development Workflow

1. **Set up development environment:**
   ```bash
   make dev-setup
   ```

2. **Make your changes and run tests:**
   ```bash
   make test
   ```

3. **Format and lint your code:**
   ```bash
   make format
   make lint
   ```

4. **Run all quality checks:**
   ```bash
   make check
   ```

5. **Build and test the package:**
   ```bash
   make build
   ```

### Configuration Files

The project includes several configuration files:

- `pyproject.toml` - Python package configuration
- `pytest.ini` - Pytest configuration
- `Makefile` - Development commands
- `env.example` - Environment variables example
- `env.multiple_models.example` - Multiple models environment example
- `config_multiple_models.yaml.example` - YAML configuration example

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
