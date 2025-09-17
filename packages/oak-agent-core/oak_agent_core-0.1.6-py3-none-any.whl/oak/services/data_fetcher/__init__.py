from functools import lru_cache
from typing import List, Callable
from oak.services.data_fetcher.prompt_service import PromptService
from .database_service import get_db_connection, get_db_engine, get_db_session
from .api_service import api_service
from .dependencies import prompt_service_factory
from .exceptions import DatabaseConnectionError

# New wrapper function to simplify PromptService instantiation
@lru_cache(maxsize=1)
def get_prompt_service_instance(shared_templates: str, library_templates: str) -> PromptService:
    """
    A cached wrapper that instantiates and returns the singleton PromptService instance.
    This simplifies the call site for other modules.
    """
    # Call the factory to get the dependency provider function.
    get_service_provider = prompt_service_factory(
        shared_templates=shared_templates, 
        library_templates=library_templates
    )
    # Call the provider function to get the actual PromptService instance.
    return get_service_provider()