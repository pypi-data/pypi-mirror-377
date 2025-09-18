"""
Pricing data for LLM providers
Updated to include Claude models alongside OpenAI and Gemini
Updated: September 2025 - Official API pricing
"""

# OpenAI Pricing - Chat models + TTS models
OPENAI_PRICING = {
    'chat': {
        'gpt-3.5-turbo': {
            'input': 0.50,  # $0.50 per 1M input tokens
            'output': 1.50  # $1.50 per 1M output tokens
        },
        'gpt-4': {
            'input': 30.00,  # $30 per 1M input tokens
            'output': 60.00  # $60 per 1M output tokens
        },
        'gpt-4-turbo': {
            'input': 10.00,  # $10 per 1M input tokens
            'output': 30.00  # $30 per 1M output tokens
        }
    },
    'tts': {
        'tts-1': 15.00,     # $15 per 1M characters
        'tts-1-hd': 30.00   # $30 per 1M characters
    }
}

# Google Gemini Pricing
GEMINI_PRICING = {
    'gemini-2.0-flash': {
        'input': 0.075,  # $0.075 per 1M input tokens
        'output': 0.30   # $0.30 per 1M output tokens
    },
    'gemini-1.5-pro': {
        'input': 1.25,   # $1.25 per 1M input tokens
        'output': 5.00   # $5.00 per 1M output tokens
    }
}

# Claude/Anthropic Pricing (September 2025)
CLAUDE_PRICING = {
    'claude-3.5-haiku': {
        'input': 0.80,   # $0.80 per 1M input tokens
        'output': 4.00   # $4.00 per 1M output tokens
    },
    'claude-3.5-sonnet': {
        'input': 3.00,   # $3.00 per 1M input tokens
        'output': 15.00  # $15.00 per 1M output tokens
    },
    'claude-4-opus': {
        'input': 15.00,  # $15 per 1M input tokens
        'output': 75.00  # $75 per 1M output tokens
    },
    'claude-4-sonnet': {
        'input': 3.00,   # $3 per 1M input tokens
        'output': 15.00  # $15 per 1M output tokens
    }
}

# Model validation lists
OPENAI_MODELS = {
    'chat': list(OPENAI_PRICING['chat'].keys()),
    'tts': list(OPENAI_PRICING['tts'].keys())
}

GEMINI_MODELS = list(GEMINI_PRICING.keys())
CLAUDE_MODELS = list(CLAUDE_PRICING.keys())

def validate_model(provider: str, model: str, service: str = 'chat') -> bool:
    """Validate if model exists for provider."""
    if provider == 'openai':
        return model in OPENAI_MODELS.get(service, [])
    elif provider == 'gemini':
        return model in GEMINI_MODELS
    elif provider == 'claude':
        return model in CLAUDE_MODELS
    return False

def get_pricing(provider: str, model: str, service: str = 'chat'):
    """Get pricing for specific model."""
    if provider == 'openai':
        return OPENAI_PRICING[service][model]
    elif provider == 'gemini':
        return GEMINI_PRICING[model]
    elif provider == 'claude':
        return CLAUDE_PRICING[model]
    return None

def list_models(provider: str = None):
    """List all available models in this package."""
    if provider == 'openai':
        return OPENAI_MODELS
    elif provider == 'gemini':
        return GEMINI_MODELS
    elif provider == 'claude':
        return CLAUDE_MODELS
    else:
        return {
            'openai': OPENAI_MODELS,
            'gemini': GEMINI_MODELS,
            'claude': CLAUDE_MODELS
        }

# Pricing source information:
# - OpenAI: Official rates September 2025
# - OpenAI TTS: Per 1,000,000 characters of text converted to speech
# - Gemini: Per 1,000,000 tokens (input and output charged separately)
# - Claude: Per 1,000,000 tokens (September 2025 rates from Anthropic)
