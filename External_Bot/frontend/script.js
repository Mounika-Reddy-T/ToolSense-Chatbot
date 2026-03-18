/**
 * External Bot Frontend - Chat Interface JavaScript
 * ================================================
 * 
 * This module handles all frontend functionality for the AI chatbot:
 * - Message display and management
 * - User input handling
 * - API communication with the backend
 * - Real-time updates and loading states
 * 
 * Key Functions:
 *   - sendMessage: Send user message to backend API
 *   - displayMessage: Show messages in the chat interface
 *   - formatToolResponse: Display tool execution results
 *   - showLoadingState: Show loading indicator while waiting
 */

/**
 * Configuration object for API settings
 * Contains the backend API endpoint URL
 */
const API_CONFIG = {
    // Backend API endpoint - adjust if running on different server
    // Format: http://hostname:port
    BASE_URL: 'http://localhost:8000',
    
    // Chat endpoint for sending messages
    CHAT_ENDPOINT: '/chat'
};

/**
 * Application state management
 * Stores conversation history and UI state
 */
let appState = {
    // Array to store conversation history for context
    // Each message object contains: { role: "user"|"assistant", content: "..." }
    conversationHistory: [],
    
    // Flag to prevent sending multiple messages simultaneously
    isWaitingForResponse: false
};

/**
 * Initialize application on page load
 * Sets up event listeners and prepares the UI
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 External Bot loaded and ready');
    
    // Get DOM elements for manipulation
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    
    // Attach event listener to form submission (when user clicks Send or presses Enter)
    if (chatForm) {
        chatForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Focus on input field for immediate typing
    if (userInput) {
        userInput.focus();
    }
});

/**
 * Handle form submission when user sends a message
 * 
 * This function:
 * 1. Gets the user input
 * 2. Displays it in the chat
 * 3. Sends it to the backend API
 * 4. Handles the response
 * 5. Displays tool information if applicable
 * 
 * @param {Event} event - Form submission event
 */
async function handleFormSubmit(event) {
    // Prevent default form submission behavior (page reload)
    event.preventDefault();
    
    // Get the input field
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    // Validate that message is not empty
    if (!message) {
        showErrorMessage('Please enter a message!');
        return;
    }
    
    // Prevent double submission if already waiting for response
    if (appState.isWaitingForResponse) {
        showErrorMessage('Please wait for the current message to be processed...');
        return;
    }
    
    // Clear input field for next message
    userInput.value = '';
    
    // Display user message in chat interface
    displayMessage({
        role: 'user',
        content: message
    });
    
    // Add to conversation history for context
    appState.conversationHistory.push({
        role: 'user',
        content: message
    });
    
    try {
        // Show loading indicator to user
        showLoadingState(true);
        appState.isWaitingForResponse = true;
        
        // Send message to backend API
        console.log('📤 Sending message to backend:', message);
        const response = await sendMessageToBackend(message, appState.conversationHistory);
        
        // Log successful response for debugging
        console.log('📥 Received response from backend:', response);
        
        // Extract assistant's response
        const assistantReply = response.assistant_reply;
        
        // Display the assistant's response in chat
        displayMessage({
            role: 'assistant',
            content: assistantReply
        });
        
        // Add assistant response to history for context
        appState.conversationHistory.push({
            role: 'assistant',
            content: assistantReply
        });
        
        // If a tool was used (e.g., weather tool), display tool information
        if (response.tool_used) {
            console.log(`🔧 Tool used: ${response.tool_used}`);
            displayToolInformation(response.tool_used, response.tool_result, response.reasoning);
        }
        
        // Hide loading indicator
        showLoadingState(false);
        
        // Clear any error messages that might be displayed
        hideErrorMessage();
        
    } catch (error) {
        // Handle errors during message sending
        console.error('❌ Error sending message:', error);
        
        // Display friendly error message to user
        const errorMsg = error.message || 'Failed to get response. Please try again.';
        showErrorMessage(errorMsg);
        
        // Hide loading indicator on error
        showLoadingState(false);
    } finally {
        // Reset waiting flag to allow next message
        appState.isWaitingForResponse = false;
        
        // Return focus to input field
        document.getElementById('userInput').focus();
    }
}

