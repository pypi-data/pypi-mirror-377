from typing import Dict, Any, Tuple

from oak.services.data_fetcher.api_service.api_service import ApiService

api_service = ApiService()

def fetch_stock_financials(symbol: str, period: str = "yearly") -> Tuple[Dict[str, Any], str | None]:
    """
    Fetches financial statements (income, balance sheet, cash flow) for a stock symbol.
    """
    args = {
        'symbol': symbol,
        'period': period,
    }
    return api_service.invoke_api(function_name='fetch_stock_financials', args=args)