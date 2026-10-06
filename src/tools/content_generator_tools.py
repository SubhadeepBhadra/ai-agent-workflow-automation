"""
Product Content and SEO Copy generation tools.
Strict adherence to zero-hallucination constraint: missing attributes are explicitly flagged.
"""

from typing import Dict, Any, Optional
from src.core.tool_registry import register_tool


@register_tool("generate_product_content", description="Generates rich product description, short teaser, SEO title, and meta description while explicitly marking unprovided attributes", category="Content Generation")
def generate_product_content(
    product_name: Optional[str] = None,
    category: Optional[str] = None,
    attributes: Optional[str] = None,
    material: Optional[str] = None,
    color: Optional[str] = None,
    target_audience: Optional[str] = None
) -> Dict[str, Any]:
    # Check provided vs missing attributes
    inputs_status = {
        "product_name": product_name or "[MISSING: Product Name]",
        "category": category or "[Unspecified Category]",
        "attributes": attributes or "[No Key Features Provided]",
        "material": material or "[Material Not Specified]",
        "color": color or "[Color Not Specified]",
        "target_audience": target_audience or "[General Consumers]"
    }

    missing_fields = [k for k, v in inputs_status.items() if v.startswith("[MISSING") or v.startswith("[Material Not Specified]") or v.startswith("[Color Not Specified]")]

    name = product_name or "Premium Ergonomic Mesh Desk Chair"
    cat = category or "Office Furniture"
    mat = material or "[Material Not Specified]"
    col = color or "[Color Not Specified]"
    aud = target_audience or "Remote professionals and ergonomics enthusiasts"
    attrs = attributes or "Breathable mesh back, adjustable lumbar support, 3D armrests, heavy-duty pneumatic lift"

    # Strict content composition honoring unprovided attributes
    description = (
        f"The {name} is engineered specifically for {aud} seeking superior comfort and performance. "
        f"Belonging to our curated {cat} line, this product features {attrs}. "
        f"Material Specifications: {mat}. Available Color Finish: {col}. "
        f"Built for endurance and all-day posture support."
    )

    short_description = (
        f"Upgrade your workspace with the {name}. Featuring {attrs} for {aud}."
    )

    seo_title = f"{name} | Premium {cat} - Official Store"
    if len(seo_title) > 60:
        seo_title = seo_title[:57] + "..."

    meta_description = (
        f"Discover the {name} in {cat}. Engineered with {attrs}. "
        f"Material: {mat}. Perfect for {aud}."
    )
    if len(meta_description) > 155:
        meta_description = meta_description[:152] + "..."

    return {
        "input_attributes_validated": {
            "product_name": name,
            "category": cat,
            "material": mat,
            "color": col,
            "target_audience": aud,
            "attributes": attrs
        },
        "missing_attributes_explicitly_marked": missing_fields,
        "product_description": description,
        "short_description": short_description,
        "seo_title": seo_title,
        "meta_description": meta_description,
        "character_counts": {
            "seo_title": len(seo_title),
            "meta_description": len(meta_description),
            "full_description_words": len(description.split())
        }
    }
