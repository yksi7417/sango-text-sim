"""
Turn Report Generator

This module generates narrative turn summaries with:
- Seasonal flavor text
- Categorized events (Economy, Military, Diplomatic, Officer)
- Narrative formatting for immersion
"""

from typing import List, Dict, Any
from ..models import Season, EventCategory, TurnEvent, GameState
from i18n import i18n
from .components import render_box, render_separator


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


def generate_turn_preview(game_state: GameState) -> str:
    """
    Generate a preview of upcoming events for the next turn.

    Shows:
    - Construction completions
    - Research completions
    - Loyalty warnings
    - Enemy threats (adjacent enemy cities with high troops)
    - Low resource warnings

    Args:
        game_state: Current game state

    Returns:
        Formatted preview string
    """
    lines = []
    faction = game_state.factions.get(game_state.player_faction)
    if not faction:
        return ""

    previews: List[str] = []

    # Construction completions next turn
    for city_name, cq in game_state.construction_queue.items():
        remaining = cq["turns_needed"] - cq["progress"]
        if remaining <= 1:
            bid = cq["building_id"]
            name = i18n.t(f"buildings.{bid}", default=bid)
            previews.append(i18n.t("preview.construction_done", building=name, city=city_name,
                                    default=f"{name} in {city_name} will be completed"))

    # Research completions next turn
    rp = game_state.research_progress.get(game_state.player_faction)
    if rp:
        remaining = rp["turns_needed"] - rp["progress"]
        if remaining <= 1:
            tid = rp["tech_id"]
            name = i18n.t(f"tech.{tid}", default=tid)
            previews.append(i18n.t("preview.research_done", tech=name,
                                    default=f"Research on {name} will be completed"))

    # Loyalty warnings
    for off_name in faction.officers:
        off = game_state.officers.get(off_name)
        if off and off.loyalty < 40:
            display_name = off.name
            previews.append(i18n.t("preview.loyalty_warning", officer=display_name,
                                    loyalty=off.loyalty,
                                    default=f"{display_name} loyalty dangerously low ({off.loyalty})"))

    # Enemy threats
    for city_name in faction.cities:
        adjacents = game_state.adj.get(city_name, [])
        for adj_name in adjacents:
            adj_city = game_state.cities.get(adj_name)
            if adj_city and adj_city.owner != game_state.player_faction:
                if adj_city.troops >= 200:
                    previews.append(i18n.t("preview.enemy_threat", city=city_name,
                                            enemy=adj_city.owner, troops=adj_city.troops,
                                            default=f"Enemy threat near {city_name} from {adj_city.owner} ({adj_city.troops} troops)"))

    # Low resource warnings
    for city_name in faction.cities:
        city = game_state.cities.get(city_name)
        if city:
            if city.food < 100:
                previews.append(i18n.t("preview.low_food", city=city_name,
                                        default=f"{city_name} food critically low ({city.food})"))
            if city.gold < 50:
                previews.append(i18n.t("preview.low_gold", city=city_name,
                                        default=f"{city_name} treasury nearly empty ({city.gold})"))

    if not previews:
        return ""

    title = i18n.t("preview.title", default="Next Turn Preview")
    lines.append(render_separator(50, "heavy"))
    lines.append(f"  {title}")
    lines.append(render_separator(50, "light"))
    for p in previews:
        lines.append(f"  > {p}")
    lines.append(render_separator(50, "heavy"))

    return "\n".join(lines)
