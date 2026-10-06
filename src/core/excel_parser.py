"""
Dynamic parser to load workflows and test suites from Excel.
Enables instant extensibility: simply add a row to the Excel sheet.
"""

import os
from typing import List, Dict, Any, Tuple
import openpyxl
from src.core.models import WorkflowDefinition


class ExcelWorkflowParser:
    """
    Parses workflow definitions and evaluation questions from Excel spreadsheets.
    """

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found at: {excel_path}")

    def load_workflows(self) -> Dict[str, WorkflowDefinition]:
        """
        Loads all workflows from the 'Workflows' sheet.
        Returns a dictionary keyed by Workflow_ID.
        """
        wb = openpyxl.load_workbook(self.excel_path, data_only=True)
        if "Workflows" not in wb.sheetnames:
            raise ValueError(f"'Workflows' sheet missing in {self.excel_path}. Available: {wb.sheetnames}")

        ws = wb["Workflows"]
        headers = [cell.value for cell in ws[1]]
        # Normalize header keys to lowercase / strip
        header_map = {str(h).strip().lower(): idx for idx, h in enumerate(headers) if h is not None}

        workflows: Dict[str, WorkflowDefinition] = {}

        for row_idx in range(2, ws.max_row + 1):
            row_vals = [ws.cell(row_idx, c + 1).value for c in range(len(headers))]
            if not any(v is not None for v in row_vals):
                continue

            def get_col(col_name: str, default: str = "") -> str:
                idx = header_map.get(col_name.lower())
                if idx is not None and idx < len(row_vals) and row_vals[idx] is not None:
                    return str(row_vals[idx]).strip()
                return default

            wf_id = get_col("workflow_id")
            if not wf_id:
                continue

            wf_name = get_col("workflow_name")
            trigger = get_col("trigger")
            inputs = get_col("inputs")
            steps_raw = get_col("steps")
            decision_logic = get_col("decision_logic")
            tools_required = get_col("tools_required")
            expected_output = get_col("expected_output")

            # Parse steps (split by arrow '→' or '->' or comma/numbered)
            parsed_steps = []
            if "→" in steps_raw:
                parsed_steps = [s.strip() for s in steps_raw.split("→") if s.strip()]
            elif "->" in steps_raw:
                parsed_steps = [s.strip() for s in steps_raw.split("->") if s.strip()]
            elif ";" in steps_raw:
                parsed_steps = [s.strip() for s in steps_raw.split(";") if s.strip()]
            else:
                parsed_steps = [steps_raw]

            wf_def = WorkflowDefinition(
                workflow_id=wf_id,
                workflow_name=wf_name,
                trigger=trigger,
                inputs=inputs,
                steps_raw=steps_raw,
                steps=parsed_steps,
                decision_logic=decision_logic,
                tools_required=tools_required,
                expected_output=expected_output
            )
            workflows[wf_id] = wf_def

        return workflows

    def load_test_questions(self) -> List[Dict[str, Any]]:
        """
        Loads the test questions sheet.
        """
        wb = openpyxl.load_workbook(self.excel_path, data_only=True)
        if "Test_Questions" not in wb.sheetnames:
            return []

        ws = wb["Test_Questions"]
        headers = [cell.value for cell in ws[1]]
        header_map = {str(h).strip().lower(): idx for idx, h in enumerate(headers) if h is not None}

        questions = []
        for row_idx in range(2, ws.max_row + 1):
            row_vals = [ws.cell(row_idx, c + 1).value for c in range(len(headers))]
            if not any(v is not None for v in row_vals):
                continue

            wf_id = ""
            idx = header_map.get("workflow_id")
            if idx is not None and row_vals[idx] is not None:
                wf_id = str(row_vals[idx]).strip()

            test_req = ""
            idx = header_map.get("test_request")
            if idx is not None and row_vals[idx] is not None:
                test_req = str(row_vals[idx]).strip()

            check = ""
            idx = header_map.get("what_to_check")
            if idx is not None and row_vals[idx] is not None:
                check = str(row_vals[idx]).strip()

            if wf_id and test_req:
                questions.append({
                    "workflow_id": wf_id,
                    "test_request": test_req,
                    "what_to_check": check
                })

        return questions
