# """
# Main cost tracking class with automatic token counting
# Supports video generation pipeline and slide creation
# Models: GPT-3.5-turbo, Gemini-2.0-flash, Claude models, TTS-1, TTS-1-HD
# """

# from datetime import datetime
# from typing import Dict, List, Optional, Any, Union
# import json
# import logging

# from .pricing import (
#     OPENAI_PRICING, GEMINI_PRICING, CLAUDE_PRICING, CLAUDE_MODELS,
#     validate_model, get_pricing, list_models
# )

# from .token_counter import count_tokens, get_token_counter_info

# class CostTracker:
#     """
#     Complete cost tracker for video generation and slide creation pipeline.
#     Tracks: GPT-3.5-turbo, Gemini-2.0-flash, Claude models, TTS-1, TTS-1-HD
#     """
    
#     def __init__(self, session_id: str = None):
#         """
#         Initialize cost tracker.
        
#         Args:
#             session_id: Unique identifier for this session
#         """
#         self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
#         self.start_time = datetime.now()
        
#         # Store API clients for automatic token counting
#         self.openai_client = None
#         self.gemini_model = None
#         self.claude_client = None
        
#         # Cost storage
#         self.transactions = []
#         self.totals = {
#             'openai': 0.0,
#             'gemini': 0.0,
#             'claude': 0.0,
#             'total': 0.0
#         }
        
#         # Token counting info
#         self.token_info = get_token_counter_info()
        
#         # Print setup info
#         self._print_setup_info()
    
#     def _print_setup_info(self):
#         """Print setup information."""
#         print(f"💰 LLM Cost Tracker initialized (Session: {self.session_id})")
#         print("📋 Tracking models: OpenAI (gpt-3.5-turbo, tts), Gemini (2.0-flash), Claude (all models)")
        
#         if not self.token_info['tiktoken_available']:
#             print("⚠️ tiktoken not available - using estimation for token counting (~90% accuracy)")
#         if not self.token_info['genai_available']:
#             print("⚠️ google-generativeai not available - using estimation for Gemini")
#         if not self.token_info['anthropic_available']:
#             print("⚠️ anthropic not available - using estimation for Claude")

#     def set_clients(self, openai_client=None, gemini_model=None, claude_client=None):
#         """Set API clients for more accurate token counting."""
#         self.openai_client = openai_client
#         self.gemini_model = gemini_model
#         self.claude_client = claude_client
        
#         if openai_client:
#             print("✅ OpenAI client set for chat and TTS tracking")
#         if gemini_model:
#             print("✅ Gemini model set for accurate token counting")
#         if claude_client:
#             print("✅ Claude client set for accurate token counting")

#     def track_openai_cost(self, model: str, input_text: str = None, output_text: str = None,
#                          input_tokens: int = None, output_tokens: int = None,
#                          description: str = '') -> float:
#         """
#         Track OpenAI chat model cost with automatic token counting.
        
#         Args:
#             model: OpenAI model (e.g., 'gpt-3.5-turbo')
#             input_text: Input text (for automatic counting)
#             output_text: Output text (for automatic counting)
#             input_tokens: Manual token count (overrides automatic)
#             output_tokens: Manual token count (overrides automatic)
#             description: Description for this transaction
            
#         Returns:
#             Cost in USD
#         """
#         if not validate_model('openai', model, 'chat'):
#             raise ValueError(f"Unknown OpenAI chat model: {model}. Supported: gpt-3.5-turbo, gpt-4, gpt-4-turbo")
        
#         # Automatic token counting if text provided
#         if input_text and input_tokens is None:
#             input_tokens = count_tokens(input_text, 'openai', model)
#         if output_text and output_tokens is None:
#             output_tokens = count_tokens(output_text, 'openai', model)
            
#         if input_tokens is None or output_tokens is None:
#             raise ValueError("Need input_tokens and output_tokens (or input_text and output_text)")
        
#         pricing = get_pricing('openai', model, 'chat')
#         input_cost = (input_tokens / 1000000) * pricing['input']  # OpenAI pricing per 1M tokens
#         output_cost = (output_tokens / 1000000) * pricing['output']
#         cost = input_cost + output_cost
        
#         transaction = {
#             'timestamp': datetime.now().isoformat(),
#             'provider': 'openai',
#             'model': model,
#             'service': 'chat',
#             'description': description,
#             'input_tokens': input_tokens,
#             'output_tokens': output_tokens,
#             'input_cost': input_cost,
#             'output_cost': output_cost,
#             'total_cost': cost
#         }
        
