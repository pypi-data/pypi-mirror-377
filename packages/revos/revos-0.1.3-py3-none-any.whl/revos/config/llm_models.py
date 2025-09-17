"""
Multiple LLM Models Configuration

This module provides support for configuring multiple LLM models
with different settings and parameters.
"""

from typing import Dict, Optional, Any
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMModelConfig(BaseModel):
    """Configuration for a single LLM model."""
    
    model: str = Field(
        description="LLM model name (e.g., 'gpt-4', 'gpt-3.5-turbo', 'claude-3')"
    )
    
    temperature: float = Field(
        default=0.1,
        description="LLM temperature setting",
        ge=0.0,
        le=2.0
    )
    
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens to generate",
        ge=1,
        le=4096
    )
    
    top_p: float = Field(
        default=1.0,
        description="Top-p sampling parameter",
        ge=0.0,
        le=1.0
    )
    
    frequency_penalty: float = Field(
        default=0.0,
        description="Frequency penalty",
        ge=-2.0,
        le=2.0
    )
    
    presence_penalty: float = Field(
        default=0.0,
        description="Presence penalty",
        ge=-2.0,
        le=2.0
    )
    
    # Model-specific settings
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the model"
    )
    
    # Custom parameters for model-specific features
    custom_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom parameters specific to this model"
    )


class LLMModelsConfig(BaseSettings):
    """Configuration for multiple LLM models."""
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_MODELS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Model configurations
    models: Dict[str, LLMModelConfig] = Field(
        default_factory=lambda: {
            "gpt-3.5-turbo": LLMModelConfig(
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=1000,
                description="Fast and cost-effective model for general tasks"
            ),
            "gpt-4": LLMModelConfig(
                model="gpt-4",
                temperature=0.1,
                max_tokens=2000,
                description="Most capable model for complex tasks"
            ),
            "gpt-4-turbo": LLMModelConfig(
                model="gpt-4-turbo",
                temperature=0.1,
                max_tokens=4000,
                description="Latest GPT-4 model with extended context"
            ),
            "claude-3": LLMModelConfig(
                model="claude-3-sonnet",
                temperature=0.1,
                max_tokens=2000,
                description="Anthropic's Claude 3 model"
            ),
            "claude_4_sonnet": LLMModelConfig(
                model="claude-4-sonnet",
                temperature=0.1,
                max_tokens=2000,
                description="Anthropic's Claude 4 Sonnet model"
            )
        },
        description="Dictionary of available LLM models"
    )
    
    def get_model(self, model_name: str) -> LLMModelConfig:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model to get.
            
        Returns:
            LLMModelConfig: Configuration for the specified model
            
        Raises:
            ValueError: If model is not found
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available models: {list(self.models.keys())}")
        
        return self.models[model_name]
    
    def list_available_models(self) -> Dict[str, str]:
        """
        List all available models.
        
        Returns:
            Dict[str, str]: Dictionary mapping model names to descriptions
        """
        return {
            name: config.description or f"{config.model} model"
            for name, config in self.models.items()
        }
    
    def add_model(self, name: str, config: LLMModelConfig) -> None:
        """
        Add a new model configuration.
        
        Args:
            name: Name for the model configuration
            config: Model configuration
        """
        self.models[name] = config
    
    def remove_model(self, name: str) -> None:
        """
        Remove a model configuration.
        
        Args:
            name: Name of the model to remove
        """
        if name in self.models:
            del self.models[name]
