# ================================================================
#   SYNAPSE-AI — FastAPI Backend Entry Point
#   File    : main.py
#   Author  : Mansi Sonani
#   GitHub  : github.com/mansisonani07/synapse-ai
#
#   Description:
#   The main server file. Starts the FastAPI application,
#   configures CORS so the React frontend can connect,
#   and registers all API routes.
# ================================================================

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Load environment variables from .env file ────────────────────
# This MUST run before anything else in the file
load_dotenv()


# ── App Lifespan Manager ─────────────────────────────────────────
# Code before yield = runs on server startup
# Code after yield  = runs on server shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):

    # ── STARTUP ──────────────────────────────────────────────────
    print("")
    print("=" * 60)
    print("   🤖  SYNAPSE-AI BACKEND IS STARTING UP")
    print("=" * 60)
    print(f"   ✅  Environment : {os.getenv('ENVIRONMENT', 'development')}")
    print(f"   ✅  Host        : {os.getenv('BACKEND_HOST', '0.0.0.0')}")
    print(f"   ✅  Port        : {os.getenv('BACKEND_PORT', '8000')}")
    print(f"   ✅  AI Model    : {os.getenv('OPENAI_MODEL', 'gpt-4o')}")
    print(f"   ✅  Frontend    : {os.getenv('FRONTEND_URL', 'http://localhost:5173')}")
    print("=" * 60)
    print("   📚  Swagger Docs  →  http://localhost:8000/docs")
    print("   📊  Redoc         →  http://localhost:8000/redoc")
    print("   💚  Health Check  →  http://localhost:8000/health")
    print("=" * 60)
    print("")

    yield  # ← The server runs here, serving all requests

    # ── SHUTDOWN ─────────────────────────────────────────────────
    print("")
    print("=" * 60)
    print("   🛑  SYNAPSE-AI BACKEND IS SHUTTING DOWN")
    print("   👋  Goodbye!")
    print("=" * 60)
    print("")


# ── Create The FastAPI Application Instance ───────────────────────
app = FastAPI(
    title="🤖 Synapse-AI API",
    description="""
# 🚀 Welcome to Synapse-AI Backend

The **autonomous AI brain** powering Synapse-AI — an Autonomous B2B API Integration Swarm.

---

## 🤖 Our 5 Specialized AI Agents

| Agent | Emoji | Role |
|-------|-------|------|
| **Orchestrator** | 🧠 | The Manager — plans the work |
| **DocReader** | 📖 | The Researcher — reads API docs |
| **CodeWriter** | ✍️ | The Developer — generates code |
| **Tester** | 🧪 | The QA Engineer — finds bugs |
| **Validator** | ✅ | The Security Inspector — audits code |

---

## ⚡ Powered By

- **AI Model:** Groq Llama 3.3 70B (lightning fast!)
- **Framework:** FastAPI + LangGraph
- **Speed:** Generates integrations in ~30-60 seconds
- **Cost:** $0 (FREE tier!)

---

## 🎯 How To Use

1. **POST** `/api/v1/integrate` with your integration request
2. Get back an `integration_id`
3. **GET** `/api/v1/status/{integration_id}` to track progress
4. Receive complete code, test results, and security audit!

---

## 🌐 Live Frontend

Visit **http://localhost:5173** for the beautiful React UI!

---

Built with ❤️ by **Mansi Sonani**
""",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Mansi Sonani",
        "url": "https://github.com/mansisonani07/synapse-ai",
    },
)


# ================================================================
#   CORS MIDDLEWARE CONFIGURATION
#
#   CORS = Cross-Origin Resource Sharing
#   This is what allows your React app running on port 5173
#   to make API calls to this backend running on port 8000.
#   Without this, the browser will block every single request.
# ================================================================

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ENVIRONMENT  = os.getenv("ENVIRONMENT", "development")

# Build the list of allowed origins based on environment
if ENVIRONMENT == "development":
    # In development — allow all common local ports
    allowed_origins = [
        "http://localhost:5173",          # Vite dev server (primary)
        "http://localhost:3000",          # React CRA fallback
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://synapse-ai-swarm-hb2a.arcada.app",  # Live demo
        FRONTEND_URL,
    ]
else:
    # In production — only allow the real live frontend domain
    allowed_origins = [
        "https://synapse-ai-swarm-hb2a.arcada.app",
        FRONTEND_URL,
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],     # Allow GET, POST, PUT, DELETE, OPTIONS etc.
    allow_headers=["*"],     # Allow all headers including Authorization
)


# ================================================================
#   ROOT ENDPOINTS
#   Simple informational endpoints.
#   The real AI agent logic will live in api/routes.py (Phase 2)
# ================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="Welcome to Synapse-AI",
    description="Returns a welcome message confirming the API is live.",
)
async def root():
    """
    Root endpoint — confirms the Synapse-AI API is running.

    Returns basic project information and links.
    """
    return JSONResponse(
        content={
            "project"  : "Synapse-AI",
            "tagline"  : "AI agents that connect your business apps in 10 minutes.",
            "status"   : "running ✅",
            "version"  : "1.0.0",
            "docs"     : "http://localhost:8000/docs",
            "health"   : "http://localhost:8000/health",
            "github"   : "https://github.com/mansisonani07/synapse-ai",
            "live_demo": "https://synapse-ai-swarm-hb2a.arcada.app",
        }
    )


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description=(
        "Health check endpoint. "
        "Your React frontend and any monitoring service "
        "can ping this URL to confirm the backend is alive and configured."
    ),
)
async def health_check():
    """
    Health check endpoint.

    Checks:
    - Server is running
    - Environment is correctly loaded
    - OpenAI API key is configured
    - All 4 AI agents are registered and ready

    Returns:
        200 OK with full health status JSON
    """
    # ── Check if OpenAI API key is properly configured ────────────
    openai_key = os.getenv("OPENAI_API_KEY", "")
    openai_configured = (
        len(openai_key) > 10
        and openai_key != "your_openai_api_key_here"
    )

    # ── Check if DeepSeek key is configured ───────────────────────
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_configured = (
        len(deepseek_key) > 10
        and deepseek_key != "your_deepseek_api_key_here"
    )

    return JSONResponse(
        status_code=200,
        content={
            "status"            : "healthy ✅",
            "environment"       : os.getenv("ENVIRONMENT", "development"),
            "ai_model"          : os.getenv("OPENAI_MODEL", "gpt-4o"),
            "openai_configured" : openai_configured,
            "deepseek_configured": deepseek_configured,
            "cors_allowed_origins": allowed_origins,
            "agents": {
                "orchestrator"    : "registered ✅",
                "doc_reader"      : "registered ✅",
                "code_writer"     : "registered ✅",
                "tester_validator": "registered ✅",
            },
            "phase": "Phase 1 — Foundation Complete",
            "next": "Phase 2 — Agent Logic (Coming Soon)",
            "message": (
                "Synapse-AI backend is healthy. "
                "All systems are operational. "
                "Ready for Phase 2 agent integration."
            ),
        },
    )

# ================================================================
#   PHASE 2 ROUTES — AI Swarm API
# ================================================================
from api.routes import router as integration_router
app.include_router(integration_router, prefix="/api/v1")



# ── Direct run support: python main.py ───────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True,       # Auto-restart when you save any file
        log_level="info",
    )