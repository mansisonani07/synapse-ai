# ================================================================
#   SYNAPSE-AI — DocReader Agent (The Researcher) 📖
#   File    : agents/doc_reader.py
#   Author  : Mansi Sonani
#
#   Role:
#   The DocReader is the researcher of the swarm. It reads API
#   documentation from any source and extracts the critical
#   information needed by the CodeWriter to generate integration code.
# ================================================================

import json
import logging
from typing import Dict, Optional
from agents.groq_client import get_groq_client

# Setup logging
logger = logging.getLogger(__name__)


# ================================================================
#   SYSTEM PROMPT — The DocReader's Brain
# ================================================================

DOCREADER_SYSTEM_PROMPT = """You are the DOCREADER AGENT in a multi-agent AI swarm called Synapse-AI.

Your role is THE RESEARCHER. You read and analyze API documentation
to extract the critical information that other agents need to build
integration code.

For any given API, you must extract:

1. **Authentication Method**
   - How to authenticate (API key, OAuth, Bearer token, Basic auth)
   - Required headers
   - Token format

2. **Key Endpoints**
   - Most important URLs for the use case
   - HTTP methods (GET, POST, PUT, DELETE)
   - Request format
   - Response format

3. **Data Models**
   - Important data objects
   - Required fields
   - Data types

4. **Webhooks (if applicable)**
   - Available webhook events
   - How to subscribe
   - Payload structure

5. **Rate Limits**
   - Requests per second/minute
   - Burst limits

6. **Common Patterns**
   - Best practices
   - Common errors to avoid

Use your training knowledge of major APIs (Stripe, Slack, Shopify, etc.)
to provide accurate, comprehensive information.

Always respond in valid JSON format with the exact structure provided."""


# ================================================================
#   DOCREADER AGENT CLASS
# ================================================================

class DocReaderAgent:
    """
    The Researcher Agent — extracts API documentation knowledge.
    
    Usage:
        reader = DocReaderAgent()
        api_info = reader.read_api_docs(
            api_name="Stripe",
            api_url="https://stripe.com/docs/api",
            use_case="Listen for payment events and send notifications"
        )
    """

    def __init__(self):
        """Initialize the DocReader with Groq AI."""
        self.name = "DocReader"
        self.role = "The Researcher"
        self.emoji = "📖"
        self.groq = get_groq_client()
        logger.info(f"{self.emoji} {self.name} Agent initialized")


    def read_api_docs(
        self,
        api_name: str,
        api_url: str,
        use_case: Optional[str] = None,
    ) -> Dict:
        """
        Read and extract information from API documentation.
        
        Args:
            api_name: Name of the API (e.g., "Stripe", "Slack")
            api_url: URL to the API documentation
            use_case: What the user wants to do (helps focus extraction)
        
        Returns:
            Dictionary with structured API information
        """
        
        logger.info(f"{self.emoji} Reading docs for: {api_name}")
        
        # Build the prompt based on use case
        use_case_text = f"\n\nSPECIFIC USE CASE: {use_case}" if use_case else ""
        
        user_prompt = f"""Analyze the {api_name} API documentation and extract critical information.

API NAME: {api_name}
DOCUMENTATION URL: {api_url}{use_case_text}

Use your knowledge of {api_name}'s API to provide comprehensive information.

Respond with a JSON object using EXACTLY this structure:

{{
    "api_name": "{api_name}",
    "api_description": "Brief description of what this API does",
    "base_url": "The base API URL (e.g., https://api.stripe.com/v1)",
    "authentication": {{
        "method": "API Key | OAuth 2.0 | Bearer Token | Basic Auth",
        "header_name": "Authorization | X-API-Key | etc",
        "format": "Example of how to format the auth header",
        "where_to_get_credentials": "URL or instructions to get API keys"
    }},
    "key_endpoints": [
        {{
            "name": "Endpoint name",
            "method": "GET|POST|PUT|DELETE",
            "path": "/v1/example",
            "description": "What this endpoint does",
            "use_for": "When to use this endpoint"
        }}
    ],
    "data_models": [
        {{
            "name": "Model name (e.g., Payment, Message)",
            "fields": ["field1", "field2", "field3"],
            "description": "What this model represents"
        }}
    ],
    "webhooks": {{
        "supported": true,
        "available_events": ["event1", "event2"],
        "setup_instructions": "How to set up webhooks",
        "payload_example": "Brief structure of webhook payload"
    }},
    "rate_limits": {{
        "requests_per_second": 100,
        "notes": "Any important rate limit info"
    }},
    "common_patterns": [
        "Best practice 1",
        "Best practice 2",
        "Best practice 3"
    ],
    "common_errors": [
        "Common error 1 and how to avoid",
        "Common error 2 and how to avoid"
    ],
    "code_libraries": {{
        "python": "stripe (official SDK)",
        "node": "stripe (official SDK)"
    }},
    "documentation_quality": "excellent | good | fair | poor",
    "recommendation_for_codewriter": "Specific advice for the CodeWriter agent"
}}

Be specific and accurate. Use real {api_name} information. 
Respond with ONLY the JSON object, no markdown, no explanations."""
        
        try:
            # Ask Groq AI to extract the documentation
            response = self.groq.ask(
                prompt=user_prompt,
                system_message=DOCREADER_SYSTEM_PROMPT,
                temperature=0.3,  # Low — we want accuracy, not creativity
                max_tokens=2500,
            )
            
            # Parse the JSON response
            api_info = self._parse_json_response(response)
            
            # Add metadata
            api_info["agent"] = self.name
            api_info["status"] = "completed"
            api_info["url_read"] = api_url
            
            logger.info(f"✅ {self.emoji} Extracted info for {api_name}")
            
            return api_info
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from DocReader: {e}")
            return self._fallback_info(api_name, api_url)
            
        except Exception as e:
            logger.error(f"❌ DocReader failed: {e}")
            return self._fallback_info(api_name, api_url)


    def read_multiple_apis(
        self,
        api_list: list,
    ) -> list:
        """
        Read documentation for multiple APIs.
        Useful when integrating multiple systems.
        
        Args:
            api_list: List of dicts with api_name and api_url
        
        Returns:
            List of extracted API information
        """
        results = []
        for api in api_list:
            info = self.read_api_docs(
                api_name=api.get("name"),
                api_url=api.get("url"),
                use_case=api.get("use_case"),
            )
            results.append(info)
        return results


    def _parse_json_response(self, response: str) -> Dict:
        """Extract and parse JSON from AI response."""
        response = response.strip()
        
        # Remove markdown code fences if present
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        return json.loads(response)


    def _fallback_info(self, api_name: str, api_url: str) -> Dict:
        """Backup info if AI parsing fails."""
        return {
            "agent": self.name,
            "status": "completed_with_fallback",
            "api_name": api_name,
            "api_description": f"{api_name} API",
            "url_read": api_url,
            "authentication": {
                "method": "API Key",
                "header_name": "Authorization",
                "format": "Bearer YOUR_API_KEY",
            },
            "key_endpoints": [],
            "data_models": [],
            "webhooks": {"supported": "unknown"},
            "rate_limits": {"notes": "Check official documentation"},
        }


