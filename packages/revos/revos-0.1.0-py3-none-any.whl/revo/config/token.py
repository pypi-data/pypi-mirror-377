"""
Token management configuration settings.

This module contains configuration classes for token management
and refresh operations.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenManagerConfig(BaseSettings):
    """Token manager configuration settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="TOKEN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    refresh_interval_minutes: int = Field(
        default=45,
        description="Token refresh interval in minutes",
        ge=5,
        le=1440  # 24 hours
    )
    
    max_failures_before_fallback: int = Field(
        default=1,
        description="Maximum failures before switching to fallback method",
        ge=1,
        le=10
    )
    
    enable_periodic_refresh: bool = Field(
        default=True,
        description="Enable automatic periodic token refresh"
    )
    
    enable_fallback: bool = Field(
        default=True,
        description="Enable fallback authentication method"
    )
