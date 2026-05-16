import json
import logging
import time
from typing import TypedDict, Optional
from agents.orchestrator import OrchestratorAgent
from agents.doc_reader import DocReaderAgent
from agents.code_writer import CodeWriterAgent
from agents.tester_validator import TesterAgent, ValidatorAgent

logger = logging.getLogger(__name__)


class SwarmState(TypedDict):
    """Shared state across all agents in the swarm."""
    integration_name: str
    api_a_name: str
    api_a_url: str
    api_b_name: str
    api_b_url: str
    tech_stack: str
    plan: dict
    api_a_info: dict
    api_b_info: dict
    code: str
    code_metadata: dict
    test_result: dict
    audit_result: dict
    current_step: str
    status: str
    error: Optional[str]
    started_at: float
    completed_at: Optional[float]


class SynapseSwarm:
    """The complete AI swarm orchestrating all 5 agents."""

    def __init__(self):
        logger.info("Initializing Synapse-AI Swarm...")
        self.orchestrator = OrchestratorAgent()
        self.doc_reader = DocReaderAgent()
        self.code_writer = CodeWriterAgent()
        self.tester = TesterAgent()
        self.validator = ValidatorAgent()
        logger.info("All 5 agents loaded successfully!")

    def run(
        self,
        integration_name: str,
        api_a_name: str,
        api_a_url: str,
        api_b_name: str,
        api_b_url: str,
        tech_stack: str = "python",
        verbose: bool = True
    ) -> SwarmState:
        """Execute the complete swarm workflow."""

        state: SwarmState = {
            "integration_name": integration_name,
            "api_a_name": api_a_name,
            "api_a_url": api_a_url,
            "api_b_name": api_b_name,
            "api_b_url": api_b_url,
            "tech_stack": tech_stack,
            "plan": {},
            "api_a_info": {},
            "api_b_info": {},
            "code": "",
            "code_metadata": {},
            "test_result": {},
            "audit_result": {},
            "current_step": "starting",
            "status": "in_progress",
            "error": None,
            "started_at": time.time(),
            "completed_at": None,
        }

        if verbose:
            self._print_header(integration_name, api_a_name, api_b_name)

        try:
            state = self._step_1_orchestrate(state, verbose)
            state = self._step_2_research_api_a(state, verbose)
            state = self._step_3_research_api_b(state, verbose)
            state = self._step_4_generate_code(state, verbose)
            state = self._step_5_test_code(state, verbose)
            state = self._step_6_validate_security(state, verbose)
            state["status"] = "completed"
            state["current_step"] = "done"
            state["completed_at"] = time.time()

            if verbose:
                self._print_summary(state)

        except Exception as e:
            logger.error(f"Swarm failed at {state['current_step']}: {e}")
            state["status"] = "failed"
            state["error"] = str(e)
            state["completed_at"] = time.time()

        return state

    def _step_1_orchestrate(self, state, verbose):
        state["current_step"] = "orchestrator"
        if verbose:
            print("\n[STEP 1/6] 🧠 ORCHESTRATOR — Creating execution plan...")

        plan = self.orchestrator.create_plan(
            integration_name=state["integration_name"],
            api_a_name=state["api_a_name"],
            api_a_url=state["api_a_url"],
            api_b_name=state["api_b_name"],
            api_b_url=state["api_b_url"],
            tech_stack=state["tech_stack"],
        )

        state["plan"] = plan
        if verbose:
            print(f"   ✅ Plan created with {len(plan.get('tasks', []))} tasks")
            print(f"   📋 Understanding: {plan.get('understanding', 'N/A')[:80]}...")

        return state

    def _step_2_research_api_a(self, state, verbose):
        state["current_step"] = "doc_reader_api_a"
        if verbose:
            print(f"\n[STEP 2/6] 📖 DOCREADER — Researching {state['api_a_name']} API...")

        info = self.doc_reader.read_api_docs(
            api_name=state["api_a_name"],
            api_url=state["api_a_url"],
            use_case=f"Send data to {state['api_b_name']}",
        )
        state["api_a_info"] = info

        if verbose:
            auth = info.get("authentication", {}).get("method", "N/A")
            endpoints = len(info.get("key_endpoints", []))
            print(f"   ✅ {state['api_a_name']} extracted: {auth} auth, {endpoints} endpoints")

        return state

    def _step_3_research_api_b(self, state, verbose):
        state["current_step"] = "doc_reader_api_b"
        if verbose:
            print(f"\n[STEP 3/6] 📖 DOCREADER — Researching {state['api_b_name']} API...")

        info = self.doc_reader.read_api_docs(
            api_name=state["api_b_name"],
            api_url=state["api_b_url"],
            use_case=f"Receive data from {state['api_a_name']}",
        )
        state["api_b_info"] = info

        if verbose:
            auth = info.get("authentication", {}).get("method", "N/A")
            endpoints = len(info.get("key_endpoints", []))
            print(f"   ✅ {state['api_b_name']} extracted: {auth} auth, {endpoints} endpoints")

        return state

    def _step_4_generate_code(self, state, verbose):
        state["current_step"] = "code_writer"
        if verbose:
            print(f"\n[STEP 4/6] ✍️  CODEWRITER — Generating {state['tech_stack']} code...")

        result = self.code_writer.generate_code(
            integration_name=state["integration_name"],
            api_a_info=state["api_a_info"],
            api_b_info=state["api_b_info"],
            tech_stack=state["tech_stack"],
        )

        state["code"] = result.get("code", "")
        state["code_metadata"] = {
            "lines": result.get("lines_of_code", 0),
            "env_variables": result.get("env_variables", ""),
            "installation": result.get("installation", ""),
            "notes": result.get("notes", []),
        }

        if verbose:
            print(f"   ✅ Generated {state['code_metadata']['lines']} lines of code")

        return state

    def _step_5_test_code(self, state, verbose):
        state["current_step"] = "tester"
        if verbose:
            print(f"\n[STEP 5/6] 🧪 TESTER — Testing code for bugs...")

        result = self.tester.test_code(
            code=state["code"],
            integration_name=state["integration_name"],
            tech_stack=state["tech_stack"],
        )
        state["test_result"] = result

        if verbose:
            verdict = result.get("verdict", "N/A")
            score = result.get("quality_score", "N/A")
            print(f"   ✅ Test verdict: {verdict} | Quality: {score}/10")

        return state

    def _step_6_validate_security(self, state, verbose):
        state["current_step"] = "validator"
        if verbose:
            print(f"\n[STEP 6/6] ✅ VALIDATOR — Security audit...")

        result = self.validator.audit_security(
            code=state["code"],
            integration_name=state["integration_name"],
            tech_stack=state["tech_stack"],
        )
        state["audit_result"] = result

        if verbose:
            verdict = result.get("verdict", "N/A")
            score = result.get("security_score", "N/A")
            print(f"   ✅ Security verdict: {verdict} | Score: {score}/10")

        return state

    def _print_header(self, name, api_a, api_b):
        print("\n" + "=" * 70)
        print(f"   🚀 SYNAPSE-AI SWARM ACTIVATED")
        print("=" * 70)
        print(f"   Integration: {name}")
        print(f"   Connecting:  {api_a} → {api_b}")
        print("=" * 70)

    def _print_summary(self, state):
        duration = state["completed_at"] - state["started_at"]
        print("\n" + "=" * 70)
        print("   🎉 SWARM EXECUTION COMPLETE!")
        print("=" * 70)
        print(f"   ⏱️  Total time:    {duration:.1f} seconds")
        print(f"   📊 Status:        {state['status']}")
        print(f"   📝 Code lines:    {state['code_metadata'].get('lines', 0)}")
        print(f"   🧪 Test verdict:  {state['test_result'].get('verdict', 'N/A')}")
        print(f"   🔐 Security:      {state['audit_result'].get('verdict', 'N/A')}")
        print("=" * 70)


