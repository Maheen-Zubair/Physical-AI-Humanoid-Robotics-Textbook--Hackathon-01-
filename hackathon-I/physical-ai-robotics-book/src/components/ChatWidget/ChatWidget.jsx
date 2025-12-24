import React, { useState, useEffect, useRef, useCallback } from 'react';
import './ChatWidget.css';

// API Configuration - Change this when deploying to production
const API_CONFIG = {
  // For local development: 'http://localhost:8001'
  // For HF Spaces: 'https://your-space.hf.space'
  baseUrl: process.env.NODE_ENV === 'development'
    ? 'http://localhost:8001'
    : '', // Empty string uses relative URLs (same origin)
};

// Streaming configuration
const STREAMING_CONFIG = {
  maxRetries: 3,
  retryDelayMs: 1000,
  connectionTimeoutMs: 30000,
  useStreaming: true, // Enable/disable streaming globally
};

// Singleton guard - prevent multiple ChatWidget instances
let instanceCount = 0;

const ChatWidget = () => {
  const instanceRef = useRef(null);

  // Track instance on mount
  useEffect(() => {
    instanceCount++;
    instanceRef.current = instanceCount;

    if (instanceCount > 1) {
      console.warn(`[ChatWidget] Multiple instances detected! Instance #${instanceCount}. Only one should exist.`);
    } else {
      console.log('[ChatWidget] Instance mounted successfully');
    }

    return () => {
      instanceCount--;
    };
  }, []);

  const [isCollapsed, setIsCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false); // Track streaming state
  const [isColdStart, setIsColdStart] = useState(false); // Track cold start scenario
  const [sessionId, setSessionId] = useState(null);
  const [selection, setSelection] = useState(null);
  const [streamingText, setStreamingText] = useState(''); // Progressive text rendering
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const abortControllerRef = useRef(null); // For cancelling streaming requests

  // Initialize session ID
  useEffect(() => {
    let currentSessionId = localStorage.getItem('chatbot-session-id');
    if (!currentSessionId) {
      currentSessionId = generateSessionId();
      localStorage.setItem('chatbot-session-id', currentSessionId);
    }
    setSessionId(currentSessionId);
  }, []);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Set up selection detection
  useEffect(() => {
    const handleSelection = () => {
      const selectedText = window.getSelection().toString().trim();
      if (selectedText) {
        setSelection(selectedText);
        console.log(`Selection captured: ${selectedText.length} chars`);
      } else {
        setSelection(null);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleSelection);
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateSessionId = () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  };

  // Streaming response handler with retry logic
  const handleStreamingResponse = useCallback(async (query, contextSelection, retryCount = 0) => {
    // Create abort controller for this request
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          query: query,
          session_id: sessionId,
          context_selection: contextSelection || null
        }),
        signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';
      let responseMode = 'retrieval';
      let sources = [];
      let isOutOfScope = false;

      setIsStreaming(true);
      setStreamingText('');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data === '[DONE]') {
              // Streaming complete
              break;
            }

            try {
              const parsed = JSON.parse(data);

              if (parsed.type === 'mode') {
                responseMode = parsed.mode;
              } else if (parsed.type === 'content') {
                accumulatedText += parsed.text;
                setStreamingText(accumulatedText);
              } else if (parsed.type === 'done') {
                sources = parsed.sources || [];
                isOutOfScope = parsed.out_of_scope || false;
                responseMode = parsed.mode || responseMode;
              } else if (parsed.type === 'error') {
                // Use the user-friendly message from backend
                const errorMessage = parsed.message || 'An error occurred';
                const errorCode = parsed.error_code || 'UNKNOWN_ERROR';
                const recoverable = parsed.recoverable !== false;

                // Throw error with the user-friendly message
                const error = new Error(errorMessage);
                error.errorCode = errorCode;
                error.recoverable = recoverable;
                throw error;
              }
            } catch (parseError) {
              // Skip malformed JSON lines
              if (data !== '[DONE]') {
                console.warn('Failed to parse SSE data:', data);
              }
            }
          }
        }
      }

      return {
        text: accumulatedText,
        sources,
        outOfScope: isOutOfScope,
        responseMode,
      };

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Streaming request was cancelled');
        throw error;
      }

      // Retry logic for connection failures
      if (retryCount < STREAMING_CONFIG.maxRetries) {
        console.log(`Streaming failed, retrying (${retryCount + 1}/${STREAMING_CONFIG.maxRetries})...`);
        await new Promise(resolve => setTimeout(resolve, STREAMING_CONFIG.retryDelayMs * (retryCount + 1)));
        return handleStreamingResponse(query, contextSelection, retryCount + 1);
      }

      throw error;
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [sessionId]);

  // Non-streaming fallback
  const handleNonStreamingResponse = async (query, contextSelection) => {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        session_id: sessionId,
        context_selection: contextSelection || null
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      text: data.response,
      sources: data.sources || [],
      outOfScope: data.out_of_scope || false,
      responseMode: data.mode || 'retrieval',
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Detect cold start scenario (first message of the session)
    const isFirstMessage = messages.length === 0;
    if (isFirstMessage) {
      setIsColdStart(true);
    }

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString(),
      contextSelection: selection
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setStreamingText('');

    try {
      const startTime = Date.now();
      let result;

      // Try streaming first if enabled, fallback to non-streaming
      if (STREAMING_CONFIG.useStreaming) {
        try {
          result = await handleStreamingResponse(userMessage.text, userMessage.contextSelection);
        } catch (streamError) {
          if (streamError.name === 'AbortError') {
            throw streamError;
          }
          console.warn('Streaming failed, falling back to non-streaming:', streamError);
          result = await handleNonStreamingResponse(userMessage.text, userMessage.contextSelection);
        }
      } else {
        result = await handleNonStreamingResponse(userMessage.text, userMessage.contextSelection);
      }

      // Check if this was a cold start and took longer than expected
      const responseTime = Date.now() - startTime;
      if (isFirstMessage && responseTime > 5000) {
        console.log('Cold start detected - response time:', responseTime, 'ms');
      }

      // Add bot response with mode indicator
      const botMessage = {
        id: Date.now() + 1,
        text: result.text,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        sources: result.sources,
        outOfScope: result.outOfScope,
        selectionMode: result.responseMode === 'selection',
        responseMode: result.responseMode
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      if (error.name === 'AbortError') {
        // Request was cancelled, don't show error
        return;
      }

      console.error('Error sending message:', error);

      // Use the user-friendly error message from the backend if available
      const errorText = error.message || 'Sorry, I encountered an error processing your request. Please try again.';
      const errorCode = error.errorCode || 'UNKNOWN_ERROR';

      // Add error message with helpful information
      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true,
        errorCode: errorCode
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setStreamingText('');
      if (isFirstMessage) {
        setIsColdStart(false);
      }
      setSelection(null);
    }
  };

  // Cancel ongoing streaming request
  const cancelStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
      setIsStreaming(false);
      setStreamingText('');
    }
  }, []);

  const formatSources = (sources) => {
    if (!sources || sources.length === 0) return null;

    return (
      <div className="sources">
        <strong>Sources:</strong>
        <ul>
          {sources.map((source, index) => (
            <li key={index}>
              <a href={source.url} target="_blank" rel="noopener noreferrer">
                {source.title}
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className={`chat-widget ${isCollapsed ? 'collapsed' : ''}`} ref={chatContainerRef}>
      <div className="chat-header">
        <h3>AI Assistant</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {selection && !isCollapsed && (
            <div className="selection-indicator">
              Using selection: "{selection.substring(0, 30)}{selection.length > 30 ? '...' : ''}"
            </div>
          )}
          <button
            className="chat-toggle-btn"
            onClick={() => setIsCollapsed(!isCollapsed)}
            aria-label={isCollapsed ? 'Expand chat' : 'Minimize chat'}
          >
            {isCollapsed ? '+' : '−'}
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {isColdStart && (
          <div className="cold-start-indicator">
            <div className="loading-spinner"></div>
            <p>Initializing the chatbot (this may take a moment on first load)...</p>
          </div>
        )}
        {messages.length === 0 && !isColdStart ? (
          <div className="welcome-message">
            <p>Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook.</p>
            <p>Ask me any questions about the content, or select text and ask me to explain it.</p>
          </div>
        ) : (
          messages.map((message) => (
            !isColdStart && (
              <div
                key={message.id}
                className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-content">
                  {message.isError ? (
                    <span className="error-text">{message.text}</span>
                  ) : (
                    <div>
                      {/* Mode indicator badge for bot messages */}
                      {message.sender === 'bot' && message.responseMode && (
                        <div className={`mode-indicator mode-${message.responseMode}`}>
                          {message.responseMode === 'selection' ? (
                            <>
                              <span className="mode-icon">📝</span>
                              <span>Answering from selected text only</span>
                            </>
                          ) : message.outOfScope || (message.sources && message.sources.length === 0) ? (
                            <>
                              <span className="mode-icon">⚠️</span>
                              <span>No book context found</span>
                            </>
                          ) : (
                            <>
                              <span className="mode-icon">📚</span>
                              <span>Answering from book content</span>
                            </>
                          )}
                        </div>
                      )}
                      <div dangerouslySetInnerHTML={{ __html: message.text.replace(/\n/g, '<br />') }} />
                      {message.sources && formatSources(message.sources)}
                      {message.outOfScope && (
                        <div className="out-of-scope-note">
                          This question appears to be outside the scope of the textbook content.
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div className="message-timestamp">
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            )
          ))
        )}
        {/* Show streaming text progressively */}
        {isStreaming && streamingText && (
          <div className="message bot-message streaming">
            <div className="message-content">
              <div className="streaming-indicator">
                <span className="streaming-dot"></span>
                <span>Streaming response...</span>
              </div>
              <div dangerouslySetInnerHTML={{ __html: streamingText.replace(/\n/g, '<br />') }} />
            </div>
          </div>
        )}
        {/* Show typing indicator when loading but not streaming yet */}
        {isLoading && !isStreaming && !isColdStart && (
          <div className="message bot-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={selection ? "Ask about the selected text..." : "Ask a question about the book..."}
          disabled={isLoading}
        />
        {isStreaming ? (
          <button type="button" className="cancel-button" onClick={cancelStreaming}>
            Cancel
          </button>
        ) : (
          <button type="submit" disabled={isLoading || !inputValue.trim()}>
            Send
          </button>
        )}
      </form>

      <div className="chat-footer">
        <small>Powered by RAG Chatbot</small>
      </div>
    </div>
  );
};

export default ChatWidget;