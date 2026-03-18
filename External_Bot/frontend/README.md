# AI Chatbot Frontend

The frontend is a responsive web interface for interacting with the AI chatbot backend. It provides a clean chat interface with real-time message updates and tool result display.

## Overview

The frontend features:
- **Interactive Chat Interface**: Real-time message display with user and bot messages
- **Tool Result Display**: Formatted display of tool execution results (e.g., weather data)
- **Connection Status**: Visual indicator of backend server status
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Keyboard Shortcuts**: Send messages with Ctrl+Enter

## Project Structure

```
frontend/
├── index.html      # Main HTML file with chat interface structure
├── styles.css      # Complete styling and responsive design
├── script.js       # Chat logic and API communication
└── README.md       # This file
```

## Getting Started

### No Installation Required

The frontend is entirely client-side and runs in any modern web browser. Simply:

1. **Open `index.html` in your browser**
   ```bash
   # Using a simple HTTP server (recommended)
   python -m http.server 8080
   
   # Then visit: http://localhost:8080
   ```

2. **Or double-click `index.html`** (may have CORS issues)

### Prerequisites

- Modern web browser (Chrome, Firefox, Safari, Edge)
- FastAPI backend running on `http://localhost:8000`

## How to Use

### 1. Starting the Application

- Open the frontend in your browser
- Ensure the backend server is running
- The status indicator in the header shows connection status

### 2. Sending Messages

**Methods to send:**
- Type message and click the send button
- Type message and press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

**Example queries:**
- "What's the weather in London?"
- "Tell me the current temperature in New York"
- "What's the weather like in Tokyo?"
- "How's the weather in Paris?"

### 3. Viewing Results

**Bot Responses**: Displayed with timestamp on hover

**Tool Results**: Formatted display of API responses
- Weather data shows: Temperature, Feels Like, Humidity, Pressure, Conditions, Location

**Errors**: Clearly marked with ❌ indicator

### 4. Managing Conversation

