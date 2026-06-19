"""
WorkflowOrchestrator
====================
A deterministic, scalable workflow coordinator that sits ABOVE all existing
components. It is NOT an AI reasoning agent — it is a pure execution manager
and result aggregator.

Design guarantees
-----------------
* NEVER raises an exception — all subsystem errors are captured in context["errors"].
* ALWAYS produces a final report (via ReportAgent or fallback).
* NEVER modifies any existing service, router, or agent.
* Adding a new module requires only one try/except block — no architectural changes.

Execution order (mandatory)
---------------------------
1. Build shared context
2. Call existing SmartOrchestrator  → context["explanation"]
3. Call VideoGenerationService      → context["video"]
4. Read IoT state snapshot          → context["iot"]
5. Call ReportAgent / fallback      → context["report"]
6. Mark context["status"] = "completed"
7. Return full context

Integration points (read-only, nothing modified)
-------------------------------------------------
* services.ai.ai_service       — SmartOrchestrator (explanation/STT/TTS)
* services.ai.educational_video_service — VideoGenerationService
* routers.iot_router           — shared `state` dict (sensor snapshot)
* services.ai.report           — fetch_logs_from_db, analyze_session_data,
                                  generate_report_logic  (Gemini report)
"""

import datetime
import uuid
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# 1. Lazy imports with graceful degradation
#    Each module is wrapped in try/except so the orchestrator starts even if
#    a subsystem is missing or misconfigured.
# ---------------------------------------------------------------------------

# --- Explanation (SmartOrchestrator) ---
try:
    from services.ai.ai_service import orchestrator as _smart_orchestrator
    EXPLANATION_AVAILABLE = True
except Exception as _e:
    _smart_orchestrator = None
    EXPLANATION_AVAILABLE = False
    print(f"⚠️  [WorkflowOrchestrator] SmartOrchestrator unavailable: {_e}")

# --- Video Generation ---
try:
    from services.ai.educational_video_service import get_video_service as _get_video_service
    VIDEO_AVAILABLE = True
except Exception as _e:
    _get_video_service = None  # type: ignore[assignment]
    VIDEO_AVAILABLE = False
    print(f"⚠️  [WorkflowOrchestrator] VideoGenerationService unavailable: {_e}")

# --- IoT State (read-only snapshot from the running iot_router module) ---
try:
    from routers.iot_router import state as _iot_state
    IOT_AVAILABLE = True
except Exception as _e:
    _iot_state = {}
    IOT_AVAILABLE = False
    print(f"⚠️  [WorkflowOrchestrator] IoT state unavailable: {_e}")

# --- Report Agent ---
try:
    from services.ai.report import (
        fetch_logs_from_db,
        analyze_session_data,
        generate_report_logic,
        gemini_client as _report_gemini_client,
    )
    REPORT_AGENT_AVAILABLE = True
except Exception as _e:
    REPORT_AGENT_AVAILABLE = False
    print(f"⚠️  [WorkflowOrchestrator] ReportAgent unavailable: {_e}")


# ---------------------------------------------------------------------------
# 2. WorkflowOrchestrator
# ---------------------------------------------------------------------------