#         self.transactions.append(transaction)
#         self.totals['openai'] += cost
#         self.totals['total'] += cost
        
#         print(f"📊 OpenAI Chat: ${cost:.6f} ({model}, {input_tokens}+{output_tokens} tokens)")
#         return cost

#     def track_claude_cost(self, model: str, input_text: str = None, output_text: str = None,
#                          input_tokens: int = None, output_tokens: int = None,
#                          description: str = '') -> float:
#         """
#         Track Claude API cost with automatic token counting.
        
#         Args:
#             model: Claude model (e.g., 'claude-3.5-sonnet')
#             input_text: Input text (for automatic counting)
#             output_text: Output text (for automatic counting)
#             input_tokens: Manual token count (overrides automatic)
#             output_tokens: Manual token count (overrides automatic)
#             description: Description for this transaction
            
#         Returns:
#             Cost in USD
#         """
#         if not validate_model('claude', model):
#             supported_models = ', '.join(CLAUDE_MODELS)
#             raise ValueError(f"Unknown Claude model: {model}. Supported: {supported_models}")
        
#         # Automatic token counting if text provided
#         if input_text and input_tokens is None:
#             input_tokens = count_tokens(input_text, 'claude', self.claude_client)
#         if output_text and output_tokens is None:
#             output_tokens = count_tokens(output_text, 'claude', self.claude_client)
            
#         if input_tokens is None or output_tokens is None:
#             raise ValueError("Need input_tokens and output_tokens (or input_text and output_text)")
        
#         pricing = get_pricing('claude', model)
#         input_cost = (input_tokens / 1000000) * pricing['input']  # Claude pricing per 1M tokens
#         output_cost = (output_tokens / 1000000) * pricing['output']
#         cost = input_cost + output_cost
        
#         transaction = {
#             'timestamp': datetime.now().isoformat(),
#             'provider': 'claude',
#             'model': model,
#             'service': 'chat',
#             'description': description,
#             'input_tokens': input_tokens,
#             'output_tokens': output_tokens,
#             'input_cost': input_cost,
#             'output_cost': output_cost,
#             'total_cost': cost
#         }
        
#         self.transactions.append(transaction)
#         self.totals['claude'] += cost
#         self.totals['total'] += cost
        
#         print(f"📊 Claude: ${cost:.6f} ({model}, {input_tokens}+{output_tokens} tokens)")
#         return cost

#     def track_gemini_cost(self, model: str = 'gemini-2.0-flash',
#                          input_text: str = None, output_text: str = None,
#                          input_tokens: int = None, output_tokens: int = None,
#                          description: str = '') -> float:
#         """
#         Track Gemini API cost with automatic token counting.
        
#         Args:
#             model: Gemini model (default: 'gemini-2.0-flash')
#             input_text: Input text (for automatic counting)
#             output_text: Output text (for automatic counting)  
#             input_tokens: Manual token count (overrides automatic)
#             output_tokens: Manual token count (overrides automatic)
#             description: Description for this transaction
            
#         Returns:
#             Cost in USD
#         """
#         if not validate_model('gemini', model):
#             supported_models = ', '.join(['gemini-2.0-flash', 'gemini-1.5-pro'])
#             raise ValueError(f"Unknown Gemini model: {model}. Supported: {supported_models}")
        
#         # Automatic token counting if text provided
#         if input_text and input_tokens is None:
#             input_tokens = count_tokens(input_text, 'gemini', self.gemini_model)
#         if output_text and output_tokens is None:
#             output_tokens = count_tokens(output_text, 'gemini', self.gemini_model)
            
#         if input_tokens is None or output_tokens is None:
#             raise ValueError("Need input_tokens and output_tokens (or input_text and output_text)")
        
#         pricing = get_pricing('gemini', model)
#         input_cost = (input_tokens / 1000000) * pricing['input']  # Gemini pricing per 1M tokens
#         output_cost = (output_tokens / 1000000) * pricing['output']
#         cost = input_cost + output_cost
        
#         transaction = {
#             'timestamp': datetime.now().isoformat(),
#             'provider': 'gemini',
#             'model': model,
#             'service': 'chat',
#             'description': description,
#             'input_tokens': input_tokens,
#             'output_tokens': output_tokens,
#             'input_cost': input_cost,
#             'output_cost': output_cost,
#             'total_cost': cost
#         }
        
