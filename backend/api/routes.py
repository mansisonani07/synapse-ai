import logging
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from swarm.graph import get_swarm

logger = logging.getLogger(__name__)
router = APIRouter()


# In-memory storage for integration jobs
# (In Phase 3 we'll use a real database)
JOBS_STORAGE = {}


class IntegrationRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    tech_stack: str = Field(default="python")
    api_a_name: str = Field(..., min_length=2, max_length=50)
    api_a_url: str = Field(...)
    api_b_name: str = Field(..., min_length=2, max_length=50)
    api_b_url: str = Field(...)


class AgentStatus(BaseModel):
    name: str
    role: str
    status: str
    message: Optional[str] = None


class IntegrationResponse(BaseModel):
    success: bool
    integration_id: str
    integration_name: str
    status: str
    message: str
    estimated_time_seconds: int
    agents: List[AgentStatus]
    created_at: str


def run_swarm_in_background(integration_id: str, request_data: dict):
    """Run the swarm in the background and update job storage."""
    try:
        logger.info(f"Starting swarm for job: {integration_id}")
        
        JOBS_STORAGE[integration_id]["status"] = "in_progress"
        JOBS_STORAGE[integration_id]["current_agent"] = "Orchestrator"
        
        swarm = get_swarm()
        result = swarm.run(
            integration_name=request_data["name"],
            api_a_name=request_data["api_a_name"],
            api_a_url=request_data["api_a_url"],
            api_b_name=request_data["api_b_name"],
            api_b_url=request_data["api_b_url"],
            tech_stack=request_data.get("tech_stack", "python"),
            verbose=False,
        )
        
        JOBS_STORAGE[integration_id]["status"] = result["status"]
        JOBS_STORAGE[integration_id]["completed_at"] = datetime.utcnow().isoformat() + "Z"
        JOBS_STORAGE[integration_id]["result"] = {
            "code": result["code"],
            "code_metadata": result["code_metadata"],
            "test_result": result["test_result"],
            "audit_result": result["audit_result"],
            "plan": result["plan"],
            "duration_seconds": result["completed_at"] - result["started_at"],
        }
        
        logger.info(f"Swarm completed for job: {integration_id}")
        
    except Exception as e:
        logger.error(f"Swarm failed for job {integration_id}: {e}")
        JOBS_STORAGE[integration_id]["status"] = "failed"
        JOBS_STORAGE[integration_id]["error"] = str(e)


@router.post(
    "/integrate",
    response_model=IntegrationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Integration"],
    summary="🚀 Launch the AI Swarm",
)
async def launch_swarm(request: IntegrationRequest, background_tasks: BackgroundTasks):
    """
    Launch the 5 AI agent swarm to build an integration.
    Real AI agents will run in the background.
    """
    
    integration_id = str(uuid.uuid4())[:12]
    
    JOBS_STORAGE[integration_id] = {
        "id": integration_id,
        "name": request.name,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "request": request.dict(),
        "result": None,
        "error": None,
    }
    
    background_tasks.add_task(
        run_swarm_in_background,
        integration_id,
        request.dict()
    )
    
    response = IntegrationResponse(
        success=True,
        integration_id=integration_id,
        integration_name=request.name,
        status="queued",
        message=f"🚀 Swarm activated! Building '{request.name}' — connecting {request.api_a_name} to {request.api_b_name}.",
        estimated_time_seconds=60,
        agents=[
            AgentStatus(name="Orchestrator", role="The Manager", status="pending", message="Waiting to start..."),
            AgentStatus(name="DocReader", role="The Researcher", status="pending", message="Waiting to start..."),
            AgentStatus(name="CodeWriter", role="The Developer", status="pending", message="Waiting to start..."),
            AgentStatus(name="Tester", role="The QA Engineer", status="pending", message="Waiting to start..."),
            AgentStatus(name="Validator", role="The Security Inspector", status="pending", message="Waiting to start..."),
        ],
        created_at=datetime.utcnow().isoformat() + "Z",
    )
    
    return response


