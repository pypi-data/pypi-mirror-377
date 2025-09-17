"""
Revos API configuration settings.

This module contains configuration classes for the Revos API authentication
and connection settings.
"""

from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RevosConfig(BaseSettings):
    """Revos API configuration settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="REVOS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Required Revos credentials
    client_id: str = Field(
        ...,
        description="Revos API client ID",
        min_length=1
    )
    
    client_secret: str = Field(
        ...,
        description="Revos API client secret",
        min_length=1
    )
    
    # Revos API endpoints
    token_url: str = Field(
        default="https://your-site.com/revo/oauth/token",
        description="OAuth token endpoint URL"
    )
    
    base_url: str = Field(
        default="https://your-site.com/revo/llm-api",
        description="Revos API base URL"
    )
    
    # Token management settings
    token_buffer_minutes: int = Field(
        default=5,
        description="Buffer time in minutes before token expiration",
        ge=1,
        le=60
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for token requests",
        ge=1,
        le=10
    )
    
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=5,
        le=300
    )
    
    @validator('token_url', 'base_url')
    def validate_urls(cls, v):
        """Validate that URLs are properly formatted."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
