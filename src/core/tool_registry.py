"""
Extensible Tool Registry for dynamic agent capabilities.
New tools can be registered with a single @register_tool decorator.
"""

from typing import Callable, Dict, Any, Optional, List
import inspect
import time
from pydantic import BaseModel
from src.core.models import ToolCallLog


class ToolDefinition(BaseModel):
    name: str
    description: str
    category: str = "General"
    parameters_schema: Dict[str, Any] = {}


class ToolRegistry:
    """
    Central repository for all agent tools and simulated APIs.
    """
    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, description: str, category: str = "General"):
        """
        Decorator to register a function as an agent tool.
        """
        def decorator(func: Callable):
            sig = inspect.signature(func)
            params = {}
            for param_name, param in sig.parameters.items():
                params[param_name] = {
                    "type": str(param.annotation) if param.annotation != inspect._empty else "Any",
                    "default": str(param.default) if param.default != inspect._empty else None,
                    "required": param.default == inspect._empty
                }

            cls._registry[name] = {
                "func": func,
                "name": name,
                "description": description,
                "category": category,
                "params": params,
                "doc": inspect.getdoc(func) or description
            }
            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Optional[Callable]:
        tool_info = cls._registry.get(name)
        if tool_info:
            return tool_info["func"]
        return None

    @classmethod
    def list_tools(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": info["description"],
                "category": info["category"],
                "parameters": info["params"]
            }
            for name, info in cls._registry.items()
        ]

    @classmethod
    def execute(cls, tool_name: str, **kwargs) -> ToolCallLog:
        """
        Safely executes a registered tool and returns a ToolCallLog with duration and results.
        """
        tool_info = cls._registry.get(tool_name)
        if not tool_info:
            return ToolCallLog(
                tool_name=tool_name,
                inputs=kwargs,
                output=None,
                success=False,
                error=f"Tool '{tool_name}' is not registered in ToolRegistry."
            )

        start_time = time.time()
        func = tool_info["func"]
        try:
            # Filter kwargs to only those accepted by function
            sig = inspect.signature(func)
            valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            result = func(**valid_kwargs)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return ToolCallLog(
                tool_name=tool_name,
                inputs=kwargs,
                output=result,
                duration_ms=duration_ms,
                success=True,
                error=None
            )
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return ToolCallLog(
                tool_name=tool_name,
                inputs=kwargs,
                output=None,
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )


# Alias for easy import
register_tool = ToolRegistry.register
Tuple_Result = ToolCallLog
