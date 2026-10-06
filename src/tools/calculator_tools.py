"""
Mathematical and threshold calculation tools.
"""

from typing import List, Dict, Any, Optional
from src.core.tool_registry import register_tool


@register_tool("calculate_stock_restock", description="Compares inventory stock with minimum threshold and computes recommended reorder quantity", category="Calculations")
def calculate_stock_restock(inventory: List[Dict[str, Any]], custom_threshold: Optional[int] = None) -> Dict[str, Any]:
    restock_needed = []
    healthy_stock = []

    for item in inventory:
        sku = item.get("sku", "UNKNOWN")
        name = item.get("product_name", "Unknown Product")
        current_stock = int(item.get("current_stock", 0))
        min_threshold = custom_threshold if custom_threshold is not None else int(item.get("minimum_threshold", 10))
        target_stock = int(item.get("target_stock", min_threshold * 2))

        # Condition logic: If current_stock < minimum_stock, mark for restock
        if current_stock < min_threshold:
            reorder_qty = max(0, target_stock - current_stock)
            shortage = min_threshold - current_stock
            restock_needed.append({
                "sku": sku,
                "product_name": name,
                "current_stock": current_stock,
                "minimum_threshold": min_threshold,
                "target_stock": target_stock,
                "shortage": shortage,
                "suggested_reorder_qty": reorder_qty,
                "unit_cost": float(item.get("unit_cost", 0.0)),
                "estimated_reorder_cost": round(reorder_qty * float(item.get("unit_cost", 0.0)), 2),
                "supplier": item.get("supplier", "N/A")
            })
        else:
            healthy_stock.append({
                "sku": sku,
                "product_name": name,
                "current_stock": current_stock,
                "minimum_threshold": min_threshold
            })

    # Sort low stock items by greatest shortage
    restock_needed.sort(key=lambda x: x["shortage"], reverse=True)
    total_reorder_units = sum(i["suggested_reorder_qty"] for i in restock_needed)
    total_reorder_budget = round(sum(i["estimated_reorder_cost"] for i in restock_needed), 2)

    return {
        "total_items_analyzed": len(inventory),
        "items_requiring_restock_count": len(restock_needed),
        "healthy_items_count": len(healthy_stock),
        "total_reorder_units": total_reorder_units,
        "total_estimated_budget": total_reorder_budget,
        "restock_list": restock_needed
    }


@register_tool("calculate_price_variance", description="Compares internal catalog prices with vendor price lists and flags discrepancies exceeding threshold percentage", category="Calculations")
def calculate_price_variance(vendor_prices: List[Dict[str, Any]], threshold_percentage: float = 10.0) -> Dict[str, Any]:
    matched_products = []
    exceptions = []

    for row in vendor_prices:
        sku = row.get("sku", "")
        name = row.get("product_name", "")
        internal_p = float(row.get("internal_price", 0.0))
        vendor_p = float(row.get("vendor_price", 0.0))
        supplier = row.get("supplier", "N/A")

        diff = vendor_p - internal_p
        pct_diff = round((diff / internal_p) * 100, 2) if internal_p > 0 else 0.0
        abs_pct = abs(pct_diff)

        is_flagged = abs_pct > threshold_percentage
        record = {
            "sku": sku,
            "product_name": name,
            "internal_price": internal_p,
            "vendor_price": vendor_p,
            "price_difference": round(diff, 2),
            "percentage_difference": f"{'+' if pct_diff > 0 else ''}{pct_diff}%",
            "is_flagged": is_flagged,
            "supplier": supplier,
            "reason": f"Variance of {abs_pct}% exceeds allowed {threshold_percentage}% threshold" if is_flagged else "Within tolerance"
        }

        matched_products.append(record)
        if is_flagged:
            exceptions.append(record)

    return {
        "total_products_checked": len(vendor_prices),
        "matched_count": len(matched_products),
        "exceptions_count": len(exceptions),
        "threshold_used_pct": threshold_percentage,
        "flagged_exceptions": exceptions,
        "all_matched_products": matched_products
    }
