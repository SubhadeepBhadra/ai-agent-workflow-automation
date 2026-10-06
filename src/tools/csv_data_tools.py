"""
CSV and File Data Reader tools.
"""

import os
import csv
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from src.core.tool_registry import register_tool

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_sources"))


@register_tool("read_inventory_csv", description="Reads product inventory records including current stock and minimum thresholds", category="Data Access")
def read_inventory_csv(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = file_path or os.path.join(DEFAULT_DATA_DIR, "inventory.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Inventory file not found: {path}")
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


@register_tool("read_vendor_prices_csv", description="Reads internal product prices and vendor price quotes", category="Data Access")
def read_vendor_prices_csv(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = file_path or os.path.join(DEFAULT_DATA_DIR, "vendor_prices.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Vendor prices file not found: {path}")
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


@register_tool("read_product_catalog_csv", description="Reads full product catalog with SKUs, titles, categories, and attributes", category="Data Access")
def read_product_catalog_csv(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = file_path or os.path.join(DEFAULT_DATA_DIR, "products_catalog.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Catalog file not found: {path}")
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


@register_tool("read_seo_keywords_csv", description="Reads SEO keywords list with search volumes and competition metrics", category="Data Access")
def read_seo_keywords_csv(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = file_path or os.path.join(DEFAULT_DATA_DIR, "seo_keywords.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Keywords file not found: {path}")
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


@register_tool("read_execution_logs_csv", description="Reads historical workflow execution logs and performance metrics", category="Analytics")
def read_execution_logs_csv(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = file_path or os.path.join(DEFAULT_DATA_DIR, "workflow_execution_logs.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Logs file not found: {path}")
    df = pd.read_csv(path)
    return df.to_dict(orient="records")
