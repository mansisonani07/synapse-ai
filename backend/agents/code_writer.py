import logging
from typing import Dict, Optional
from agents.groq_client import get_groq_client

logger = logging.getLogger(__name__)


CODEWRITER_SYSTEM_PROMPT = """You are the CODEWRITER AGENT in a multi-agent AI swarm.
Your role is THE DEVELOPER. You write production-ready integration code.
Always use environment variables, add error handling, include logging.
Respond with code in markdown blocks plus env variables, install instructions, and notes."""


class CodeWriterAgent:
    def __init__(self):
        self.name = "CodeWriter"
        self.role = "The Developer"
        self.emoji = "writing"
        self.groq = get_groq_client()
        logger.info(f"CodeWriter Agent initialized")


    def generate_code(self, integration_name, api_a_info, api_b_info, tech_stack="python", additional_requirements=None):
        logger.info(f"Generating code for: {integration_name}")
        
        api_a_name = api_a_info.get("api_name", "Source API")
        api_b_name = api_b_info.get("api_name", "Target API")
        api_a_auth = api_a_info.get("authentication", {})
        api_b_auth = api_b_info.get("authentication", {})
        
        extra_reqs = ""
        if additional_requirements:
            extra_reqs = "\n\nADDITIONAL: " + additional_requirements
        
        events_list = api_a_info.get("webhooks", {}).get("available_events", [])[:5]
        api_a_events = ", ".join(events_list)
        
        endpoints_list = [ep.get("path") for ep in api_b_info.get("key_endpoints", [])[:3]]
        api_b_endpoints = str(endpoints_list)
        
        user_prompt = f"""Generate complete production-ready {tech_stack} code for: {integration_name}

SOURCE API ({api_a_name}):
- Description: {api_a_info.get('api_description', 'N/A')}
- Base URL: {api_a_info.get('base_url', 'N/A')}
- Auth: {api_a_auth.get('method', 'API Key')}
- Format: {api_a_auth.get('format', 'Bearer TOKEN')}
- Webhook Events: {api_a_events}

TARGET API ({api_b_name}):
- Description: {api_b_info.get('api_description', 'N/A')}
- Auth: {api_b_auth.get('method', 'API Key')}
- Format: {api_b_auth.get('format', 'Bearer TOKEN')}
- Endpoints: {api_b_endpoints}{extra_reqs}

Write {tech_stack} code that connects these APIs with error handling, logging, and env variables.

Format your response with sections: ## CODE, ## REQUIRED ENVIRONMENT VARIABLES, ## INSTALLATION, ## USAGE, ## IMPORTANT NOTES

Generate REAL working code, no placeholders."""
        
        try:
            response = self.groq.ask(
                prompt=user_prompt,
                system_message=CODEWRITER_SYSTEM_PROMPT,
                temperature=0.4,
                max_tokens=4000,
            )
            
            result = self._parse_response(response)
            result["agent"] = self.name
            result["status"] = "completed"
            result["integration_name"] = integration_name
            result["tech_stack"] = tech_stack
            result["lines_of_code"] = len(result.get("code", "").split("\n"))
            
            logger.info(f"Generated {result['lines_of_code']} lines of code")
            return result
            
        except Exception as e:
            logger.error(f"CodeWriter failed: {e}")
            return {
                "agent": self.name,
                "status": "failed",
                "error": str(e),
                "code": "",
            }


    def _parse_response(self, response):
        result = {
            "code": "",
            "env_variables": "",
            "installation": "",
            "usage": "",
            "notes": [],
            "raw_response": response,
        }
        
        sections = response.split("##")
        
        for section in sections:
            section = section.strip()
            if section.startswith("CODE"):
                result["code"] = self._get_code(section)
            elif section.startswith("REQUIRED ENVIRONMENT"):
                result["env_variables"] = self._get_code(section)
            elif section.startswith("INSTALLATION"):
                result["installation"] = self._get_code(section)
            elif section.startswith("USAGE"):
                result["usage"] = section.replace("USAGE", "").strip()
            elif section.startswith("IMPORTANT NOTES"):
                notes_text = section.replace("IMPORTANT NOTES", "").strip()
                result["notes"] = [
                    line.strip("- ").strip()
                    for line in notes_text.split("\n")
                    if line.strip().startswith("-")
                ]
        
        return result


    def _get_code(self, text):
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 3:
                code = parts[1]
                lines = code.split("\n")
                if lines and len(lines[0]) < 20 and " " not in lines[0]:
                    code = "\n".join(lines[1:])
                return code.strip()
        return text.strip()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   TESTING CODEWRITER AGENT")
    print("=" * 60 + "\n")
    
    try:
        writer = CodeWriterAgent()
        print("CodeWriter Agent ready!\n")
        
        stripe_info = {
            "api_name": "Stripe",
            "api_description": "Payment processing API",
            "base_url": "https://api.stripe.com/v1",
            "authentication": {
                "method": "Bearer Token",
                "format": "Bearer sk_test_YOUR_KEY"
            },
            "webhooks": {
                "supported": True,
                "available_events": ["payment_intent.succeeded", "payment_intent.failed"]
            },
            "key_endpoints": [{"path": "/v1/charges", "method": "POST"}]
        }
        
        slack_info = {
            "api_name": "Slack",
            "api_description": "Team communication API",
            "authentication": {
                "method": "Bearer Token",
                "format": "Bearer xoxb-YOUR-BOT-TOKEN"
            },
            "key_endpoints": [{"path": "/api/chat.postMessage", "method": "POST"}]
        }
        
        print("Generating code for: Stripe to Slack Notifier")
        print("Tech Stack: Python\n")
        print("AI is writing code (5-10 seconds)...\n")
        
        result = writer.generate_code(
            integration_name="Stripe to Slack Notifier",
            api_a_info=stripe_info,
            api_b_info=slack_info,
            tech_stack="python",
            additional_requirements="Send Slack message when payment succeeds"
        )
        
        print("=" * 60)
        print("   CODE GENERATED!")
        print("=" * 60 + "\n")
        
        print(f"Lines of code: {result.get('lines_of_code', 0)}")
        print(f"Status: {result.get('status', 'N/A')}\n")
        
        print("=" * 60)
        print("GENERATED CODE:")
        print("=" * 60)
        code = result.get("code", "")
        if code:
            code_lines = code.split("\n")
            for i, line in enumerate(code_lines[:50], 1):
                print(f"{i:3} | {line}")
            if len(code_lines) > 50:
                print(f"... and {len(code_lines) - 50} more lines")
        print()
        
        print("=" * 60)
        print("ENVIRONMENT VARIABLES:")
        print("=" * 60)
        env_vars = result.get("env_variables", "")
        if env_vars:
            print(env_vars)
        print()
        
        print("=" * 60)
        print("INSTALLATION:")
        print("=" * 60)
        install = result.get("installation", "")
        if install:
            print(install)
        print()
        
        print("=" * 60)
        print("NOTES:")
        print("=" * 60)
        notes = result.get("notes", [])
        for note in notes:
            print(f"  - {note}")
        
        print("\n" + "=" * 60)
        print("   CODEWRITER AGENT WORKING!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nERROR: {e}\n")
        import traceback
        traceback.print_exc()