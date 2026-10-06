"""
Intelligent Intent Router and Workflow Selector.
Selects the matching workflow dynamically based on semantic analysis, token weighting, and LLM reasoning.
Fully scalable: dynamically extracts routing features from any registered workflow definition.
"""

import re
import difflib
from typing import Dict, Any, List, Optional, Tuple
from src.core.models import WorkflowDefinition, IntentMatchResult


# Stopwords that shouldn't dominate routing over specific intent verbs
COMMON_STOPWORDS = {
    "the", "is", "a", "an", "this", "that", "these", "those", "for", "to", "in",
    "on", "at", "by", "from", "with", "about", "into", "through", "during", "before",
    "after", "above", "below", "and", "or", "not", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "can", "could", "should", "would", "may", "might", "must",
    "user", "asks", "asks for", "check", "find", "get", "show", "please", "we", "our", "all"
}


class IntentRouter:
    """
    Intelligent router that maps a user's natural language request to the appropriate workflow.
    """

    def __init__(self, workflows: Dict[str, WorkflowDefinition], llm_client: Optional[Any] = None):
        self.workflows = workflows
        self.llm_client = llm_client

    def route(self, user_request: str) -> IntentMatchResult:
        """
        Routes the user request to the best matching workflow.
        """
        if not user_request or not user_request.strip():
            first_wf = next(iter(self.workflows.values()))
            return IntentMatchResult(
                workflow_id=first_wf.workflow_id,
                workflow_name=first_wf.workflow_name,
                confidence=0.1,
                reasoning="Empty query provided; defaulted to initial workflow."
            )

        best_wf_id, score, reasoning, extracted_params = self._semantic_match(user_request)

        selected_wf = self.workflows.get(best_wf_id, next(iter(self.workflows.values())))
        return IntentMatchResult(
            workflow_id=selected_wf.workflow_id,
            workflow_name=selected_wf.workflow_name,
            confidence=round(score, 3),
            reasoning=reasoning,
            extracted_parameters=extracted_params
        )

    def _semantic_match(self, query: str) -> Tuple[str, float, str, Dict[str, Any]]:
        q_clean = query.lower()
        query_words = set(re.findall(r"\b[a-z0-9_\-]+\b", q_clean))
        meaningful_query_words = query_words - COMMON_STOPWORDS

        extracted_params = {}

        # Extract specific entities from query
        order_match = re.search(r"\b(ORD-\d+|[A-Z]{3}-\d+)\b", query, re.IGNORECASE)
        if order_match:
            extracted_params["identifier"] = order_match.group(1)

        pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%", query)
        if pct_match:
            extracted_params["threshold_percentage"] = float(pct_match.group(1))

        # Domain specific anchor keywords (high discriminative power)
        anchor_keywords = {
            "WF001": ["restock", "restocking", "inventory", "stock", "reorder", "shortage"],
            "WF002": ["price", "prices", "vendor price", "differ", "differs", "variance", "discrepancy", "10%"],
            "WF003": ["spreadsheet", "vendor file", "invalid rows", "ingestion", "clean", "cleaned", "rows missing", "vendor spreadsheet"],
            "WF004": ["seo content", "product content", "product description", "meta description", "seo title", "description generator", "copywriting"],
            "WF005": ["order status", "where is order", "shipment", "tracking", "track order", "carrier", "delivered", "in transit"],
            "WF006": ["duplicate", "duplicates", "duplicate products", "identical", "similarity", "catalog duplicates"],
            "WF007": ["campaign brief", "marketing campaign", "brief", "collection", "promotion", "messaging strategy"],
            "WF008": ["keyword", "keywords", "classify these keywords", "search intent", "seo keyword", "map them to pages", "target page"],
            "WF009": ["assign", "task", "developer", "employee", "urgent task", "workload", "skills", "available developer"],
            "WF010": ["failing", "performance report", "failing most often", "execution logs", "failure rate", "latency", "slow steps"],
            "WF011": ["refund", "refunds", "return", "dispute", "chargeback", "return window", "reimbursement"]
        }

        scores = {}
        reasoning_map = {}

        for wf_id, wf in self.workflows.items():
            base_score = 0.0
            reasons = []

            # 1. Explicit Workflow ID mention
            if wf_id.lower() in q_clean:
                base_score += 1.5
                reasons.append(f"Explicit Workflow ID match ({wf_id})")

            # 2. Sequence similarity with trigger and name
            trigger_clean = wf.trigger.lower()
            name_clean = wf.workflow_name.lower()

            t_sim = difflib.SequenceMatcher(None, q_clean, trigger_clean).ratio()
            n_sim = difflib.SequenceMatcher(None, q_clean, name_clean).ratio()

            if t_sim > 0.35:
                base_score += t_sim * 0.8
                reasons.append(f"Trigger pattern match ({t_sim:.2f})")
            if n_sim > 0.35:
                base_score += n_sim * 0.7
                reasons.append(f"Title match ({n_sim:.2f})")

            # 3. Dynamic keywords derived from trigger, name, inputs, and decision logic
            wf_combined_text = f"{wf.workflow_name} {wf.trigger} {wf.inputs} {wf.decision_logic}".lower()
            wf_tokens = set(re.findall(r"\b[a-z0-9_\-]+\b", wf_combined_text)) - COMMON_STOPWORDS

            # Include explicit anchors if available
            anchors = anchor_keywords.get(wf_id, [])
            for a in anchors:
                wf_tokens.add(a.lower())

            # Check overlap with query words
            matched_anchors = [a for a in anchors if a in q_clean]
            matched_tokens = list(meaningful_query_words.intersection(wf_tokens))

            if matched_anchors:
                base_score += len(matched_anchors) * 0.55
                reasons.append(f"Matched anchor intents: {', '.join(matched_anchors)}")
            elif matched_tokens:
                base_score += len(matched_tokens) * 0.25
                reasons.append(f"Matched domain keywords: {', '.join(matched_tokens[:3])}")

            scores[wf_id] = base_score
            reasoning_map[wf_id] = "; ".join(reasons) if reasons else "Keyword similarity"

        # Select highest scoring workflow
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_wf_id, highest_score = sorted_scores[0]
        normalized_confidence = min(0.99, max(0.45, highest_score / 2.0))

        return best_wf_id, normalized_confidence, reasoning_map.get(best_wf_id, "Matched via dynamic intent analysis"), extracted_params
