"""
LLM Cost Calculator

Complete cost tracking for OpenAI, Gemini, and Claude APIs
Supports: GPT-3.5-turbo, Gemini-2.0-flash, Claude models, TTS-1, TTS-1-HD
"""

from .cost_tracker import CostTracker
from .token_counter import count_tokens, estimate_tokens_simple
from .pricing import list_models, get_pricing, validate_model

__version__ = "3.0.0"
__author__ = "Anonymous"
__all__ = ["CostTracker", "count_tokens", "estimate_tokens_simple", "list_models", "get_pricing", "validate_model"]

# Convenience functions for quick access
def quick_openai_cost(model, input_text, output_text):
    """Quick OpenAI cost calculation."""
    tracker = CostTracker()
    return tracker.track_openai_cost(model, input_text=input_text, output_text=output_text)

def quick_gemini_cost(input_text, output_text):
    """Quick Gemini cost calculation."""
    tracker = CostTracker()
    return tracker.track_gemini_cost('gemini-2.0-flash', input_text=input_text, output_text=output_text)

def quick_claude_cost(model, input_text, output_text):
    """Quick Claude cost calculation."""
    tracker = CostTracker()
    return tracker.track_claude_cost(model, input_text=input_text, output_text=output_text)

def quick_tts_cost(model, text):
    """Quick TTS cost calculation."""
    tracker = CostTracker()
    return tracker.track_tts_cost(model, text)