@router.get(
    "/status/{integration_id}",
    tags=["Integration"],
    summary="📊 Check integration status",
)
async def get_integration_status(integration_id: str):
    """Get the current status of an integration build."""
    
    if integration_id not in JOBS_STORAGE:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    job = JOBS_STORAGE[integration_id]
    
    response = {
        "integration_id": integration_id,
        "name": job["name"],
        "status": job["status"],
        "created_at": job["created_at"],
    }
    
    if job["status"] == "completed" and job.get("result"):
        result = job["result"]
        response["result"] = {
            "code": result["code"],
            "lines_of_code": result["code_metadata"].get("lines", 0),
            "env_variables": result["code_metadata"].get("env_variables", ""),
            "installation": result["code_metadata"].get("installation", ""),
            "notes": result["code_metadata"].get("notes", []),
            "duration_seconds": result.get("duration_seconds", 0),
            "test": {
                "verdict": result["test_result"].get("verdict", "N/A"),
                "quality_score": result["test_result"].get("quality_score", 0),
                "summary": result["test_result"].get("summary", ""),
                "production_ready": result["test_result"].get("production_ready", False),
            },
            "security": {
                "verdict": result["audit_result"].get("verdict", "N/A"),
                "security_score": result["audit_result"].get("security_score", 0),
                "summary": result["audit_result"].get("summary", ""),
                "production_safe": result["audit_result"].get("production_safe", False),
            },
        }
    
    if job["status"] == "failed":
        response["error"] = job.get("error", "Unknown error")
    
    return response


@router.get(
    "/integrations",
    tags=["Integration"],
    summary="📜 List all integrations",
)
async def list_integrations():
    """Get list of all integrations (in-memory)."""
    
    real_jobs = []
    for job_id, job in JOBS_STORAGE.items():
        real_jobs.append({
            "id": job_id,
            "title": job["name"],
            "from_api": job["request"]["api_a_name"],
            "to_api": job["request"]["api_b_name"],
            "status": job["status"],
            "created_at": job["created_at"],
        })
    
    if not real_jobs:
        real_jobs = [
            {"id": "int_001", "title": "Slack to Salesforce Notification Bridge", "from_api": "Slack", "to_api": "Salesforce", "status": "completed", "created_at": "2026-04-03T10:00:00Z"},
            {"id": "int_002", "title": "HubSpot to Shopify Order Sync", "from_api": "HubSpot", "to_api": "Shopify", "status": "completed", "created_at": "2026-04-02T15:30:00Z"},
            {"id": "int_003", "title": "Stripe to Mailchimp Pro Upgrade", "from_api": "Stripe", "to_api": "Mailchimp", "status": "completed", "created_at": "2026-04-01T09:15:00Z"},
        ]
    
    return {
        "total": len(real_jobs),
        "integrations": real_jobs,
    }


@router.get(
    "/agents",
    tags=["Agents"],
    summary="🤖 List all AI agents",
)
async def list_agents():
    """Get info about all 5 AI agents."""
    return {
        "total": 5,
        "agents": [
            {"name": "Orchestrator", "emoji": "🧠", "role": "The Manager", "powered_by": "Groq Llama 3.3 70B"},
            {"name": "DocReader", "emoji": "📖", "role": "The Researcher", "powered_by": "Groq Llama 3.3 70B"},
            {"name": "CodeWriter", "emoji": "✍️", "role": "The Developer", "powered_by": "Groq Llama 3.3 70B"},
            {"name": "Tester", "emoji": "🧪", "role": "The QA Engineer", "powered_by": "Groq Llama 3.3 70B"},
            {"name": "Validator", "emoji": "✅", "role": "The Security Inspector", "powered_by": "Groq Llama 3.3 70B"},
        ],
    }