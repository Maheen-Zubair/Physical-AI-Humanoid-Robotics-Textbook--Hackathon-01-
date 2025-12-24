import React, { useEffect, useRef } from 'react';
import ChatWidget from '../components/ChatWidget/ChatWidget';
import '../components/ChatWidget/ChatWidget.css';

// Singleton guard to prevent multiple mounts
let chatWidgetMounted = false;

function Root({ children }) {
  const mountedRef = useRef(false);

  useEffect(() => {
    if (chatWidgetMounted && !mountedRef.current) {
      console.warn('[ChatWidget] Attempted duplicate mount - blocked by singleton guard');
      return;
    }

    if (!mountedRef.current) {
      chatWidgetMounted = true;
      mountedRef.current = true;
      console.log('[ChatWidget] Mounted successfully (singleton)');
    }

    return () => {
      // Only reset on true unmount, not on re-renders
      if (mountedRef.current) {
        chatWidgetMounted = false;
        mountedRef.current = false;
      }
    };
  }, []);

  return (
    <>
      {children}
      {/* ChatWidget is mounted ONLY here - nowhere else */}
      <ChatWidget />
    </>
  );
}

export default Root;
