"""
Data Models and Request/Response Schemas
==========================================

This module defines all the Pydantic schemas used for request validation and response formatting
throughout the API. These schemas ensure type safety and provide automatic API documentation.

Key Components:
    - WeatherToolInput: Schema for weather query parameters
    - ChatMessage: Schema for individual chat messages
    - ChatRequest: Schema for incoming chat requests
    - ChatResponse: Schema for chat responses with reasoning
    - ToolCall: Schema for tool invocation data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum


class ToolType(str, Enum):
    """
    Enumeration of available tool types that the LLM can invoke.
    
    Attributes:
        WEATHER: Tool for retrieving weather information
    """
    WEATHER = "weather"


class WeatherToolInput(BaseModel):
    """
    Schema for weather tool input parameters.
    
    This schema validates the parameters needed to query the weather API.
    The LLM will parse its decisions into this format when deciding to fetch weather data.
    
    Attributes:
        location (str): The city name or coordinates to get weather for (e.g., "London", "New York")
        unit (str, optional): Temperature unit - "metric" (Celsius) or "imperial" (Fahrenheit).
                            Defaults to "metric"
    """
    location: str = Field(..., description="City name or location identifier for weather query")
    unit: str = Field(default="metric", description="Temperature unit: 'metric' or 'imperial'")


class ChatMessage(BaseModel):
    """
    Schema for individual chat messages in conversation history.
    
    Attributes:
        role (str): The sender of the message - either "user" or "assistant"
        content (str): The actual message content text
    """
    role: str = Field(..., description="Message sender: 'user' or 'assistant'")
    content: str = Field(..., description="The message text content")


class ToolCall(BaseModel):
    """
    Schema for representing a tool call made by the LLM.
    
    When the LLM decides to use a tool (like weather), this schema captures
    the tool information and its arguments.
    
    Attributes:
        tool_name (str): Name of the tool to invoke (e.g., "weather")
        tool_arguments (Dict[str, Any]): Dictionary of arguments to pass to the tool
                                        (e.g., {"location": "London", "unit": "metric"})
    """
    tool_name: str = Field(..., description="Name of the tool to invoke")
    tool_arguments: Dict[str, Any] = Field(..., description="Tool arguments as a dictionary")


class ChatRequest(BaseModel):
    """
    Schema for incoming chat requests from the frontend.
    
    This validates the structure of user queries sent to the API. Each request
    can include chat history to maintain conversation context.
    
    Attributes:
        user_message (str): The current user query/input
        conversation_history (List[ChatMessage], optional): Previous messages in the conversation
                                                            to maintain context for the LLM
    """
    user_message: str = Field(..., description="The current user query or message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous chat messages for context (optional)"
    )


class ChatResponse(BaseModel):
    """
    Schema for the chat response sent back to the frontend.
    
    This response includes the assistant's reply, reasoning about tool use,
    and any retrieved data from external APIs.
    
    Attributes:
        assistant_reply (str): The natural language response from the LLM
        tool_used (str, optional): Name of the tool invoked, if any (e.g., "weather")
        tool_result (Dict[str, Any], optional): Data returned from the tool execution
        reasoning (str, optional): The LLM's reasoning about whether to use a tool
    """
    assistant_reply: str = Field(..., description="The LLM's response message")
    tool_used: Optional[str] = Field(default=None, description="Tool that was invoked, if any")
    tool_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Data returned from tool execution"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="LLM's reasoning about tool usage decision"
    )


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    
    Used when an error occurs during request processing to provide clear
    error information to the frontend.
    
    Attributes:
        error (str): Description of the error that occurred
        details (str, optional): Additional details about the error
    """
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(default=None, description="Additional error details")
