import requests
import logging

logger = logging.getLogger("duckflow")

def duckduckgo_research_node(user_input: str, duck) -> str:
    """
    Fetch information from DuckDuckGo Instant Answer API.
    Returns abstract text or related topics (flattened).
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": user_input, "format": "json", "no_redirect": 1}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data.get("AbstractText"):
            return f"Search result: {data['AbstractText']}"

        related_texts = []

        def extract_text(topics):
            for t in topics:
                if "Text" in t:
                    related_texts.append(t["Text"])
                if "Topics" in t:  # nested
                    extract_text(t["Topics"])

        if "RelatedTopics" in data:
            extract_text(data["RelatedTopics"])

        if related_texts:
            return "Related info: " + "; ".join(related_texts[:5])

        return "No relevant web info found."
    except Exception as e:
        logger.warning(f"DuckDuckGo research failed: {e}")
        return "No web research available."

NODES = {
    "duckduckgo_research": duckduckgo_research_node
}
