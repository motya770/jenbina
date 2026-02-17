"""Background user research for the Deep Emotional Mirror feature.

Searches the web for public information about users and generates
a psychological dossier that Jenbina uses to inform her conversations.
"""

import json
import os
from typing import Dict, Any, List

from langchain.schema import HumanMessage, SystemMessage

# Generic email domains where the domain itself is not informative
_GENERIC_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                    "icloud.com", "protonmail.com", "mail.com", "aol.com"}


def build_search_query(display_name: str, email: str) -> str:
    """Build a web search query from user info."""
    parts = [display_name]
    if email:
        domain = email.split("@")[-1].lower() if "@" in email else ""
        if domain and domain not in _GENERIC_DOMAINS:
            parts.append(domain)
    return " ".join(parts)


def search_web(query: str) -> Dict[str, Any]:
    """Call the SerpAPI/Serper web search API.

    Returns raw JSON response from the search API.
    Requires SERPER_API_KEY env var.
    """
    import requests

    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise ValueError("SERPER_API_KEY environment variable is not set")

    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query, "num": 10},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def parse_research_results(raw_results: Dict[str, Any]) -> List[str]:
    """Extract useful text snippets from search results."""
    snippets = []
    for result in raw_results.get("organic", []):
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        if title or snippet:
            snippets.append(f"{title}: {snippet}".strip(": "))
    return snippets


_DOSSIER_PROMPT = """\
You are analyzing publicly available information about a person to build \
a psychological profile. This will be used by Jenbina (an AGI simulation) \
to have more meaningful conversations with this person.

Person's name: {name}

Public information found:
{snippets}

Based on this information, generate a JSON object with these fields:
- "personality_traits": list of 2-4 likely personality traits
- "values": list of 2-3 core values
- "communication_style": one sentence describing likely communication style
- "likely_motivations": list of 1-3 things that likely drive this person
- "potential_insecurities": list of 0-2 possible insecurities (be respectful)
- "professional_context": one sentence about their professional life
- "interests": list of 2-5 interests/topics they care about

Be insightful but not invasive. Focus on what would help someone have a \
genuinely meaningful conversation with this person. If information is sparse, \
make reasonable inferences but note lower confidence.

Return ONLY valid JSON."""


def generate_user_dossier(llm, name: str, snippets: List[str]) -> Dict[str, Any]:
    """Use LLM to generate a psychological profile from research snippets."""
    if not snippets:
        return {}

    prompt = _DOSSIER_PROMPT.format(
        name=name,
        snippets="\n".join(f"- {s}" for s in snippets),
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        # Strip markdown code fences if present
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except (json.JSONDecodeError, IndexError):
        return {}


def research_user(llm, display_name: str, email: str) -> Dict[str, Any]:
    """Full pipeline: search web -> parse -> generate dossier.

    Returns a dossier dict, or empty dict on failure.
    """
    try:
        query = build_search_query(display_name, email)
        raw_results = search_web(query)
        snippets = parse_research_results(raw_results)
        if not snippets:
            return {}
        return generate_user_dossier(llm, display_name, snippets)
    except Exception as e:
        print(f"User research failed: {e}")
        return {}
