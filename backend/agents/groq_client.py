# ================================================================
#   SYNAPSE-AI — Groq AI Client
#   File    : agents/groq_client.py
#   Author  : Mansi Sonani
#
#   Description:
#   This is the REAL AI brain of Synapse-AI.
#   Every agent in our swarm will use this client to talk to Groq.
#   Groq runs Llama 3.3 70B model — fast, free, and powerful.
# ================================================================

import os
import logging
from typing import Optional, List, Dict
from groq import Groq, GroqError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging so we can see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================================================================
#   GROQ CLIENT CLASS
# ================================================================

class GroqClient:
    """
    Wrapper around the Groq API for easier use across all agents.
    
    Usage:
        client = GroqClient()
        response = client.ask("What is Python?")
        print(response)
    """

    def __init__(self):
        """Initialize Groq client with API key from .env file."""
        
        # Get API key from environment
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        # Validate API key exists
        if not self.api_key:
            raise ValueError(
                "❌ GROQ_API_KEY not found in .env file!\n"
                "Please add: GROQ_API_KEY=gsk_your_key_here"
            )
        
        if not self.api_key.startswith("gsk_"):
            raise ValueError(
                "❌ Invalid Groq API key format!\n"
                "Groq keys must start with 'gsk_'"
            )
        
        # Initialize the Groq client
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"✅ Groq client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq: {e}")
            raise


    def ask(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Send a simple question to Groq and get a response.
        
        Args:
            prompt: The user's question or task
            system_message: Optional instructions for the AI's behavior
            temperature: 0.0 (focused) to 1.0 (creative)
            max_tokens: Maximum length of response
        
        Returns:
            The AI's response as a string
        
        Example:
            response = client.ask(
                prompt="Explain Python in 1 sentence",
                system_message="You are a helpful coding teacher"
            )
        """
        
        # Build the messages list
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Add user prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            logger.info(f"🤖 Sending request to Groq ({self.model})...")
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract the response text
            answer = response.choices[0].message.content
            
            # Log success with token usage
            tokens_used = response.usage.total_tokens
            logger.info(f"✅ Groq response received! Tokens used: {tokens_used}")
            
            return answer.strip() if answer else ""
            
        except GroqError as e:
            logger.error(f"❌ Groq API error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise


    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        More advanced — send a full conversation history.
        Used by agents that need multi-turn conversations.
        
        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            temperature: Creativity level
            max_tokens: Max response length
        
        Returns:
            The AI's response
        """
        try:
            logger.info(f"🤖 Sending chat to Groq ({self.model})...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            answer = response.choices[0].message.content
            logger.info(f"✅ Groq chat response received!")
            
            return answer.strip() if answer else ""
            
        except Exception as e:
            logger.error(f"❌ Groq chat error: {e}")
            raise


    def test_connection(self) -> bool:
        """
        Test if Groq is working with a simple ping.
        
        Returns:
            True if working, False otherwise
        """
        try:
            response = self.ask(
                prompt="Reply with exactly: PONG",
                temperature=0.0,
                max_tokens=10,
            )
            return "PONG" in response.upper()
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


# ================================================================
#   SINGLETON INSTANCE
#   Use this everywhere instead of creating new clients
# ================================================================

# Global instance — created once, used everywhere
_groq_instance: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """
    Get the global Groq client instance.
    Creates it once, reuses it everywhere.
    
    Usage in other files:
        from agents.groq_client import get_groq_client
        
        groq = get_groq_client()
        response = groq.ask("Hello AI!")
    """
    global _groq_instance
    if _groq_instance is None:
        _groq_instance = GroqClient()
    return _groq_instance


# ================================================================
#   QUICK TEST — Run this file directly to test
#   Usage: python -m agents.groq_client
# ================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   🧪  TESTING GROQ AI CONNECTION")
    print("=" * 60 + "\n")
    
    try:
        # Create client
        groq = get_groq_client()
        
        # Test 1: Connection ping
        print("Test 1: Connection ping...")
        if groq.test_connection():
            print("✅ Connection works!\n")
        else:
            print("❌ Connection failed!\n")
        
        # Test 2: Simple question
        print("Test 2: Simple question...")
        response = groq.ask(
            prompt="In one sentence, explain what Python is.",
            system_message="You are a helpful coding teacher.",
            temperature=0.5,
        )
        print(f"AI Response: {response}\n")
        
        # Test 3: AI agent simulation
        print("Test 3: Agent simulation...")
        response = groq.ask(
            prompt=(
                "You are an Orchestrator AI agent. A user wants to "
                "build an integration between Stripe and Slack. "
                "List 3 high-level steps you would take."
            ),
            system_message="You are an expert at planning API integrations.",
            temperature=0.7,
        )
        print(f"Agent Response:\n{response}\n")
        
        print("=" * 60)
        print("   🎉  ALL TESTS PASSED! Groq is ready to use!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        print("Check your GROQ_API_KEY in .env file")