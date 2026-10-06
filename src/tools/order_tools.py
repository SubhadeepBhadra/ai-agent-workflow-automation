"""
Order database and shipment tracking lookup tools.
"""

import os
import json
from typing import Dict, Any, Optional
from src.core.tool_registry import register_tool

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_sources"))


@register_tool("lookup_order_and_shipment", description="Searches order database by Order ID or customer email and retrieves order and tracking status", category="Orders & Logistics")
def lookup_order_and_shipment(identifier: Optional[str] = "ORD-1001", data_path: Optional[str] = None) -> Dict[str, Any]:
    path = data_path or os.path.join(DEFAULT_DATA_DIR, "orders.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Orders database not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        orders_db = json.load(f)

    if not identifier:
        return {
            "found": False,
            "message": "No identifier provided. Please provide a valid Order ID (e.g. 'ORD-1001') or customer email.",
            "searched_identifier": ""
        }

    clean_id = identifier.strip().upper()
    found_order = None

    # Search by key or order_id
    if clean_id in orders_db:
        found_order = orders_db[clean_id]
    else:
        # Search by order_id or email inside values
        for key, order in orders_db.items():
            if order.get("order_id", "").upper() == clean_id or order.get("customer_email", "").lower() == identifier.strip().lower():
                found_order = order
                break

    if not found_order:
        available_sample_ids = list(orders_db.keys())
        return {
            "found": False,
            "message": f"Order matching identifier '{identifier}' was not found in the database. Please verify the identifier and try again.",
            "available_sample_orders": available_sample_ids,
            "decision_branch": "IDENTIFIER_NOT_FOUND"
        }

    shipment = found_order.get("shipment", {})

    return {
        "found": True,
        "order_id": found_order.get("order_id"),
        "customer_email": found_order.get("customer_email"),
        "order_date": found_order.get("order_date"),
        "order_status": found_order.get("status"),
        "total_amount": found_order.get("total_amount"),
        "items": found_order.get("items", []),
        "shipment_details": {
            "carrier": shipment.get("carrier", "N/A"),
            "tracking_number": shipment.get("tracking_number", "N/A"),
            "shipped_at": shipment.get("shipped_at"),
            "estimated_delivery": shipment.get("estimated_delivery"),
            "current_location": shipment.get("current_location"),
            "last_checkpoint": shipment.get("last_checkpoint")
        },
        "summary_statement": f"Order {found_order.get('order_id')} is currently {found_order.get('status')}. Carrier: {shipment.get('carrier')}, Tracking: {shipment.get('tracking_number')}."
    }
