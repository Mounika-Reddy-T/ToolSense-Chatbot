"""
FastAPI Backend - Main Application Entry Point
==============================================

This is the main application file that sets up the FastAPI server, configures routes,
handles CORS, and orchestrates the AI chatbot functionality. It receives user queries
from the frontend, processes them through the LLM and tool orchestrator, and returns
structured responses.

Architecture:
    1. Frontend sends user message and conversation history
    2. Backend receives request in /chat endpoint
    3. LLM service checks if weather data is needed
    4. If needed, tool orchestrator fetches weather data
    5. LLM generates final response using tool data
    6. Response is sent back to frontend

Key Endpoints:
    - POST /chat: Process user messages and return AI responses
    - GET /health: Health check endpoint
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

# Import configuration
from config import (
    SERVER_HOST, SERVER_PORT, CORS_ORIGINS, DEBUG, LOG_LEVEL, ENV
)

# Import models and schemas for request/response validation
from models.schemas import ChatRequest, ChatResponse, ErrorResponse

# Import services for LLM and tool execution
from services.llm_service import call_llm, parse_tool_call
from services.tool_orchestrator import execute_tool, format_tool_result

# Import logger
from utils.logger import setup_logger

# Configure logger for this module
logger = setup_logger(__name__)


# ==================== APPLICATION LIFESPAN MANAGEMENT ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events using modern lifespan context manager.
    
    This replaces the deprecated @app.on_event() decorators with the modern
    FastAPI lifespan pattern. The code before 'yield' runs on startup,
    and code after 'yield' runs on shutdown.
    
    Useful for:
    - Startup: Initializing connections, loading configuration, validation checks
    - Shutdown: Closing connections, cleanup operations, flushing logs
    
    See: https://fastapi.tiangolo.com/advanced/events/
    """
    # ==================== STARTUP CODE ====================
    logger.info("=" * 50)
    logger.info("External Bot Backend Starting...")
    logger.info(f"Environment: {ENV}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info(f"Server: {SERVER_HOST}:{SERVER_PORT}")
    logger.info("=" * 50)
    
    yield  # Application runs between startup and shutdown
    
    # ==================== SHUTDOWN CODE ====================
    logger.info("External Bot Backend Shutting Down...")


# ==================== FASTAPI APPLICATION SETUP ====================

# Create FastAPI application instance with lifespan management
# The FastAPI framework handles HTTP routing and automatic API documentation
# The lifespan parameter manages startup and shutdown events
app = FastAPI(
    title="External Bot - AI Chatbot",
    description="A full-stack AI chatbot with LLM reasoning and external tool integration",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation at /docs
    redoc_url="/redoc",  # ReDoc documentation at /redoc
    lifespan=lifespan  # Modern lifespan event handler (replaces deprecated on_event)
)

# Configure CORS middleware to allow frontend to communicate with backend
# CORS (Cross-Origin Resource Sharing) is needed because frontend and backend
# run on different ports during development
app.add_middleware(
    CORSMiddleware,
    # List of allowed origins that can make requests to this backend
    allow_origins=CORS_ORIGINS,
    # Allow credentials (cookies, authorization headers) in cross-origin requests
    allow_credentials=True,
    # Allowed HTTP methods for cross-origin requests
    allow_methods=["*"],
    # Allowed headers in cross-origin requests
    allow_headers=["*"],
    # How long browsers can cache CORS preflight responses (in seconds)
    max_age=600
)

logger.info(f"Backend initialized in {ENV} mode")


# ==================== HEALTH CHECK ENDPOINT ====================

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify the backend is running.
    
    This simple endpoint is useful for:
    - Load balancers to check if the service is alive
    - Monitoring systems to verify uptime
    - Frontend to confirm backend connectivity
    
    Returns:
        dict: Status information with service state and environment
    
    Example Response:
        {
            "status": "healthy",
            "service": "External Bot API",
            "environment": "development"
        }
    """
    logger.debug("Health check endpoint called")
    return {
        "status": "healthy",
        "service": "External Bot API",
        "environment": ENV
    }


# ==================== MAIN CHAT ENDPOINT ====================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process user chat messages and return AI responses with optional tool invocation.
    
    This is the main endpoint that handles the entire chat flow:
    1. Receives user message and conversation history
    2. Sends to LLM with available tools
    3. If LLM requests a tool, executes it
    4. Sends tool result back to LLM for final response
    5. Returns final response to frontend
    
    Args:
        request (ChatRequest): Request body containing:
            - user_message: Current user query
            - conversation_history: Previous chat messages (optional)
    
    Returns:
        ChatResponse: Response containing:
            - assistant_reply: The LLM's text response
            - tool_used: Name of tool invoked, if any
            - tool_result: Data from tool execution, if any
            - reasoning: Why the LLM chose to use/not use a tool
    
    Raises:
        HTTPException: If an error occurs during processing
    
    Example Request:
        {
            "user_message": "What's the weather in London?",
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
    
    Example Response (with tool use):
        {
            "assistant_reply": "The weather in London is...",
            "tool_used": "weather",
            "tool_result": {"success": true, "data": "..."},
            "reasoning": "User asked about weather, so I used the weather tool..."
        }
    
    Notes:
        - Conversation history helps the LLM maintain context across messages
        - The LLM can decide whether to use tools or respond directly
        - All errors are caught and returned as user-friendly error messages
    """
    try:
        # Extract user message and conversation history from request
        user_message = request.user_message.strip()
        conversation_history = request.conversation_history or []
        
        # Log user message for debugging and monitoring
        logger.info(f"Received chat message: {user_message[:100]}...")
        
        # ========== STEP 1: SEND TO LLM WITH TOOLS AVAILABLE ==========
        # The LLM receives the user message and sees available tools (weather)
        # It decides whether to invoke a tool or respond directly
        logger.debug("Calling LLM service...")
        
        assistant_reply, tool_call_info = call_llm(
            user_message=user_message,
            conversation_history=_convert_history_to_messages(conversation_history),
            tool_results=None  # No previous tool results on first call
        )
        
        # ========== STEP 2: CHECK IF LLM WANTS TO USE A TOOL ==========
        tool_used = None
        tool_result = None
        tool_result_formatted = None
        
        if tool_call_info:
            logger.info(f"LLM decided to use tool: {tool_call_info.get('tool_name')}")
            
            # Parse and validate the tool call information
            validated_tool_call = parse_tool_call(assistant_reply, tool_call_info)
            
            if validated_tool_call:
                tool_name = validated_tool_call["tool_name"]
                tool_arguments = validated_tool_call["tool_arguments"]
                
                # ========== STEP 3: EXECUTE THE TOOL ==========
                logger.debug(f"Executing tool: {tool_name} with arguments: {tool_arguments}")
                
                tool_result = execute_tool(tool_name, tool_arguments)
                tool_used = tool_name
                
                if tool_result:
                    # ========== STEP 4: FORMAT TOOL RESULT FOR LLM ==========
                    tool_result_formatted = format_tool_result(tool_name, tool_result)
                    logger.debug(f"Tool result: {tool_result_formatted[:100]}...")
                    
                    # ========== STEP 5: SEND TOOL RESULT BACK TO LLM ==========
                    # The LLM now has the actual data and can generate a final response
                    logger.debug("Calling LLM again with tool results...")
                    
                    assistant_reply, _ = call_llm(
                        user_message=user_message,
                        conversation_history=_convert_history_to_messages(conversation_history),
                        tool_results=tool_result_formatted
                    )
                    if not assistant_reply:
                        assistant_reply = tool_result_formatted
        
        # ========== STEP 6: PREPARE AND RETURN RESPONSE ==========
        # Create the response object with all relevant information
        response = ChatResponse(
            assistant_reply=assistant_reply or "",
            tool_used=tool_used,
            tool_result=tool_result,
            reasoning=(
                f"LLM analyzed the query and determined that "
                f"{'a tool was needed' if tool_used else 'no tools were needed'}"
            )
        )
        
        logger.info(f"Successfully processed chat message")
        return response
        
    except ValueError as e:
        # Handle validation errors (e.g., missing required fields)
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
        
    except RuntimeError as e:
        # Handle configuration errors (e.g., missing API keys)
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error. Please contact administrator."
        )
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )


