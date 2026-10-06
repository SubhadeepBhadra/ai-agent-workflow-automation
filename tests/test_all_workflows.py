"""
Automated Test Suite for validating all 10 Workflows, intent routing, and decision logic.
"""

import pytest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.engine import WorkflowEngine
from src.core.models import WorkflowDefinition
from src.core.tool_registry import ToolRegistry


@pytest.fixture(scope="module")
def engine():
    return WorkflowEngine()


def test_excel_loading(engine):
    assert len(engine.workflows) == 10, f"Expected 10 workflows, got {len(engine.workflows)}"
    assert len(engine.test_questions) == 10, f"Expected 10 test questions, got {len(engine.test_questions)}"
    for i in range(1, 11):
        wid = f"WF00{i}" if i < 10 else f"WF0{i}"
        assert wid in engine.workflows, f"Missing workflow {wid}"


@pytest.mark.parametrize("index", range(10))
def test_workflow_test_questions(engine, index):
    tq = engine.test_questions[index]
    expected_wid = tq["workflow_id"]
    test_req = tq["test_request"]

    trace = engine.execute(test_req)

    # Validate correct workflow selection
    assert trace.selected_workflow_id == expected_wid, (
        f"For query '{test_req}', expected {expected_wid} but got {trace.selected_workflow_id}"
    )

    # Validate execution success
    assert trace.status == "SUCCESS"
    assert trace.final_output is not None
    assert len(trace.steps_executed) >= 1
    assert len(trace.decisions_evaluated) >= 1
    assert len(trace.formatted_result) > 0


def test_wf001_inventory_restock(engine):
    trace = engine.execute("Which products need restocking?")
    assert trace.selected_workflow_id == "WF001"
    restock_list = trace.final_output.get("restock_list", [])
    assert len(restock_list) > 0
    for item in restock_list:
        assert item["current_stock"] < item["minimum_threshold"]


def test_wf002_price_validation(engine):
    trace = engine.execute("Find products where vendor price differs by more than 10%.")
    assert trace.selected_workflow_id == "WF002"
    exceptions = trace.final_output.get("flagged_exceptions", [])
    assert len(exceptions) > 0


def test_wf003_vendor_file_processing(engine):
    trace = engine.execute("Process this vendor spreadsheet and show invalid rows.")
    assert trace.selected_workflow_id == "WF003"
    assert trace.final_output.get("invalid_rows_count") > 0
    assert trace.final_output.get("valid_rows_count") > 0


def test_wf004_product_description_no_hallucination(engine):
    trace = engine.execute("Generate SEO content for this product.")
    assert trace.selected_workflow_id == "WF004"
    assert "seo_title" in trace.final_output
    assert "meta_description" in trace.final_output
    assert len(trace.final_output.get("missing_attributes_explicitly_marked", [])) > 0


def test_wf005_order_status_lookup(engine):
    trace = engine.execute("Where is order ORD-1001?")
    assert trace.selected_workflow_id == "WF005"
    assert trace.final_output.get("found") is True
    assert trace.final_output.get("order_id") == "ORD-1001"

    # Test not found case
    trace_not_found = engine.execute("Where is order ORD-9999?")
    assert trace_not_found.final_output.get("found") is False


def test_wf006_duplicate_detection(engine):
    trace = engine.execute("Find likely duplicate products in the catalog.")
    assert trace.selected_workflow_id == "WF006"
    assert trace.final_output.get("exact_sku_duplicates_count") >= 1
    assert trace.final_output.get("fuzzy_similarity_duplicates_count") >= 1


def test_wf007_campaign_brief(engine):
    trace = engine.execute("Create a campaign brief for the new collection.")
    assert trace.selected_workflow_id == "WF007"
    assert "messaging_framework" in trace.final_output
    assert "channel_strategy" in trace.final_output


def test_wf008_seo_keywords_classification(engine):
    trace = engine.execute("Classify these keywords and map them to pages.")
    assert trace.selected_workflow_id == "WF008"
    assert trace.final_output.get("duplicates_removed_count") >= 1
    intents = trace.final_output.get("intent_distribution", {})
    assert "Transactional" in intents
    assert "Commercial" in intents


def test_wf009_employee_assignment(engine):
    trace = engine.execute("Assign this urgent task to the best available developer.")
    assert trace.selected_workflow_id == "WF009"
    assert trace.final_output.get("selected_employee") is not None
    assert trace.final_output.get("escalation_status") == "ASSIGNED_SUCCESSFULLY"


def test_wf010_workflow_performance_report(engine):
    trace = engine.execute("Which workflows are failing most often?")
    assert trace.selected_workflow_id == "WF010"
    assert len(trace.final_output.get("flagged_problem_workflows", [])) > 0


def test_extensibility_11th_workflow(engine):
    """
    Validates that adding an 11th workflow dynamically requires zero core changes.
    """
    wf11 = WorkflowDefinition(
        workflow_id="WF011",
        workflow_name="Customer Refund Request Processing",
        trigger="User requests a refund or payment dispute",
        inputs="Customer Order ID; refund reason; purchase date",
        steps_raw="Verify order eligibility -> check return window policy -> calculate refund amount -> submit transaction",
        steps=["Verify order eligibility", "check return window policy", "calculate refund amount", "submit transaction"],
        decision_logic="If purchase was made within 30 days and item is undamaged, approve refund; otherwise escalate",
        tools_required="Payment gateway API; policy checker",
        expected_output="Refund approval status, transaction ID, and customer notification"
    )

    engine.register_custom_workflow(wf11)
    assert "WF011" in engine.workflows

    trace = engine.execute("User requests a refund for order ORD-1001 within 30 days")
    assert trace.selected_workflow_id == "WF011"
    assert trace.status == "SUCCESS"
