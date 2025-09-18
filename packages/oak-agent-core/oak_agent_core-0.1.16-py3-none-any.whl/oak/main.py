import logging
import os

from sqlalchemy import text
import uvicorn
from fastapi import FastAPI, HTTPException
from oak.modules.user.goals import get_user_goals
from oak.modules.user.portfolio import get_portfolio_holdings
from oak.services.data_fetcher.api_service import fetch_stock_info
from oak.services.data_fetcher.database_service import get_db_session 
from oak.services.data_fetcher import get_prompt_service_instance
from oak.celery_app import celery_app
from oak.tasks.library import say_hello_task
from oak.config import Config

# Configure logging to display messages from the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI()

SAMPLE_USER_ID = "00ec53c9-c86a-4fdb-9cd4-9dff79b31392"
            
# Instantiate the PromptService using environment variables
shared_templates_path = os.getenv('SHARED_TEMPLATES_PATH', '/app/src/oak/prompt/shared_templates')
prompt_templates_path = os.getenv('PROMPT_TEMPLATES_PATH', '/app/src/oak/prompt/library')
prompt_service = get_prompt_service_instance(
    shared_templates=shared_templates_path, 
    library_templates=prompt_templates_path
)

@app.on_event("startup")
async def startup_event():
    """
    On application startup, check the database connection and
    ping the Celery worker to ensure all services are running.
    """
    logger.info("Starting up the application...")
    # Check database connection
    try:
        with get_db_session() as conn:
            # Execute a simple query to test the connection
            conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to the database.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")

    # Check Celery worker connection
    try:
        # Ping the worker to check for a successful connection
        task_id = say_hello_task.delay("application startup").id
        logger.info(f"Sent a test task to Celery worker with ID: {task_id}")
    except Exception as e:
        logger.error(f"Failed to connect to Celery worker: {e}")

@app.get("/")
def read_root():
    """
    Root endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is running and services are connected."}

@app.get("/get-tables")
def get_tables():
    """
    Endpoint to retrieve a list of all tables in the database.
    """
    try:
        with get_db_session() as conn:
            # Query the database for a list of all table names.
            # This query works for postgresql; adjust if using a different database.
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))

            tables = [row[0] for row in result.fetchall()]
        
        return {"status": "success", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

@app.get("/sample-prompt")
def get_sample_prompt():
    """
    Endpoint to test the PromptService and return a rendered prompt.
    """
    logger.info("Generating sample prompt...")
    user_goals = get_user_goals(SAMPLE_USER_ID)
    portfolio_holdings = get_portfolio_holdings(SAMPLE_USER_ID)
    context_data = {
        'user_question': "What is a good stock recommendation for me?",
        'personal_context': {
            "user_goals": user_goals, 
            "portfolio_holdings": portfolio_holdings
        },
        'knowledge_context': "I have a very high risk threshold."
    }
    # NOTE: You will need a template file named 'sample.jinja2' in your prompt library directory
    # for this to work.
    try:
        prompt = prompt_service.get_prompt('sample.jinja2', context_data)
        return {"status": "success", "prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt generation failed: {e}")

@app.get("/test-stock-info/{symbol}")
async def test_stock_info(symbol: str):
    """
    Tests the fetch_stock_info function by making a call to the external API.
    """
    logger.info(f"Testing fetch_stock_info for symbol: {symbol}")
    try:
        result = fetch_stock_info(symbol=symbol)
        if isinstance(result, tuple) and len(result) == 2:
            return_data, error = result
            if error:
                return HTTPException(status_code=500, detail=f"Failed to fetch stock info: {error}")
            return {"status": "success", "data": return_data}
        
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while calling fetch_stock_info: {e}")
 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)