# ==================== HELPER FUNCTIONS ====================

def _convert_history_to_messages(conversation_history) -> list:
    """
    Convert conversation history from ChatMessage schema to message format for LLM.
    
    This helper function transforms the ChatMessage objects from the request
    into a format that the LLM service expects.
    
    Args:
        conversation_history: List of ChatMessage objects or dicts from request
    
    Returns:
        list: List of message dicts in format [{"role": "...", "content": "..."}, ...]
    """
    if not conversation_history:
        return []
    
    messages = []
    for msg in conversation_history:
        # Handle both ChatMessage objects and plain dictionaries
        if hasattr(msg, 'role') and hasattr(msg, 'content'):
            messages.append({"role": msg.role, "content": msg.content})
        elif isinstance(msg, dict):
            messages.append(msg)
    
    return messages


# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    """
    Entry point for running the application directly.
    
    Usage:
        python main.py
    
    This starts the FastAPI development server with:
    - Auto-reload enabled (refreshes on code changes) when DEBUG=True
    - Detailed error messages
    - Access to /docs for API documentation
    
    Note: When reload is enabled, the app must be passed as an import string
    ("main:app") to allow uvicorn to reload the module on code changes.
    """
    import uvicorn
    
    logger.info(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    
    # When DEBUG mode is enabled and reload is True, we need to pass the app
    # as an import string ("main:app") instead of the app object.
    # This allows uvicorn to properly reload the module on code changes.
    if DEBUG:
        # Use import string format for reload capability
        uvicorn.run(
            "main:app",  # Import string format required for reload
            host=SERVER_HOST,
            port=SERVER_PORT,
            reload=True,  # Enable auto-reload on code changes
            log_level=LOG_LEVEL.lower()
        )
    else:
        # In production, pass the app object directly (reload not needed)
        uvicorn.run(
            app,  # Direct app object for production
            host=SERVER_HOST,
            port=SERVER_PORT,
            reload=False,  # Disable reload in production
            log_level=LOG_LEVEL.lower()
        )
