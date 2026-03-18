"""
LLM Service - OpenRouter Integration
====================================

This module handles all communication with language models through the OpenRouter API.
It manages model selection, request formatting, tool availability, and response parsing.

Functions:
    - get_available_tools: Define tools that LLM can invoke (e.g., weather)
    - call_llm: Make requests to OpenRouter with tool support
    - parse_tool_call: Extract tool invocation details from LLM response
"""

import requests
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from utils.logger import setup_logger

# Configure logger for this module
logger = setup_logger(__name__)


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Define the tools available for the LLM to invoke via function calling.
    
    This function returns a list of tool definitions that the LLM can decide to use.
    Each tool is defined with its name, description, and required parameters.
    The LLM will be aware of these tools and can choose to invoke them when appropriate.
    
    Returns:
        List[Dict[str, Any]]: List of tool definitions in OpenAI function-calling format
                            Example structure:
                            [
                                {
                                    "type": "function",
                                    "function": {
                                        "name": "weather",
                                        "description": "Tool for fetching weather information",
                                        "parameters": {...}
                                    }
                                }
                            ]
    
    Notes:
        - Tool names should be lowercase and descriptive
        - Descriptions help the LLM decide when to use the tool
        - Parameters define what the LLM should provide when calling the tool
        - Following OpenAI's function calling schema for compatibility
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "weather",
                "description": (
                    "Fetches current weather information for a specified location. "
                    "Use this when the user asks about weather, temperature, or climate conditions. "
                    "Returns temperature, humidity, wind speed, and weather description."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name or location to get weather for (e.g., 'London', 'New York', 'Tokyo')"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["metric", "imperial"],
                            "description": "Temperature unit: 'metric' for Celsius or 'imperial' for Fahrenheit",
                            "default": "metric"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]


