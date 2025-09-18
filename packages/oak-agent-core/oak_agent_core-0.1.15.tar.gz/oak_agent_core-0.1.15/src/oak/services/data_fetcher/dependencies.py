from functools import lru_cache
from typing import List, Callable
from oak.services.data_fetcher.prompt_service import PromptService

# Define a factory function that takes the paths as arguments
def prompt_service_factory(shared_templates: str, library_templates: str) -> Callable[[], PromptService]:
    @lru_cache
    def get_prompt_service() -> PromptService:
        return PromptService(template_dirs=[shared_templates, library_templates])
    return get_prompt_service