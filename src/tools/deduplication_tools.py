"""
Duplicate Product Detection tools with exact SKU match and fuzzy text similarity clustering.
"""

from typing import List, Dict, Any, Optional
import difflib
import re
from src.core.tool_registry import register_tool


def _clean_text(s: str) -> str:
    if not s:
        return ""
    # remove punctuation and normalize spacing
    return re.sub(r"[^\w\s]", "", s.lower()).strip()


@register_tool("detect_duplicate_products", description="Identifies duplicate products via exact SKU collision (100% confidence) and fuzzy attribute/title similarity", category="Data Quality")
def detect_duplicate_products(catalog: List[Dict[str, Any]], similarity_threshold: float = 0.75) -> Dict[str, Any]:
    exact_sku_groups = {}
    items_by_sku = {}

    # Step 1: Detect exact SKU matches
    for item in catalog:
        sku = str(item.get("sku", "")).strip().upper()
        if not sku:
            continue
        if sku not in items_by_sku:
            items_by_sku[sku] = []
        items_by_sku[sku].append(item)

    exact_duplicates = []
    for sku, items in items_by_sku.items():
        if len(items) > 1:
            exact_duplicates.append({
                "duplicate_type": "EXACT_SKU_COLLISION",
                "matching_field": "sku",
                "matched_value": sku,
                "confidence_score": 1.0,
                "confidence_label": "Definite Duplicate (100%)",
                "products_count": len(items),
                "items": items
            })

    # Step 2: Compare fuzzy product name & category similarity across items with different SKUs
    fuzzy_duplicates = []
    seen_pairs = set()

    for i in range(len(catalog)):
        for j in range(i + 1, len(catalog)):
            item_a = catalog[i]
            item_b = catalog[j]

            # If same SKU, already handled in exact
            if item_a.get("sku") == item_b.get("sku"):
                continue

            name_a = _clean_text(item_a.get("name", ""))
            name_b = _clean_text(item_b.get("name", ""))
            cat_a = _clean_text(item_a.get("category", ""))
            cat_b = _clean_text(item_b.get("category", ""))

            # Calculate string similarity ratio
            sim_ratio = difflib.SequenceMatcher(None, name_a, name_b).ratio()

            # Boost if category and brand match
            brand_match = _clean_text(item_a.get("brand", "")) == _clean_text(item_b.get("brand", "")) and item_a.get("brand")
            if brand_match and sim_ratio >= 0.65:
                sim_ratio = min(0.98, sim_ratio + 0.10)

            if sim_ratio >= similarity_threshold:
                pair_key = tuple(sorted([item_a.get("product_id", str(i)), item_b.get("product_id", str(j))]))
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    conf_label = "High Probability Duplicate" if sim_ratio >= 0.85 else "Possible Duplicate"
                    fuzzy_duplicates.append({
                        "duplicate_type": "HIGH_ATTRIBUTE_SIMILARITY",
                        "matching_field": "name_and_brand_similarity",
                        "confidence_score": round(sim_ratio, 3),
                        "confidence_label": f"{conf_label} ({round(sim_ratio*100, 1)}%)",
                        "products_count": 2,
                        "items": [item_a, item_b],
                        "comparison_notes": f"Name similarity '{item_a.get('name')}' vs '{item_b.get('name')}'"
                    })

    all_duplicate_groups = exact_duplicates + fuzzy_duplicates

    return {
        "total_catalog_items_scanned": len(catalog),
        "duplicate_groups_found": len(all_duplicate_groups),
        "exact_sku_duplicates_count": len(exact_duplicates),
        "fuzzy_similarity_duplicates_count": len(fuzzy_duplicates),
        "duplicate_groups": all_duplicate_groups
    }