**Clear Conversation**: 
- Click "🗑️ Clear Conversation" button
- Confirmation dialog appears
- All history is deleted (can't be undone)

## File Descriptions

### index.html

Contains the complete HTML structure for the chat interface:

**Key Sections:**
- **Header**: App title and status indicator
- **Messages Container**: Where chat messages are displayed
- **Input Area**: Where users type and send messages
- **Templates**: Reusable templates for messages and tool results

**Features:**
- Semantic HTML5 structure
- Accessibility attributes (aria-labels where appropriate)
- Responsive meta viewport tag
- Template elements for dynamic content

### styles.css

Complete styling with:

**Organization:**
- CSS Variables for colors, spacing, shadows
- Component-based styling (header, messages, input, etc.)
- Responsive breakpoints for mobile (768px, 480px)
- Accessibility features (high contrast mode, reduced motion)

**Key Features:**
- **Color Scheme**: Indigo/purple primary colors with accessibility
- **Animations**: Smooth transitions, message slide-in effects
- **Scrollbar**: Custom styling for webkit browsers
- **Typography**: System font stack, optimized line-height
- **Dark Mode Ready**: Can be easily adapted for dark theme

**Responsive Breakpoints:**
- **Desktop**: 1024px+
- **Tablet**: 768px - 1023px
- **Mobile**: 480px - 767px
- **Small Mobile**: < 480px

### script.js

JavaScript application logic:

**Key Components:**

1. **Configuration**
   - Backend API URL settings
   - UI behavior configuration

2. **State Management**
   - Conversation history tracking
   - Loading state management
   - Server connection status

3. **Utility Functions**
   - Time formatting
   - HTML escaping (XSS prevention)
   - JSON data formatting
   - Auto-scroll management

4. **UI Functions**
   - Message display
   - Typing indicator
   - Loading states
   - Notification system

5. **API Communication**
   - `sendMessage()`: Main function to send messages to backend
   - Error handling with user-friendly messages
   - Conversation history maintenance

6. **Event Handling**
   - Form submission
   - Keyboard shortcuts
   - Dynamic scroll behavior

## Customization

### Change Backend URL

Edit in `script.js`:
```javascript
const API_CONFIG = {
    baseURL: 'http://your-backend-url.com',  // Change this
    // ...
};
```

### Change Colors

Edit CSS variables in `styles.css`:
```css
:root {
    --primary-color: #your-color;           /* Change primary color */
    --msg-user-bg: #your-color;            /* Change message color */
    // ...
}
```

### Add Dark Mode

Add CSS query in `styles.css`:
```css
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #1a1a1a;
        --text-primary: #ffffff;
        /* ... more dark mode colors ... */
    }
}
```

### Customize UI Behavior

Edit `UI_CONFIG` in `script.js`:
```javascript
const UI_CONFIG = {
    showTimestamps: false,        // Hide timestamps
    autoScroll: false,            // Manual scrolling only
    messageDelay: 200,            // Slower message animation
    maxHistoryLength: 100         // Keep more history
};
```

## Architecture

### Component Flow

```
User Types Message
        ↓
Form Submit Event
        ↓
sendMessage() Function
        ↓
Display User Message (UI)
        ↓
Send to Backend API
        ↓
Show Loading Indicator
        ↓
Receive Response
        ↓
Display Bot Response (UI)
        ↓
Display Tool Results (if any)
        ↓
Update Conversation History
```

### Message Lifecycle

1. **User Input**: Message typed in input field
2. **Validation**: Empty message rejected
3. **Display**: User message shown immediately
4. **API Call**: Sent to backend with conversation history
5. **Processing**: Backend processes with LLM and tools
6. **Response**: Bot response received
7. **Display**: Bot message shown with any tool results
8. **History**: Added to conversation for context

### Tool Result Display

Tool results are formatted based on type:
- **Weather**: Special grid layout with labeled values
- **Generic**: JSON formatted with syntax highlighting
- **Errors**: Clearly marked with error styling

## Performance Optimization

### Frontend Optimizations:
- DOM element caching (not re-querying the same elements)
- Template cloning (faster than string concatenation)
- Event delegation (single listeners instead of many)
- Debounced scroll listener (auto-scroll optimization)
- Lazy rendering (messages only when visible)

### Network Optimization:
- Single API request per message
- Efficient JSON payload
- Conversation history sent for context

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome/Edge | ✓ Full | Latest versions |
| Firefox | ✓ Full | Latest versions |
| Safari | ✓ Full | iOS 14+ |
| Opera | ✓ Full | Latest version |
| IE 11 | ✗ No | Not supported (uses modern JS) |

**Required Features:**
- ES6 JavaScript (async/await, template literals)
- Fetch API
- CSS Grid and Flexbox
- CSS Custom Properties (variables)

## Security Considerations

### Implemented Security Measures:
1. **XSS Prevention**: HTML escaping with `escapeHtml()` function
2. **CORS**: Backend handles CORS headers
3. **Input Validation**: Empty message rejection
4. **Error Handling**: No sensitive data in error messages
5. **Content Sanitization**: Message content escaped before display

### Best Practices:
- Messages are escaped before insertion into DOM
- No use of `innerHTML` directly with user input
- Template text content prevents script injection
- Proper error boundaries in API calls

## Troubleshooting

### Backend Connection Issues

**Symptom**: "Unable to connect to the backend server"

**Solutions:**
1. Verify backend is running: `python main.py`
2. Check backend URL in `script.js`
3. Ensure CORS is enabled on backend
4. Check firewall/network settings
5. Try accessing http://localhost:8000/health directly

### Messages Not Sending

**Symptom**: Send button doesn't work

**Solutions:**
1. Check browser console for errors (F12)
2. Ensure backend service keys are configured
3. Check network tab for API response
4. Verify input field isn't empty
5. Try refreshing the page

### Styling Issues

**Symptom**: Layout broken or colors wrong

**Solutions:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Check if styles.css is loading (inspect element)
3. Verify CSS variables are supported by browser
4. Try different browser
5. Check browser console for CSS errors

## Development

### Debug Mode

Add to browser console:
```javascript
// Enable detailed logging
DEBUG = true;

// View conversation history
console.log(AppState.conversationHistory);

// Change API URL temporarily
API_CONFIG.baseURL = 'http://new-url:port';
```

### Live Reload

Use a live server extension:
- VS Code: "Live Server" extension
- Python: `python -m http.server --directory . 8080`
- Node: `npx http-server`

## Deployment

### Static File Hosting

The frontend can be deployed to:
- **Vercel**: Drag and drop files
- **Netlify**: Connect GitHub repo
- **AWS S3**: Static hosting
- **GitHub Pages**: Push to gh-pages branch
- **Any CDN**: Firebase, Azure, etc.

### For Production:

1. Update `API_CONFIG.baseURL` to production backend URL
2. Test all API endpoints
3. Enable HTTPS (required for modern browsers)
4. Add security headers (CSP, X-Frame-Options)
5. Minify CSS/JavaScript (optional)

```bash
# Example deployment with Python HTTP server
python -m http.server --directory . 8000
```

## Further Improvements

**Potential Enhancements:**
- [ ] Message search functionality
- [ ] Export conversation as PDF
- [ ] Multiple conversation threads
- [ ] User authentication
- [ ] Message editing/deletion
- [ ] Typing indicators from bot
- [ ] Rich media support (images, files)
- [ ] Voice input/output
- [ ] Dark mode toggle
- [ ] Settings panel

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review browser console for errors
3. Check backend logs for API errors
4. Ensure backend and frontend are in sync
