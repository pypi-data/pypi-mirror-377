import json
from fastapi import HTTPException
from sqlalchemy import text
from typing import List, Dict, Any
from oak.services.data_fetcher.database_service import get_db_session 
from oak.utils.helpers import sanitize_for_json  

def get_portfolio_holdings(user_id: str) -> List[Dict[str, Any]]:
    """
    Queries the database for all portfolio holdings associated with a given user ID.
    """
    try:
        with get_db_session() as conn:
            query = text("SELECT stock_symbol, total_shares, average_cost_basis FROM portfolio_holdings WHERE user_id = :user_id")
            result = conn.execute(query, {"user_id": user_id})
            holdings = [dict(row._mapping) for row in result.fetchall()]
        return json.dumps(holdings, default=sanitize_for_json, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

if __name__ == "__main__":
    try:
        user_id_to_query = "your_test_user_id"
        print(f"Querying portfolio holdings for user_id: {user_id_to_query}")
        portfolio_data = get_portfolio_holdings(user_id_to_query)
        print(portfolio_data)
    except HTTPException as he:
        print(f"Error: {he.detail}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")