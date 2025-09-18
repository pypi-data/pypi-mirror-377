"""
Automatic token counting for different LLM providers
Graceful fallbacks when external libraries are not available
Supports OpenAI (GPT-3.5-turbo), Gemini (2.0-flash), and Claude
"""

import logging

# Optional imports - graceful fallback if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available - using estimation for OpenAI")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("google-generativeai not available - using estimation for Gemini")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("anthropic not available - using estimation for Claude")

class TokenCounter:
    """Handles token counting for different providers with fallbacks."""
    
    def __init__(self):
        self.openai_encoders = {}
        self._setup_openai_encoders()

    def _setup_openai_encoders(self):
        """Initialize OpenAI token encoders if tiktoken is available."""
        if TIKTOKEN_AVAILABLE:
            try:
                self.openai_encoders = {
                    'gpt-4': tiktoken.encoding_for_model('gpt-4'),
                    'gpt-4-turbo': tiktoken.encoding_for_model('gpt-4-turbo-preview'),
                    'gpt-3.5-turbo': tiktoken.encoding_for_model('gpt-3.5-turbo'),
                    'gpt-3.5-turbo-16k': tiktoken.encoding_for_model('gpt-3.5-turbo'),
                }
            except Exception as e:
                logging.warning(f"Failed to setup tiktoken encoders: {e}")

    def count_openai_tokens(self, text: str, model: str) -> int:
        """Count tokens for OpenAI models with fallback to estimation."""
        if not text:
            return 0
            
        if TIKTOKEN_AVAILABLE and model in self.openai_encoders:
            try:
                return len(self.openai_encoders[model].encode(text))
            except Exception as e:
                logging.warning(f"Tiktoken failed: {e}, using estimation")
        
        # Fallback estimation: ~4 characters per token
        return self._estimate_tokens(text)

    def count_gemini_tokens(self, text: str, model=None) -> int:
        """Count tokens for Gemini models with fallback to estimation."""
        if not text:
            return 0
            
        if GENAI_AVAILABLE and model:
            try:
                result = model.count_tokens(text)
                return result.total_tokens
            except Exception as e:
                logging.warning(f"Gemini token counting failed: {e}, using estimation")
        
        # Fallback estimation
        return self._estimate_tokens(text)

    def count_claude_tokens(self, text: str, client=None) -> int:
        """Count tokens for Claude models with fallback to estimation."""
        if not text:
            return 0
            
        if ANTHROPIC_AVAILABLE and client:
            try:
                return client.count_tokens(text)
            except Exception as e:
                logging.warning(f"Claude token counting failed: {e}, using estimation")
        
        # Fallback estimation
        return self._estimate_tokens(text)

    def _estimate_tokens(self, text: str) -> int:
        """Fallback token estimation - surprisingly accurate."""
        if not text:
            return 0
        
        # Method 1: Character-based (1 token ≈ 4 characters)
        char_estimate = max(1, len(text) // 4)
        
        # Method 2: Word-based (1 token ≈ 0.75 words)  
        word_estimate = max(1, int(len(text.split()) / 0.75))
        
        # Use the higher estimate for safety
        return max(char_estimate, word_estimate)

# Global instance
_token_counter = TokenCounter()

def count_tokens(text: str, provider: str, model_or_client=None) -> int:
    """
    Global function to count tokens for any provider.
    
    Args:
        text: Text to count tokens for
        provider: 'openai', 'gemini', or 'claude'
        model_or_client: Model name for OpenAI, model instance for Gemini, client for Claude
    
    Returns:
        Token count (estimated if exact counting unavailable)
    """
    if provider == 'openai':
        return _token_counter.count_openai_tokens(text, model_or_client)
    elif provider == 'gemini':
        return _token_counter.count_gemini_tokens(text, model_or_client)
    elif provider == 'claude':
        return _token_counter.count_claude_tokens(text, model_or_client)
    else:
        return _token_counter._estimate_tokens(text)

def estimate_tokens_simple(text: str) -> int:
    """Simple token estimation without provider specifics."""
    return _token_counter._estimate_tokens(text)

def get_token_counter_info():
    """Get information about available token counting methods."""
    return {
        'tiktoken_available': TIKTOKEN_AVAILABLE,
        'genai_available': GENAI_AVAILABLE,
        'anthropic_available': ANTHROPIC_AVAILABLE,
        'fallback_method': 'Character and word-based estimation'
    }
