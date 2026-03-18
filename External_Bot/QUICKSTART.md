# Quick Start Guide

Get your AI Chatbot running in **5 minutes**!

## 📋 Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** installed
   - Check: `python --version`
   - [Download Python](https://www.python.org/downloads/)

2. **Two API Keys** (FREE tier available):
   - [OpenRouter API Key](https://openrouter.io/keys) - For AI model access
     - Sign up → Create account → Get API key
     - FREE: $5 free credits to try
   - [OpenWeatherMap API Key](https://openweathermap.org/api) - For weather data
     - Sign up → API keys section → Generate free key
     - FREE: 1000 calls/day

3. **Text Editor or IDE** (optional but recommended)
   - VS Code, Sublime, PyCharm, etc.

## 🚀 Installation (5 Minutes)

### Step 1: Get the Code

```bash
# Navigate to your project folder
cd External_Bot
```

The project should already have this structure:
```
External_Bot/
├── backend/          # FastAPI server
├── frontend/         # Web interface
└── README.md
```

### Step 2: Setup Backend

**Terminal 1** (Keep this open while using the app)

```bash
# Navigate to backend
cd backend

# Create virtual environment (isolates dependencies)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies (this downloads required packages)
pip install -r requirements.txt

# Setup configuration
cp .env.example .env

# Edit .env file (open with any text editor)
# ADD YOUR API KEYS:
# OPENROUTER_API_KEY=your_key_here
# OPENWEATHER_API_KEY=your_key_here
```

**First time tips:**
- If `python` doesn't work, try `python3`
- If `venv` creation fails, try: `python -m virtualenv venv`
- On Windows, you might need to allow scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Step 3: Start Backend

**In Terminal 1** (in backend directory with venv activated):

```bash
python main.py
```

✅ You should see:
```
✓ Configuration validated successfully
✓ All services initialized successfully
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If it fails:**
- Check API keys in `.env` are correct
- Verify internet connection
- Try: `pip install -r requirements.txt` again

### Step 4: Setup Frontend

**Terminal 2** (New terminal window)

```bash
# Navigate to frontend (from project root)
cd frontend

# Start a simple web server
python -m http.server 8080
```

✅ You should see:
```
Serving HTTP on 0.0.0.0 port 8080 ...
```

**Alternative options:**
```bash
# Option 1: Using Node.js (if installed)
npx http-server

# Option 2: Using Python 3.7+
python -m http.server --directory . 8000

# Option 3: Just open the file directly (may have CORS issues)
# Double-click index.html in the frontend folder
```

### Step 5: Open in Browser

```
http://localhost:8080
```

✅ You should see:
- 🤖 AI Chatbot title
- Chat interface with input box
- "Ready" status indicator (green dot)

## 💬 Using the Chatbot

### Example Queries

**Weather Queries (Uses Tool Calling):**
```
"What's the weather in London?"
"Tell me the current weather in New York"
"How's the temperature in Tokyo?"
"What's the weather like in Paris today?"
```

**General Queries (Regular Chat):**
```
"Hello! How are you?"
"What's the capital of France?"
"Explain quantum computing"
"Tell me a joke"
```

### How to Send Messages

**Method 1: Click Send Button**
1. Type your message
2. Click the send (arrow) button

**Method 2: Keyboard Shortcut**
1. Type your message
2. Press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

**Method 3: Press Enter (if configured)**
1. Type message
2. Press Enter

### Understanding the Response

**Example Response:**
```
🤖 Bot: The weather in London is currently 15°C...

🔧 get_weather
Temperature: 15°C
Feels Like: 13°C
Humidity: 72%
Condition: Partly cloudy
```

**What you're seeing:**
- Bot's natural language response
- 🔧 Tool badge showing which tools were used
- Formatted tool results with readable data

### Clear Conversation

Click **🗑️ Clear Conversation** button to:
- Delete all chat history
- Start fresh conversation
- Note: Cannot be undone!

## 🆘 Troubleshooting

### Frontend shows "Backend server is offline"

**Problem:** Status indicator shows red X

**Solutions:**
```bash
# 1. Check backend is running
# (Should see "Application startup complete" in Terminal 1)

# 2. Verify it's on localhost:8000
# Visit: http://localhost:8000/health
# Should show: {"status": "healthy", "version": "1.0.0"}

# 3. If using different ports, edit script.js
# Change: baseURL: 'http://localhost:8000'
# To: baseURL: 'http://localhost:YOURPORT'
```

### "Error: 401" or "Invalid API Key"

**Problem:** OpenRouter or OpenWeatherMap API key issue

**Solutions:**
```bash
# 1. Double-check API keys in .env file
# Are they exactly as provided? (no quotes, spaces, etc.)

# 2. Generate new API keys
# OpenRouter: https://openrouter.io/keys
# OpenWeather: https://openweathermap.org/api

# 3. Restart backend after changing .env
# Stop it: Ctrl+C
# Start it: python main.py
```

### "Connection refused" or "Cannot connect"

**Problem:** Backend not running

**Solutions:**
```bash
# 1. Make sure Terminal 1 is still open showing:
# "Application startup complete"

# 2. If it crashed, restart:
cd backend
venv\Scripts\activate  # (or source venv/bin/activate)
python main.py

# 3. Check port 8000 isn't already in use:
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -i :8000
# If in use, kill it or use different port
```

### Messages not sending

**Problem:** Send button doesn't work

**Solutions:**
```bash
# 1. Check browser console for errors
# Press F12 → Console tab → Look for red errors

# 2. Verify message isn't empty
# Try: "Hello" (at least one character)

# 3. Check network tab (F12 → Network)
# Send a message
# Look for request to /api/chat
# Check response status (should be 200)

# 4. Restart both backend and frontend
```

### Styling looks broken

**Problem:** Colors, layout, or fonts wrong

**Solutions:**
```bash
# 1. Clear browser cache
# Chrome: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Delete
# Check "Cached images and files" box

# 2. Hard refresh page
# Ctrl+F5 (Windows)  or  Cmd+Shift+R (Mac)

# 3. Try different browser
# If works elsewhere, it's a browser cache issue

# 4. Check console for CSS errors (F12 → Console)
```

## 📚 Next Steps

### Explore API Documentation

Visit your backend's interactive API documentation:
```
http://localhost:8000/docs
```

You can:
- See all API endpoints
- Test endpoints directly
- View request/response formats
- Understand parameters

### Add More Tools

Extend the chatbot with new tools:

**Example: Add a Calculator Tool**

1. Edit `backend/services/tool_orchestrator.py`
2. Add handler:
```python
async def _handle_calculate(self, arguments):
    """Handle math calculations"""
    operation = arguments.get("operation")
    a = arguments.get("a")
    b = arguments.get("b")
    
    if operation == "add":
        result = a + b
    elif operation == "multiply":
        result = a * b
    
    return {"success": True, "result": result}
```

3. Register in `__init__`:
```python
self.tool_handlers = {
    "get_weather": self._handle_get_weather,
    "calculate": self._handle_calculate  # Add this
}
```

4. Add tool definition in `llm_service.py` `_get_tool_definitions()`

### Customize Frontend

**Change colors** in `frontend/styles.css`:
```css
:root {
    --primary-color: #ff6b6b;  /* Change to red */
    --msg-user-bg: #ff6b6b;    /* User message color */
    /* ... more colors ... */
}
```

**Change backend URL** in `frontend/script.js`:
```javascript
const API_CONFIG = {
    baseURL: 'http://localhost:8000',  // Change here
    // ...
};
```

**Add new message animations** in `frontend/styles.css`

### Deploy to Production

Once working locally:

**Backend Deployment:**
- Use Heroku, DigitalOcean, AWS, or Azure
- Set environment variables
- Use production ASGI server (Gunicorn)

**Frontend Deployment:**
- Use Vercel, Netlify, GitHub Pages, or AWS S3
- Update API URL to production backend
- Enable HTTPS

## 📖 Full Documentation

For detailed information:

- **Backend Details**: See `backend/README.md`
- **Frontend Details**: See `frontend/README.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Full Project**: See `README.md`

## 🎓 Learning Resources

**Understanding Key Concepts:**

1. **Tool Calling**
   - [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
   - [LLM Agents Tutorial](https://www.deeplearning.ai/short-courses/)

2. **FastAPI**
   - [Official FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
   - [Interactive Learning](https://realpython.com/fastapi-python-web-apis/)

3. **Web Development**
   - [MDN Web Docs](https://developer.mozilla.org/)
   - [JavaScript Async/Await](https://javascript.info/async-await)

4. **REST APIs**
   - [REST API Tutorial](https://restfulapi.net/)
   - [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

## 💡 Tips & Tricks

### Use the API Docs (Swagger UI)

Visit `http://localhost:8000/docs` to:
- Test endpoints without frontend
- See exact request/response formats
- Try different parameters
- Understand error responses

### Debug Mode

Add to `.env`:
```
DEBUG=True
```

This enables:
- More detailed error messages
- Stack traces
- Verbose logging

### Monitor Logs

Check `backend/logs/` folder:
- `info_*.log` - General information
- `error_*.log` - Error details

Use these to debug issues:
```bash
# Watch logs in real-time (Mac/Linux)
tail -f backend/logs/error_*.log

# Windows: Just open the file in a text editor
```

### Keyboard Shortcuts

In the chat app:
- `Ctrl+Enter` / `Cmd+Enter`: Send message
- `F12`: Open browser developer tools
- `Ctrl+Shift+Delete`: Clear browser cache

## 🎉 You're Ready!

Congratulations! Your AI Chatbot with tool calling is now running.

**Next time you want to use it:**
```bash
# Terminal 1 (Backend)
cd backend
venv\Scripts\activate  # (or source venv/bin/activate)
python main.py

# Terminal 2 (Frontend)
cd frontend
python -m http.server 8080

# Browser
http://localhost:8080
```

## ❓ Got Questions?

**For help, check:**
1. Troubleshooting section above
2. Backend logs: `backend/logs/`
3. Browser console: Press F12
4. API docs: http://localhost:8000/docs
5. Full README.md files in each folder

## 🐛 Report Issues

If something doesn't work:
1. Check the Troubleshooting section
2. Review logs and error messages
3. Verify all prerequisites are installed
4. Try restarting both backend and frontend

---

**Enjoy your AI Chatbot! 🚀**
