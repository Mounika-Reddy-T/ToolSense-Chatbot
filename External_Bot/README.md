# 🤖 External Bot - AI Chatbot with Tool Integration

A full-stack AI chatbot application that combines **GPT-4 Turbo** via OpenRouter with real-time external tools. Demonstrates intelligent function calling where the LLM decides when to invoke tools for real-time data.

## 📋 Quick Overview

**Backend**: FastAPI (Python) with comprehensive documentation
- ✅ **Docstrings on every function** explaining purpose, parameters, returns
- ✅ **Inline comments** explaining complex logic
- ✅ **Type hints** throughout for clarity
- ✅ Tool orchestration and LLM integration

**Frontend**: HTML, CSS, JavaScript with detailed comments
- ✅ **Detailed comments** throughout the code  
- ✅ **Clear variable naming** and function descriptions
- ✅ **Interactive chat interface** with tool visualization
- ✅ Responsive design for all devices

## 📂 Project Structure

```
External_Bot/
├── backend/                      # FastAPI backend
│   ├── main.py                  # App entry point (FULLY DOCUMENTED)
│   ├── config.py                # Configuration (ALL VARIABLES EXPLAINED)
│   ├── requirements.txt          # Dependencies
│   ├── .env.example             # Environment template
│   ├── models/schemas.py        # Request schemas (DOCSTRINGS)
│   ├── services/
│   │   ├── llm_service.py       # OpenRouter (EXTENSIVE COMMENTS)
│   │   ├── weather_service.py   # Weather API (FULLY DOCUMENTED)
│   │   └── tool_orchestrator.py # Tool execution (DETAILED DOCS)
│   └── utils/logger.py          # Logging (DOCUMENTED)
│
└── frontend/                     # Web interface
    ├── index.html               # HTML (DESCRIPTIVE COMMENTS)
    ├── script.js                # Chat logic (EXTENSIVE DOCS)
    └── styles.css               # Styling (SECTION COMMENTS)
```

## 🚀 Getting Started

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
# Copy .env.example to .env
# Edit .env and add:
#   OPENROUTER_API_KEY=your_key
#   OPENWEATHER_API_KEY=your_key

# Run the server
python main.py
```

**Backend runs at**: `http://localhost:8000`
**API Docs**: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Option A: Use Python's built-in server
cd frontend
python -m http.server 8080

# Option B: Use Live Server in VS Code
# Right-click index.html → Open with Live Server

# Option C: Just open in browser
# Double-click frontend/index.html
```

**Frontend runs at**: `http://localhost:8080` or `http://localhost:5500`

## 📖 Code Documentation Guide

### All Files Have Clear Documentation

**Start Reading Here:**

1. **`backend/main.py`** - Complete flow explanation
   - HTTP endpoints documented
   - Request/response flow explained
   - Error handling documented

2. **`backend/services/llm_service.py`** - LLM Integration
   - Tool calling mechanism explained
   - Response parsing documented
   - Tool definitions documented

3. **`backend/services/tool_orchestrator.py`** - Tool Execution
   - Tool routing explained
   - Weather tool documented
   - Result formatting documented

4. **`frontend/script.js`** - Frontend Logic
   - API communication explained
   - Message handling documented
   - Tool visualization explained

### Documentation Levels

Every file includes:
- ✅ **Module docstring** - What the file does
- ✅ **Function docstring** - What each function does
- ✅ **Parameter docs** - What goes in
- ✅ **Return docs** - What comes out
- ✅ **Example usage** - How to use it
- ✅ **Inline comments** - Why code does what it does
- ✅ **Error handling** - What can go wrong

## 🔄 How It Works

### The Agentic Flow

```
User Query
    ↓
Frontend sends to Backend API
    ↓
Backend receives and sends to LLM
    ↓
LLM thinks: "Do I need weather data?"
    ↓
LLM requests weather tool
    ↓
Backend executes weather tool
    ↓
Weather data is formatted
    ↓
Backend sends data back to LLM
    ↓
LLM generates natural response
    ↓
Response sent to Frontend
    ↓
User sees formatted response
```

## 🛠️ API Endpoints

### POST /chat
Send a message and get a response

**Request:**
```json
{
  "user_message": "What's the weather in London?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "assistant_reply": "The weather in London is...",
  "tool_used": "weather",
  "tool_result": {
    "success": true,
    "data": "Weather in London: ..."
  },
  "reasoning": "User asked about weather, so I used..."
}
```

