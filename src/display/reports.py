"""
Turn Report Generator

This module generates narrative turn summaries with:
- Seasonal flavor text
- Categorized events (Economy, Military, Diplomatic, Officer)
- Narrative formatting for immersion
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any
from ..models import Season
from i18n import i18n
from .components import render_box, render_separator


class EventCategory(Enum):
    """Categories for turn events."""
    ECONOMY = "economy"
    MILITARY = "military"
    DIPLOMATIC = "diplomatic"
    OFFICER = "officer"


@dataclass
class TurnEvent:
    """
    Represents a single event that occurred during a turn.

    Attributes:
        category: Event category (Economy, Military, etc.)
        message: Human-readable description of the event
        data: Additional structured data about the event
    """
    category: EventCategory
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


def get_seasonal_flavor(season: Season) -> str:
    """
    Get narrative flavor text for the season.

    Args:
        season: Current season

    Returns:
        Seasonal flavor text string
    """
    season_key = season.value  # 'spring', 'summer', 'autumn', 'winter'
    return i18n.t(f"seasons.{season_key}_desc")


def categorize_events(events: List[TurnEvent]) -> Dict[EventCategory, List[TurnEvent]]:
    """
    Group events by category.

    Args:
        events: List of all turn events

    Returns:
        Dictionary mapping categories to their events
    """
    categorized: Dict[EventCategory, List[TurnEvent]] = {
        EventCategory.ECONOMY: [],
        EventCategory.MILITARY: [],
        EventCategory.DIPLOMATIC: [],
        EventCategory.OFFICER: [],
    }

    for event in events:
        if event.category in categorized:
            categorized[event.category].append(event)

    return categorized


def format_category_section(category: EventCategory, events: List[TurnEvent]) -> str:
    """
    Format a section for a specific event category.

    Args:
        category: Event category
        events: Events in this category

    Returns:
        Formatted section string
    """
    if not events:
        return ""

    # Get localized category name
    category_name = i18n.t(f"reports.category_{category.value}")

    lines = [f"\n{category_name}:", render_separator(50, "light")]

    for event in events:
        lines.append(f"  • {event.message}")

    return "\n".join(lines)


def generate_turn_report(events: List[TurnEvent], season: Season) -> str:
    """
    Generate a narrative turn report with seasonal flavor and categorized events.

    Args:
        events: List of events that occurred during the turn
        season: Current season for flavor text

    Returns:
        Formatted turn report string
    """
    lines = []

    # Seasonal flavor text
    flavor = get_seasonal_flavor(season)
    lines.append(render_box(flavor, i18n.t("reports.season_title"), 60))
    lines.append("")

    # Categorize and format events
    categorized = categorize_events(events)

    # Order: Economy -> Military -> Diplomatic -> Officer
    for category in [EventCategory.ECONOMY, EventCategory.MILITARY,
                     EventCategory.DIPLOMATIC, EventCategory.OFFICER]:
        section = format_category_section(category, categorized[category])
        if section:
            lines.append(section)

    # If no events occurred
    if not events:
        lines.append(render_separator(50, "light"))
        lines.append(i18n.t("reports.no_events"))

    lines.append("")

    return "\n".join(lines)
