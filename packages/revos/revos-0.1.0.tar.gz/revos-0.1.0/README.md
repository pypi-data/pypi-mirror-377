# Revo

A Python library for Revo API authentication and LangChain-based LLM tools with support for multiple LLM models and robust configuration management.

## Features

- **🔐 Revo API Authentication**: Dual authentication methods with automatic fallback
- **🤖 LangChain Integration**: Structured data extraction using LLMs
- **⚙️ Multiple LLM Models**: Support for multiple models with different configurations
- **🔄 Token Management**: Automatic token refresh with configurable intervals
- **🛡️ Robust Error Handling**: Comprehensive retry logic and fallback mechanisms
- **🔧 Flexible Configuration**: Environment variables, YAML, JSON, and programmatic configuration
- **📊 OpenAI-Compatible**: Works with OpenAI-compatible APIs through Revo
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

The Revo library uses `pydantic_settings` for robust configuration management. You can configure the library in several ways:

### 1. Environment Variables

Set the following environment variables:

```bash
# Required Revo credentials
export REVO_CLIENT_ID="your_client_id"
export REVO_CLIENT_SECRET="your_client_secret"

# Optional Revo settings
export REVO_TOKEN_URL="https://your-site.com/revo/oauth/token"
export REVO_BASE_URL="https://your-site.com/revo/llm-api"
export REVO_TOKEN_BUFFER_MINUTES="5"
export REVO_MAX_RETRIES="3"
export REVO_REQUEST_TIMEOUT="30"

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
REVO_CLIENT_ID=your_client_id
REVO_CLIENT_SECRET=your_client_secret
REVO_TOKEN_URL=https://your-site.com/revo/oauth/token
REVO_BASE_URL=https://your-site.com/revo/llm-api
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1
LOG_LEVEL=INFO
TOKEN_REFRESH_INTERVAL_MINUTES=45
DEBUG=false
```

### 3. Programmatic Configuration

```python
from revo import RevoMainConfig, RevoConfig, LLMConfig, LoggingConfig, TokenManagerConfig

# Create custom configuration
config = RevoMainConfig(
    revo=RevoConfig(
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
from revo import RevoTokenManager, LangChainExtractor

token_manager = RevoTokenManager(settings_instance=config)
extractor = LangChainExtractor(settings_instance=config)
```

### 4. Custom Environment Variable Prefixes

If you need to use different environment variable prefixes (e.g., to avoid conflicts or follow your organization's naming conventions), you can use the `create_config_with_prefixes()` function:

```python
from revo import create_config_with_prefixes

# Create configuration with custom prefixes
config = create_config_with_prefixes(
    revo_prefix="MY_API_",      # Instead of "REVO_"
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
- **Multiple Instances**: Run multiple Revo configurations in the same environment
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
from revo import get_revo_token, RevoTokenManager

# Get a token using the global token manager
token = get_revo_token()

# Or create your own token manager
token_manager = RevoTokenManager()
token = token_manager.get_token()
```

### Structured Data Extraction

```python
from revo import LangChainExtractor
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
from revo import TokenManager
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
from revo import get_revo_token, RevoTokenManager

# Get a token using the global token manager
token = get_revo_token()
print(f"Token: {token[:20]}...")

# Create your own token manager with custom settings
token_manager = RevoTokenManager()
token = token_manager.get_token(force_refresh=True)
print(f"Fresh token: {token[:20]}...")

# Invalidate token to force refresh on next request
token_manager.invalidate_token()
```

#### 2. Single Model Data Extraction

```python
from revo import get_langchain_extractor
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
from revo import RevoMainConfig, list_available_extractors, get_langchain_extractor
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
config = RevoMainConfig.from_file('config_multiple_models.yaml')

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
from revo import RevoMainConfig, LLMModelConfig, LLMModelsConfig
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
config = RevoMainConfig(
    revo=RevoConfig(
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
from revo import get_langchain_extractor, RevoAuthenticationError, RevoAPIError
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
        
    except RevoAuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Please check your credentials and try again.")
        
    except RevoAPIError as e:
        print(f"API error: {e}")
        print("The API might be temporarily unavailable.")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check your configuration and try again.")

asyncio.run(robust_extraction())
```

#### 6. Background Token Refresh

```python
from revo import BackgroundTokenManager
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
from revo import RevoMainConfig, create_config_with_prefixes
import os

# Example 1: Load from YAML file
config = RevoMainConfig.from_file('config.yaml')
print("Loaded from YAML:", config.llm_models.list_available_models())

# Example 2: Load from JSON file
config = RevoMainConfig.from_file('config.json')
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
    config = RevoMainConfig.from_file('config.prod.yaml')
else:
    config = RevoMainConfig.from_file('config.dev.yaml')
```

#### 8. Batch Processing with Multiple Models

```python
from revo import get_langchain_extractor, list_available_extractors
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
    config = RevoMainConfig.from_file('config_multiple_models.yaml')
    
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
from revo import create_config_with_prefixes

# Create configuration with custom prefixes
config = create_config_with_prefixes(
    revo_prefix="MY_API_",      # Instead of "REVO_"
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
from revo import RevoMainConfig, RevoConfig, LLMConfig, LLMModelConfig, LLMModelsConfig

# Create configuration programmatically
config = RevoMainConfig(
    revo=RevoConfig(
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

## API Reference

### Configuration Classes

#### RevoMainConfig

Main configuration class for the Revo library.

**Methods:**
- `from_file(config_path)`: Load configuration from a file (YAML, JSON, or .env)
- `save_to_file(config_path, format)`: Save configuration to a file

**Functions:**
- `create_config_with_prefixes()`: Create configuration with custom environment variable prefixes

**Properties:**
- `revo`: RevoConfig instance
- `llm`: LLMConfig instance
- `logging`: LoggingConfig instance
- `token_manager`: TokenManagerConfig instance
- `debug`: Global debug flag

#### RevoConfig

Revo API configuration settings.

**Properties:**
- `client_id`: Revo API client identifier (required)
- `client_secret`: Revo API client secret (required)
- `token_url`: OAuth token endpoint URL
- `base_url`: Revo API base URL
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

### RevoTokenManager

Manages Revo API authentication tokens with dual authentication methods.

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

### RevoConfig

Configuration class for Revo API settings.

#### Properties

- `client_id`: Revo API client identifier
- `client_secret`: Revo API client secret
- `token_url`: OAuth token endpoint URL
- `base_url`: Revo API base URL
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