### GET /health
Check if backend is running

**Response:**
```json
{
  "status": "healthy",
  "service": "External Bot API",
  "environment": "development"
}
```

## 📝 Environment Setup

Create `.env` file in `backend/` folder:

```bash
# Required API Keys
OPENROUTER_API_KEY=your_openrouter_key
OPENWEATHER_API_KEY=your_openweather_key

# Optional Configuration
ENV=development
DEBUG=true
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
WEATHER_UNIT_DEFAULT=metric
```

**Get API Keys:**
- OpenRouter: https://openrouter.ai/
- OpenWeatherMap: https://openweathermap.org/api

## 🎯 Key Features

### Tool Calling (Function Calling)
- LLM decides when to use tools
- Automatic weather API invocation when relevant
- Tool results fed back to LLM for context
- Multi-step reasoning supported

### Conversation History
- Frontend maintains chat history
- History sent to backend for context
- LLM understands previous messages
- Natural multi-turn conversations

### Error Handling
- Graceful API error handling
- User-friendly error messages
- Detailed logging for debugging
- Connection error recovery

### Security
- CORS configured for local development
- XSS protection in frontend
- Environment variables for secrets
- Input validation on backend

## 📊 Testing the System

### Test 1: Simple Chat
```
User: "Tell me a joke"
→ LLM responds directly (no tool needed)
```

### Test 2: Weather Query
```
User: "What's the weather in Paris?"
→ LLM decides to use weather tool
→ Tool fetches weather data
→ Response includes weather info
```

### Test 3: Multi-turn Conversation
```
User 1: "How is the weather in Tokyo?"
Bot: Uses weather tool, returns data
User 2: "Is it raining there?"
Bot: Uses conversation history + new logic
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check API keys in `.env` file |
| Frontend can't connect | Ensure backend is running on port 8000 |
| 404 on API docs | Backend must be running, visit http://localhost:8000/docs |
| Weather tool fails | Verify OPENWEATHER_API_KEY is valid |
| CORS errors | Frontend must be on different port (8080 vs 8000) |
| Messages not displaying | Check browser console (F12) for JavaScript errors |

## 📚 Technology Stack

**Backend:**
- FastAPI 0.104.1
- uvicorn (ASGI server)
- Pydantic (request validation)
- requests (HTTP client)
- python-dotenv (config)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- No dependencies needed!
- Modern browser features only

**External APIs:**
- OpenRouter (LLM access)
- OpenWeatherMap (weather data)

## 🔐 Important Notes

- **Never commit `.env` file** to version control
- **API keys are sensitive** - keep them private
- **This is for local development** - production requires security hardening
- **CORS is permissive** - restrict in production

## 🎓 Learning Resources

This project teaches:
- ✅ Function calling / tool use patterns
- ✅ Full-stack development (backend + frontend)
- ✅ API integration and error handling
- ✅ Async/await programming
- ✅ Professional code documentation
- ✅ Request/response validation
- ✅ Responsive web design

## 💡 Next Steps

To extend this project:

1. **Add more tools** (stock prices, news, calendar, etc.)
2. **Add user persistence** (save conversations to database)
3. **Add authentication** (user accounts, login)
4. **Improve UI** (rich text, file uploads, voice)
5. **Deploy** (Docker, cloud platforms)
6. **Add tests** (unit tests, integration tests)

## 📝 File Reading Guide

**For complete understanding, read files in this order:**

1. **README.md** (this file) - Overview
2. **backend/config.py** - Configuration values explained
3. **backend/main.py** - Express full flow
4. **backend/services/llm_service.py** - Tool definition and calling
5. **backend/services/tool_orchestrator.py** - Tool execution
6. **backend/models/schemas.py** - Data structures
7. **frontend/script.js** - Frontend interaction
8. **frontend/styles.css** - UI styling
9. **frontend/index.html** - HTML structure

## 📞 Support

For issues:
1. Check the **inline comments** in the relevant file
2. Read the **function docstrings** for detailed information
3. Check error messages in terminal (backend) or console (frontend)
4. Verify API keys are set correctly

---

**Made with ❤️ using FastAPI, OpenRouter, and OpenWeatherMap**

**All code is thoroughly documented - read the comments!** 📖
