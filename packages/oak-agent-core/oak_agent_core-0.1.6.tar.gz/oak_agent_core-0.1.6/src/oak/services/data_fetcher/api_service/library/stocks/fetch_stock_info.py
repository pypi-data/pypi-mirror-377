from typing import Dict, Any, Tuple

from oak.services.data_fetcher.api_service.api_service import ApiService

api_service = ApiService()

def fetch_stock_info(symbol: str) -> Tuple[Dict[str, Any], str | None]:
    """
    Fetches comprehensive company information for a stock symbol.
    """
    args = {
        'symbol': symbol,
    }
    return api_service.invoke_api(function_name='fetch_stock_info', args=args)