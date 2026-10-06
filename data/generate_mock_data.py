import os
import json
import csv
import pandas as pd
import random
from datetime import datetime, timedelta

base_dir = r"C:\Users\Subho\.gemini\antigravity-ide\scratch\ai-agent-workflow-automation\data\mock_sources"
os.makedirs(base_dir, exist_ok=True)

# 1. Inventory Data (for WF001)
inventory_data = [
    {"sku": "SKU-101", "product_name": "Ergonomic Office Chair", "category": "Furniture", "current_stock": 12, "minimum_threshold": 25, "target_stock": 50, "unit_cost": 120.00, "supplier": "ErgoWorks"},
    {"sku": "SKU-102", "product_name": "Mechanical Keyboard RGB", "category": "Electronics", "current_stock": 8, "minimum_threshold": 15, "target_stock": 40, "unit_cost": 65.00, "supplier": "KeyTech"},
    {"sku": "SKU-103", "product_name": "UltraWide Monitor 34-inch", "category": "Electronics", "current_stock": 4, "minimum_threshold": 10, "target_stock": 20, "unit_cost": 340.00, "supplier": "VisionPro"},
    {"sku": "SKU-104", "product_name": "Noise Cancelling Headphones", "category": "Audio", "current_stock": 45, "minimum_threshold": 20, "target_stock": 60, "unit_cost": 95.00, "supplier": "SoundMax"},
    {"sku": "SKU-105", "product_name": "USB-C Multiport Dock", "category": "Accessories", "current_stock": 6, "minimum_threshold": 30, "target_stock": 75, "unit_cost": 28.50, "supplier": "ConnectHub"},
    {"sku": "SKU-106", "product_name": "Standing Desk Frame", "category": "Furniture", "current_stock": 18, "minimum_threshold": 15, "target_stock": 35, "unit_cost": 180.00, "supplier": "ErgoWorks"},
    {"sku": "SKU-107", "product_name": "Wireless Vertical Mouse", "category": "Accessories", "current_stock": 3, "minimum_threshold": 20, "target_stock": 50, "unit_cost": 22.00, "supplier": "KeyTech"},
    {"sku": "SKU-108", "product_name": "HD Webcam 1080p", "category": "Electronics", "current_stock": 28, "minimum_threshold": 20, "target_stock": 50, "unit_cost": 45.00, "supplier": "VisionPro"},
    {"sku": "SKU-109", "product_name": "Acoustic Desk Divider", "category": "Furniture", "current_stock": 2, "minimum_threshold": 12, "target_stock": 30, "unit_cost": 55.00, "supplier": "OfficeSpace"},
    {"sku": "SKU-110", "product_name": "LED Desk Lamp with Qi Charger", "category": "Accessories", "current_stock": 50, "minimum_threshold": 25, "target_stock": 60, "unit_cost": 19.50, "supplier": "BrightLife"}
]
with open(os.path.join(base_dir, "inventory.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=inventory_data[0].keys())
    writer.writeheader()
    writer.writerows(inventory_data)

# 2. Vendor Prices (for WF002)
vendor_prices_data = [
    {"sku": "SKU-101", "product_name": "Ergonomic Office Chair", "internal_price": 120.00, "vendor_price": 145.00, "supplier": "ErgoWorks"},  # +20.8% discrepancy -> FLAG
    {"sku": "SKU-102", "product_name": "Mechanical Keyboard RGB", "internal_price": 65.00, "vendor_price": 66.50, "supplier": "KeyTech"},       # +2.3% -> OK
    {"sku": "SKU-103", "product_name": "UltraWide Monitor 34-inch", "internal_price": 340.00, "vendor_price": 395.00, "supplier": "VisionPro"}, # +16.2% -> FLAG
    {"sku": "SKU-104", "product_name": "Noise Cancelling Headphones", "internal_price": 95.00, "vendor_price": 94.00, "supplier": "SoundMax"},   # -1.1% -> OK
    {"sku": "SKU-105", "product_name": "USB-C Multiport Dock", "internal_price": 28.50, "vendor_price": 35.00, "supplier": "ConnectHub"},       # +22.8% -> FLAG
    {"sku": "SKU-106", "product_name": "Standing Desk Frame", "internal_price": 180.00, "vendor_price": 182.00, "supplier": "ErgoWorks"},       # +1.1% -> OK
    {"sku": "SKU-107", "product_name": "Wireless Vertical Mouse", "internal_price": 22.00, "vendor_price": 18.00, "supplier": "KeyTech"},        # -18.2% -> FLAG (undercut/change)
    {"sku": "SKU-108", "product_name": "HD Webcam 1080p", "internal_price": 45.00, "vendor_price": 46.00, "supplier": "VisionPro"},             # +2.2% -> OK
    {"sku": "SKU-109", "product_name": "Acoustic Desk Divider", "internal_price": 55.00, "vendor_price": 72.00, "supplier": "OfficeSpace"},     # +30.9% -> FLAG
    {"sku": "SKU-110", "product_name": "LED Desk Lamp with Qi Charger", "internal_price": 19.50, "vendor_price": 19.00, "supplier": "BrightLife"} # -2.5% -> OK
]
with open(os.path.join(base_dir, "vendor_prices.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=vendor_prices_data[0].keys())
    writer.writeheader()
    writer.writerows(vendor_prices_data)

# 3. Raw Vendor File with invalid rows & unnormalized columns (for WF003)
raw_vendor_rows = [
    {"vendor_sku": "VN-901", "Item_Title": "Leather Gaming Seat", "cost_usd": 150.0, "qty_avail": 40, "category_name": "Chairs"},
    {"vendor_sku": "", "Item_Title": "Missing SKU Headset", "cost_usd": 45.0, "qty_avail": 10, "category_name": "Audio"}, # INVALID: Missing SKU
    {"vendor_sku": "VN-903", "Item_Title": None, "cost_usd": 85.0, "qty_avail": 25, "category_name": "Keyboards"},       # INVALID: Missing Name
    {"vendor_sku": "VN-904", "Item_Title": "Dual Monitor Arm Heavy Duty", "cost_usd": 68.5, "qty_avail": 55, "category_name": "Accessories"},
    {"vendor_sku": "VN-905", "Item_Title": "Cable Management Spine", "cost_usd": 18.0, "qty_avail": 100, "category_name": "Accessories"},
    {"vendor_sku": None, "Item_Title": "Unnamed Gadget", "cost_usd": 12.0, "qty_avail": 15, "category_name": "Misc"},      # INVALID: Missing SKU
    {"vendor_sku": "VN-907", "Item_Title": "Under Desk Footrest", "cost_usd": 24.5, "qty_avail": 60, "category_name": "Comfort"},
    {"vendor_sku": "VN-908", "Item_Title": "", "cost_usd": 99.0, "qty_avail": 5, "category_name": "Storage"}             # INVALID: Missing Name
]
df_raw_vendor = pd.DataFrame(raw_vendor_rows)
df_raw_vendor.to_csv(os.path.join(base_dir, "vendor_raw_sample.csv"), index=False)
df_raw_vendor.to_excel(os.path.join(base_dir, "vendor_raw_sample.xlsx"), index=False)

# 4. Orders Data (for WF005)
orders_data = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_email": "sarah.connor@cyberdyne.io",
        "order_date": "2026-10-02T14:30:00Z",
        "status": "In Transit",
        "items": [
            {"sku": "SKU-101", "name": "Ergonomic Office Chair", "qty": 1, "price": 189.99},
            {"sku": "SKU-107", "name": "Wireless Vertical Mouse", "qty": 1, "price": 39.99}
        ],
        "total_amount": 229.98,
        "shipment": {
            "carrier": "FedEx Express",
            "tracking_number": "FDX-88392019482",
            "shipped_at": "2026-10-03T09:15:00Z",
            "estimated_delivery": "2026-10-08T18:00:00Z",
            "current_location": "Memphis Sorting Hub, TN",
            "last_checkpoint": "Departed FedEx facility"
        }
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_email": "alex.chen@innovate.tech",
        "order_date": "2026-10-05T10:15:00Z",
        "status": "Processing",
        "items": [
            {"sku": "SKU-103", "name": "UltraWide Monitor 34-inch", "qty": 2, "price": 499.99}
        ],
        "total_amount": 999.98,
        "shipment": {
            "carrier": "UPS Ground",
            "tracking_number": "Pending Assignment",
            "shipped_at": None,
            "estimated_delivery": "2026-10-11T17:00:00Z",
            "current_location": "Warehouse Fulfillment Center, Austin TX",
            "last_checkpoint": "Pick & Pack in Progress"
        }
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_email": "elena.rostova@designworks.com",
        "order_date": "2026-09-28T16:45:00Z",
        "status": "Delivered",
        "items": [
            {"sku": "SKU-102", "name": "Mechanical Keyboard RGB", "qty": 1, "price": 109.99},
            {"sku": "SKU-110", "name": "LED Desk Lamp with Qi Charger", "qty": 1, "price": 49.99}
        ],
        "total_amount": 159.98,
        "shipment": {
            "carrier": "DHL Express",
            "tracking_number": "DHL-4491028301",
            "shipped_at": "2026-09-29T11:00:00Z",
            "estimated_delivery": "2026-10-01T14:00:00Z",
            "current_location": "Delivered to Front Porch - Signed by E. Rostova",
            "last_checkpoint": "Delivered"
        }
    }
}
with open(os.path.join(base_dir, "orders.json"), "w", encoding="utf-8") as f:
    json.dump(orders_data, f, indent=2)

# 5. Product Catalog with Duplicates (for WF006)
catalog_data = [
    {"product_id": "P001", "sku": "SKU-201", "name": "Wireless Noise Cancelling Over-Ear Headphones Black", "category": "Audio", "brand": "AcoustiQ", "price": 149.99},
    {"product_id": "P002", "sku": "SKU-201", "name": "Wireless Noise Cancelling Over-Ear Headphones Black (Duplicate SKU)", "category": "Audio", "brand": "AcoustiQ", "price": 149.99}, # Exact SKU match (100%)
    {"product_id": "P003", "sku": "SKU-203", "name": "Wireless Noise Canceling Over Ear Headphone - Midnight Black", "category": "Audio", "brand": "AcoustiQ", "price": 154.99}, # High Fuzzy match (~90%)
    {"product_id": "P004", "sku": "SKU-204", "name": "Pro Aluminium Laptop Stand Foldable Ergonomic", "category": "Accessories", "brand": "DeskCraft", "price": 39.99},
    {"product_id": "P005", "sku": "SKU-205", "name": "Aluminum Foldable Laptop Riser Stand Pro", "category": "Accessories", "brand": "DeskCraft", "price": 42.00}, # Fuzzy match (~86%)
    {"product_id": "P006", "sku": "SKU-206", "name": "Mechanical Gaming Keyboard Tenkeyless Blue Switch", "category": "Keyboards", "brand": "Vortex", "price": 89.99},
    {"product_id": "P007", "sku": "SKU-207", "name": "4K Ultra HD Streaming Webcam with Privacy Shutter", "category": "Electronics", "brand": "OpticLens", "price": 79.99},
    {"product_id": "P008", "sku": "SKU-207", "name": "4K Ultra HD Streaming Webcam w/ Privacy Shutter (Duplicate SKU)", "category": "Electronics", "brand": "OpticLens", "price": 79.99}  # Exact SKU match (100%)
]
with open(os.path.join(base_dir, "products_catalog.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=catalog_data[0].keys())
    writer.writeheader()
    writer.writerows(catalog_data)

# 6. SEO Keywords Data (for WF008)
keywords_data = [
    {"keyword": "buy ergonomic office chair online", "search_volume": 12500, "cpc": 3.45, "competition": "High"},
    {"keyword": "what is the best chair for lower back pain", "search_volume": 8400, "cpc": 1.20, "competition": "Medium"},
    {"keyword": "best wireless mechanical keyboards 2026", "search_volume": 14200, "cpc": 2.10, "competition": "High"},
    {"keyword": "how to set up standing desk height", "search_volume": 6700, "cpc": 0.85, "competition": "Low"},
    {"keyword": "ergonomic office chair price comparison", "search_volume": 5300, "cpc": 2.90, "competition": "Medium"},
    {"keyword": "visionpro ultrawide monitor official store", "search_volume": 9100, "cpc": 1.75, "competition": "Medium"},
    {"keyword": "noise cancelling headphones discount code", "search_volume": 11000, "cpc": 4.10, "competition": "High"},
    {"keyword": "usb-c dock troubleshooting guide", "search_volume": 4200, "cpc": 0.50, "competition": "Low"},
    {"keyword": "buy ergonomic office chair online", "search_volume": 12500, "cpc": 3.45, "competition": "High"}, # Duplicate keyword
    {"keyword": "ergonomic workstation setup checklist", "search_volume": 3800, "cpc": 0.70, "competition": "Low"}
]
with open(os.path.join(base_dir, "seo_keywords.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=keywords_data[0].keys())
    writer.writeheader()
    writer.writerows(keywords_data)

# 7. Employees & Developers Data (for WF009)
employees_data = [
    {
        "employee_id": "EMP-01",
        "name": "David Kim",
        "role": "Senior Backend Developer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "System Architecture", "Docker"],
        "active_tasks_count": 1,
        "capacity_percentage": 30,
        "is_available": True,
        "performance_rating": 4.9
    },
    {
        "employee_id": "EMP-02",
        "name": "Maria Garcia",
        "role": "Full Stack Engineer",
        "skills": ["React", "TypeScript", "Node.js", "Python", "GraphQL"],
        "active_tasks_count": 4,
        "capacity_percentage": 95,
        "is_available": False,
        "performance_rating": 4.8
    },
    {
        "employee_id": "EMP-03",
        "name": "Liam Thorne",
        "role": "DevOps & Cloud Engineer",
        "skills": ["AWS", "Kubernetes", "Terraform", "CI/CD", "Linux"],
        "active_tasks_count": 2,
        "capacity_percentage": 50,
        "is_available": True,
        "performance_rating": 4.7
    },
    {
        "employee_id": "EMP-04",
        "name": "Priya Patel",
        "role": "Lead Data & AI Engineer",
        "skills": ["Python", "Machine Learning", "LangChain", "LLMs", "Pandas"],
        "active_tasks_count": 2,
        "capacity_percentage": 45,
        "is_available": True,
        "performance_rating": 4.95
    },
    {
        "employee_id": "EMP-05",
        "name": "Ethan Vance",
        "role": "Frontend Specialist",
        "skills": ["React", "Next.js", "TailwindCSS", "UI/UX", "Web Accessibility"],
        "active_tasks_count": 5,
        "capacity_percentage": 100,
        "is_available": False,
        "performance_rating": 4.6
    }
]
with open(os.path.join(base_dir, "employees.json"), "w", encoding="utf-8") as f:
    json.dump(employees_data, f, indent=2)

# 8. Workflow Execution Logs (for WF010)
wf_logs = []
random.seed(42)
wf_ids = [f"WF00{i}" if i < 10 else f"WF0{i}" for i in range(1, 11)]
error_messages = {
    "WF003": ["Invalid CSV Schema format", "Missing mandatory column 'SKU'"],
    "WF005": ["Order ID lookup timeout on 3rd party logistics API", "Tracking code format mismatch"],
    "WF007": ["Missing mandatory dates input", "Incomplete product specifications"],
    "WF002": ["Vendor endpoint 503 Service Unavailable"]
}

for i in range(1, 151):
    wf_id = random.choice(wf_ids)
    # Give WF003 and WF005 higher failure rates for clear detection
    if wf_id == "WF003":
        status = "FAILED" if random.random() < 0.22 else "SUCCESS"
    elif wf_id == "WF005":
        status = "FAILED" if random.random() < 0.16 else "SUCCESS"
    elif wf_id == "WF007":
        status = "FAILED" if random.random() < 0.12 else "SUCCESS"
    else:
        status = "FAILED" if random.random() < 0.03 else "SUCCESS"
    
    # Execution times
    if wf_id == "WF007":
        exec_time = round(random.uniform(5.5, 9.2), 2) # Slow step (LLM brief)
    elif wf_id == "WF004":
        exec_time = round(random.uniform(3.5, 6.0), 2)
    elif wf_id == "WF006":
        exec_time = round(random.uniform(4.0, 7.5), 2) # Text similarity matching
    else:
        exec_time = round(random.uniform(0.4, 2.1), 2)
        
    err_step = None
    err_msg = None
    if status == "FAILED":
        err_step = "Data Validation" if wf_id == "WF003" else ("Shipment API Lookup" if wf_id == "WF005" else "Input Sanitization")
        err_msg = random.choice(error_messages.get(wf_id, ["Unknown internal error", "Timeout during execution"]))
        
    wf_logs.append({
        "execution_id": f"EXEC-{1000 + i}",
        "workflow_id": wf_id,
        "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
        "execution_time_sec": exec_time,
        "status": status,
        "step_failed": err_step or "",
        "error_message": err_msg or ""
    })

with open(os.path.join(base_dir, "workflow_execution_logs.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=wf_logs[0].keys())
    writer.writeheader()
    writer.writerows(wf_logs)

print(f"Generated all mock business datasets in {base_dir}")
