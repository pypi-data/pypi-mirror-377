from typing import Dict, Any, Tuple

from oak.services.data_fetcher.api_service.api_service import ApiService

api_service = ApiService()

def fetch_stock_news(symbol: str, limit: int = 10) -> Tuple[Dict[str, Any], str | None]:
    """
    Fetches recent news articles for a stock symbol from an external API.
    """
    args = {
        'symbol': symbol,
        'limit': limit,
    }
    return api_service.invoke_api(function_name='fetch_stock_news', args=args)