"""
Weather Service - External API Integration
===========================================

This module handles all weather-related API calls and data processing.
It communicates with OpenWeatherMap API to fetch real-time weather data
and formats it for use by the LLM and frontend.

Functions:
    - fetch_weather_data: Retrieve weather information from OpenWeatherMap API
    - format_weather_response: Transform API response into human-readable format
"""

import requests
import os
from typing import Dict, Any, Optional
from utils.logger import setup_logger

# Configure logger for this module
logger = setup_logger(__name__)


def fetch_weather_data(location: str, unit: str = "metric") -> Optional[Dict[str, Any]]:
    """
    Fetch weather data from OpenWeatherMap API for a specified location.
    
    This function makes an HTTP request to the OpenWeatherMap API using the
    provided API key from environment variables. It handles errors gracefully
    and returns None if the request fails.
    
    Args:
        location (str): The city name or location to get weather for (e.g., "London")
        unit (str, optional): Temperature unit - "metric" (Celsius) or "imperial" (Fahrenheit).
                            Defaults to "metric"
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing weather data if successful, None if failed
                                  Typical data includes: temperature, description, humidity, 
                                  wind_speed, clouds, etc.
    
    Raises:
        No exceptions are raised; errors are logged and None is returned.
    
    Example:
        >>> weather = fetch_weather_data("London", "metric")
        >>> if weather:
        ...     print(f"Temperature: {weather['main']['temp']}°C")
    
    Notes:
        - Requires OPENWEATHER_API_KEY environment variable to be set
        - Makes HTTP request to api.openweathermap.org
        - Response includes complete weather data structure from OpenWeatherMap
    """
    # Retrieve API key from environment variables (must be set before running)
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # Check if API key is configured
    if not api_key:
        logger.error("OPENWEATHER_API_KEY environment variable is not set")
        return None
    
    # Construct the API endpoint URL with parameters
    # q: location query
    # appid: API authentication key
    # units: temperature unit (metric for Celsius, imperial for Fahrenheit)
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": unit
    }
    
    try:
        # Log the API request for debugging and monitoring
        logger.info(f"Fetching weather data for: {location} (unit: {unit})")
        
        # Make the HTTP GET request with timeout to prevent hanging
        response = requests.get(url, params=params, timeout=10)
        
        # Raise exception if HTTP status code indicates an error (4xx or 5xx)
        response.raise_for_status()
        
        # Parse the JSON response
        weather_data = response.json()
        
        # Log successful data retrieval
        logger.info(f"Successfully fetched weather for {location}")
        
        return weather_data
        
    except requests.exceptions.Timeout:
        # Handle request timeout (response took too long)
        logger.error(f"Request timeout while fetching weather for {location}")
        return None
        
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (4xx, 5xx status codes)
        # This often means location not found or API limit exceeded
        logger.error(f"HTTP Error fetching weather for {location}: {e.response.status_code} - {e.response.text}")
        return None
        
    except requests.exceptions.RequestException as e:
        # Handle any other request-related errors (network issues, etc.)
        logger.error(f"Error fetching weather data: {str(e)}")
        return None
        
    except ValueError as e:
        # Handle JSON parsing errors
        logger.error(f"Invalid JSON in weather response: {str(e)}")
        return None


def format_weather_response(weather_data: Dict[str, Any]) -> str:
    """
    Transform raw OpenWeatherMap API data into a human-readable format.
    
    This function extracts key weather information from the API response
    and formats it into a nice string that can be displayed to users or
    passed to the LLM for processing.
    
    Args:
        weather_data (Dict[str, Any]): Raw weather data from OpenWeatherMap API
    
    Returns:
        str: Formatted weather information as a readable string
    
    Example:
        >>> data = fetch_weather_data("London")
        >>> formatted = format_weather_response(data)
        >>> print(formatted)
        "Weather in London: Clear skies, 15°C, Humidity: 65%, Wind: 10 m/s"
    
    Notes:
        - Handles missing data gracefully with default values
        - Extracts temperature, description, humidity, and wind speed
        - Uses metric units by default (can be modified based on input)
    """
    try:
        # Extract location name
        city = weather_data.get("name", "Unknown location")
        country = weather_data.get("sys", {}).get("country", "")
        location_str = f"{city}, {country}".rstrip(", ")
        
        # Extract main weather metrics
        main_data = weather_data.get("main", {})
        temperature = main_data.get("temp", "N/A")
        feels_like = main_data.get("feels_like", "N/A")
        humidity = main_data.get("humidity", "N/A")
        pressure = main_data.get("pressure", "N/A")
        
        # Extract wind data
        wind_data = weather_data.get("wind", {})
        wind_speed = wind_data.get("speed", "N/A")
        wind_gust = wind_data.get("gust", None)
        
        # Extract weather description (e.g., "Clear sky", "Light rain")
        weather_description = "N/A"
        if weather_data.get("weather"):
            weather_description = weather_data["weather"][0].get("description", "N/A")
        
        # Extract cloud coverage percentage
        clouds = weather_data.get("clouds", {}).get("all", "N/A")
        
        # Build formatted string with all weather information
        formatted_text = (
            f"Weather in {location_str}:\n"
            f"  • Condition: {weather_description.title()}\n"
            f"  • Temperature: {temperature}°C (feels like {feels_like}°C)\n"
            f"  • Humidity: {humidity}%\n"
            f"  • Pressure: {pressure} hPa\n"
            f"  • Wind Speed: {wind_speed} m/s"
        )
        
        # Add wind gust information if available
        if wind_gust:
            formatted_text += f" (gusts up to {wind_gust} m/s)"
        
        # Add cloud coverage information
        formatted_text += f"\n  • Cloud Coverage: {clouds}%"
        
        logger.info(f"Successfully formatted weather response for {location_str}")
        return formatted_text
        
    except Exception as e:
        # Handle any unexpected errors during formatting
        logger.error(f"Error formatting weather response: {str(e)}")
        return "Error formatting weather data"
