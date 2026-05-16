# ================================================================
#   SYNAPSE-AI — Orchestrator Agent (The Manager) 🧠
#   File    : agents/orchestrator.py
#   Author  : Mansi Sonani
#
#   Role:
#   The Orchestrator is the brain that reads what the user wants
#   and creates a step-by-step plan for the entire AI swarm.
#   Think of it as the Project Manager of the team.
# ================================================================

import json
import logging
from typing import Dict, List, Optional
from agents.groq_client import get_groq_client

# Setup logging
logger = logging.getLogger(__name__)


# ================================================================
#   SYSTEM PROMPT — The Orchestrator's Brain & Personality
# ================================================================

ORCHESTRATOR_SYSTEM_PROMPT = """You are the ORCHESTRATOR AGENT in a multi-agent AI swarm called Synapse-AI.

Your role is THE MANAGER. You receive integration requests from users
and create detailed execution plans for the other 4 agents in the swarm:

1. 📖 DocReader Agent — fetches and reads API documentation
2. ✍️ CodeWriter Agent — generates production-ready integration code
3. 🧪 Tester Agent — tests the generated code in a sandbox
4. ✅ Validator Agent — performs security audit on the code

Your job is to:
1. Understand the user's integration request clearly
2. Identify the source API (Company A) and target API (Company B)
3. Determine what data flow is needed
4. Create a detailed step-by-step plan
5. Identify potential challenges
6. Decide what each agent must do

Always respond in valid JSON format with the exact structure provided.
Be precise, professional, and think like a senior software architect."""


# ================================================================
#   ORCHESTRATOR AGENT CLASS
# ================================================================

class OrchestratorAgent:
    """
    The Manager Agent — plans and delegates tasks to other agents.
    
    Usage:
        orchestrator = OrchestratorAgent()
        plan = orchestrator.create_plan(
            integration_name="Stripe to Slack",
            api_a_name="Stripe",
            api_a_url="https://stripe.com/docs",
            api_b_name="Slack",
            api_b_url="https://api.slack.com",
            tech_stack="python"
        )
    """

    def __init__(self):
        """Initialize the Orchestrator with Groq AI."""
        self.name = "Orchestrator"
        self.role = "The Manager"
        self.emoji = "🧠"
        self.groq = get_groq_client()
        logger.info(f"{self.emoji} {self.name} Agent initialized")


    def create_plan(
        self,
        integration_name: str,
        api_a_name: str,
        api_a_url: str,
        api_b_name: str,
        api_b_url: str,
        tech_stack: str = "python",
    ) -> Dict:
        """
        Create a detailed integration plan using AI.
        
        Args:
            integration_name: User-friendly name (e.g., "Stripe to Slack")
            api_a_name: Source API name (e.g., "Stripe")
            api_a_url: Source API documentation URL
            api_b_name: Target API name (e.g., "Slack")
            api_b_url: Target API documentation URL
            tech_stack: Programming language ("python" or "node")
        
        Returns:
            Dictionary containing the complete execution plan
        """
        
        logger.info(f"{self.emoji} Creating plan for: {integration_name}")
        
        # Build the user prompt with all integration details
        user_prompt = f"""Create a detailed execution plan for this integration:

INTEGRATION REQUEST:
- Name: {integration_name}
- Source API (Company A): {api_a_name}
- Source API Documentation: {api_a_url}
- Target API (Company B): {api_b_name}
- Target API Documentation: {api_b_url}
- Tech Stack: {tech_stack}

Respond with a JSON object using EXACTLY this structure:

{{
    "understanding": "Brief description of what the user wants to achieve",
    "data_flow": "How data should flow from {api_a_name} to {api_b_name}",
    "estimated_complexity": "low|medium|high",
    "estimated_time_minutes": 10,
    "tasks": [
        {{
            "step": 1,
            "agent": "DocReader",
            "action": "Fetch {api_a_name} API documentation",
            "expected_outcome": "Extract auth methods, endpoints, and data models"
        }},
        {{
            "step": 2,
            "agent": "DocReader",
            "action": "Fetch {api_b_name} API documentation",
            "expected_outcome": "Extract auth methods, endpoints, and webhooks"
        }},
        {{
            "step": 3,
            "agent": "CodeWriter",
            "action": "Generate {tech_stack} integration code",
            "expected_outcome": "Production-ready code connecting both APIs"
        }},
        {{
            "step": 4,
            "agent": "Tester",
            "action": "Run code in secure sandbox",
            "expected_outcome": "Verify code works without errors"
        }},
        {{
            "step": 5,
            "agent": "Validator",
            "action": "Security audit and final approval",
            "expected_outcome": "No exposed credentials or security issues"
        }}
    ],
    "potential_challenges": [
        "List 2-3 specific challenges for this integration"
    ],
    "success_criteria": [
        "List 3 specific things that must work for success"
    ]
}}

Respond with ONLY the JSON object, no markdown, no explanations."""
        
        try:
            # Ask Groq AI to create the plan
            response = self.groq.ask(
                prompt=user_prompt,
                system_message=ORCHESTRATOR_SYSTEM_PROMPT,
                temperature=0.5,  # Balanced — not too creative
                max_tokens=2000,
            )
            
            # Parse the JSON response
            plan = self._parse_json_response(response)
            
            # Add metadata
            plan["agent"] = self.name
            plan["integration_name"] = integration_name
            plan["status"] = "completed"
            
            logger.info(f"✅ {self.emoji} Plan created with {len(plan.get('tasks', []))} tasks")
            
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from Orchestrator: {e}")
            return self._fallback_plan(integration_name, api_a_name, api_b_name, tech_stack)
            
        except Exception as e:
            logger.error(f"❌ Orchestrator failed: {e}")
            return self._fallback_plan(integration_name, api_a_name, api_b_name, tech_stack)


    def _parse_json_response(self, response: str) -> Dict:
        """Extract and parse JSON from AI response."""
        # Sometimes AI adds markdown code blocks — clean them
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


    def _fallback_plan(
        self,
        integration_name: str,
        api_a_name: str,
        api_b_name: str,
        tech_stack: str,
    ) -> Dict:
        """Backup plan if AI parsing fails."""
        return {
            "agent": self.name,
            "integration_name": integration_name,
            "status": "completed_with_fallback",
            "understanding": f"Integration between {api_a_name} and {api_b_name}",
            "data_flow": f"Data flows from {api_a_name} to {api_b_name}",
            "estimated_complexity": "medium",
            "estimated_time_minutes": 10,
            "tasks": [
                {"step": 1, "agent": "DocReader", "action": f"Fetch {api_a_name} docs"},
                {"step": 2, "agent": "DocReader", "action": f"Fetch {api_b_name} docs"},
                {"step": 3, "agent": "CodeWriter", "action": f"Generate {tech_stack} code"},
                {"step": 4, "agent": "Tester", "action": "Test in sandbox"},
                {"step": 5, "agent": "Validator", "action": "Security audit"},
            ],
            "potential_challenges": ["API rate limits", "Authentication setup"],
            "success_criteria": ["Code runs", "Tests pass", "Secure credentials"],
        }


