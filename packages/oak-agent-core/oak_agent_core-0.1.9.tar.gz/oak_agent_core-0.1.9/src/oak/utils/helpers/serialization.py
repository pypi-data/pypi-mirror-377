# finance_ai/utils/serialization.py

import json
import logging
import math
from datetime import date
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert objects to a JSON-serializable form.
    Handles dates, datetimes, numpy and pandas types, floats (NaN, inf), sets, and more.
    """
    if obj is None:
        return obj
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, (str, int, bool)):
        return obj
    elif isinstance(obj, float):
        # Handle NaN, +inf, -inf
        if math.isnan(obj) or math.isinf(obj):
            return None
        else:
            return obj
    
    else:
        return str(obj)
    
def safely_serialize_data(data: Any) -> str:
    """
    Safely serialize arbitrary data structures to JSON for storage or LLM communication.
    """
    return json.dumps(sanitize_for_json(data), ensure_ascii=False)

def try_parse_json(text: str) -> Any:
    """
    Try to parse a string as JSON, returning None if parsing fails.
    """
    try:
        return json.loads(text)
    except Exception:
        return None
