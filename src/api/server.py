"""
FastAPI REST API Server for AI Agent Workflow Automation.
Provides endpoints for executing requests, listing workflows, running test suites, and querying tools.
"""

import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.core.engine import WorkflowEngine
from src.core.models import ExecutionTrace, WorkflowDefinition
from src.core.tool_registry import ToolRegistry


app = FastAPI(
    title="AI Agent Workflow Automation API",
    description="Scalable orchestration engine for business workflows parsed dynamically from Excel.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = WorkflowEngine()


class ExecuteRequest(BaseModel):
    user_request: str
    custom_inputs: Optional[Dict[str, Any]] = None


class CustomWorkflowPayload(BaseModel):
    workflow_id: str
    workflow_name: str
    trigger: str
    inputs: str
    steps_raw: str
    decision_logic: str
    tools_required: str
    expected_output: str


@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "AI Agent Workflow Automation Engine",
        "loaded_workflows_count": len(engine.workflows),
        "registered_tools_count": len(ToolRegistry.list_tools())
    }


@app.get("/api/workflows")
def get_workflows():
    """Returns all workflows loaded from Excel."""
    return {
        "count": len(engine.workflows),
        "workflows": [wf.dict() for wf in engine.workflows.values()]
    }


@app.post("/api/execute", response_model=ExecutionTrace)
def execute_workflow(payload: ExecuteRequest):
    """Executes a user request through the agent workflow engine."""
    if not payload.user_request.strip():
        raise HTTPException(status_code=400, detail="Request string cannot be empty.")
    trace = engine.execute(payload.user_request, payload.custom_inputs)
    return trace


@app.get("/api/tools")
def get_tools():
    """Lists all registered tools and their schemas."""
    return {
        "count": len(ToolRegistry.list_tools()),
        "tools": ToolRegistry.list_tools()
    }


@app.post("/api/workflows/register")
def register_workflow(payload: CustomWorkflowPayload):
    """Dynamically registers an 11th workflow at runtime."""
    wf_obj = WorkflowDefinition(
        workflow_id=payload.workflow_id,
        workflow_name=payload.workflow_name,
        trigger=payload.trigger,
        inputs=payload.inputs,
        steps_raw=payload.steps_raw,
        steps=[s.strip() for s in payload.steps_raw.split("→")] if "→" in payload.steps_raw else [payload.steps_raw],
        decision_logic=payload.decision_logic,
        tools_required=payload.tools_required,
        expected_output=payload.expected_output
    )
    engine.register_custom_workflow(wf_obj)
    return {
        "message": f"Successfully registered workflow {payload.workflow_id}",
        "workflow": wf_obj.dict()
    }


@app.get("/api/test-suite")
def run_test_suite_api():
    """Runs all 10 evaluation test questions and returns the report."""
    results = []
    for tq in engine.test_questions:
        trace = engine.execute(tq["test_request"])
        results.append({
            "expected_workflow_id": tq["workflow_id"],
            "selected_workflow_id": trace.selected_workflow_id,
            "test_request": tq["test_request"],
            "passed": trace.selected_workflow_id == tq["workflow_id"] and trace.status == "SUCCESS",
            "execution_time_sec": trace.execution_time_total_sec
        })
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "total": len(results),
        "passed": passed_count,
        "score_percentage": (passed_count / len(results)) * 100,
        "results": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, reload=True)
