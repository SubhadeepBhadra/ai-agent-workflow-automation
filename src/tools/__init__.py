"""
Tool module initialization and registry aggregator.
"""

from src.core.tool_registry import ToolRegistry, register_tool

# Import all tool implementations to trigger decorator registration
from src.tools.csv_data_tools import *
from src.tools.calculator_tools import *
from src.tools.data_cleaning_tools import *
from src.tools.content_generator_tools import *
from src.tools.order_tools import *
from src.tools.deduplication_tools import *
from src.tools.campaign_tools import *
from src.tools.seo_tools import *
from src.tools.employee_tools import *
from src.tools.analytics_tools import *

__all__ = ["ToolRegistry", "register_tool"]
