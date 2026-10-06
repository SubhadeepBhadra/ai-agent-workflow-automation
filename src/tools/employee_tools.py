"""
Employee Skill Matching, Workload Analysis, and Task Assignment ranking tools.
"""

import os
import json
from typing import Dict, Any, Optional, List
from src.core.tool_registry import register_tool

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_sources"))


@register_tool("assign_employee_task", description="Matches required technical skills, checks available capacity, ranks candidates, and selects the best employee or triggers escalation", category="Resource Management")
def assign_employee_task(
    task_description: Optional[str] = "Fix critical production API latency bottleneck and optimize database query indexes",
    required_skills: Optional[List[str]] = None,
    priority: Optional[str] = "High",
    deadline: Optional[str] = "Immediate (within 24 hours)",
    data_path: Optional[str] = None
) -> Dict[str, Any]:
    path = data_path or os.path.join(DEFAULT_DATA_DIR, "employees.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Employees data not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        employees = json.load(f)

    # Infer required skills if not explicitly provided
    if not required_skills:
        desc_lower = task_description.lower()
        inferred = []
        if "python" in desc_lower or "backend" in desc_lower or "api" in desc_lower:
            inferred.extend(["Python", "FastAPI", "PostgreSQL"])
        if "react" in desc_lower or "frontend" in desc_lower or "ui" in desc_lower:
            inferred.extend(["React", "TypeScript"])
        if "devops" in desc_lower or "cloud" in desc_lower or "docker" in desc_lower or "aws" in desc_lower:
            inferred.extend(["AWS", "Docker", "Kubernetes"])
        if "ai" in desc_lower or "model" in desc_lower or "llm" in desc_lower:
            inferred.extend(["Python", "LLMs", "LangChain"])
        target_skills = list(set(inferred)) if inferred else ["Python", "System Architecture"]
    else:
        target_skills = required_skills

    # Candidate evaluation & scoring
    scored_candidates = []
    for emp in employees:
        emp_skills = [s.lower() for s in emp.get("skills", [])]
        matched = [s for s in target_skills if s.lower() in emp_skills]
        skill_score = (len(matched) / len(target_skills)) * 50 if target_skills else 25

        # Capacity score: 100 - capacity_percentage (more available = higher score)
        cap_pct = emp.get("capacity_percentage", 100)
        available = emp.get("is_available", False)
        capacity_score = max(0, (100 - cap_pct)) * 0.35

        # Rating score
        perf_score = emp.get("performance_rating", 4.0) * 3

        # Availability penalty
        avail_multiplier = 1.0 if available and cap_pct < 85 else 0.3

        total_score = round((skill_score + capacity_score + perf_score) * avail_multiplier, 2)

        scored_candidates.append({
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "role": emp["role"],
            "skills": emp["skills"],
            "matched_skills": matched,
            "capacity_percentage": cap_pct,
            "is_available": available,
            "performance_rating": emp["performance_rating"],
            "composite_score": total_score
        })

    # Sort candidates by composite score descending
    scored_candidates.sort(key=lambda x: x["composite_score"], reverse=True)

    # Decision logic: Prefer employees with required skills and available capacity; escalate if no suitable employee exists
    top_candidate = scored_candidates[0] if scored_candidates else None
    escalation_required = False
    escalation_reason = ""

    if not top_candidate or top_candidate["composite_score"] < 20 or not top_candidate["matched_skills"]:
        escalation_required = True
        escalation_reason = "No qualified developer with matching skills and available bandwidth found."

    return {
        "task_summary": task_description,
        "priority_level": priority or "High",
        "target_deadline": deadline or "Within 24-48 hours",
        "skills_evaluated": target_skills,
        "total_candidates_evaluated": len(employees),
        "escalation_status": "ESCALATE_TO_ENGINEERING_LEAD" if escalation_required else "ASSIGNED_SUCCESSFULLY",
        "escalation_reason": escalation_reason,
        "selected_employee": {
            "employee_id": top_candidate["employee_id"],
            "name": top_candidate["name"],
            "role": top_candidate["role"],
            "current_workload": f"{top_candidate['capacity_percentage']}% Capacity",
            "matched_skills": top_candidate["matched_skills"],
            "composite_score": top_candidate["composite_score"]
        } if top_candidate and not escalation_required else None,
        "assignment_reasoning": (
            f"{top_candidate['name']} was selected as the optimal assignee with a top composite score of {top_candidate['composite_score']}. "
            f"They possess key matching skills ({', '.join(top_candidate['matched_skills'])}) and have available capacity ({top_candidate['capacity_percentage']}% current workload)."
        ) if top_candidate and not escalation_required else escalation_reason,
        "ranked_candidate_pool": scored_candidates
    }
