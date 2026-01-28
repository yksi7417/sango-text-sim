"""
Officer Dialogue System - Personality-based dialogue generation.

Officers speak differently based on their traits:
- Brave: direct, bold, action-oriented
- Scholar: philosophical, measured, analytical
- Charismatic: persuasive, inspiring, warm
- Merchant: pragmatic, calculating, wealth-focused
- Engineer: technical, methodical, detail-oriented
"""
import random
from typing import Optional
from ..models import Officer
from i18n import i18n


# Map traits to dialogue style
TRAIT_STYLE_MAP = {
    "Brave": "brave",
    "Scholar": "scholar",
    "Charismatic": "charismatic",
    "Merchant": "merchant",
    "Engineer": "engineer",
    "Strict": "strict",
    "Benevolent": "benevolent",
}

CONTEXTS = ["greeting", "advice", "battle_start", "victory", "defeat"]


def _get_style(officer: Officer) -> str:
    """Determine dialogue style from officer traits."""
    for trait in officer.traits:
        if trait in TRAIT_STYLE_MAP:
            return TRAIT_STYLE_MAP[trait]
    # Fallback based on highest stat
    stats = {
        "brave": officer.leadership,
        "scholar": officer.intelligence,
        "charismatic": officer.charisma,
        "merchant": officer.politics,
    }
    return max(stats, key=stats.get)


def generate_dialogue(officer: Officer, context: str) -> str:
    """
    Generate dialogue for an officer in a given context.

    Args:
        officer: The speaking officer
        context: One of: greeting, advice, battle_start, victory, defeat

    Returns:
        Dialogue string
    """
    style = _get_style(officer)
    key = f"dialogue.{style}.{context}"
    text = i18n.t(key, name=officer.name, default="")

    if not text:
        # Fallback to default style
        key = f"dialogue.default.{context}"
        text = i18n.t(key, name=officer.name, default=f"{officer.name}: ...")

    return text
