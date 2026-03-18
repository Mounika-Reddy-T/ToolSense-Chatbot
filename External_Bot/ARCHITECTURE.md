# Architecture Documentation

## System Design Overview

This document explains the architectural decisions, design patterns, and system structure of the AI Chatbot application.

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Agentic Pattern](#agentic-pattern)
3. [Service-Oriented Architecture](#service-oriented-architecture)
4. [Data Flow](#data-flow)
5. [Design Patterns](#design-patterns)
6. [Security Architecture](#security-architecture)
7. [Scalability Considerations](#scalability-considerations)

## High-Level Architecture

### Three-Tier Architecture

```
┌────────────────────────────────────────────────────────┐
│                   PRESENTATION TIER                     │
│         (Frontend: HTML, CSS, JavaScript)               │
│  - Chat Interface                                       │
│  - Message Display                                      │
│  - User Input Handling                                  │
│  - Real-time UI Updates                                │
└────────────────┬─────────────────────────────────────┘
                 │ HTTP/REST API
                 │
┌────────────────▼─────────────────────────────────────┐
│                  BUSINESS LOGIC TIER                   │
│         (Backend: FastAPI, Services, Orchestration)    │
│  - Request Routing                                     │
│  - Tool Orchestration                                  │
│  - Conversation Management                             │
│  - LLM Integration                                     │
│  - API Error Handling                                  │
└────────────────┬─────────────────────────────────────┘
                 │ HTTP/REST APIs
                 │
┌────────────────▼─────────────────────────────────────┐
│                   EXTERNAL SERVICES TIER               │
│    (Third-party APIs, Data Sources)                    │
│  - OpenRouter LLM API                                  │
│  - OpenWeatherMap API                                  │
│  - Future: News API, Stock API, Database, etc.         │
└────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                               │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────────┐   │
│  │  index.html  │  │ styles.css │  │  script.js       │   │
│  │ (Structure)  │  │ (Styling)  │  │ (Logic/API Comm) │   │
│  └──────────────┘  └────────────┘  └──────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                    HTTP/JSON
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                      BACKEND (FastAPI)                      │
│  ┌──────────────────┐                                       │
│  │  main.py         │  ← Main Application & Routing        │
│  ├──────────────────┤                                       │
│  │  SERVICES LAYER  │                                       │
│  ├──────────────────┤                                       │
│  │ llm_service.py   │──→ OpenRouter API                    │
│  │ weather_service │──→ OpenWeatherMap API                │
│  │ tool_orchestr.py │──→ Handles Tool Calling Logic       │
│  ├──────────────────┤                                       │
│  │  DATA LAYER      │                                       │
│  ├──────────────────┤                                       │
│  │ schemas.py      │ ← Pydantic Models (Validation)       │
│  │ logger.py       │ ← Logging System                     │
│  │ config.py       │ ← Configuration Management            │
│  └──────────────────┘                                       │
└──────────┬─────────────────────────────────────────────────┘
           │
     ┌─────┴────────┬─────────────────┐
     │              │                 │
     ▼              ▼                 ▼
┌─────────────┐ ┌─────────────┐  ┌──────────────┐
│ OpenRouter  │ │ OpenWeather │  │ Future Tools │
│ (LLM)       │ │ (Weather)   │  │ (News, Stock)│
└─────────────┘ └─────────────┘  └──────────────┘
```

## Agentic Pattern

The system implements the **Agentic Pattern** - a loop where an AI agent can make decisions, invoke tools, and iterate.

### The Agentic Loop

```
Step 1: USER MESSAGE
   Input: "What's the weather in London?"
   
Step 2: LLM DECISION
   LLM: "I need current weather data"
   Decision: Tool calling needed
   
Step 3: TOOL INVOCATION
   Tool: get_weather(city="London")
   
Step 4: TOOL EXECUTION
   Result: {temperature: 15, humidity: 72, ...}
   
Step 5: FEEDBACK TO LLM
   Provide tool result to LLM
   
Step 6: RESPONSE GENERATION
   LLM: "The weather in London is 15°C..."
   
Step 7: USER SEES RESPONSE
   Display with tool results and formatted data
```

### Why This Pattern?

**Advantages:**
- ✓ LLM decides when tools are needed (not hardcoded rules)
- ✓ Combines LLM reasoning with real data
- ✓ Natural, conversational responses
- ✓ Scalable (add new tools without changing core logic)
- ✓ More accurate than LLM alone

**Example Without Tool Calling (Bad):**
```
User: "What's the weather?"
LLM: "I don't have access to real-time weather data"
Result: User must find weather elsewhere
```

**Example With Tool Calling (Good):**
```
User: "What's the weather?"
LLM: "Let me check" [calls tool]
LLM: "The weather is 15°C and cloudy"
Result: Complete, accurate response
```

## Service-Oriented Architecture

### Four Core Services

#### 1. LLMService
**Responsibility**: Handle all LLM interactions
```python
class LLMService:
    # Purpose: Encapsulate OpenRouter API logic
    
    async def chat_completion(messages, enable_tools):
        # Delegate: Send messages to OpenRouter
        # Return: LLM response with optional tool calls
        
    def _get_tool_definitions():
        # Define: What tools LLM can use
        # Return: Tool definitions for LLM
```

**Why separate?**
- Changes to OpenRouter API only affect one file
- Can swap LLM providers easily
- Testable in isolation
- Reusable across projects

#### 2. WeatherService
**Responsibility**: Handle weather API interactions
```python
class WeatherService:
    # Purpose: Encapsulate OpenWeatherMap API logic
    
    async def get_current_weather(city, country_code):
        # Delegate: Fetch weather data
        # Return: Formatted weather information
        
    def format_weather_response(data):
        # Transform: Raw API data to readable format
        # Return: User-friendly string
```

**Why separate?**
- Weather logic isolated from chat logic
- Easy to add weather features (forecasts, alerts, etc.)
- Can use different weather API
- Reusable in other applications

#### 3. ToolOrchestrator
**Responsibility**: Manage tool calling workflow
```python
class ToolOrchestrator:
    # Purpose: Orchestrate tool calls and LLM interaction
    
    async def process_chat_with_tools(message, history):
        # Loop: Send to LLM, check for tools, execute, repeat
        # Return: Final response with tool results
        
    async def execute_tools(tool_calls):
        # Delegate: Route tools to handlers
        # Return: All tool results
        
    async def _handle_get_weather(arguments):
        # Specific: Handle weather tool calls
        # Return: Weather data
```

**Why separate?**
- Handles complex orchestration logic cleanly
- Tool handlers in one place
- Easy to add new tools
- Central point for iteration control

#### 4. Logger (Utils)
**Responsibility**: Structured logging for debugging
```python
def setup_logger(name, log_level):
    # Purpose: Configure consistent logging
    # Return: Logger instance with handlers
```

**Why separate?**
- Consistent logging across application
- Easy to change log format/destinations
- Debug and error separation
- Color-coded console output

### Service Interaction Pattern

```
Request → main.py (FastAPI)
           ↓
    tool_orchestrator.process_chat_with_tools()
           ↓
    ┌──────┴──────────┐
    ▼                 ▼
llm_service.      weather_service.
chat_completion   get_current_weather
    ↓                 ↓
OpenRouter API    OpenWeather API
    ↓                 ↓
    └──────┬──────────┘
           ▼
    Response → main.py (FastAPI)
           ↓
     Frontend
```

## Data Flow

### Complete Message Flow

```
┌─ FRONTEND ────────────────────────────────────────┐
│                                                    │
│  User Types: "What's the weather?"                │
│       ↓                                            │
│  Input Validation: Not empty ✓                    │
│       ↓                                            │
│  Display User Message in UI                       │
│       ↓                                            │
│  Create ChatRequest:                              │
│  {                                                │
│    "message": "What's the weather?",              │
│    "conversation_history": [...]                  │
│  }                                                │
│       │                                            │
│       │ POST /api/chat (JSON)                    │
│       ▼                                            │
└────────────────────────────────────────────────────┘

┌─ BACKEND ─────────────────────────────────────────┐
│                                                    │
│  Receive Request → main.py                        │
│       ↓                                            │
│  Validate Input (Pydantic)                        │
│       ↓                                            │
│  tool_orchestrator.process_chat_with_tools()     │
│       ↓                                            │
│  ┌─ ITERATION 1 ───────────────────────────┐    │
│  │                                           │    │
│  │  Add user message to history             │    │
│  │       ↓                                   │    │
│  │  llm_service.chat_completion()           │    │
│  │       │                                   │    │
│  │       │ Send messages + tool defs to     │    │
│  │       │ OpenRouter API                    │    │
│  │       ▼                                   │    │
│  │  Receive: response + tool_calls         │    │
│  │       ↓                                   │    │
│  │  Check: Any tool calls? YES              │    │
│  │       ↓                                   │    │
│  │  execute_tools(tool_calls)               │    │
│  │       ├─ Tool: get_weather               │    │
│  │       │  Arguments: {city: "London"}     │    │
│  │       │       ↓                           │    │
│  │       │  weather_service.get_...weather()│    │
│  │       │       │                           │    │
│  │       │       │ Call OpenWeatherMap API  │    │
│  │       │       ▼                           │    │
│  │       │  Result: {temp: 15, humidity: ...}    │
│  │       │                                  │    │
│  │       └─ Return: [ToolResult]             │    │
│  │       ↓                                   │    │
│  │  Add tool results to messages             │    │
│  │  Add assistant's empty message            │    │
│  │       ↓                                   │    │
│  │  Continue? (max 3 iterations) → YES     │    │
│  └─────────────────────────────────────────┘    │
│       ↓                                            │
│  ┌─ ITERATION 2 ───────────────────────────┐    │
│  │                                           │    │
│  │  llm_service.chat_completion() [AGAIN]   │    │
│  │       │ With tool results now included   │    │
│  │       ▼                                   │    │
│  │  LLM has weather data                    │    │
│  │  Generates natural response               │    │
│  │       ↓                                   │    │
│  │  Response: "The weather in London..."    │    │
│  │  tool_calls: [] (no more calls)          │    │
│  │  finish_reason: "stop"                   │    │
│  │       ↓                                   │    │
│  │  Add response to messages                 │    │
│  │  break (no more iterations)               │    │
│  │                                           │    │
│  └─────────────────────────────────────────┘    │
│       ↓                                            │
│  Build ChatResponse:                              │
│  {                                                │
│    "response": "The weather in London...",       │
│    "tool_calls": [{id, name, args}],             │
│    "tool_results": [{id, name, result}],         │
│    "conversation_history": [...]                 │
│  }                                                │
│       ↓                                            │
│  Return JSON Response                             │
│       │                                            │
│       │ HTTP 200 (JSON)                           │
│       ▼                                            │
└────────────────────────────────────────────────────┘

┌─ FRONTEND ────────────────────────────────────────┐
│                                                    │
│  Receive ChatResponse JSON                        │
│       ↓                                            │
│  Parse Response                                   │
│       ↓                                            │
│  Display Bot Message: "The weather in London..."  │
│       ↓                                            │
│  Display Tool Badge: 🔧 get_weather               │
│       ↓                                            │
│  Format & Display Tool Results:                   │
│  ┌─────────────────────────────┐                 │
│  │ Temperature:     15°C        │                 │
│  │ Feels Like:      13°C        │                 │
│  │ Humidity:        72%         │                 │
│  │ Pressure:        1013 hPa    │                 │
│  │ Condition:       Partly...   │                 │
│  │ Location:        London, UK  │                 │
│  └─────────────────────────────┘                 │
│       ↓                                            │
│  Update Conversation History (Client-side)        │
│       ↓                                            │
│  User Can Now Send Next Message                   │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Dependency Injection

**In Backend:**
```python
def __init__(self, llm_service, weather_service):
    self.llm_service = llm_service      # Injected
    self.weather_service = weather_service  # Injected
```

**Why:**
- Easy to test (pass mock services)
- Loosely coupled
- Easy to swap implementations

### 2. Strategy Pattern (Service Implementations)

Each service implements different strategies for same interface:
```python
class LLMService:
    async def chat_completion(...):  # Strategy for LLM access

class WeatherService:
    async def get_current_weather(...):  # Strategy for weather
```

**Why:**
- Interchangeable implementations
- Easy to add new providers
- Clean separation of concerns

### 3. Observer Pattern (Conversation History)

Frontend observes backend responses and updates UI:
```javascript
// Frontend: Observes API response
const response = await fetch(...);
// Upon response: Update UI (observe pattern)
displayMessage(response.data);
```

**Why:**
- Decoupled UI from API
- Easy to add new UI reactions
- Clean event-driven flow

### 4. Factory Pattern (Message Creation)

```javascript
// Factory for creating message elements
function createMessageElement(content, role) {
    // Creates and returns message DOM element
}
```

**Why:**
- Centralized creation logic
- Easy to modify message structure
- Reusable message creation

### 5. Singleton Pattern (Services)

```python
# Global service instances created once at startup
llm_service = LLMService()  # Created once
weather_service = WeatherService()  # Created once

# Used throughout application lifetime
```

**Why:**
- One connection pool to OpenRouter
- One connection pool to OpenWeatherMap
- Efficient resource usage

### 6. Template Method Pattern (Request Handling)

```python
# Common flow for all service calls
1. Validate input
2. Make API call
3. Parse response
4. Handle errors
5. Return formatted result
```

**Why:**
- Consistent error handling
- Predictable flow
- Easy to maintain

## Security Architecture

### Input Validation Layer

```
User Input
    ↓
JavaScript Validation (Client-side)
    ├─ Check not empty
    ├─ Check length limits
    └─ Sanitize HTML entities
    ↓
Backend Validation (Pydantic)
    ├─ Type checking
    ├─ Range validation
    └─ Required field checking
    ↓
LLM Service Validation
    ├─ Token limit checking
    └─ Content safety (future)
    ↓
Tool Input Validation
    ├─ Parameter validation
    └─ Range checking
    ↓
Approved for Processing
```

### API Communication Security

```
Frontend → HTTPS/TLS → Backend
                ↓
        Backend Validates:
        ├─ CORS headers
        ├─ Content-Type
        ├─ API key presence (for external APIs)
        └─ Request signature (optional)
                ↓
        Backend → HTTPS/TLS → External APIs
                ↓
        Response Validation:
        ├─ Status code check
        ├─ Content-Type check
        ├─ Payload sanity check
        └─ Size limit check
                ↓
        Backend → HTTPS/TLS → Frontend
                ↓
        Frontend:
        ├─ HTML escape all content
        ├─ Type check response
        └─ Display safely
```

### Error Handling Security

```
Error Occurs
    ↓
Log Full Details (Server-side only, in logs/)
    ├─ Stack trace
    ├─ Request data
    ├─ System state
    └─ Timestamps
    ↓
Generate User-Safe Response
    ├─ No stack trace
    ├─ No system details
    ├─ No file paths
    ├─ Generic error message
    └─ Time to contact support
    ↓
Send to User
    │
    └─ [DEBUG mode: Full error details sent]
```

## Scalability Considerations

### Current Architecture (Single Server)

```
Frontend (Static)       Backend Server        External APIs
    ↓                        ↓                    ↓
HTML/CSS/JS        FastAPI App (1)   OpenRouter, OpenWeather
                   - Sync requests  
                   - In-memory history
                   - No persistence
```

### Scalable Architecture (Future)

```
┌──────────────────────────────────────────────────────────────┐
│                    CDN / Load Balancer                         │
└─────────────────┬──────────────────────────┬──────────────────┘
                  │                          │
            ┌─────▼─────┐            ┌──────▼──────┐
            │ Backend 1  │            │  Backend 2  │
            ├────────────┤            ├─────────────┤
            │ FastAPI    │ ◄─────────►│ FastAPI     │
            │ Instance   │   Redis    │ Instance    │
            └─────┬──────┘  Cache     └──────┬──────┘
                  │                          │
            ┌─────▼─────────────────────────▼─────┐
            │         Shared Cache (Redis)        │
            │  - Conversation history             │
            │  - Session data                     │
            │  - Rate limiting                    │
            └─────┬──────────────────────────────┘
                  │
            ┌─────▼──────────────────────┐
            │    Database (PostgreSQL)   │
            │  - Persistent storage      │
            │  - User data               │
            │  - Conversation history    │
            └────────────────────────────┘
```

### Scalability Strategies

**Horizontal Scaling:**
1. Add multiple backend instances
2. Use load balancer (nginx, AWS ELB)
3. Cache conversation history in Redis
4. Store persistent data in database

**Vertical Scaling:**
1. Increase server resources (CPU, memory)
2. Optimize database queries
3. Use connection pooling

**Database Scaling:**
1. Read replicas for queries
2. Write master for writes
3. Sharding by user ID or conversation ID

**Caching Strategy:**
```
User Request
    ↓
Check Redis Cache
    ├─ Hit → Return cached result
    └─ Miss → Fetch from API
    ↓
Update Cache
    ↓
Return to User
```

### Performance Optimization Roadmap

1. **Implement conversation storage** (database)
2. **Add caching layer** (Redis)
3. **Database indexing** (faster queries)
4. **Connection pooling** (reduce overhead)
5. **API response caching** (don't call same API twice)
6. **Conversation summarization** (reduce context size)
7. **WebSocket support** (real-time updates)
8. **GraphQL endpoint** (query optimization)

## Concurrency Model

### Backend (Python Async)

The FastAPI backend uses **async/await** for concurrency:

```python
# Async allows many requests to be handled concurrently
async def chat_endpoint(request):
    # While waiting for OpenRouter API response,
    # other requests can be processed
    response = await llm_service.chat_completion(messages)
```

**Benefits:**
- Handle 1000s of concurrent requests
- Single-threaded (GIL not an issue)
- Better than synchronous
- Event-driven

### Frontend (JavaScript Event Loop)

The frontend uses **event-driven** concurrency:

```javascript
// Event listener for submit
asyncform.addEventListener('submit', async (e) => {
    // Async fetch doesn't block UI
    const response = await fetch(...);
    // UI remains responsive
});
```

**Benefits:**
- Non-blocking API calls
- UI remains responsive
- Promise-based async

## Monitoring and Observability

### Logging Strategy

```
┌─────────────────────────────────────┐
│        Application Events           │
└────────────┬────────────────────────┘
             │
       ┌─────┴─────┐
       │            │
       ▼            ▼
   INFO LOGS    ERROR LOGS
       │            │
       ▼            ▼
logs/info_...  logs/error_...
```

**Log Levels:**
- DEBUG: Detailed info for developers
- INFO: Normal application flow
- WARNING: Something unexpected
- ERROR: Error occurred, action needed
- CRITICAL: System failure

### Metrics to Track

1. **Performance:**
   - Response time per request
   - LLM API latency
   - Tool execution time

2. **Usage:**
   - Messages per hour
   - Tools invoked per message
   - Error rate

3. **System:**
   - Memory usage
   - CPU usage
   - Active connections

## Conclusion

This architecture provides:
- ✓ Clean separation of concerns
- ✓ Scalability for growth
- ✓ Security best practices
- ✓ Maintainability for teams
- ✓ Extensibility for new features
- ✓ Testability for quality
- ✓ Performance optimization
- ✓ Clear error handling

The modular design allows each component to be developed, tested, and deployed independently while maintaining system cohesion.
