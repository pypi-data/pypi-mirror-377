from typing import Dict, Any, Tuple
from datetime import datetime

from oak.services.data_fetcher.api_service.api_service import ApiService

api_service = ApiService()

def fetch_stock_daily_summary(symbol: str, date: datetime) -> Tuple[Dict[str, Any], str | None]:
    """
    Fetches a daily summary of a stock's trading activity.
    """
    args = {
        'symbol': symbol,
        'date': date,
    }
    return api_service.invoke_api(function_name='fetch_stock_daily_summary', args=args)