/**
 * Send message to backend API and receive response
 * 
 * This function:
 * 1. Prepares the request with message and history
 * 2. Makes HTTP POST request to backend
 * 3. Processes the JSON response
 * 4. Handles errors gracefully
 * 
 * @param {string} userMessage - The user's message to send
 * @param {Array} conversationHistory - Previous messages for context
 * @returns {Promise<Object>} Response from backend containing:
 *    - assistant_reply: Text response from the LLM
 *    - tool_used: Name of tool invoked, if any
 *    - tool_result: Result from tool execution
 *    - reasoning: Why the tool was/wasn't used
 * 
 * @throws {Error} If API request fails or response is invalid
 */
async function sendMessageToBackend(userMessage, conversationHistory) {
    try {
        // Construct the full API URL
        const url = `${API_CONFIG.BASE_URL}${API_CONFIG.CHAT_ENDPOINT}`;
        
        // Filter conversation history to only include role and content (required fields)
        const filteredHistory = conversationHistory.map(msg => ({
            role: msg.role,
            content: msg.content
        }));
        
        // Prepare request body with message and history
        const requestBody = {
            user_message: userMessage,
            conversation_history: filteredHistory
        };
        
        console.log('📡 API Request:', url);
        console.log('Request Body:', requestBody);
        
        // Make HTTP POST request to backend
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Add any authentication headers if needed
            },
            body: JSON.stringify(requestBody)
        });
        
        // Check if response is OK (status 200-299)
        if (!response.ok) {
            // Try to get error message from response
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                // If we can't parse error details, use status text
            }
            
            throw new Error(errorMessage);
        }
        
        // Parse response JSON
        const data = await response.json();
        
        // Validate response has required fields
        if (data.assistant_reply === undefined || data.assistant_reply === null) {
            throw new Error('Invalid response format from backend');
        }
        
        return data;
        
    } catch (error) {
        // Handle network errors or other fetch issues
        if (error instanceof TypeError) {
            throw new Error(
                'Cannot connect to backend server. Make sure the backend is running at ' +
                API_CONFIG.BASE_URL
            );
        }
        
        // Re-throw any other error
        throw error;
    }
}

/**
 * Display a message in the chat interface
 * 
 * Creates a message element with appropriate styling based on sender role
 * and appends it to the chat messages container
 * 
 * @param {Object} message - Message object containing:
 *    - role: "user" or "assistant"
 *    - content: Text content of the message
 */
function displayMessage(message) {
    // Get or create the chat messages container
    const chatMessages = document.getElementById('chatMessages');
    
    if (!chatMessages) {
        console.error('❌ Chat messages container not found');
        return;
    }
    
    // Create a new message element
    const messageElement = document.createElement('div');
    
    // Add appropriate CSS class based on message role
    // This determines styling (user messages on right, assistant on left, different colors)
    messageElement.classList.add('message');
    messageElement.classList.add(message.role === 'user' ? 'user-message' : 'assistant-message');
    
    // Create container for message content
    const contentElement = document.createElement('div');
    contentElement.classList.add('message-content');
    
    // Convert message content to HTML-safe format
    // This prevents XSS attacks and preserves formatting
    contentElement.innerHTML = `<p>${escapeHtml(message.content)}</p>`;
    
    // Add content to message element
    messageElement.appendChild(contentElement);
    
    // Add timestamp to message (optional, for debugging)
    const timestamp = new Date().toLocaleTimeString();
    const timeElement = document.createElement('div');
    timeElement.classList.add('message-time');
    timeElement.textContent = timestamp;
    messageElement.appendChild(timeElement);
    
    // Append message to chat
    chatMessages.appendChild(messageElement);
    
    // Auto-scroll to latest message
    scrollToBottom();
}

/**
 * Display tool execution information to the user
 * 
 * Shows details about which tool was used and its results
 * This helps users understand the reasoning behind responses
 * 
 * @param {string} toolName - Name of the tool used (e.g., "weather")
 * @param {Object} toolResult - Result data from tool execution
 * @param {string} reasoning - Explanation of why the tool was used
 */