class WorkflowOrchestrator:
    """
    Top-level deterministic workflow coordinator.

    Usage
    -----
    orchestrator = WorkflowOrchestrator()
    result = await orchestrator.run(
        input_text="النباتات",
        session_id="student_1_lesson_5",
        lesson_id=5,
        student_id=1,
    )
    # result["report"] is always present.
    """

    # -------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------

    async def run(
        self,
        input_text: str,
        session_id: Optional[str] = None,
        lesson_id: Optional[int] = None,
        student_id: Optional[int] = None,
        enable_video: bool = False,   # off by default — expensive async op
    ) -> Dict[str, Any]:
        """
        Execute the full workflow and return the aggregated context.

        Parameters
        ----------
        input_text   : Arabic topic text sent by the user.
        session_id   : Stable identifier for the student session.
        lesson_id    : Lesson identifier (used for video generation).
        student_id   : Student identifier (used for video generation).
        enable_video : Whether to trigger video generation (slow, ~minutes).

        Returns
        -------
        context dict — always contains "report", even on partial failure.
        """
        run_id = str(uuid.uuid4())
        session_id = session_id or f"workflow_{run_id[:8]}"

        # ------------------------------------------------------------------
        # Step 0 — Initialise shared context
        # ------------------------------------------------------------------
        context: Dict[str, Any] = {
            "run_id": run_id,
            "input": input_text,
            "session_id": session_id,
            "lesson_id": lesson_id,
            "student_id": student_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "explanation": None,
            "video": None,
            "iot": None,
            "report": None,
            "errors": [],
            "module_status": {},
            "status": "running",
        }

        print(f"\n{'='*60}")
        print(f"🚀 [WorkflowOrchestrator] Starting run {run_id[:8]}")
        print(f"   input   : {input_text!r}")
        print(f"   session : {session_id}")
        print(f"{'='*60}\n")

        # ------------------------------------------------------------------
        # Step 1 — Explanation (existing SmartOrchestrator)
        # ------------------------------------------------------------------
        context = await self._step_explanation(context)

        # ------------------------------------------------------------------
        # Step 2 — Video Generation (independent, optional)
        # ------------------------------------------------------------------
        if enable_video:
            context = await self._step_video(context)
        else:
            context["module_status"]["video"] = "skipped (enable_video=False)"
            print("⏭️  [Step 2] Video generation skipped (enable_video=False)")

        # ------------------------------------------------------------------
        # Step 3 — IoT Snapshot (independent, non-blocking)
        # ------------------------------------------------------------------
        context = self._step_iot(context)

        # ------------------------------------------------------------------
        # Step 4 — Report (always produced)
        # ------------------------------------------------------------------
        context = self._step_report(context)

        # ------------------------------------------------------------------
        # Step 5 — Finalise
        # ------------------------------------------------------------------
        context["status"] = "completed"
        print(f"\n✅ [WorkflowOrchestrator] Run {run_id[:8]} completed")
        print(f"   errors  : {context['errors']}")
        print(f"   status  : {context['status']}\n")

        return context

    # -------------------------------------------------------------------
    # Module health
    # -------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """Return the availability status of every integrated module."""
        return {
            "orchestrator": "healthy",
            "modules": {
                "explanation": EXPLANATION_AVAILABLE,
                "video": VIDEO_AVAILABLE,
                "iot": IOT_AVAILABLE,
                "report_agent": REPORT_AGENT_AVAILABLE,
            },
        }

    # -------------------------------------------------------------------
    # Private step implementations
    # -------------------------------------------------------------------

    async def _step_explanation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1 — Call SmartOrchestrator for explanation/STT/TTS routing."""
        print("📖 [Step 1] Explanation pipeline...")
        if not EXPLANATION_AVAILABLE or _smart_orchestrator is None:
            msg = "SmartOrchestrator not available"
            context["errors"].append(f"explanation_failed: {msg}")
            context["module_status"]["explanation"] = "unavailable"
            print(f"   ⚠️  {msg}")
            return context

        try:
            # Use existing handle_user_input — routes to cutter or explanation
            # depending on word count. We do NOT reimplement this logic.
            result = _smart_orchestrator.handle_user_input(
                context["input"],
                context["session_id"],
            )
            context["explanation"] = result
            context["module_status"]["explanation"] = (
                "success" if result.get("success") else "partial"
            )
            print(f"   ✅ explanation agent returned: success={result.get('success')}")
        except Exception as e:
            context["errors"].append(f"explanation_failed: {str(e)}")
            context["module_status"]["explanation"] = "error"
            print(f"   ❌ explanation error: {e}")

        return context

    async def _step_video(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2 — Call VideoGenerationService (async subprocess pipeline)."""
        print("🎬 [Step 2] Video generation...")
        if not VIDEO_AVAILABLE or _get_video_service is None:
            msg = "VideoGenerationService not available"
            context["errors"].append(f"video_failed: {msg}")
            context["module_status"]["video"] = "unavailable"
            print(f"   ⚠️  {msg}")
            return context

        try:
            # Derive topic from explanation if available, else fall back to raw input
            explanation_result = context.get("explanation") or {}
            topic = (
                explanation_result.get("message")
                or explanation_result.get("response")
                or context["input"]
            )

            video_service = _get_video_service()
            result = await video_service.generate_video_sync(
                topic=topic,
                duration=None,                    # use service default
                lesson_id=context.get("lesson_id"),
                student_id=context.get("student_id"),
            )
            context["video"] = result
            context["module_status"]["video"] = (
                "success" if result.get("success") else "pipeline_error"
            )
            print(f"   ✅ video result: success={result.get('success')}")
        except Exception as e:
            context["errors"].append(f"video_failed: {str(e)}")
            context["module_status"]["video"] = "error"
            print(f"   ❌ video error: {e}")

        return context

    def _step_iot(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3 — Read latest IoT sensor snapshot (non-destructive read)."""
        print("📡 [Step 3] IoT state snapshot...")
        if not IOT_AVAILABLE:
            msg = "IoT state module not available"
            context["errors"].append(f"iot_failed: {msg}")
            context["module_status"]["iot"] = "unavailable"
            print(f"   ⚠️  {msg}")
            return context

        try:
            # Read the in-memory snapshot; never trigger MQTT or modify state
            snapshot = _iot_state.get("latest_sensor_reading")
            context["iot"] = snapshot
            context["module_status"]["iot"] = (
                "success" if snapshot is not None else "no_data_yet"
            )
            print(f"   ✅ iot snapshot: {snapshot}")
        except Exception as e:
            context["errors"].append(f"iot_failed: {str(e)}")
            context["module_status"]["iot"] = "error"
            print(f"   ❌ iot error: {e}")

        return context

    def _step_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 4 — Generate report.

        Case A: ReportAgent available → fetch DB logs, analyse, call Gemini.
        Case B: ReportAgent missing   → produce structured fallback report.

        A report is ALWAYS produced.
        """
        print("📄 [Step 4] Report generation...")

        if REPORT_AGENT_AVAILABLE:
            try:
                logs = fetch_logs_from_db()
                stats = analyze_session_data(logs)
                report_text = generate_report_logic(stats, _report_gemini_client)
                context["report"] = {
                    "source": "report_agent",
                    "report_content": report_text,
                    "stats": {
                        "total_topics": stats.get("total_topics", 0),
                        "mcq_total": stats.get("mcq_total", 0),
                        "mcq_correct": stats.get("mcq_correct", 0),
                    },
                }
                context["module_status"]["report"] = "success"
                print("   ✅ Report generated by ReportAgent")
            except Exception as e:
                context["errors"].append(f"report_agent_failed: {str(e)}")
                context["module_status"]["report"] = "agent_error_fallback"
                print(f"   ⚠️  ReportAgent error ({e}), using fallback report")
                context["report"] = self._build_fallback_report(context)
        else:
            context["module_status"]["report"] = "fallback"
            print("   ℹ️  ReportAgent unavailable — using fallback report")
            context["report"] = self._build_fallback_report(context)

        return context

    # -------------------------------------------------------------------
    # Fallback report builder
    # -------------------------------------------------------------------

    @staticmethod
    def _build_fallback_report(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct a structured report from the context alone — used when the
        ReportAgent is unavailable or raises an exception.
        """
        explanation_result = context.get("explanation") or {}
        explanation_text = (
            explanation_result.get("message")
            or explanation_result.get("response")
            or "لم يتم الحصول على شرح"
        )

        video_result = context.get("video") or {}
        iot_result = context.get("iot")

        return {
            "source": "fallback",
            "status": "completed_with_fallback_report",
            "input": context.get("input"),
            "explanation_summary": explanation_text,
            "video": {
                "generated": video_result.get("success", False),
                "url": video_result.get("video_url"),
                "session_id": video_result.get("session_id"),
                "error": video_result.get("error"),
            },
            "iot": {
                "available": iot_result is not None,
                "latest_reading": iot_result,
            },
            "errors_captured": context.get("errors", []),
            "generated_at": datetime.datetime.utcnow().isoformat(),
        }


# ---------------------------------------------------------------------------
# 3. Module-level singleton
# ---------------------------------------------------------------------------

workflow_orchestrator = WorkflowOrchestrator()
