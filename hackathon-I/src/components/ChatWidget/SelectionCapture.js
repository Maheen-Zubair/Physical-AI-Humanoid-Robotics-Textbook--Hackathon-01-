/**
 * Utility functions for capturing text selection in the browser
 */

/**
 * Gets the currently selected text in the browser
 * @returns {string|null} The selected text, or null if no text is selected
 */
export const getSelectedText = () => {
  const selection = window.getSelection();
  const selectedText = selection.toString().trim();
  return selectedText || null;
};

/**
 * Gets the currently selected text along with additional context
 * @returns {Object|null} Object containing selected text and context, or null if no selection
 */
export const getSelectedTextWithContext = () => {
  const selection = window.getSelection();
  if (!selection.rangeCount) {
    return null;
  }

  const range = selection.getRangeAt(0);
  const selectedText = selection.toString().trim();

  if (!selectedText) {
    return null;
  }

  // Get context around the selection
  const startRange = document.createRange();
  startRange.setStart(range.startContainer, range.startOffset);
  startRange.collapse(true);
  startRange.setStartBefore(range.startContainer.parentElement.closest('p, div, h1, h2, h3, h4, h5, h6, li, td, th') || document.body);
  const contextBefore = startRange.toString().slice(-100); // Last 100 chars before selection

  const endRange = document.createRange();
  endRange.setEnd(range.endContainer, range.endOffset);
  endRange.collapse(false);
  endRange.setEndAfter(range.endContainer.parentElement.closest('p, div, h1, h2, h3, h4, h5, h6, li, td, th') || document.body);
  const contextAfter = endRange.toString().substring(range.toString().length, range.toString().length + 100); // Next 100 chars after selection

  return {
    text: selectedText,
    startOffset: range.startOffset,
    endOffset: range.endOffset,
    contextBefore,
    contextAfter,
    range: range.cloneRange()
  };
};

/**
 * Validates the selected text based on requirements
 * @param {string} selectedText - The selected text to validate
 * @param {number} maxTokens - Maximum allowed tokens (default: 4000)
 * @returns {Object} Validation result with isValid flag and message
 */
export const validateSelectedText = (selectedText, maxTokens = 4000) => {
  if (!selectedText) {
    return {
      isValid: false,
      message: "No text selected",
      tokenCount: 0
    };
  }

  // Simple token estimation (rough approximation: 1 token ≈ 4 characters)
  const estimatedTokens = Math.ceil(selectedText.length / 4);

  if (estimatedTokens > maxTokens) {
    return {
      isValid: false,
      message: `Selection too long (${estimatedTokens} tokens, max ${maxTokens})`,
      tokenCount: estimatedTokens
    };
  }

  if (selectedText.trim().length === 0) {
    return {
      isValid: false,
      message: "Selection is empty or contains only whitespace",
      tokenCount: 0
    };
  }

  return {
    isValid: true,
    message: "Valid selection",
    tokenCount: estimatedTokens
  };
};

/**
 * Sets up event listeners for text selection
 * @param {Function} onSelectionChange - Callback function when selection changes
 * @returns {Function} Cleanup function to remove event listeners
 */
export const setupSelectionListener = (onSelectionChange) => {
  const handleSelection = () => {
    const selectedText = getSelectedText();
    onSelectionChange(selectedText);
  };

  // Listen for mouse and keyboard events that might change selection
  document.addEventListener('mouseup', handleSelection);
  document.addEventListener('keyup', handleSelection);
  document.addEventListener('touchend', handleSelection); // For mobile touch selection

  // Return cleanup function
  return () => {
    document.removeEventListener('mouseup', handleSelection);
    document.removeEventListener('keyup', handleSelection);
    document.removeEventListener('touchend', handleSelection);
  };
};

/**
 * Counts tokens in text (approximation)
 * @param {string} text - Text to count tokens for
 * @returns {number} Estimated token count
 */
export const countTokens = (text) => {
  if (!text) return 0;
  // Rough approximation: 1 token ≈ 4 characters for English text
  return Math.ceil(text.length / 4);
};

/**
 * Gets word count in selected text
 * @param {string} text - Text to count words for
 * @returns {number} Word count
 */
export const countWords = (text) => {
  if (!text) return 0;
  return text.trim().split(/\s+/).filter(word => word.length > 0).length;
};