from datetime import date
import json
import logging
from fastapi import HTTPException
from langchain.agents import tool

from oak.modules.user.goals import get_user_goals
from oak.modules.user.portfolio import get_portfolio_holdings
from oak.services.data_fetcher.rag_service import search_embeddings
from oak.services.data_fetcher.database_service import get_db_connection, get_db_session
from oak.utils.decorators.skill import skill
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

@skill(
    name="financial_context_tool",
    description=(
        "Retrieves a user's financial portfolio and goals. "
        "Use this to get personal_context and other relevant user financial data "
        "when that information is missing from a query. "
        "This skill aggregates portfolio holdings and current goals for comprehensive context."
    ),
    examples=[
        "analyze my portfolio performance",
        "what are my financial goals?",
        "show me my current financial position"
    ],
    input_schema={
        "user_id": {"type": "string", "description": "The unique identifier for the user."},
        "query": {"type": "string", "description": "User's financial query or request."}
    },
    output_schema={
        "user_goals": {"type": "object", "description": "User's financial goals data."},
        "portfolio_holdings": {"type": "object", "description": "User's portfolio holdings data."}
    },
    capabilities={
        "streaming": False,
        "authentication_required": True
    }
)
@tool(description="Gets a user's financial context combining portfolio and goals data")
def financial_context_tool(user_id: str, query: str) -> str:
    """
    Retrieves and provides financial context for a user's query.

    Args:
        user_id: The unique identifier of the user.
        query: The user's specific financial question.

    Returns:
        A string containing relevant financial information.
    """
    response = get_financial_context(user_id=user_id, query=query)
    
    return json.dumps(response, default=json_serial)

def get_financial_context(user_id: str, query: str) -> str:
    logger.info(f"Fetching financial context for user: {user_id}, query: {query}")
    goals = get_user_goals(user_id)
    logger.info(f"User goals: {goals}")
    holdings = get_portfolio_holdings(user_id)
    logger.info(f"Portfolio holdings: {holdings}")
    return {
        "user_goals": goals,
        "portfolio_holdings": holdings,
    }