"""
SEO Keyword Classification, Search Intent Mapping, and Priority Identification tools.
"""

from typing import List, Dict, Any, Optional
import re
from src.core.tool_registry import register_tool


def _classify_intent(keyword: str) -> str:
    kw = keyword.lower()
    # Transactional: buy, discount, price, shop, store, order, coupon, sale, online
    if any(w in kw for w in ["buy", "order", "discount", "price", "coupon", "sale", "online store", "purchase", "cheap"]):
        return "Transactional"
    # Commercial: best, top, review, vs, comparison, compare, rating, vs
    elif any(w in kw for w in ["best", "top", "review", "comparison", "compare", "vs", "ratings", "features"]):
        return "Commercial"
    # Navigational: brand or official store queries
    elif any(w in kw for w in ["official store", "login", "website", "visionpro", "soundmax", "ergoworks", "acoustiq"]):
        return "Navigational"
    # Informational: how, what, why, guide, checklist, setup, tips
    else:
        return "Informational"


def _map_category_and_page(keyword: str) -> (str, str):
    kw = keyword.lower()
    if "chair" in kw or "back pain" in kw:
        return "Ergonomic Chairs", "/products/ergonomic-office-chair"
    elif "keyboard" in kw:
        return "Keyboards", "/products/mechanical-keyboards"
    elif "standing desk" in kw or "desk" in kw or "workstation" in kw:
        return "Desks & Workstations", "/products/standing-desks"
    elif "monitor" in kw:
        return "Monitors & Displays", "/products/ultrawide-monitors"
    elif "headphone" in kw or "audio" in kw:
        return "Audio", "/products/noise-cancelling-headphones"
    elif "dock" in kw or "usb" in kw:
        return "Accessories", "/products/usb-c-docks"
    else:
        return "General Office", "/collections/workspace"


@register_tool("classify_and_map_keywords", description="Deduplicates keywords, classifies into 4 search intents (Informational, Commercial, Transactional, Navigational), maps to pages and ranks priority", category="SEO & Growth")
def classify_and_map_keywords(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    seen_keywords = set()
    unique_items = []
    duplicates_count = 0

    # Step 1: Remove duplicates
    for item in keywords:
        kw = str(item.get("keyword", "")).strip().lower()
        if not kw:
            continue
        if kw in seen_keywords:
            duplicates_count += 1
            continue
        seen_keywords.add(kw)
        unique_items.append(item)

    # Step 2: Classify intent, map target page, assign priority
    classified_records = []
    intent_distribution = {"Informational": 0, "Commercial": 0, "Transactional": 0, "Navigational": 0}

    for item in unique_items:
        kw_text = item.get("keyword", "")
        vol = int(item.get("search_volume", 1000))
        cpc = float(item.get("cpc", 1.0))

        intent = _classify_intent(kw_text)
        intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
        category, target_page = _map_category_and_page(kw_text)

        # Priority score: High volume + Transactional/Commercial = High priority
        if (intent in ["Transactional", "Commercial"] and vol >= 8000) or vol >= 12000:
            priority = "HIGH"
        elif vol >= 5000 or intent == "Commercial":
            priority = "MEDIUM"
        else:
            priority = "LOW"

        classified_records.append({
            "keyword": kw_text,
            "search_volume": vol,
            "cpc_usd": cpc,
            "search_intent": intent,
            "mapped_category": category,
            "recommended_target_page": target_page,
            "priority": priority
        })

    # Sort high priority and high volume first
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    classified_records.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["search_volume"]))

    return {
        "total_keywords_ingested": len(keywords),
        "unique_keywords_count": len(unique_items),
        "duplicates_removed_count": duplicates_count,
        "intent_distribution": intent_distribution,
        "high_priority_keywords_count": sum(1 for r in classified_records if r["priority"] == "HIGH"),
        "classified_keywords_report": classified_records
    }