function displayToolInformation(toolName, toolResult, reasoning) {
    // Get chat messages container
    const chatMessages = document.getElementById('chatMessages');
    
    if (!chatMessages) {
        return;
    }
    
    // Create container for tool information
    const toolElement = document.createElement('div');
    toolElement.classList.add('message');
    toolElement.classList.add('tool-message');
    
    // Create content element with tool details
    const contentElement = document.createElement('div');
    contentElement.classList.add('message-content');
    
    // Build HTML for tool information
    let toolHTML = `<div class="tool-info">`;
    toolHTML += `<strong>🔧 Tool Used: ${escapeHtml(toolName)}</strong>`;
    
    // Show reasoning if available
    if (reasoning) {
        toolHTML += `<p class="tool-reasoning">${escapeHtml(reasoning)}</p>`;
    }
    
    // Show tool result data if successful
    if (toolResult && toolResult.success) {
        toolHTML += `<details class="tool-result">
            <summary>📊 Tool Result Details</summary>
            <pre>${escapeHtml(JSON.stringify(toolResult, null, 2))}</pre>
        </details>`;
    } else if (toolResult && !toolResult.success) {
        // Show error if tool execution failed
        toolHTML += `<p class="tool-error">❌ Tool Error: ${escapeHtml(toolResult.error)}</p>`;
    }
    
    toolHTML += `</div>`;
    
    // Set the content
    contentElement.innerHTML = toolHTML;
    
    // Append to tool element and to chat
    toolElement.appendChild(contentElement);
    chatMessages.appendChild(toolElement);
    
    // Scroll to see tool information
    scrollToBottom();
}

/**
 * Show loading indicator while waiting for response
 * 
 * Displays animated loading indicator and disables send button
 * 
 * @param {boolean} show - True to show loading, false to hide
 */
function showLoadingState(show) {
    // Get loading indicator element
    const loadingIndicator = document.getElementById('loadingIndicator');
    const sendButton = document.getElementById('sendButton');
    const userInput = document.getElementById('userInput');
    
    if (show) {
        // Show loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'flex';
        }
        
        // Disable send button and input
        if (sendButton) {
            sendButton.disabled = true;
        }
        if (userInput) {
            userInput.disabled = true;
        }
        
    } else {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        // Enable send button and input
        if (sendButton) {
            sendButton.disabled = false;
        }
        if (userInput) {
            userInput.disabled = false;
        }
    }
}

/**
 * Display an error message to the user
 * 
 * Shows error message in red at the bottom of the chat area
 * 
 * @param {string} message - Error message to display
 */
function showErrorMessage(message) {
    // Get error message container
    const errorElement = document.getElementById('errorMessage');
    
    if (errorElement) {
        // Set error text
        errorElement.textContent = '❌ ' + message;
        
        // Show error message
        errorElement.style.display = 'block';
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            hideErrorMessage();
        }, 5000);
    }
}

/**
 * Hide the error message display
 */
function hideErrorMessage() {
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

/**
 * Scroll chat area to bottom to show latest message
 * 
 * Smoothly scrolls to the bottom of the chat so the latest
 * message is visible to the user
 */
function scrollToBottom() {
    // Get chat messages container
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatMessages) {
        // Use setTimeout to ensure scroll happens after DOM update
        setTimeout(() => {
            // Scroll to bottom of container
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 0);
    }
}

/**
 * Escape HTML special characters to prevent XSS attacks
 * 
 * Converts special characters to HTML entities so user input
 * cannot inject malicious HTML/JavaScript
 * 
 * @param {string} text - Text to escape
 * @returns {string} Escaped text safe for HTML insertion
 */
function escapeHtml(text) {
    // Create a temporary element to leverage browser's HTML escaping
    const tempDiv = document.createElement('div');
    tempDiv.textContent = text;
    return tempDiv.innerHTML;
}

/**
 * Clear conversation history
 * 
 * Resets the chat to start a new conversation
 * Useful for starting fresh or testing
 */
function clearHistory() {
    // Clear conversation history array
    appState.conversationHistory = [];
    
    // Clear displayed messages (optional - only clear messages after welcome)
    console.log('🧹 Conversation history cleared');
}

// Log when script loads
console.log('✅ Chat script loaded successfully');
