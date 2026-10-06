"""
Command Line Interface (CLI) for the AI Agent Workflow Automation System.
Supports interactive mode, single queries, batch test suite execution, and extensibility demo.
"""

import sys
import os
import argparse
import json

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.tree import Tree

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.engine import WorkflowEngine
from src.core.models import WorkflowDefinition, ExecutionTrace
from src.core.tool_registry import ToolRegistry


console = Console()


def display_trace(trace: ExecutionTrace, show_full_json: bool = False):
    """
    Renders a visually rich execution trace in the terminal.
    """
    header_text = (
        f"[bold cyan]Workflow Selected:[/bold cyan] [bold yellow]{trace.selected_workflow_id}[/bold yellow] - "
        f"[bold white]{trace.selected_workflow_name}[/bold white]\n"
        f"[dim]Confidence:[/dim] {trace.workflow_selection_confidence * 100:.1f}% | "
        f"[dim]Execution Time:[/dim] {trace.execution_time_total_sec:.3f}s | "
        f"[dim]Status:[/dim] [{'green' if trace.status == 'SUCCESS' else 'red'}]{trace.status}[/]"
    )
    console.print(Panel(header_text, title=f"🎯 Request: '{trace.user_request}'", border_style="cyan"))

    # Steps Executed Tree
    tree = Tree("[bold green]🪜 Executed Steps & Tool Calls[/bold green]")
    for step in trace.steps_executed:
        step_branch = tree.add(
            f"[bold white]Step {step.step_index}: {step.name}[/bold white] "
            f"([dim]{step.tool_required} - {step.duration_ms}ms[/dim]) [green]✔[/green]"
        )
        step_branch.add(f"[dim]Description:[/dim] {step.description}")

    console.print(tree)
    console.print()

    # Decision Logic Evaluated
    if trace.decisions_evaluated:
        dec_table = Table(title="⚖️ Decision Rules & Conditions Evaluated", border_style="yellow")
        dec_table.add_column("Rule / Logic", style="white")
        dec_table.add_column("Condition Met", style="bold")
        dec_table.add_column("Action Taken", style="cyan")

        for dec in trace.decisions_evaluated:
            met_str = "[green]YES[/green]" if dec.condition_met else "[blue]NO[/blue]"
            dec_table.add_row(dec.condition_rule, met_str, dec.action_taken)
        console.print(dec_table)
        console.print()

    # Final Output Result
    console.print(Panel(Markdown(trace.formatted_result), title="📊 Final Result / Output", border_style="green"))

    if show_full_json:
        console.print(Panel(json.dumps(trace.dict(), indent=2, default=str), title="Raw Execution Trace JSON", border_style="dim"))


def run_test_suite(engine: WorkflowEngine):
    """
    Runs all 10 test questions from the Excel file and summarizes the scorecard.
    """
    console.print(Panel.fit("[bold magenta]🚀 Executing Full Test Suite Across All 10 Excel Workflows[/bold magenta]"))

    summary_table = Table(title="Evaluation Scorecard (10/10 Workflows)", border_style="magenta")
    summary_table.add_column("#", justify="right", style="cyan")
    summary_table.add_column("Expected ID", style="bold yellow")
    summary_table.add_column("Selected ID", style="bold white")
    summary_table.add_column("Test Request Query", style="white")
    summary_table.add_column("Steps", justify="center")
    summary_table.add_column("Latency", justify="right")
    summary_table.add_column("Result", style="bold")

    passed_count = 0
    total = len(engine.test_questions)

    for idx, tq in enumerate(engine.test_questions, 1):
        req = tq["test_request"]
        expected_id = tq["workflow_id"]

        trace = engine.execute(req)
        is_pass = trace.selected_workflow_id == expected_id and trace.status == "SUCCESS"
        if is_pass:
            passed_count += 1

        res_badge = "[bold green]PASS[/bold green]" if is_pass else "[bold red]FAIL[/bold red]"
        summary_table.add_row(
            str(idx),
            expected_id,
            trace.selected_workflow_id or "NONE",
            req[:45] + ("..." if len(req) > 45 else ""),
            str(len(trace.steps_executed)),
            f"{trace.execution_time_total_sec:.2f}s",
            res_badge
        )

    console.print(summary_table)
    console.print(Panel.fit(f"[bold green]✨ Benchmark Complete: {passed_count}/{total} Passed ({passed_count/total*100:.0f}% Success Rate)[/bold green]"))


