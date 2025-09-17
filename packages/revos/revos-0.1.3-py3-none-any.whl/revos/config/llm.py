"""
LLM configuration settings.

This module contains configuration classes for LLM model settings
and generation parameters.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """LLM configuration settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Model settings
    model: str = Field(
        default="gpt-3.5-turbo",
        description="LLM model name to use"
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
    
    # Model parameters
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
