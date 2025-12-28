/**
 * Session management for the chatbot
 */

const SESSION_STORAGE_KEY = 'chatbot-session-id';
const SESSION_EXPIRY_HOURS = 30; // 30 minutes in hours

/**
 * Generates a new session ID
 * @returns {string} New session ID
 */
export const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

/**
 * Gets the current session ID from localStorage
 * @returns {string|null} Session ID if exists, null otherwise
 */
export const getSessionId = () => {
  const sessionData = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!sessionData) {
    return null;
  }

  try {
    const parsed = JSON.parse(sessionData);
    const now = new Date();

    // Check if session has expired
    if (new Date(parsed.expiry) < now) {
      localStorage.removeItem(SESSION_STORAGE_KEY);
      return null;
    }

    return parsed.sessionId;
  } catch (error) {
    console.error('Error parsing session data:', error);
    // If there's an error, remove the corrupted session data
    localStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  }
};

/**
 * Sets the session ID in localStorage with expiry
 * @param {string} sessionId - Session ID to store
 */
export const setSessionId = (sessionId) => {
  const expiryDate = new Date();
  expiryDate.setHours(expiryDate.getHours() + SESSION_EXPIRY_HOURS);

  const sessionData = {
    sessionId: sessionId,
    createdAt: new Date().toISOString(),
    expiry: expiryDate.toISOString()
  };

  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(sessionData));
};

/**
 * Creates a new session or returns existing valid session
 * @returns {string} Valid session ID
 */
export const createOrGetSession = () => {
  let sessionId = getSessionId();

  if (!sessionId) {
    sessionId = generateSessionId();
    setSessionId(sessionId);
  }

  return sessionId;
};

/**
 * Clears the current session
 */
export const clearSession = () => {
  localStorage.removeItem(SESSION_STORAGE_KEY);
};

/**
 * Gets session metadata
 * @returns {Object|null} Session metadata or null if no valid session
 */
export const getSessionMetadata = () => {
  const sessionData = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!sessionData) {
    return null;
  }

  try {
    return JSON.parse(sessionData);
  } catch (error) {
    console.error('Error parsing session metadata:', error);
    return null;
  }
};

/**
 * Checks if the current session is still valid
 * @returns {boolean} True if session is valid, false otherwise
 */
export const isSessionValid = () => {
  const sessionData = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!sessionData) {
    return false;
  }

  try {
    const parsed = JSON.parse(sessionData);
    const now = new Date();
    return new Date(parsed.expiry) >= now;
  } catch (error) {
    console.error('Error checking session validity:', error);
    return false;
  }
};

/**
 * Refreshes the session expiry time
 * @returns {boolean} True if session was refreshed, false if no valid session
 */
export const refreshSession = () => {
  const sessionData = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!sessionData) {
    return false;
  }

  try {
    const parsed = JSON.parse(sessionData);
    const now = new Date();

    // Only refresh if session is still valid
    if (new Date(parsed.expiry) >= now) {
      const newExpiry = new Date();
      newExpiry.setHours(newExpiry.getHours() + SESSION_EXPIRY_HOURS);

      parsed.expiry = newExpiry.toISOString();
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(parsed));
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error refreshing session:', error);
    return false;
  }
};