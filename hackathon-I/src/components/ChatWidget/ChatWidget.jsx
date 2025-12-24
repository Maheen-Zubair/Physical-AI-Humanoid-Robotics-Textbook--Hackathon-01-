import React, { useState, useEffect, useRef } from 'react';
import './ChatWidget.css';

const ChatWidget = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isColdStart, setIsColdStart] = useState(false); // Track cold start scenario
  const [sessionId, setSessionId] = useState(null);
  const [selection, setSelection] = useState(null);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

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

    try {
      // Call backend API
      const startTime = Date.now();
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.text,
          session_id: sessionId,
          context_selection: userMessage.contextSelection || null
        }),
      });

      // Check if this was a cold start and took longer than expected
      const responseTime = Date.now() - startTime;
      if (isFirstMessage && responseTime > 5000) { // 5 seconds threshold for cold start
        console.log('Cold start detected - response time:', responseTime, 'ms');
        setIsColdStart(false); // Reset cold start indicator after first response
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        sources: data.sources || [],
        outOfScope: data.out_of_scope || false,
        selectionMode: data.selection_mode || false
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      if (isFirstMessage) {
        setIsColdStart(false); // Reset cold start indicator
      }
      setSelection(null); // Clear selection after sending
    }
  };

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
    <div className="chat-widget" ref={chatContainerRef}>
      <div className="chat-header">
        <h3>AI Assistant</h3>
        {selection && (
          <div className="selection-indicator">
            Using selection: "{selection.substring(0, 30)}{selection.length > 30 ? '...' : ''}"
          </div>
        )}
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
        {isLoading && !isColdStart && (
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
        <button type="submit" disabled={isLoading || !inputValue.trim()}>
          Send
        </button>
      </form>

      <div className="chat-footer">
        <small>Powered by RAG Chatbot</small>
      </div>
    </div>
  );
};

export default ChatWidget;