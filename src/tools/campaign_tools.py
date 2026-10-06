"""
Marketing Campaign Brief Composer tools.
Validates campaign objectives and schedule requirements before generating the structured brief.
"""

from typing import Dict, Any, Optional, List
from src.core.tool_registry import register_tool


@register_tool("generate_campaign_brief", description="Validates inputs and creates a structured marketing campaign brief including messaging, channels, timeline, and checklist", category="Marketing")
def generate_campaign_brief(
    campaign_goal: Optional[str] = None,
    dates: Optional[str] = None,
    product_list: Optional[List[str]] = None,
    target_audience: Optional[str] = None,
    promotion: Optional[str] = None
) -> Dict[str, Any]:
    # Decision logic: If campaign goal or dates are missing, request them before generating the brief
    missing_critical_fields = []
    if not campaign_goal or campaign_goal.strip() == "":
        missing_critical_fields.append("campaign_goal")
    if not dates or dates.strip() == "":
        missing_critical_fields.append("dates")

    # If user provided a high-level trigger like "Create a campaign brief for the new collection", provide defaults while noting the decision rule
    if missing_critical_fields:
        # Check if we should prompt or create a provisional brief with explicit alerts
        goal = campaign_goal or "Launch Q4 Ergonomic Workstation Collection and drive 30% revenue growth"
        timeline = dates or "Nov 15, 2026 - Dec 31, 2026 (Holiday Peak Season)"
        provisional_note = f"Warning: Critical fields {missing_critical_fields} were not fully specified in initial request. Using standard default parameters for generation."
    else:
        goal = campaign_goal
        timeline = dates
        provisional_note = "All mandatory parameters (goal, dates) successfully validated."

    products = product_list or ["Ergonomic Office Chair", "UltraWide Monitor 34-inch", "Wireless Vertical Mouse", "Standing Desk Frame"]
    audience = target_audience or "Remote professionals, tech workers, and home-office creators"
    promo_offer = promotion or "20% off bundles with code COMFORT20 + Free Shipping"

    # Messaging Strategy
    key_messages = [
        f"Hero Tagline: 'Work Smarter, Feel Better - Upgrade Your Desk Space'",
        f"Value Proposition: Ergonomically certified products engineered to relieve fatigue and supercharge daily focus.",
        f"Promotional Hook: {promo_offer} on our bestselling workstation essentials."
    ]

    # Channel Recommendations
    channels = [
        {
            "channel": "Email Marketing",
            "tactic": "3-stage lifecycle drip (Announcement, VIP Early Access, Final Countdown)",
            "allocation_percentage": "30%"
        },
        {
            "channel": "Paid Social (Instagram / LinkedIn / Meta)",
            "tactic": "Video before/after workstation transformations and developer testimonials",
            "allocation_percentage": "45%"
        },
        {
            "channel": "Search / Google Performance Max",
            "tactic": "Target high-intent keywords ('ergonomic chair sale', 'standing desk promotion')",
            "allocation_percentage": "25%"
        }
    ]

    # Campaign Checklist
    checklist = [
        {"item": "Finalize product photography & lifestyle 3D renders", "status": "Pending"},
        {"item": "Create dedicated landing page with promo coupon logic", "status": "In Progress"},
        {"item": "Configure Klaviyo email automation workflows", "status": "Pending"},
        {"item": "Review inventory safety stock thresholds prior to launch", "status": "Completed"},
        {"item": "Set up Google Analytics 4 campaign tracking UTM tags", "status": "Pending"}
    ]

    return {
        "campaign_objective": goal,
        "schedule_and_dates": timeline,
        "target_audience": audience,
        "featured_products": products,
        "promotional_offer": promo_offer,
        "validation_status": "VALIDATED" if not missing_critical_fields else "PROVISIONAL_DEFAULT_APPLIED",
        "validation_details": provisional_note,
        "messaging_framework": key_messages,
        "channel_strategy": channels,
        "campaign_execution_checklist": checklist
    }
