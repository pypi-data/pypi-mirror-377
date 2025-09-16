import json
from fastapi import HTTPException
from sqlalchemy import text
from typing import List, Dict, Any
from oak.services.data_fetcher.database_service import get_db_session 
from oak.utils.helpers import sanitize_for_json

def get_user_goals(user_id: str) -> List[Dict[str, Any]]:
    """
    Queries the database for all goals associated with a given user ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A serialized list of dictionaries, where each dictionary represents a user goal.

    Raises:
        HTTPException: If the database query fails.
    """
    try:
        with get_db_session() as conn:
            query = text("SELECT name, target_amount, target_date, current_amount, updated_at FROM user_goal WHERE user_id = :user_id AND status = 'active'")
            result = conn.execute(query, {"user_id": user_id})
            goals = [dict(row._mapping) for row in result.fetchall()]
        return json.dumps(goals, default=sanitize_for_json, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

if __name__ == "__main__":
    # Example usage for demonstration purposes
    try:
        user_id_to_query = "your_test_user_id"  # Replace with a valid user ID
        print(f"Querying goals for user_id: {user_id_to_query}")
        goals_data = get_user_goals(user_id_to_query)
        print(goals_data)
    except HTTPException as he:
        print(f"Error: {he.detail}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")