#         self.transactions.append(transaction)
#         self.totals['gemini'] += cost
#         self.totals['total'] += cost
        
#         print(f"📊 Gemini: ${cost:.6f} ({model}, {input_tokens}+{output_tokens} tokens)")
#         return cost

#     def track_tts_cost(self, model: str, text: str, description: str = '') -> float:
#         """
#         Track OpenAI TTS cost with automatic character counting.
        
#         Args:
#             model: TTS model ('tts-1' or 'tts-1-hd')
#             text: Text to be converted to speech
#             description: Description for this transaction
            
#         Returns:
#             Cost in USD
#         """
#         if not validate_model('openai', model, 'tts'):
#             raise ValueError(f"Unknown TTS model: {model}. Supported: tts-1, tts-1-hd")
        
#         characters = len(text)
#         pricing = get_pricing('openai', model, 'tts')
#         cost = (characters / 1000000) * pricing  # Correct calculation for per-1M pricing
        
#         transaction = {
#             'timestamp': datetime.now().isoformat(),
#             'provider': 'openai',
#             'model': model,
#             'service': 'tts',
#             'description': description,
#             'characters': characters,
#             'total_cost': cost
#         }
        
#         self.transactions.append(transaction)
#         self.totals['openai'] += cost
#         self.totals['total'] += cost
        
#         print(f"📊 OpenAI TTS: ${cost:.6f} ({model}, {characters} chars)")
#         return cost

#     def print_summary(self):
#         """Print a formatted summary of all costs."""
#         print(f"\n💰 COST SUMMARY - Session: {self.session_id}")
#         print("=" * 50)
        
#         if not self.transactions:
#             print("No transactions recorded.")
#             return
        
#         # Print per-provider totals
#         print("📊 Provider Totals:")
#         for provider, total in self.totals.items():
#             if provider != 'total' and total > 0:
#                 print(f"  {provider.title()}: ${total:.6f}")
        
#         print(f"\n🎯 TOTAL SESSION COST: ${self.totals['total']:.6f}")
        
#         # Print transaction details
#         print(f"\n📋 Transaction Details ({len(self.transactions)} transactions):")
#         for i, trans in enumerate(self.transactions[-5:], 1):  # Show last 5
#             provider = trans['provider']
#             model = trans['model']
#             cost = trans['total_cost']
#             desc = trans.get('description', 'No description')
#             print(f"  {i}. {provider}/{model}: ${cost:.6f} - {desc}")
        
#         if len(self.transactions) > 5:
#             print(f"  ... and {len(self.transactions) - 5} more transactions")
        
#         # Calculate session duration
#         duration = datetime.now() - self.start_time
#         print(f"\n⏱️ Session Duration: {duration}")

#     def export_to_csv(self, filename: str):
#     """Export transaction data to CSV file."""
#     try:
#         import csv
        
#         if not self.transactions:
#             print(f"No transactions to export to {filename}")
#             return None
        
#         # Simple approach: export essential info only
#         with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#             writer = csv.writer(csvfile)
            
#             # Write header
#             writer.writerow(['timestamp', 'provider', 'model', 'description', 'cost'])
            
#             # Write data rows
#             for trans in self.transactions:
#                 writer.writerow([
#                     trans['timestamp'],
#                     trans['provider'], 
#                     trans['model'],
#                     trans.get('description', ''),
#                     trans['total_cost']
#                 ])
        
#         print(f"✅ Exported {len(self.transactions)} transactions to {filename}")
#         return filename
        
#     except Exception as e:
#         print(f"❌ Error exporting to CSV: {e}")
#         return None


#     def export_to_dict(self) -> dict:
#         """Export all session data as dictionary."""
#         return {
#             'session_id': self.session_id,
#             'start_time': self.start_time.isoformat(),
#             'end_time': datetime.now().isoformat(),
#             'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
#             'totals': self.totals.copy(),
#             'transaction_count': len(self.transactions),
#             'transactions': self.transactions.copy(),
#             'token_counter_info': self.token_info
#         }

#     def get_session_report(self) -> str:
#         """Get formatted session report as string."""
#         report = []
#         report.append(f"Session ID: {self.session_id}")
#         report.append(f"Duration: {datetime.now() - self.start_time}")
#         report.append(f"Total Cost: ${self.totals['total']:.6f}")
#         report.append(f"Transactions: {len(self.transactions)}")
        
