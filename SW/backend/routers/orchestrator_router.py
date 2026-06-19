"""
Orchestrator Router
===================
FastAPI router exposing the WorkflowOrchestrator over HTTP.

Endpoints
---------
POST /orchestrator/workflow/run      — Execute the full workflow pipeline
GET  /orchestrator/workflow/health   — Check availability of all sub-modules

Nothing in this router modifies any existing router, service, or agent.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from orchestrator.workflow_orchestrator import workflow_orchestrator
from services.ai.ai_service import fetch_lesson_by_id

router = APIRouter(prefix="/orchestrator", tags=["Workflow Orchestrator"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class WorkflowRunRequest(BaseModel):
    """Request body for the main workflow endpoint."""

    lesson_id: int = Field(
        ...,
        description="Lesson ID — used to query the topic content and for the video generator.",
        example=1,
    )
    student_id: int = Field(
        ...,
        description="Student ID — used to generate the session ID and for the video generator.",
        example=1,
    )
    enable_video: bool = Field(
        default=False,
        description=(
            "Set to true to trigger video generation. "
            "WARNING: this is a long-running subprocess (~minutes). "
            "Disabled by default."
        ),
    )


class WorkflowRunResponse(BaseModel):
    """Full context object returned after workflow execution."""

    run_id: str
    input: str
    session_id: str
    lesson_id: Optional[int]
    student_id: Optional[int]
    timestamp: str
    explanation: Optional[Dict[str, Any]]
    video: Optional[Dict[str, Any]]
    iot: Optional[Dict[str, Any]]
    report: Dict[str, Any]          # always present
    errors: list
    module_status: Dict[str, str]
    status: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/workflow/run",
    response_model=WorkflowRunResponse,
    summary="Run the full AI workflow pipeline",
    description=(
        "Executes the top-level workflow orchestrator. "
        "Calls the explanation pipeline, optionally generates a video, "
        "reads the IoT sensor snapshot, then generates a final report. "
        "The endpoint ALWAYS returns a report even when sub-systems fail."
    ),
)
async def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    """Execute the full workflow and return the aggregated context."""
    # Resolve input_text dynamically from lesson_id
    lesson_data = fetch_lesson_by_id(request.lesson_id)
    if lesson_data and lesson_data.get("content"):
        resolved_input = lesson_data["content"]
    else:
        # Fallback for local testing if DB is not configured/offline
        if request.lesson_id == 1:
            resolved_input = "النباتات"
        else:
            resolved_input = f"الدرس رقم {request.lesson_id}"

    # Resolve session_id from student_id and lesson_id
    resolved_session = f"student_{request.student_id}_lesson_{request.lesson_id}"

    # The orchestrator never raises — it captures all errors internally.
    context = await workflow_orchestrator.run(
        input_text=resolved_input,
        session_id=resolved_session,
        lesson_id=request.lesson_id,
        student_id=request.student_id,
        enable_video=request.enable_video,
    )

    return WorkflowRunResponse(**context)


@router.get(
    "/workflow/health",
    summary="Workflow orchestrator health check",
    description="Returns the availability status of every integrated module.",
)
async def workflow_health() -> Dict[str, Any]:
    """Check which sub-modules are available."""
    return workflow_orchestrator.health()
