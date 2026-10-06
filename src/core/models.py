"""
Core Pydantic models and data structures for the AI Agent Workflow Engine.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WorkflowStep(BaseModel):
    step_index: int
    name: str
    description: str
    tool_required: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, SKIPPED, FAILED
    inputs: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Any] = None
    duration_ms: float = 0.0
    error_message: Optional[str] = None


class WorkflowDefinition(BaseModel):
    workflow_id: str
    workflow_name: str
    trigger: str
    inputs: str
    steps_raw: str
    steps: List[str] = Field(default_factory=list)
    decision_logic: str
    tools_required: str
    expected_output: str
    category: Optional[str] = "General Business"


class DecisionEvaluation(BaseModel):
    condition_rule: str
    condition_met: bool
    action_taken: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ToolCallLog(BaseModel):
    tool_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Any] = None
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class ExecutionTrace(BaseModel):
    request_id: str
    user_request: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    selected_workflow_id: Optional[str] = None
    selected_workflow_name: Optional[str] = None
    workflow_selection_confidence: float = 0.0
    workflow_selection_reasoning: str = ""
    steps_executed: List[WorkflowStep] = Field(default_factory=list)
    decisions_evaluated: List[DecisionEvaluation] = Field(default_factory=list)
    tool_calls: List[ToolCallLog] = Field(default_factory=list)
    final_output: Any = None
    formatted_result: str = ""
    status: str = "SUCCESS"  # SUCCESS, FAILED, NEED_INPUT
    error: Optional[str] = None
    execution_time_total_sec: float = 0.0


class IntentMatchResult(BaseModel):
    workflow_id: str
    workflow_name: str
    confidence: float
    reasoning: str
    extracted_parameters: Dict[str, Any] = Field(default_factory=dict)
