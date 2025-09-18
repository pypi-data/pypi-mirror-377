import os
import requests
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class ApiService:
    """
    A singleton service for making API calls to an external reference lookup endpoint.
    It reads the base URL from an environment variable for dynamic configuration.
    """
    # A class-level attribute to hold the single instance
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Controls the creation of the singleton instance.
        """
        if not cls._instance:
            cls._instance = super(ApiService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the service. This will only run once.
        """
        if not self._is_initialized:
            self.base_url = os.getenv('REFERENCE_API_URL')
            if not self.base_url:
                raise ValueError("Environment variable 'REFERENCE_API_URL' is not set.")
            # Ensure the URL ends with a slash for consistent path joining
            if not self.base_url.endswith('/'):
                self.base_url += '/'
            logger.info(f"ApiService initialized with base URL: {self.base_url}")
            self._is_initialized = True

    def invoke_api(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invokes a specific function on the external API.

        Args:
            function_name (str): The name of the function to call (e.g., 'fetch_stock_info').
            args (Dict[str, Any]): A dictionary of arguments for the function.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: For network-related errors.
            ValueError: For non-200 HTTP status codes or invalid JSON responses.
        """
        # Construct the full URL for the /call-function endpoint
        url = f"{self.base_url}call-function"
        
        # The JSON payload for the POST request
        payload = {
            "function_name": function_name,
            "args": args
        }

        logger.info(f"Invoking API endpoint {url} for function '{function_name}'")

        try:
            # Use the 'json' parameter of requests.post() which automatically sets
            # the 'Content-Type' header to 'application/json' and serializes the data.
            response = requests.post(url, json=payload, timeout=30)
            
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            logger.info(f"API call to '{function_name}' successful.")
            
            # Parse the JSON response
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error for {function_name}: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"API call failed with HTTP status {e.response.status_code}: {e.response.text}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Network or timeout error for {function_name}: {e}")
            raise ConnectionError(f"Failed to connect to the API endpoint: {e}") from e
        except ValueError as e:
            logger.error(f"Failed to decode JSON response for {function_name}: {e}")
            raise ValueError(f"Invalid JSON response from API: {e}") from e