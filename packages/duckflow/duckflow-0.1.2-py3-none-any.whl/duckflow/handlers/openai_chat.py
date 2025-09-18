import logging
from duckflow.core.registry import ServiceRegistry

logger = logging.getLogger("duckflow")

def openai_chat_node(user_input: str, duck) -> str:
    """OpenAI Chat duck execution with optional knowledge base."""
    if not duck.api_key:
        logger.error(f"No API key available for AI duck {duck.id}")
        return "ERROR: Missing API key"

    try:
        client = ServiceRegistry.get_openai(duck.api_key)
    except Exception as e:
        logger.error(f"Could not initialize OpenAI client for duck {duck.id}: {e}")
        return "ERROR: Failed to initialize OpenAI client"

    messages = []
    if duck.system_message:
        messages.append({"role": "system", "content": duck.system_message})

    if duck.knowledge_base:
        try:
            with open(duck.knowledge_base) as f:
                kb_text = f.read()
            messages.append({"role": "system", "content": f"Knowledge base:\n{kb_text}"})
        except Exception as e:
            logger.warning(f"Knowledge base not loaded for {duck.id}: {e}")

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=duck.model,
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API call failed for duck {duck.id}: {e}")
        return "ERROR: OpenAI call failed"

NODES = {
    "openai_chat": openai_chat_node
}
