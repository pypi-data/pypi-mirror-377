from typing import Dict, Any, Tuple

from oak.services.data_fetcher.api_service.api_service import ApiService

api_service = ApiService()

def fetch_stock_data_by_period(symbol: str, period: str) -> Tuple[Dict[str, Any], str | None]:
    """
    Fetches historical stock price data for a predefined period (e.g., '1y', '5y').
    """
    args = {
        'symbol': symbol,
        'period': period,
    }
    return api_service.invoke_api(function_name='fetch_stock_data_by_period', args=args)