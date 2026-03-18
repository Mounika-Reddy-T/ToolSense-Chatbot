# AI Chatbot Backend

The backend is a FastAPI server that provides the core AI chatbot functionality with tool calling capabilities.

## Overview

The backend handles:
- **LLM Integration**: Connects to OpenRouter to access advanced language models
- **Tool Orchestration**: Manages intelligent function calling (weather API, etc.)
- **Chat Management**: Processes conversations with history management
- **API Communication**: Secure and efficient communication with external APIs

## Project Structure

```
backend/
├── main.py                 # FastAPI application server
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── models/
│   └── schemas.py        # Pydantic data models
├── services/
│   ├── llm_service.py           # OpenRouter LLM integration
│   ├── weather_service.py       # OpenWeatherMap API integration
│   └── tool_orchestrator.py     # Tool calling orchestration
└── utils/
    └── logger.py         # Logging configuration
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- API keys from:
  - [OpenRouter](https://openrouter.io/keys) for LLM access
  - [OpenWeatherMap](https://openweathermap.org/api) for weather data

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy .env template
cp .env.example .env

# Edit .env with your API keys
# Required:
# - OPENROUTER_API_KEY
# - OPENWEATHER_API_KEY
```

### 4. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 5. Access API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation

## API Endpoints

### POST `/api/chat`
Process a user message and get AI response with tool results

**Request:**
```json
{
  "message": "What is the weather in London?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "The current weather in London is...",
  "tool_calls": [],
  "tool_results": [{
    "tool_call_id": "123",
    "tool_name": "get_weather",
    "result": {
      "temperature": 15,
      "humidity": 72
    },
    "is_error": false
  }],
  "conversation_history": [...]
}
```

### GET `/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### GET `/api/models`
Get available LLM models

**Response:**
```json
{
  "current_model": "gpt-3.5-turbo",
  "available_models": ["gpt-3.5-turbo", "mistralai/mistral-7b-instruct"]
}
```

## Code Architecture

### Services

#### LLMService (`services/llm_service.py`)
- Manages OpenRouter API integration
- Handles chat completions with tool definitions
- Manages function calling in conversations
- Error handling and logging

#### WeatherService (`services/weather_service.py`)
- Fetches weather data from OpenWeatherMap
- Supports city name and coordinate-based lookups
- Formats weather data for display
- Handles API errors gracefully

#### ToolOrchestrator (`services/tool_orchestrator.py`)
- Implements the "agentic" pattern
- Detects when LLM requests tool invocation
- Routes tools to handlers
- Feeds results back to LLM for semantic response generation
- Supports multi-iteration conversations (max 3 by default)

### Data Models (`models/schemas.py`)
All request/response models use Pydantic for:
- Type validation
- Automatic documentation
- Clear API contracts

## How Tool Calling Works

1. **User Query**: Frontend sends message to backend
2. **LLM Processing**: Backend sends to LLM with tool definitions
3. **Tool Detection**: LLM decides if tools are needed
4. **Tool Execution**: ToolOrchestrator executes requested tools
5. **Result Feeding**: Tool results sent back to LLM
6. **Final Response**: LLM uses tool results to formulate natural response
7. **Response Return**: Complete response sent to frontend

## Configuration Options

### Environment Variables
- `OPENROUTER_API_KEY`: API key for OpenRouter (required)
- `OPENWEATHER_API_KEY`: API key for OpenWeatherMap (required)
- `BACKEND_HOST`: Server host (default: 0.0.0.0)
- `BACKEND_PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)
- `DEBUG`: Debug mode (default: False)

### Service Configuration
Located in `config.py`:
- LLM model selection
- Temperature control (randomness)
- Max tokens per response
- API base URLs

## Logging

Logs are stored in the `logs/` directory:
- `info_YYYYMMDD.log`: Information and above
- `error_YYYYMMDD.log`: Errors and above

Console output includes color-coded log levels for easy reading.

## Development

### Adding New Tools

1. Create handler in `ToolOrchestrator`:
```python
async def _handle_new_tool(self, arguments):
    # Implementation
    return {"success": True, "data": ...}
```

2. Add to tool handlers map:
```python
self.tool_handlers = {
    "new_tool": self._handle_new_tool
}
```

3. Add tool definition to LLMService:
```python
{
    "type": "function",
    "function": {
        "name": "new_tool",
        "description": "...",
        "parameters": {...}
    }
}
```

### Testing
```bash
# Run with pytest
pytest

# Run with coverage
pytest --cov=.
```

## Error Handling

The backend includes:
- Try-catch blocks for API calls
- Graceful error responses
- Detailed logging for debugging
- Validation of all inputs
- Timeout protection for external APIs

## Performance Considerations

- HTTP connection pooling via httpx.AsyncClient
- Async/await for non-blocking I/O
- Request timeouts to prevent hanging
- Configurable conversation iteration limits
- Efficient JSON serialization

## Troubleshooting

### Missing API Keys
```
ValueError: OPENROUTER_API_KEY environment variable is not set
```
Solution: Add API key to `.env` file

### Connection Errors
Check:
- Network connectivity
- API keys are valid
- CORS configuration if calling from different domain
- Firewall settings

### LLM Errors
- Check OpenRouter API status
- Verify rate limits haven't been exceeded
- Check model availability in your region

## Production Deployment

For production:
1. Set `DEBUG=False`
2. Use a production ASGI server (e.g., Gunicorn)
3. Configure proper CORS origins
4. Use environment-specific `.env` files
5. Enable SSL/HTTPS
6. Monitor logs and errors
7. Set up proper rate limiting
8. Use connection pooling for databases

### Example Gunicorn Command
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Further Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenRouter API Docs](https://openrouter.io/docs)
- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [Pydantic Documentation](https://docs.pydantic.dev/)