_swarm_instance = None


def get_swarm():
    global _swarm_instance
    if _swarm_instance is None:
        _swarm_instance = SynapseSwarm()
    return _swarm_instance


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("   🚀 TESTING THE COMPLETE AI SWARM")
    print("=" * 70)
    print("   This will run all 5 agents in sequence")
    print("   Total time: ~30-60 seconds")
    print("=" * 70)

    try:
        swarm = get_swarm()

        result = swarm.run(
            integration_name="Stripe to Slack Notifier",
            api_a_name="Stripe",
            api_a_url="https://stripe.com/docs/api",
            api_b_name="Slack",
            api_b_url="https://api.slack.com/web",
            tech_stack="python",
            verbose=True,
        )

        print("\n" + "=" * 70)
        print("   📋 FINAL RESULTS")
        print("=" * 70)

        print(f"\n📊 STATUS: {result['status']}")
        print(f"⏱️  DURATION: {result['completed_at'] - result['started_at']:.1f} seconds\n")

        print("=" * 70)
        print("📝 GENERATED CODE (first 30 lines):")
        print("=" * 70)
        code_lines = result["code"].split("\n")
        for i, line in enumerate(code_lines[:30], 1):
            print(f"{i:3} | {line}")
        if len(code_lines) > 30:
            print(f"... and {len(code_lines) - 30} more lines\n")

        print("=" * 70)
        print("🧪 TEST RESULTS:")
        print("=" * 70)
        test = result["test_result"]
        print(f"   Verdict: {test.get('verdict', 'N/A')}")
        print(f"   Quality: {test.get('quality_score', 'N/A')}/10")
        print(f"   Summary: {test.get('summary', 'N/A')}")

        print("\n" + "=" * 70)
        print("🔐 SECURITY AUDIT:")
        print("=" * 70)
        audit = result["audit_result"]
        print(f"   Verdict: {audit.get('verdict', 'N/A')}")
        print(f"   Score:   {audit.get('security_score', 'N/A')}/10")
        print(f"   Summary: {audit.get('summary', 'N/A')}")

        print("\n" + "=" * 70)
        print("   🎉 ALL 5 AGENTS WORKED TOGETHER SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Swarm failed: {e}\n")
        import traceback
        traceback.print_exc()