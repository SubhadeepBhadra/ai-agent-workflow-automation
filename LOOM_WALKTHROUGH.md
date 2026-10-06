# 🎥 Loom Video Presentation Script & Walkthrough Guide

Use this structured script to record your **Loom Video Submission**. It is optimized to cover every required evaluation rubric in under 5–7 minutes with clear, high-impact talking points and live demonstrations.

---

## ⏱️ Video Breakdown & Agenda

| Time | Section | Screen to Show | Key Talking Points |
|---|---|---|---|
| **0:00 - 1:00** | **Introduction & Architecture Overview** | Architecture Diagram / README | System design, decoupled components, zero hardcoding |
| **1:00 - 2:00** | **Excel Workflow Ingestion & Registry** | `AI_Agent_Workflow_Assessment.xlsx` + `src/core/excel_parser.py` | How workflows are dynamically parsed from Excel |
| **2:00 - 3:15** | **Intent Routing & Step Execution** | Terminal CLI / Streamlit UI | Dynamic semantic routing, tool execution trace |
| **3:15 - 4:15** | **Condition & Error Handling Demo** | Streamlit UI | Showing decision evaluations (e.g. WF004 missing data, WF002 price variance, WF005 order lookup) |
| **4:15 - 5:15** | **Extensibility (11th Workflow Demo)** | `examples/add_11th_workflow_demo.py` or 11th Workflow Builder UI | Adding WF011 in seconds with zero core code edits |
| **5:15 - 6:00** | **Automated Test Suite & Wrap-up** | Running `pytest` (22/22 PASS) & CLI Scorecard | Reusability, reliability, and conclusion |

---

## 🎙️ Section-by-Section Talking Points

### 1. Introduction & Architecture (0:00 - 1:00)
> *"Hello! In this video, I'm presenting the **AI Agent Workflow Automation System** built for the Technical Assessment.*
>
> *The core objective was to take 10 distinct business workflows defined in an Excel spreadsheet and build an intelligent, scalable, and reusable agent architecture. Crucially, **we did not build 10 hardcoded chatbots**—instead, we built a dynamic orchestration engine where workflows are parsed directly from configuration, tools are modularly registered in a Tool Registry, and an intelligent Intent Router dynamically matches user requests to the appropriate workflow."*

### 2. How the Excel Workflows are Processed (1:00 - 2:00)
> *(Show `AI_Agent_Workflow_Assessment.xlsx` and `src/core/excel_parser.py`)*
>
> *"Let's look at how the Excel file is ingested:*
> 1. *Our `ExcelWorkflowParser` dynamically scans the `Workflows` sheet.*
> 2. *It extracts the Workflow ID, Trigger, Input requirements, Step sequence, Decision Logic, and Expected Outputs into Pydantic models (`WorkflowDefinition`).*
> 3. *It also loads the evaluation test suite from the `Test_Questions` sheet.*
> 4. *This means updating or adding a workflow doesn't require modifying the core agent engine—it can be done directly in the Excel file!"*

### 3. Workflow Identification & Tool Execution (2:00 - 3:15)
> *(Open Streamlit Web UI or run `python src/main.py` in terminal)*
>
> *"When a user inputs a natural language prompt, here's what happens:*
> 1. *The **Intent Router** analyzes semantic intent, keywords, and entity parameters (e.g., identifying order IDs like `ORD-1001` or thresholds like `10%`).*
> 2. *The system selects the correct workflow with a confidence score and rationale.*
> 3. *The **Workflow Engine** steps through the workflow sequentially, dynamically invoking atomic functions registered in our `ToolRegistry` via Python decorators (`@register_tool`).*
> 4. *Every step is timed and logged into a structured `ExecutionTrace`."*

### 4. Decision Logic & Error Handling (3:15 - 4:15)
> *(Demonstrate key workflows in Streamlit)*
>
> *"Let's look at how condition logic is enforced:*
> - **Workflow 1 (Inventory Restock):** *Evaluates `current_stock < minimum_stock` and automatically computes reorder quantities.*
> - **Workflow 2 (Price Validation):** *Flags discrepancies whenever variance exceeds 10%.*
> - **Workflow 4 (Product SEO Generator):** *Strict zero-hallucination constraint—any unprovided attributes are explicitly flagged with `[Not Specified]` badges rather than invented.*
> - **Workflow 5 (Order Status):** *If an order ID is not found (e.g. `ORD-9999`), the decision branch handles it gracefully by prompting for alternate identifiers.*
> - **Workflow 10 (Performance Report):** *Automatically flags workflows with failure rates > 10% or latency > 5 seconds, providing strategic recommendations."*

### 5. Extensibility Showcase: Adding an 11th Workflow (4:15 - 5:15)
> *(Run `python examples/add_11th_workflow_demo.py` or use the 11th Workflow Builder tab in Streamlit)*
>
> *"One of the most important requirements is scalability. What happens when an organization needs an 11th workflow—for example, **Customer Refund Processing**?*
>
> *Watch this: we simply register `WF011` with its trigger, steps, and decision rules. With **zero modifications** to the core orchestration engine, we submit a query: 'Process customer refund request for order ORD-1001 due to accidental double charge'. The engine immediately routes it to WF011, executes the steps, evaluates return window policies, and outputs the result!"*

### 6. Automated Test Suite & Summary (5:15 - 6:00)
> *(Run `python -m pytest tests/test_all_workflows.py -v` and `python src/main.py --test-all`)*
>
> *"To ensure enterprise-grade reliability, we have 22 automated test cases verifying:*
> - *100% accuracy on all 10 Excel test questions.*
> - *Every tool and decision rule.*
> - *Extensibility of dynamic workflows.*
>
> *The entire solution is documented with setup instructions, CLI, Streamlit UI, and FastAPI REST endpoints. Thank you for your time!"*
