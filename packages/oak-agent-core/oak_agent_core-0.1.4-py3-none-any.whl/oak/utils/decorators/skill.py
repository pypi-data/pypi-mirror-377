import functools
import inspect
from typing import List, Dict, Any, Callable, Optional

# Global registry to hold all registered skills metadata
_SKILL_REGISTRY: List[Dict[str, Any]] = []

def skill(
    name: str,
    description: str,
    examples: Optional[List[str]] = None,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    capabilities: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to mark a function as a skill and register its metadata.

    Args:
        name: The name of the skill.
        description: A detailed description of the skill's capability.
        examples: List of example queries.
        input_schema: JSON schema or descriptor for input parameters.
        output_schema: JSON schema or descriptor for output.
        capabilities: JSON schema or descriptor for capabilites this skill supports, e.g., streaming or context.
    """
    def decorator(func: Callable):
        # Extract function signature details
        signature = inspect.signature(func)
        parameters = {}
        for param in signature.parameters.values():
            parameters[param.name] = {
                "kind": str(param.kind),
                "default": param.default if param.default is not inspect.Parameter.empty else None,
                "annotation": param.annotation if param.annotation is not inspect.Parameter.empty else None,
            }

        # Register the skill metadata
        skill_info = {
            "name": name,
            "description": description,
            "examples": examples or [],
            "input_schema": input_schema or parameters,
            "output_schema": output_schema or None,
            "capabilities": capabilities or {},
        }
        _SKILL_REGISTRY.append(skill_info)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator

def get_all_skills_info() -> List[Dict[str, Any]]:
    """
    Returns the list of all registered skills with metadata.
    """
    return _SKILL_REGISTRY