#         if self.totals['openai'] > 0:
#             report.append(f"OpenAI Cost: ${self.totals['openai']:.6f}")
#         if self.totals['gemini'] > 0:
#             report.append(f"Gemini Cost: ${self.totals['gemini']:.6f}")
#         if self.totals['claude'] > 0:
#             report.append(f"Claude Cost: ${self.totals['claude']:.6f}")
        
#         return "\n".join(report)

#     def reset_session(self):
#         """Reset current session data."""
#         self.transactions = []
#         self.totals = {
#             'openai': 0.0,
#             'gemini': 0.0,
#             'claude': 0.0,
#             'total': 0.0
#         }
#         self.start_time = datetime.now()
#         print(f"🔄 Session {self.session_id} reset")

#     def get_cost_by_provider(self, provider: str) -> float:
#         """Get total cost for specific provider."""
#         return self.totals.get(provider, 0.0)

#     def get_transaction_count(self) -> int:
#         """Get total number of transactions."""
#         return len(self.transactions)

#     def get_last_transaction(self) -> dict:
#         """Get the last transaction."""
#         return self.transactions[-1] if self.transactions else None






















"""
Main cost tracking class with automatic token counting
Supports video generation pipeline and slide creation
Models: GPT-3.5-turbo, Gemini-2.0-flash, Claude models, TTS-1, TTS-1-HD
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import json
import logging
from .pricing import (
    OPENAI_PRICING, GEMINI_PRICING, CLAUDE_PRICING, CLAUDE_MODELS,
    validate_model, get_pricing, list_models
)
from .token_counter import count_tokens, get_token_counter_info

class CostTracker:
    """
    Complete cost tracker for video generation and slide creation pipeline.
    Tracks: GPT-3.5-turbo, Gemini-2.0-flash, Claude models, TTS-1, TTS-1-HD
    """

    def __init__(self, session_id: str = None):
        """
        Initialize cost tracker.

        Args:
            session_id: Unique identifier for this session
        """
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()

        # Store API clients for automatic token counting
        self.openai_client = None
        self.gemini_model = None
        self.claude_client = None

        # Cost storage
        self.transactions = []
        self.totals = {
            'openai': 0.0,
            'gemini': 0.0,
            'claude': 0.0,
            'total': 0.0
        }

        # Token counting info
        self.token_info = get_token_counter_info()

        # Print setup info
        self._print_setup_info()

    def _print_setup_info(self):
        """Print setup information."""
        print(f"💰 LLM Cost Tracker initialized (Session: {self.session_id})")
        print("📋 Tracking models: OpenAI (gpt-3.5-turbo, tts), Gemini (2.0-flash), Claude (all models)")

        if not self.token_info['tiktoken_available']:
            print("⚠️ tiktoken not available - using estimation for token counting (~90% accuracy)")
        if not self.token_info['genai_available']:
            print("⚠️ google-generativeai not available - using estimation for Gemini")
        if not self.token_info['anthropic_available']:
            print("⚠️ anthropic not available - using estimation for Claude")

    def set_clients(self, openai_client=None, gemini_model=None, claude_client=None):
        """Set API clients for more accurate token counting."""
        self.openai_client = openai_client
        self.gemini_model = gemini_model
        self.claude_client = claude_client

        if openai_client:
            print("✅ OpenAI client set for chat and TTS tracking")
        if gemini_model:
            print("✅ Gemini model set for accurate token counting")
        if claude_client:
            print("✅ Claude client set for accurate token counting")

    def track_openai_cost(self, model: str, input_text: str = None, output_text: str = None,
                         input_tokens: int = None, output_tokens: int = None,
                         description: str = '') -> float:
        """
        Track OpenAI chat model cost with automatic token counting.

        Args:
            model: OpenAI model (e.g., 'gpt-3.5-turbo')
            input_text: Input text (for automatic counting)
            output_text: Output text (for automatic counting)
            input_tokens: Manual token count (overrides automatic)
            output_tokens: Manual token count (overrides automatic)
            description: Description for this transaction

        Returns:
            Cost in USD
        """
        if not validate_model('openai', model, 'chat'):
            raise ValueError(f"Unknown OpenAI chat model: {model}. Supported: gpt-3.5-turbo, gpt-4, gpt-4-turbo")

        # Automatic token counting if text provided
        if input_text and input_tokens is None:
            input_tokens = count_tokens(input_text, 'openai', model)
        if output_text and output_tokens is None:
            output_tokens = count_tokens(output_text, 'openai', model)

        if input_tokens is None or output_tokens is None:
            raise ValueError("Need input_tokens and output_tokens (or input_text and output_text)")

        pricing = get_pricing('openai', model, 'chat')
        input_cost = (input_tokens / 1000000) * pricing['input']  # OpenAI pricing per 1M tokens
        output_cost = (output_tokens / 1000000) * pricing['output']
        cost = input_cost + output_cost

        transaction = {
            'timestamp': datetime.now().isoformat(),
            'provider': 'openai',
            'model': model,
            'service': 'chat',
            'description': description,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': cost
        }

        self.transactions.append(transaction)
        self.totals['openai'] += cost
        self.totals['total'] += cost

        print(f"📊 OpenAI Chat: ${cost:.6f} ({model}, {input_tokens}+{output_tokens} tokens)")
        return cost

    def track_claude_cost(self, model: str, input_text: str = None, output_text: str = None,
                         input_tokens: int = None, output_tokens: int = None,
                         description: str = '') -> float:
        """
        Track Claude API cost with automatic token counting.

        Args:
            model: Claude model (e.g., 'claude-3.5-sonnet')
            input_text: Input text (for automatic counting)
            output_text: Output text (for automatic counting)
            input_tokens: Manual token count (overrides automatic)
            output_tokens: Manual token count (overrides automatic)
            description: Description for this transaction

        Returns:
            Cost in USD
        """
        if not validate_model('claude', model):
            supported_models = ', '.join(CLAUDE_MODELS)
            raise ValueError(f"Unknown Claude model: {model}. Supported: {supported_models}")

        # Automatic token counting if text provided
        if input_text and input_tokens is None:
            input_tokens = count_tokens(input_text, 'claude', self.claude_client)
        if output_text and output_tokens is None:
            output_tokens = count_tokens(output_text, 'claude', self.claude_client)

        if input_tokens is None or output_tokens is None:
            raise ValueError("Need input_tokens and output_tokens (or input_text and output_text)")

        pricing = get_pricing('claude', model)
        input_cost = (input_tokens / 1000000) * pricing['input']  # Claude pricing per 1M tokens
        output_cost = (output_tokens / 1000000) * pricing['output']
        cost = input_cost + output_cost

        transaction = {
            'timestamp': datetime.now().isoformat(),
            'provider': 'claude',
            'model': model,
            'service': 'chat',
            'description': description,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': cost
        }

        self.transactions.append(transaction)
        self.totals['claude'] += cost
        self.totals['total'] += cost

        print(f"📊 Claude: ${cost:.6f} ({model}, {input_tokens}+{output_tokens} tokens)")
        return cost

    def track_gemini_cost(self, model: str = 'gemini-2.0-flash',
                         input_text: str = None, output_text: str = None,
                         input_tokens: int = None, output_tokens: int = None,
                         description: str = '') -> float:
        """
        Track Gemini API cost with automatic token counting.

        Args:
            model: Gemini model (default: 'gemini-2.0-flash')
            input_text: Input text (for automatic counting)
            output_text: Output text (for automatic counting)
            input_tokens: Manual token count (overrides automatic)
            output_tokens: Manual token count (overrides automatic)
            description: Description for this transaction

        Returns:
            Cost in USD
        """
        if not validate_model('gemini', model):
            supported_models = ', '.join(['gemini-2.0-flash', 'gemini-1.5-pro'])
            raise ValueError(f"Unknown Gemini model: {model}. Supported: {supported_models}")

        # Automatic token counting if text provided
        if input_text and input_tokens is None:
            input_tokens = count_tokens(input_text, 'gemini', self.gemini_model)
        if output_text and output_tokens is None:
            output_tokens = count_tokens(output_text, 'gemini', self.gemini_model)

        if input_tokens is None or output_tokens is None:
            raise ValueError("Need input_tokens and output_tokens (or input_text and output_text)")

        pricing = get_pricing('gemini', model)
        input_cost = (input_tokens / 1000000) * pricing['input']  # Gemini pricing per 1M tokens
        output_cost = (output_tokens / 1000000) * pricing['output']
        cost = input_cost + output_cost

        transaction = {
            'timestamp': datetime.now().isoformat(),
            'provider': 'gemini',
            'model': model,
            'service': 'chat',
            'description': description,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': cost
        }

        self.transactions.append(transaction)
        self.totals['gemini'] += cost
        self.totals['total'] += cost

        print(f"📊 Gemini: ${cost:.6f} ({model}, {input_tokens}+{output_tokens} tokens)")
        return cost

    def track_tts_cost(self, model: str, text: str, description: str = '') -> float:
        """
        Track OpenAI TTS cost with automatic character counting.

        Args:
            model: TTS model ('tts-1' or 'tts-1-hd')
            text: Text to be converted to speech
            description: Description for this transaction

        Returns:
            Cost in USD
        """
        if not validate_model('openai', model, 'tts'):
            raise ValueError(f"Unknown TTS model: {model}. Supported: tts-1, tts-1-hd")

        characters = len(text)
        pricing = get_pricing('openai', model, 'tts')
        cost = (characters / 1000000) * pricing  # Correct calculation for per-1M pricing

        transaction = {
            'timestamp': datetime.now().isoformat(),
            'provider': 'openai',
            'model': model,
            'service': 'tts',
            'description': description,
            'characters': characters,
            'total_cost': cost
        }

        self.transactions.append(transaction)
        self.totals['openai'] += cost
        self.totals['total'] += cost

        print(f"📊 OpenAI TTS: ${cost:.6f} ({model}, {characters} chars)")
        return cost

    def print_summary(self):
        """Print a formatted summary of all costs."""
        print(f"\n💰 COST SUMMARY - Session: {self.session_id}")
        print("=" * 50)

        if not self.transactions:
            print("No transactions recorded.")
            return

        # Print per-provider totals
        print("📊 Provider Totals:")
        for provider, total in self.totals.items():
            if provider != 'total' and total > 0:
                print(f"  {provider.title()}: ${total:.6f}")

        print(f"\n🎯 TOTAL SESSION COST: ${self.totals['total']:.6f}")

        # Print transaction details
        print(f"\n📋 Transaction Details ({len(self.transactions)} transactions):")
        for i, trans in enumerate(self.transactions[-5:], 1):  # Show last 5
            provider = trans['provider']
            model = trans['model']
            cost = trans['total_cost']
            desc = trans.get('description', 'No description')
            print(f"  {i}. {provider}/{model}: ${cost:.6f} - {desc}")

        if len(self.transactions) > 5:
            print(f"  ... and {len(self.transactions) - 5} more transactions")

        # Calculate session duration
        duration = datetime.now() - self.start_time
        print(f"\n⏱️ Session Duration: {duration}")

    def export_to_csv(self, filename: str):
        """Export transaction data to CSV file."""
        try:
            import csv

            if not self.transactions:
                print(f"No transactions to export to {filename}")
                return None

            # Simple approach: export essential info only
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(['timestamp', 'provider', 'model', 'description', 'cost'])

                # Write data rows
                for trans in self.transactions:
                    writer.writerow([
                        trans['timestamp'],
                        trans['provider'],
                        trans['model'],
                        trans.get('description', ''),
                        trans['total_cost']
                    ])

            print(f"✅ Exported {len(self.transactions)} transactions to {filename}")
            return filename

        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return None

    def export_to_dict(self) -> dict:
        """Export all session data as dictionary."""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'totals': self.totals.copy(),
            'transaction_count': len(self.transactions),
            'transactions': self.transactions.copy(),
            'token_counter_info': self.token_info
        }

    def get_session_report(self) -> str:
        """Get formatted session report as string."""
        report = []
        report.append(f"Session ID: {self.session_id}")
        report.append(f"Duration: {datetime.now() - self.start_time}")
        report.append(f"Total Cost: ${self.totals['total']:.6f}")
        report.append(f"Transactions: {len(self.transactions)}")

        if self.totals['openai'] > 0:
            report.append(f"OpenAI Cost: ${self.totals['openai']:.6f}")
        if self.totals['gemini'] > 0:
            report.append(f"Gemini Cost: ${self.totals['gemini']:.6f}")
        if self.totals['claude'] > 0:
            report.append(f"Claude Cost: ${self.totals['claude']:.6f}")

        return "\n".join(report)

    def reset_session(self):
        """Reset current session data."""
        self.transactions = []
        self.totals = {
            'openai': 0.0,
            'gemini': 0.0,
            'claude': 0.0,
            'total': 0.0
        }
        self.start_time = datetime.now()
        print(f"🔄 Session {self.session_id} reset")

    def get_cost_by_provider(self, provider: str) -> float:
        """Get total cost for specific provider."""
        return self.totals.get(provider, 0.0)

    def get_transaction_count(self) -> int:
        """Get total number of transactions."""
        return len(self.transactions)

    def get_last_transaction(self) -> dict:
        """Get the last transaction."""
        return self.transactions[-1] if self.transactions else None
