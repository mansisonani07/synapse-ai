import json
import logging
import re
from typing import Dict
from agents.groq_client import get_groq_client

logger = logging.getLogger(__name__)

TESTER_PROMPT = """You are a QA TESTER. Analyze code for bugs. Respond in JSON with: verdict (PASS/FAIL/PASS_WITH_WARNINGS), quality_score (1-10), bugs_found (list), improvements (list), production_ready (true/false), summary (string)."""

VALIDATOR_PROMPT = """You are a SECURITY AUDITOR. Audit code for security issues. Respond in JSON with: verdict (APPROVED/REJECTED/APPROVED_WITH_WARNINGS), security_score (1-10), critical_issues (list), warnings (list), checklist (object), exposed_credentials (bool), production_safe (bool), summary (string)."""


class TesterAgent:
    def __init__(self):
        self.name = "Tester"
        self.groq = get_groq_client()
        logger.info("Tester Agent initialized")

    def test_code(self, code, integration_name, tech_stack="python"):
        logger.info(f"Testing code for: {integration_name}")
        if not code or len(code.strip()) < 10:
            return {"agent": self.name, "status": "failed", "verdict": "FAIL"}

        prompt = f"Test this {tech_stack} code for bugs:\n\n```\n{code}\n```\n\nRespond in JSON with verdict, quality_score, bugs_found, improvements, production_ready, summary."

        try:
            response = self.groq.ask(prompt=prompt, system_message=TESTER_PROMPT, temperature=0.3, max_tokens=2500)
            result = self._parse(response)
            result["agent"] = self.name
            result["status"] = "completed"
            logger.info(f"Test verdict: {result.get('verdict')}")
            return result
        except Exception as e:
            logger.error(f"Tester failed: {e}")
            return {"agent": self.name, "status": "failed", "error": str(e)}

    def _parse(self, response):
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return json.loads(response.strip())


class ValidatorAgent:
    def __init__(self):
        self.name = "Validator"
        self.groq = get_groq_client()
        logger.info("Validator Agent initialized")

    def audit_security(self, code, integration_name, tech_stack="python"):
        logger.info(f"Auditing security for: {integration_name}")
        if not code or len(code.strip()) < 10:
            return {"agent": self.name, "status": "failed", "verdict": "FAIL"}

        quick = self._quick_scan(code)

        prompt = f"Security audit this {tech_stack} code:\n\n```\n{code}\n```\n\nQuick scan: {quick}\n\nRespond in JSON with verdict, security_score, critical_issues, warnings, checklist, exposed_credentials, production_safe, summary."

        try:
            response = self.groq.ask(prompt=prompt, system_message=VALIDATOR_PROMPT, temperature=0.2, max_tokens=2500)
            result = self._parse(response)
            result["agent"] = self.name
            result["status"] = "completed"
            result["quick_scan"] = quick
            logger.info(f"Audit verdict: {result.get('verdict')}")
            return result
        except Exception as e:
            logger.error(f"Validator failed: {e}")
            return {"agent": self.name, "status": "failed", "error": str(e)}

    def _quick_scan(self, code):
        return {
            "hardcoded_keys": len(re.findall(r'sk_[a-zA-Z0-9]{20,}', code)),
            "env_vars_used": code.count("os.environ"),
            "https_count": code.count("https://"),
            "http_count": len(re.findall(r'(?<!s)http://', code)),
            "try_except": code.count("try:"),
            "logger_calls": code.count("logger."),
        }

    def _parse(self, response):
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return json.loads(response.strip())


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   TESTING TESTER + VALIDATOR AGENTS")
    print("=" * 60)

    sample_code = """import os
import requests
import json

STRIPE_KEY = os.environ.get('STRIPE_SECRET_KEY')
SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

def send_slack(event):
    try:
        url = 'https://slack.com/api/chat.postMessage'
        headers = {'Authorization': f'Bearer {SLACK_TOKEN}', 'Content-Type': 'application/json'}
        payload = {'channel': '#general', 'text': f'Payment: {event["data"]["object"]["id"]}'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print('Sent')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Error: {e}')

def webhook(event):
    if event['type'] == 'payment_intent.succeeded':
        send_slack(event)
"""

    print("\n--- PART 1: TESTER ---\n")
    try:
        tester = TesterAgent()
        print("Testing code...\n")
        result = tester.test_code(sample_code, "Stripe to Slack", "python")
        print(f"Verdict: {result.get('verdict', 'N/A')}")
        print(f"Quality: {result.get('quality_score', 'N/A')}/10")
        print(f"Summary: {result.get('summary', 'N/A')}")
        bugs = result.get("bugs_found", [])
        if bugs:
            print(f"\nBugs ({len(bugs)}):")
            for b in bugs[:5]:
                print(f"  [{b.get('severity','?')}] {b.get('issue','')}")
        improvements = result.get("improvements", [])
        if improvements:
            print(f"\nImprovements:")
            for i in improvements[:5]:
                print(f"  - {i}")
    except Exception as e:
        print(f"Tester Error: {e}")

    print("\n--- PART 2: VALIDATOR ---\n")
    try:
        validator = ValidatorAgent()
        print("Auditing security...\n")
        result = validator.audit_security(sample_code, "Stripe to Slack", "python")
        print(f"Verdict: {result.get('verdict', 'N/A')}")
        print(f"Security: {result.get('security_score', 'N/A')}/10")
        print(f"Summary: {result.get('summary', 'N/A')}")
        print(f"\nQuick Scan: {result.get('quick_scan', {})}")
        issues = result.get("critical_issues", [])
        if issues:
            print(f"\nCritical Issues ({len(issues)}):")
            for i in issues[:5]:
                print(f"  - {i.get('issue','')}")
        checklist = result.get("checklist", {})
        if checklist:
            print(f"\nChecklist:")
            for k, v in checklist.items():
                print(f"  [{'OK' if v else 'NO'}] {k}")
    except Exception as e:
        print(f"Validator Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("   DONE!")
    print("=" * 60)