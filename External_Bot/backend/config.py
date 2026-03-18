"""
Application Configuration
=========================

This module contains all configuration settings for the application.
It loads environment variables and provides configuration constants
used throughout the application.

Environment Variables Required:
    - OPENROUTER_API_KEY: API key for OpenRouter LLM service
    - OPENWEATHER_API_KEY: API key for OpenWeatherMap service
    - DEBUG (optional): Set to "true" for debug mode (default: false)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
# This allows for local development without exporting env vars to system
load_dotenv()


# ==================== API CONFIGURATION ====================

# OpenRouter API configuration
# OpenRouter provides access to multiple LLM models including GPT-4, Claude, etc.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# OpenWeatherMap API configuration
# Used for fetching real-time weather data for specific locations
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


# ==================== APPLICATION CONFIGURATION ====================

# Application environment (development, production, testing)
# Affects logging level, error handling, and debug features
ENV = os.getenv("ENV", "development")

# Debug mode - when True, enables verbose logging and stack traces
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Log level for Winston logger
# Options: debug, info, warning, error
LOG_LEVEL = "debug" if DEBUG else "info"


# ==================== SERVER CONFIGURATION ====================

# FastAPI server host and port
# Host: "0.0.0.0" allows connections from any IP (production should restrict this)
# Port: 8000 is the standard development port
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Enable CORS (Cross-Origin Resource Sharing) for frontend communication
# This allows the frontend to make requests to the backend from different origins
CORS_ORIGINS = [
    "http://localhost:3000",      # Local frontend development
    "http://localhost:5173",      # Vite dev server (alternative)
    "http://localhost:8080",      # Alternative dev port
    "http://127.0.0.1",           # Localhost
]

# In production, be more restrictive:
# CORS_ORIGINS = ["https://yourdomain.com"]


# ==================== LLM CONFIGURATION ====================

# Model selection and parameters
# "openai/gpt-4-turbo" - OpenRouter routes to OpenAI's latest GPT-4 Turbo model
LLM_MODEL = "openai/gpt-4-turbo"

# Temperature controls randomness in LLM responses
# 0.0 = deterministic (same response every time)
# 0.7 = balanced (good mix of consistency and creativity)
# 1.0 = very creative (high variation in responses)
LLM_TEMPERATURE = 0.7

# Maximum number of tokens (words) the LLM can generate per response
# One token ≈ 4 characters, so 1024 tokens ≈ 4096 characters
LLM_MAX_TOKENS = 1024

# Timeout in seconds for LLM API requests
# Prevents the backend from hanging if the LLM service is slow
LLM_REQUEST_TIMEOUT = 30


# ==================== EXTERNAL API CONFIGURATION ====================

# OpenWeatherMap API settings
# Unit for temperature responses: "metric" (Celsius) or "imperial" (Fahrenheit)
WEATHER_UNIT_DEFAULT = "metric"

# Timeout for external API requests in seconds
EXTERNAL_API_TIMEOUT = 10


# ==================== VALIDATION ====================

def validate_config():
    """
    Validate that all required configuration variables are set.
    
    This function checks for required API keys and other critical settings.
    It should be called at application startup to catch configuration errors
    early rather than during runtime.
    
    Raises:
        ValueError: If any required configuration is missing
    
    Example:
        >>> validate_config()  # At application startup
    """
    # List of required environment variables
    required_keys = [
        "OPENROUTER_API_KEY",
        "OPENWEATHER_API_KEY"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_keys)}\n"
            f"Please set these variables in your .env file or system environment"
        )


# Validate configuration on module import
try:
    validate_config()
except ValueError as e:
    print(f"Configuration Error: {e}")
    # In development, we might want to continue with a warning
    # In production, we'd want to exit the application
    if not DEBUG:
        raise
