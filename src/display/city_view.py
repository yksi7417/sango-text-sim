"""
ASCII City Detail View Renderer

This module renders detailed city views with:
- ASCII art city icons based on walls level
- Progress bars for development (agriculture, commerce, tech, walls)
- Resource display (gold, food, troops)
- Stationed officers list with current tasks
- Adjacent cities display
"""

from typing import List
from ..models import City, Officer
from ..world import ADJACENCY_MAP
from i18n import i18n


def render_progress_bar(value: int, max_value: int = 100, width: int = 10) -> str:
    """
    Render a progress bar using block characters.

    Args:
        value: Current value (0-max_value)
        max_value: Maximum value for the bar
        width: Width of the bar in characters

    Returns:
        Progress bar string like "████░░░░░░"
    """
    filled = int((value / max_value) * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def get_city_icon(walls: int) -> str:
    """
    Get ASCII art city icon based on walls level.

    Args:
        walls: Walls development level (0-100)

    Returns:
        Multi-line ASCII art string representing the city
    """
    if walls >= 80:
        # Strong fortress
        return """
    ╔═══╗
    ║ █ ║
    ╚═══╝"""
    elif walls >= 50:
        # Medium fortification
        return """
    ┌───┐
    │ ▓ │
    └───┘"""
    else:
        # Weak walls
        return """
    ┌───┐
    │ ░ │
    └───┘"""


def render_city_detail(city: City, officers: List[Officer]) -> str:
    """
    Render detailed city view with all information.

    Args:
        city: City object to render
        officers: List of officers stationed in this city

    Returns:
        Multi-line string with formatted city details
    """
    lines = []

    # Header with city name and owner
    header = i18n.t("city_view.header", city=city.name, owner=city.owner,
                   default=f"═══ {city.name} [{city.owner}] ═══")
    lines.append("")
    lines.append(header)
    lines.append("")

    # ASCII city icon
    icon = get_city_icon(city.walls)
    lines.append(icon)
    lines.append("")

    # Resources section
    resources_title = i18n.t("city_view.resources_title", default="Resources:")
    lines.append(resources_title)

    gold_label = i18n.t("city_view.gold", default="Gold")
    food_label = i18n.t("city_view.food", default="Food")
    troops_label = i18n.t("city_view.troops", default="Troops")
    defense_label = i18n.t("city_view.defense", default="Defense")
    morale_label = i18n.t("city_view.morale", default="Morale")

    lines.append(f"  {gold_label}: {city.gold:>6}    {food_label}: {city.food:>6}    {troops_label}: {city.troops:>6}")
    lines.append(f"  {defense_label}: {city.defense:>6}    {morale_label}: {city.morale:>6}")
    lines.append("")

    # Development section with progress bars
    development_title = i18n.t("city_view.development_title", default="Development:")
    lines.append(development_title)

    agri_label = i18n.t("city_view.agriculture", default="Agriculture")
    commerce_label = i18n.t("city_view.commerce", default="Commerce")
    tech_label = i18n.t("city_view.technology", default="Technology")
    walls_label = i18n.t("city_view.walls", default="Walls")

    agri_bar = render_progress_bar(city.agri)
    commerce_bar = render_progress_bar(city.commerce)
    tech_bar = render_progress_bar(city.tech)
    walls_bar = render_progress_bar(city.walls)

    lines.append(f"  {agri_label:12} [{agri_bar}] {city.agri:3}/100")
    lines.append(f"  {commerce_label:12} [{commerce_bar}] {city.commerce:3}/100")
    lines.append(f"  {tech_label:12} [{tech_bar}] {city.tech:3}/100")
    lines.append(f"  {walls_label:12} [{walls_bar}] {city.walls:3}/100")
    lines.append("")

    # Officers section
    officers_title = i18n.t("city_view.officers_title", default="Stationed Officers:")
    lines.append(officers_title)

    if officers:
        for officer in officers:
            # Get officer display name (could be translated)
            officer_name = i18n.t(f"officers.{officer.name}", default=officer.name)

            if officer.busy and officer.task:
                task_label = i18n.t(f"tasks.{officer.task}", default=officer.task)
                status = i18n.t("city_view.officer_busy", task=task_label,
                               default=f"(Working: {task_label})")
                lines.append(f"  • {officer_name} {status}")
            else:
                idle_label = i18n.t("city_view.officer_idle", default="(Idle)")
                lines.append(f"  • {officer_name} {idle_label}")
    else:
        no_officers = i18n.t("city_view.no_officers", default="  (No officers stationed)")
        lines.append(no_officers)

    lines.append("")

    # Adjacent cities section
    adjacent_title = i18n.t("city_view.adjacent_title", default="Adjacent Cities:")
    lines.append(adjacent_title)

    if city.name in ADJACENCY_MAP:
        adjacent_cities = ADJACENCY_MAP[city.name]
        if adjacent_cities:
            for adj_city in adjacent_cities:
                lines.append(f"  → {adj_city}")
        else:
            no_adjacent = i18n.t("city_view.no_adjacent", default="  (Isolated)")
            lines.append(no_adjacent)
    else:
        no_adjacent = i18n.t("city_view.no_adjacent", default="  (Isolated)")
        lines.append(no_adjacent)

    lines.append("")

    return "\n".join(lines)