def demo_extensibility(engine: WorkflowEngine):
    """
    Demonstrates adding an 11th workflow at runtime with zero core engine code modifications.
    """
    console.print(Panel.fit("[bold yellow]⚡ Extensibility Showcase: Adding 11th Workflow Dynamically[/bold yellow]"))

    # Register Workflow 11
    wf11 = WorkflowDefinition(
        workflow_id="WF011",
        workflow_name="Customer Refund Request Processing",
        trigger="User requests a refund or payment dispute for an order",
        inputs="Customer Order ID; refund reason; purchase date",
        steps_raw="Verify order eligibility -> check return window policy -> calculate refund amount -> submit transaction",
        steps=["Verify order eligibility", "check return window policy", "calculate refund amount", "submit transaction"],
        decision_logic="If purchase was made within 30 days and item is undamaged, approve refund; otherwise escalate",
        tools_required="Payment gateway API; policy checker",
        expected_output="Refund approval status, transaction ID, and customer notification"
    )

    console.print(f"[bold cyan]Registering new workflow:[/bold cyan] {wf11.workflow_id} - {wf11.workflow_name}")
    engine.register_custom_workflow(wf11)

    test_query = "Process customer refund request for order ORD-1001 due to accidental double charge"
    console.print(f"[dim]Submitting user query:[/dim] '{test_query}'\n")

    trace = engine.execute(test_query)
    display_trace(trace)


def interactive_mode(engine: WorkflowEngine):
    """
    Interactive terminal REPL.
    """
    console.print(Panel.fit(
        "[bold cyan]🤖 AI Agent Workflow Automation - Interactive Console[/bold cyan]\n"
        "[dim]Type your business request, or type 'exit' / 'test' / 'list' / 'demo'[/dim]"
    ))

    while True:
        try:
            user_input = console.input("\n[bold green]User Request > [/bold green]").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[yellow]Exiting. Goodbye![/yellow]")
                break
            if user_input.lower() == "test":
                run_test_suite(engine)
                continue
            if user_input.lower() == "demo":
                demo_extensibility(engine)
                continue
            if user_input.lower() == "list":
                table = Table(title="Loaded Workflows from Excel", border_style="cyan")
                table.add_column("ID", style="yellow")
                table.add_column("Name", style="bold white")
                table.add_column("Trigger Description", style="dim")
                for w in engine.workflows.values():
                    table.add_row(w.workflow_id, w.workflow_name, w.trigger)
                console.print(table)
                continue

            trace = engine.execute(user_input)
            display_trace(trace)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting interactive mode.[/yellow]")
            break


def main():
    parser = argparse.ArgumentParser(description="AI Agent Workflow Automation Runner")
    parser.add_argument("--request", "-r", type=str, help="Single request prompt to process")
    parser.add_argument("--test-all", "-t", action="store_true", help="Execute evaluation test suite for all 10 workflows")
    parser.add_argument("--demo-extensibility", "-d", action="store_true", help="Demonstrate adding and running an 11th workflow")
    parser.add_argument("--list-workflows", "-l", action="store_true", help="List all workflows loaded from Excel")
    parser.add_argument("--json", action="store_true", help="Output raw JSON trace")

    args = parser.parse_args()
    engine = WorkflowEngine()

    if args.test_all:
        run_test_suite(engine)
    elif args.demo_extensibility:
        demo_extensibility(engine)
    elif args.list_workflows:
        table = Table(title="Loaded Workflows from Excel", border_style="cyan")
        table.add_column("ID", style="yellow")
        table.add_column("Name", style="bold white")
        table.add_column("Trigger Description", style="dim")
        for w in engine.workflows.values():
            table.add_row(w.workflow_id, w.workflow_name, w.trigger)
        console.print(table)
    elif args.request:
        trace = engine.execute(args.request)
        display_trace(trace, show_full_json=args.json)
    else:
        interactive_mode(engine)


if __name__ == "__main__":
    main()
