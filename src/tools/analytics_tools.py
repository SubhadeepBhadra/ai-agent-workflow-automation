"""
Workflow Log Analytics, Failure Rate Aggregation, Latency Profiling, and Performance Reporting tools.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from src.core.tool_registry import register_tool


@register_tool("analyze_workflow_performance", description="Aggregates execution logs, computes failure rates & latencies, flags problem workflows (>10% fail or >5s), and generates recommendations", category="Analytics")
def analyze_workflow_performance(
    logs: List[Dict[str, Any]],
    failure_threshold_pct: float = 10.0,
    latency_threshold_sec: float = 5.0
) -> Dict[str, Any]:
    wf_stats = defaultdict(lambda: {
        "total_runs": 0,
        "success_runs": 0,
        "failed_runs": 0,
        "total_time": 0.0,
        "error_counts": defaultdict(int),
        "failed_steps": defaultdict(int)
    })

    for log in logs:
        wf_id = log.get("workflow_id", "UNKNOWN")
        status = str(log.get("status", "SUCCESS")).upper()
        exec_time = float(log.get("execution_time_sec", 0.0))
        err_msg = log.get("error_message")
        failed_step = log.get("step_failed")

        stats = wf_stats[wf_id]
        stats["total_runs"] += 1
        stats["total_time"] += exec_time

        if status == "SUCCESS":
            stats["success_runs"] += 1
        else:
            stats["failed_runs"] += 1
            if err_msg:
                stats["error_counts"][err_msg] += 1
            if failed_step:
                stats["failed_steps"][failed_step] += 1

    # Summaries and Flagged Workflows
    wf_summaries = []
    flagged_problem_workflows = []

    for wf_id, s in wf_stats.items():
        total = s["total_runs"]
        fail_count = s["failed_runs"]
        fail_rate = round((fail_count / total) * 100, 2) if total > 0 else 0.0
        avg_time = round(s["total_time"] / total, 2) if total > 0 else 0.0

        # Decision rule: Flag workflows with failure rate > 10% or avg execution time > 5.0s
        fail_flag = fail_rate > failure_threshold_pct
        slow_flag = avg_time > latency_threshold_sec
        is_flagged = fail_flag or slow_flag

        reasons = []
        if fail_flag:
            reasons.append(f"High failure rate ({fail_rate}% > {failure_threshold_pct}% threshold)")
        if slow_flag:
            reasons.append(f"High latency ({avg_time}s > {latency_threshold_sec}s threshold)")

        top_errors = sorted(s["error_counts"].items(), key=lambda x: x[1], reverse=True)[:3]
        top_failed_steps = sorted(s["failed_steps"].items(), key=lambda x: x[1], reverse=True)[:3]

        item_summary = {
            "workflow_id": wf_id,
            "total_executions": total,
            "success_count": s["success_runs"],
            "failure_count": fail_count,
            "failure_rate_percentage": fail_rate,
            "average_execution_time_sec": avg_time,
            "is_flagged": is_flagged,
            "flag_reasons": reasons,
            "top_errors": [{"error": e, "occurrences": count} for e, count in top_errors],
            "failing_steps": [{"step": st, "occurrences": count} for st, count in top_failed_steps]
        }
        wf_summaries.append(item_summary)

        if is_flagged:
            flagged_problem_workflows.append(item_summary)

    # Sort flagged workflows by highest failure rate first, then highest latency
    flagged_problem_workflows.sort(key=lambda x: (x["failure_rate_percentage"], x["average_execution_time_sec"]), reverse=True)
    wf_summaries.sort(key=lambda x: x["workflow_id"])

    # Strategic recommendations
    recommendations = []
    for flagged in flagged_problem_workflows:
        wid = flagged["workflow_id"]
        if flagged["failure_rate_percentage"] > failure_threshold_pct:
            top_err = flagged["top_errors"][0]["error"] if flagged["top_errors"] else "Unknown errors"
            recommendations.append(
                f"Workflow [{wid}]: Remediate high failure rate ({flagged['failure_rate_percentage']}%). Root cause: '{top_err}'. Add input schema pre-validation and exponential backoff retry logic."
            )
        if flagged["average_execution_time_sec"] > latency_threshold_sec:
            recommendations.append(
                f"Workflow [{wid}]: Optimize latency bottleneck ({flagged['average_execution_time_sec']}s). Introduce prompt caching, parallel tool execution, or asynchronous background job processing."
            )

    return {
        "total_log_entries_analyzed": len(logs),
        "total_workflows_monitored": len(wf_stats),
        "flagged_problem_workflows_count": len(flagged_problem_workflows),
        "thresholds": {
            "max_failure_rate_pct": failure_threshold_pct,
            "max_latency_sec": latency_threshold_sec
        },
        "flagged_problem_workflows": flagged_problem_workflows,
        "all_workflows_metrics": wf_summaries,
        "strategic_recommendations": recommendations
    }