# ================================================================
#   QUICK TEST — Run this file directly to test
#   Usage: python -m agents.orchestrator
# ================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   🧠  TESTING ORCHESTRATOR AGENT")
    print("=" * 60 + "\n")
    
    try:
        # Create the agent
        orchestrator = OrchestratorAgent()
        print(f"✅ {orchestrator.emoji} {orchestrator.name} Agent ready!\n")
        
        # Test it with a real integration request
        print("📨 Sending integration request:")
        print("   - Connect Stripe to Slack")
        print("   - Tech: Python\n")
        print("⏳ Asking AI to create plan... (takes 3-5 seconds)\n")
        
        plan = orchestrator.create_plan(
            integration_name="Stripe to Slack Notifier",
            api_a_name="Stripe",
            api_a_url="https://stripe.com/docs/api",
            api_b_name="Slack",
            api_b_url="https://api.slack.com/web",
            tech_stack="python",
        )
        
        # Display the plan beautifully
        print("=" * 60)
        print("   🎉 PLAN CREATED BY AI!")
        print("=" * 60 + "\n")
        
        print(f"📋 Understanding: {plan.get('understanding', 'N/A')}\n")
        print(f"🌊 Data Flow: {plan.get('data_flow', 'N/A')}\n")
        print(f"⚡ Complexity: {plan.get('estimated_complexity', 'N/A')}")
        print(f"⏱️  Estimated Time: {plan.get('estimated_time_minutes', 0)} minutes\n")
        
        print("📝 EXECUTION PLAN:")
        print("-" * 60)
        for task in plan.get("tasks", []):
            agent = task.get("agent", "Unknown")
            action = task.get("action", "N/A")
            outcome = task.get("expected_outcome", "")
            print(f"  Step {task.get('step')}: {agent}")
            print(f"     Action: {action}")
            if outcome:
                print(f"     Outcome: {outcome}")
            print()
        
        print("⚠️  POTENTIAL CHALLENGES:")
        for challenge in plan.get("potential_challenges", []):
            print(f"  • {challenge}")
        
        print("\n✅ SUCCESS CRITERIA:")
        for criteria in plan.get("success_criteria", []):
            print(f"  • {criteria}")
        
        print("\n" + "=" * 60)
        print("   🎉 ORCHESTRATOR AGENT WORKING PERFECTLY!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")