from openai import OpenAI

class ServiceRegistry:
    """Centralized place to manage long-lived external service clients (e.g., OpenAI)."""
    _services = {}

    @classmethod
    def get_openai(cls, api_key: str):
        if not api_key:
            raise ValueError("Missing API key for OpenAI")
        if "openai" not in cls._services:
            cls._services["openai"] = OpenAI(api_key=api_key)
        return cls._services["openai"]
