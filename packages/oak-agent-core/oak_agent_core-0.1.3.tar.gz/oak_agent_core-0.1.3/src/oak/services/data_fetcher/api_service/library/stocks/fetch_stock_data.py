from typing import Dict, Any, Tuple

from oak.services.data_fetcher.api_service.api_service import ApiService

api_service = ApiService()

def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> Tuple[Dict[str, Any], str | None]:
    """
    Fetches historical stock price data for a specific date range.
    """
    args = {
        'symbol': symbol,
        'start_date': start_date,
        'end_date': end_date,
    }
    return api_service.invoke_api(function_name='fetch_stock_data', args=args)