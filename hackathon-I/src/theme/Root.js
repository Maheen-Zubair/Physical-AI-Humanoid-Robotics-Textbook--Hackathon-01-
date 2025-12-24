import React, { useEffect } from 'react';
import ChatWidget from '../components/ChatWidget/ChatWidget';
import '../components/ChatWidget/ChatWidget.css';

// Default implementation, that you can customize
function Root({ children }) {
  useEffect(() => {
    // Add any global initialization code here
    // For example, setting up global event listeners for selection
    console.log('Chatbot widget loaded');
  }, []);

  return (
    <>
      {children}
      <div className="chatbot-container">
        <ChatWidget />
      </div>
    </>
  );
}

export default Root;