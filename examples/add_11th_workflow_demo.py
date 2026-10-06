"""
Extensibility Tutorial: Demonstrating how to add an 11th business workflow with ZERO core engine code changes.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.engine import WorkflowEngine
from src.core.models import WorkflowDefinition
from src.core.tool_registry import register_tool


def main():
    print("=" * 70)
    print("EXTENSIBILITY SHOWCASE: ADDING WORKFLOW #11 (Customer Refund Processing)")
    print("=" * 70)

    # Step 1: Initialize Engine (loads existing 10 workflows from Excel)
    engine = WorkflowEngine()
    print(f"[1] Base Engine initialized with {len(engine.workflows)} existing workflows.")

    # Step 2: (Optional) Register custom domain tools if new capabilities are needed
    @register_tool("verify_return_policy", description="Checks if refund request is within 30-day window", category="Finance")
    def verify_return_policy(days_since_purchase: int = 14) -> dict:
        is_eligible = days_since_purchase <= 30
        return {
            "eligible": is_eligible,
            "days_since_purchase": days_since_purchase,
            "return_window_days": 30,
            "policy_decision": "APPROVED_FOR_REFUND" if is_eligible else "REJECTED_EXCEEDED_WINDOW"
        }

    print("[2] Registered new domain tool '@verify_return_policy'.")

    # Step 3: Define Workflow 11 (Matching the Excel schema)
    wf11 = WorkflowDefinition(
        workflow_id="WF011",
        workflow_name="Customer Refund Request Processing",
        trigger="User requests a refund, return, or payment dispute for an order",
        inputs="Customer Order ID; refund reason; purchase date; return status",
        steps_raw="Verify order eligibility → check return window policy → calculate refund amount → submit transaction",
        steps=["Verify order eligibility", "check return window policy", "calculate refund amount", "submit transaction"],
        decision_logic="If purchase was made within 30 days and item is undamaged, approve refund; otherwise escalate",
        tools_required="verify_return_policy; payment_gateway",
        expected_output="Refund approval status, transaction ID, and customer notification"
    )

    # Step 4: Register Workflow 11 into Engine
    engine.register_custom_workflow(wf11)
    print(f"[3] Dynamically registered {wf11.workflow_id}: '{wf11.workflow_name}'. Total workflows: {len(engine.workflows)}")

    # Step 5: Execute a natural language request targeted at Workflow 11
    user_request = "The customer is asking for a refund on order ORD-1001 because the package arrived damaged within 14 days"
    print(f"\n[4] Submitting Natural Language User Request:\n    \"{user_request}\"\n")

    trace = engine.execute(user_request)

    # Step 6: Verify Execution Results
    print("=" * 70)
    print("EXECUTION TRACE RESULT:")
    print(f"- Selected Workflow ID:   {trace.selected_workflow_id}")
    print(f"- Selected Workflow Name: {trace.selected_workflow_name}")
    print(f"- Intent Confidence:      {trace.workflow_selection_confidence * 100:.1f}%")
    print(f"- Routing Reason:         {trace.workflow_selection_reasoning}")
    print(f"- Steps Executed Count:   {len(trace.steps_executed)}")
    print(f"- Execution Time:         {trace.execution_time_total_sec:.3f}s")
    print(f"- Status:                 {trace.status}")
    print("-" * 70)
    print("Formatted Result Output:\n")
    print(trace.formatted_result)
    print("=" * 70)


if __name__ == "__main__":
    main()