def call_llm(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    tool_results: Optional[str] = None
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Make a request to OpenRouter LLM with optional tool calling support.
    
    This function sends a user message to the LLM through OpenRouter, including
    conversation history and available tools. It handles the LLM's response,
    including any tool invocation decisions.
    
    Args:
        user_message (str): The current user query or message
        conversation_history (Optional[List[Dict[str, str]]]): Previous messages for context.
                                                              Each message is {"role": "user"|"assistant", "content": "..."}
        tool_results (Optional[str]): Results from a previously executed tool call.
                                     When provided, this becomes part of the conversation
                                     to show the LLM what the tool returned.
    
    Returns:
        Tuple[str, Optional[Dict[str, Any]]]: A tuple containing:
            - str: The LLM's text response
            - Optional[Dict[str, Any]]: Tool call information if the LLM decided to invoke a tool,
                                       None if no tool was used. Format:
                                       {"tool_name": "weather", "tool_arguments": {...}}
    
    Raises:
        RuntimeError: If OpenRouter API key is not configured
        requests.RequestException: For network/API errors (logged and handled)
    
    Example:
        >>> reply, tool_call = call_llm("What's the weather in London?")
        >>> if tool_call:
        ...     print(f"LLM wants to use: {tool_call['tool_name']}")
        ... else:
        ...     print(f"LLM replied: {reply}")
    
    Notes:
        - Model: gpt-4-turbo (via OpenRouter)
        - Tools: Weather function is available for the LLM to invoke
        - Temperature: Set to 0.7 for balanced creativity and consistency
        - Handles both cases: LLM responds directly or LLM chooses to call a tool
    """
    # Retrieve API configuration from environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable is not set")
        raise RuntimeError("OpenRouter API key not configured")
    
    # Define the API endpoint for OpenRouter
    # OpenRouter provides access to multiple LLM models
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Build the request headers with authentication
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # OpenRouter requires these headers for compatibility
        "HTTP-Referer": "http://localhost",
        "X-Title": "External Bot Chatbot"
    }
    
    # Initialize message list with conversation history or empty list
    messages = conversation_history.copy() if conversation_history else []
    
    # If tool previously returned results, add them as a system message
    # This helps the LLM understand the context of what happened
    if tool_results:
        messages.append({
            "role": "user",
            "content": f"Tool execution result:\n{tool_results}\n\nBased on this information, provide a natural response to the user's original query."
        })
    
    # Add the current user message to the conversation
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Construct the request payload for the LLM API
    request_payload = {
        # Use GPT-4 Turbo model for best reasoning and comprehension
        "model": "openai/gpt-4-turbo",
        "messages": messages,
        # Enable function calling so the LLM can invoke tools
        "tools": get_available_tools(),
        "tool_choice": "auto",  # Let the model decide whether to use tools
        # Temperature controls randomness (0=deterministic, 1=creative)
        # 0.7 is a good balance between consistency and variety
        "temperature": 0.7,
        # Maximum tokens to generate in the response (prevents very long outputs)
        "max_tokens": 512
    }
    
    try:
        # Log the LLM request for debugging
        logger.info(f"Calling LLM with user message: {user_message[:100]}...")
        
        # Make the HTTP POST request to OpenRouter
        response = requests.post(url, json=request_payload, headers=headers, timeout=30)
        
        # Raise exception if HTTP request failed (4xx or 5xx errors)
        response.raise_for_status()
        
        # Parse the JSON response
        response_data = response.json()
        
        # Extract the first choice's message (LLM response)
        message = response_data.get("choices", [{}])[0].get("message", {})
        assistant_text = message.get("content") or ""
        
        # Check if the LLM decided to invoke a tool
        # Tool calls appear in the "tool_calls" field of the response
        tool_calls = message.get("tool_calls", [])
        
        # Process tool call if present
        tool_call_info = None
        if tool_calls:
            # Extract the first tool call (there's usually only one per response)
            tool_call = tool_calls[0]
            tool_name = tool_call.get("function", {}).get("name")
            tool_arguments_str = tool_call.get("function", {}).get("arguments", "{}")
            
            try:
                # Parse the tool arguments from JSON string
                tool_arguments = json.loads(tool_arguments_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse tool arguments: {tool_arguments_str}")
                tool_arguments = {}
            
            # Package tool call information for return
            tool_call_info = {
                "tool_name": tool_name,
                "tool_arguments": tool_arguments
            }
            
            logger.info(f"LLM decided to use tool: {tool_name} with args: {tool_arguments}")
        else:
            logger.info("LLM responded directly without tool invocation")
        
        # Return both the text response and tool call information (if any)
        return assistant_text, tool_call_info
        
    except requests.exceptions.Timeout:
        # Handle request timeout (took too long to respond)
        logger.error("OpenRouter API request timeout")
        error_msg = "The LLM service took too long to respond. Please try again."
        return error_msg, None
        
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (API errors, authentication failures, rate limits)
        logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
        error_msg = f"Error from LLM service: {e.response.status_code}"
        return error_msg, None
        
    except requests.exceptions.RequestException as e:
        # Handle network errors or other request-related issues
        logger.error(f"Error calling OpenRouter API: {str(e)}")
        error_msg = "Network error while connecting to LLM service."
        return error_msg, None
        
    except (KeyError, IndexError, TypeError) as e:
        # Handle unexpected response structure
        logger.error(f"Unexpected response structure from OpenRouter: {str(e)}")
        error_msg = "Unexpected response format from LLM service."
        return error_msg, None


def parse_tool_call(response_text: str, tool_call_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse and validate tool call information from LLM response.
    
    This function takes the tool call data from the LLM and ensures it's
    properly formatted for execution. It validates the tool name and arguments.
    
    Args:
        response_text (str): The text response from the LLM (for logging)
        tool_call_info (Optional[Dict[str, Any]]): Raw tool call information from LLM
    
    Returns:
        Dict[str, Any]: Validated and formatted tool call information:
                       {"tool_name": "...", "tool_arguments": {...}}
                       Returns empty dict if no valid tool call
    
    Example:
        >>> tool_call = parse_tool_call(response_text, raw_tool_info)
        >>> if tool_call:
        ...     execute_tool(tool_call["tool_name"], tool_call["tool_arguments"])
    
    Notes:
        - Returns empty dict if tool_call_info is None or invalid
        - Validates tool name is in list of available tools
        - Handles missing or malformed arguments gracefully
    """
    # Return empty dict if no tool call information provided
    if not tool_call_info:
        return {}
    
    # Validate that the tool call has required fields
    if not isinstance(tool_call_info, dict):
        logger.warning("Tool call info is not a dictionary")
        return {}
    
    tool_name = tool_call_info.get("tool_name", "").lower().strip()
    tool_arguments = tool_call_info.get("tool_arguments", {})
    
    # Validate tool name is in allowed list
    allowed_tools = ["weather"]
    if tool_name not in allowed_tools:
        logger.warning(f"Unknown tool requested: {tool_name}")
        return {}
    
    # Validate that tool_arguments is a dictionary
    if not isinstance(tool_arguments, dict):
        logger.warning(f"Tool arguments for {tool_name} are not a dictionary")
        return {}
    
    # Return validated tool call information
    return {
        "tool_name": tool_name,
        "tool_arguments": tool_arguments
    }
