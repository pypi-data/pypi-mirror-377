import logging

logger = logging.getLogger("pipeline")

def example_duck(user_input: str, duck) -> str:
    """
    Example duck handler.
    
    Args:
        user_input (str): The text passed into this duck.
        duck (Node): The Node object, which may contain:
            - id (str): Unique identifier of the duck.
            - type (str): Node type ("ai", "logic", etc.).
            - system_message (str): Optional system message from config.
            - model (str): AI model name (from config or global default).
            - knowledge_base (str): Optional path to a KB file.
            - api_key (str): API key resolved from settings/.env.
    
    Returns:
        str: The processed output.
    """
    logger.debug(f"{duck.id} received input: {user_input}")

    # Example: using duck config values
    if duck.system_message:
        logger.debug(f"{duck.id} system_message: {duck.system_message}")
    if duck.model:
        logger.debug(f"{duck.id} using model: {duck.model}")

    # Your custom logic goes here
    result = f"[{duck.id}] Processed input: {user_input}"

    return result

NODES = {
    "example_duck": example_duck
}