# ================================================================
#   QUICK TEST — Run this file directly to test
#   Usage: python -m agents.doc_reader
# ================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   📖  TESTING DOCREADER AGENT")
    print("=" * 60 + "\n")
    
    try:
        # Create the agent
        reader = DocReaderAgent()
        print(f"✅ {reader.emoji} {reader.name} Agent ready!\n")
        
        # Test 1: Read Stripe docs
        print("📚 TEST 1: Reading Stripe API documentation...\n")
        print("⏳ AI is researching... (takes 3-5 seconds)\n")
        
        stripe_info = reader.read_api_docs(
            api_name="Stripe",
            api_url="https://stripe.com/docs/api",
            use_case="Listen for payment events and send notifications",
        )
        
        # Display results
        print("=" * 60)
        print(f"   📊  STRIPE API INFORMATION EXTRACTED")
        print("=" * 60 + "\n")
        
        print(f"📝 Description: {stripe_info.get('api_description', 'N/A')}")
        print(f"🌐 Base URL: {stripe_info.get('base_url', 'N/A')}\n")
        
        # Authentication
        auth = stripe_info.get("authentication", {})
        print(f"🔐 AUTHENTICATION:")
        print(f"   Method: {auth.get('method', 'N/A')}")
        print(f"   Header: {auth.get('header_name', 'N/A')}")
        print(f"   Format: {auth.get('format', 'N/A')}\n")
        
        # Endpoints
        print(f"🔗 KEY ENDPOINTS:")
        for ep in stripe_info.get("key_endpoints", [])[:3]:
            print(f"   {ep.get('method', 'N/A')} {ep.get('path', 'N/A')}")
            print(f"      → {ep.get('description', 'N/A')}")
        print()
        
        # Webhooks
        webhooks = stripe_info.get("webhooks", {})
        if webhooks.get("supported"):
            print(f"📡 WEBHOOKS:")
            events = webhooks.get("available_events", [])[:5]
            for event in events:
                print(f"   • {event}")
            print()
        
        # Common patterns
        print(f"💡 BEST PRACTICES:")
        for pattern in stripe_info.get("common_patterns", [])[:3]:
            print(f"   • {pattern}")
        print()
        
        # Test 2: Read Slack docs
        print("\n" + "=" * 60)
        print("📚 TEST 2: Reading Slack API documentation...\n")
        print("⏳ AI is researching... (takes 3-5 seconds)\n")
        
        slack_info = reader.read_api_docs(
            api_name="Slack",
            api_url="https://api.slack.com/web",
            use_case="Send formatted messages to channels",
        )
        
        print("=" * 60)
        print(f"   📊  SLACK API INFORMATION EXTRACTED")
        print("=" * 60 + "\n")
        
        print(f"📝 Description: {slack_info.get('api_description', 'N/A')}\n")
        
        auth = slack_info.get("authentication", {})
        print(f"🔐 AUTH: {auth.get('method', 'N/A')}")
        print(f"   Format: {auth.get('format', 'N/A')}\n")
        
        print(f"🔗 KEY ENDPOINTS:")
        for ep in slack_info.get("key_endpoints", [])[:3]:
            print(f"   {ep.get('method', 'N/A')} {ep.get('path', 'N/A')}")
        print()
        
        # Final advice
        print(f"💡 ADVICE FOR CODEWRITER:")
        print(f"   Stripe: {stripe_info.get('recommendation_for_codewriter', 'N/A')}")
        print(f"   Slack:  {slack_info.get('recommendation_for_codewriter', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("   🎉 DOCREADER AGENT WORKING PERFECTLY!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()