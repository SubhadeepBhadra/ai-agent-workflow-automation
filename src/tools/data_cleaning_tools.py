"""
Data cleaning and validation tools for vendor files and batch ingestion.
"""

import os
import pandas as pd
from typing import Dict, Any, Optional
from src.core.tool_registry import register_tool

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_sources"))


@register_tool("ingest_and_clean_vendor_file", description="Ingests raw vendor CSV/Excel file, normalizes columns, validates required fields, and isolates invalid rows", category="Data Processing")
def ingest_and_clean_vendor_file(file_path: Optional[str] = None) -> Dict[str, Any]:
    path = file_path or os.path.join(DEFAULT_DATA_DIR, "vendor_raw_sample.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Vendor raw file not found: {path}")

    # Read CSV or XLSX
    if path.endswith(".xlsx") or path.endswith(".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    raw_columns = list(df.columns)

    # Column normalization mapping
    column_mapping = {
        "vendor_sku": "sku",
        "item_sku": "sku",
        "sku_code": "sku",
        "item_title": "product_name",
        "product_title": "product_name",
        "name": "product_name",
        "cost_usd": "unit_cost",
        "cost": "unit_cost",
        "price": "unit_cost",
        "qty_avail": "quantity_available",
        "stock": "quantity_available",
        "category_name": "category",
        "cat": "category"
    }

    normalized_cols = {}
    for col in raw_columns:
        norm_key = str(col).strip().lower().replace(" ", "_")
        mapped_name = column_mapping.get(norm_key, norm_key)
        normalized_cols[col] = mapped_name

    df_normalized = df.rename(columns=normalized_cols)

    # Validation: Rows missing SKU or product name are invalid
    valid_rows = []
    invalid_rows = []

    for index, row in df_normalized.iterrows():
        row_dict = row.to_dict()
        sku_val = row_dict.get("sku")
        name_val = row_dict.get("product_name")

        reasons = []
        if pd.isna(sku_val) or str(sku_val).strip() in ("", "None", "nan"):
            reasons.append("Missing required field 'sku'")
        if pd.isna(name_val) or str(name_val).strip() in ("", "None", "nan"):
            reasons.append("Missing required field 'product_name'")

        if reasons:
            invalid_rows.append({
                "original_row_number": index + 2,
                "raw_data": {k: (None if pd.isna(v) else v) for k, v in row_dict.items()},
                "failure_reasons": reasons
            })
        else:
            cleaned_row = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
            valid_rows.append(cleaned_row)

    return {
        "file_source": os.path.basename(path),
        "detected_raw_columns": raw_columns,
        "normalized_column_schema": list(df_normalized.columns),
        "total_rows_processed": len(df),
        "valid_rows_count": len(valid_rows),
        "invalid_rows_count": len(invalid_rows),
        "cleaned_dataset": valid_rows,
        "invalid_rows_report": invalid_rows
    }
