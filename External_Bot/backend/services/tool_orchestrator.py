"""
Tool Orchestrator - Central Tool Execution Manager
=================================================

This module orchestrates the execution of external tools (like weather API).
It acts as the middleman between the LLM (which decides what tool to use)
and the actual tool services (which execute the requests).

Functions:
    - execute_tool: Route and execute tool requests with error handling
    - format_tool_result: Convert tool output to a message for the LLM
"""

from typing import Dict, Any, Optional
from services.weather_service import fetch_weather_data, format_weather_response
from models.schemas import WeatherToolInput
from utils.logger import setup_logger

# Configure logger for this module
logger = setup_logger(__name__)


def execute_tool(tool_name: str, tool_arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Execute the requested tool and return its results.
    
    This is the main tool execution router. Based on the tool name received
    from the LLM, it calls the appropriate service to execute the tool with
    the provided arguments, handling any errors gracefully.
    
    Args:
        tool_name (str): The name of the tool to execute (e.g., "weather")
        tool_arguments (Dict[str, Any]): Arguments to pass to the tool as key-value pairs
                                        Example: {"location": "London", "unit": "metric"}
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary with tool execution results:
                                 - If successful: {"success": True, "data": {...}}
                                 - If failed: {"success": False, "error": "error message"}
                                 - If tool not found: returns None
    
    Raises:
        No exceptions raised; all errors are caught and returned in result dict.
    
    Example:
        >>> result = execute_tool("weather", {"location": "London"})
        >>> if result and result.get("success"):
        ...     print(f"Weather data: {result['data']}")
    
    Notes:
        - Tool names are case-insensitive
        - Unknown tools return None with an error log
        - Each tool has its own validation and error handling
    """
    # Normalize tool name to lowercase for case-insensitive comparison
    tool_name = tool_name.lower().strip()
    
    logger.info(f"Executing tool: {tool_name} with arguments: {tool_arguments}")
    
    # Route to appropriate tool handler based on tool name
    if tool_name == "weather":
        return _execute_weather_tool(tool_arguments)
    else:
        # Unknown tool - log error and return None
        logger.error(f"Unknown tool requested: {tool_name}")
        return None


def _execute_weather_tool(tool_arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the weather tool to fetch and format weather data.
    
    This is an internal helper function that handles the specific logic
    for the weather tool. It validates inputs, calls the weather service,
    and formats the results for return to the LLM.
    
    Args:
        tool_arguments (Dict[str, Any]): Arguments for weather tool:
                                        - location (required): City name or location
                                        - unit (optional): "metric" or "imperial"
    
    Returns:
        Dict[str, Any]: Execution result in format:
                       {"success": True, "data": formatted_string, "raw_data": {...}}
                       or
                       {"success": False, "error": "error message"}
    
    Notes:
        - Validates that 'location' argument is provided
        - Defaults unit to "metric" if not supplied
        - Returns both formatted text and raw data
    """
    try:
        # Extract and validate required arguments
        location = tool_arguments.get("location", "").strip()
        if not location:
            logger.error("Weather tool called without location parameter")
            return {
                "success": False,
                "error": "Location parameter is required for weather query"
            }
        
        # Extract optional unit parameter, default to metric (Celsius)
        unit = tool_arguments.get("unit", "metric").lower().strip()
        if unit not in ["metric", "imperial"]:
            logger.warning(f"Invalid unit '{unit}', defaulting to 'metric'")
            unit = "metric"
        
        # Call the weather service to fetch data from OpenWeatherMap
        logger.info(f"Fetching weather for {location} in {unit} units")
        weather_data = fetch_weather_data(location, unit)
        
        # Check if weather data was successfully retrieved
        if not weather_data:
            return {
                "success": False,
                "error": f"Could not fetch weather data for '{location}'. Location may not exist or API limits exceeded."
            }
        
        # Format the raw weather data into a human-readable string
        formatted_weather = format_weather_response(weather_data)
        
        logger.info(f"Successfully executed weather tool for {location}")
        
        # Return both formatted text and raw data for flexibility
        return {
            "success": True,
            "data": formatted_weather,
            "raw_data": weather_data  # Raw data can be useful for advanced processing
        }
        
    except ValueError as e:
        # Handle validation errors in weather parameters
        logger.error(f"Validation error in weather tool: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid weather query parameters: {str(e)}"
        }
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error executing weather tool: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": "An unexpected error occurred while fetching weather data"
        }


def format_tool_result(tool_name: str, tool_result: Dict[str, Any]) -> str:
    """
    Convert tool execution results into a message string for the LLM.
    
    This function takes the structured result from a tool execution and
    formats it into text that can be sent back to the LLM. The LLM uses
    this formatted result to generate a natural response to the user.
    
    Args:
        tool_name (str): The name of the tool that was executed
        tool_result (Dict[str, Any]): The result dictionary from tool execution:
                                     {"success": bool, "data": str, ...}
                                     or
                                     {"success": bool, "error": str, ...}
    
    Returns:
        str: A formatted message containing the tool result for LLM processing.
            - If successful: Returns the data string from the tool
            - If failed: Returns an error message
    
    Example:
        >>> result = execute_tool("weather", {"location": "London"})
        >>> llm_input = format_tool_result("weather", result)
        >>> # llm_input can now be sent to the LLM for response generation
    
    Notes:
        - The formatted result is designed to be clear and concise for LLM processing
        - Error messages are included to provide context when tools fail
        - Each tool type can have custom formatting if needed
    """
    # Check if tool execution was successful
    if tool_result.get("success"):
        # Tool executed successfully - return the data
        data = tool_result.get("data", "No data returned from tool")
        logger.info(f"Successfully formatted result from {tool_name} tool")
        return data
    else:
        # Tool execution failed - return error message
        error = tool_result.get("error", "Unknown error occurred")
        logger.warning(f"Tool {tool_name} returned error: {error}")
        return f"Error from {tool_name} tool: {error}"
