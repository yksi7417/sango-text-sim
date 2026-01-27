"""
ASCII Officer Profile View Renderer

This module renders detailed officer profiles with:
- ASCII portrait placeholder (character-based)
- Progress bars for all stats (leadership, intelligence, politics, charisma)
- Traits display with descriptions
- Condition section (energy, loyalty)
- Relationships section (placeholder for Phase 3)
- Personality-based quotes
"""

from typing import Optional
from ..models import Officer
from i18n import i18n
from .components import render_progress_bar


def get_portrait_char(name: str) -> str:
    """
    Get a portrait placeholder character based on officer name.

    Args:
        name: Officer's name

    Returns:
        Single character representing the officer
    """
    if not name:
        return "?"
    # Use first character of name
    return name[0].upper()


def get_personality_quote(officer: Officer) -> str:
    """
    Get a personality-based quote for the officer.

    Args:
        officer: Officer object

    Returns:
        Quote string based on officer's traits
    """
    # Check for specific traits
    if "Brave" in officer.traits:
        return i18n.t("officer_view.quote.brave",
                     default="Victory or death!")
    elif "Scholar" in officer.traits:
        return i18n.t("officer_view.quote.scholar",
                     default="Knowledge is the path to victory.")
    elif "Charismatic" in officer.traits:
        return i18n.t("officer_view.quote.charismatic",
                     default="Together, we shall achieve greatness.")
    elif "Merchant" in officer.traits:
        return i18n.t("officer_view.quote.merchant",
                     default="Prosperity brings power.")
    elif "Loyal" in officer.traits:
        return i18n.t("officer_view.quote.loyal",
                     default="My loyalty is unwavering.")
    elif "Ambitious" in officer.traits:
        return i18n.t("officer_view.quote.ambitious",
                     default="The realm shall be mine.")
    elif "Brilliant" in officer.traits:
        return i18n.t("officer_view.quote.brilliant",
                     default="Strategy wins wars, not strength alone.")
    else:
        # Default quote
        return i18n.t("officer_view.quote.default",
                     default="I serve with honor.")


def render_ascii_portrait(officer: Officer) -> str:
    """
    Render an ASCII portrait box for the officer.

    Args:
        officer: Officer object

    Returns:
        Multi-line ASCII art portrait
    """
    char = get_portrait_char(officer.name)

    portrait = f"""
    ┌─────────┐
    │         │
    │    {char}    │
    │         │
    └─────────┘"""

    return portrait


def render_officer_profile(officer: Officer) -> str:
    """
    Render detailed officer profile with all information.

    Args:
        officer: Officer object to render

    Returns:
        Multi-line string with formatted officer profile
    """
    lines = []

    # Header with officer name and faction
    header = i18n.t("officer_view.header",
                   officer=officer.name,
                   faction=officer.faction,
                   default=f"═══ {officer.name} [{officer.faction}] ═══")
    lines.append("")
    lines.append(header)
    lines.append("")

    # ASCII portrait
    portrait = render_ascii_portrait(officer)
    lines.append(portrait)
    lines.append("")

    # Quote
    quote = get_personality_quote(officer)
    lines.append(f'    "{quote}"')
    lines.append("")

    # Stats section with progress bars
    stats_title = i18n.t("officer_view.stats_title", default="Statistics:")
    lines.append(stats_title)

    leadership_label = i18n.t("officer_view.leadership", default="Leadership")
    intelligence_label = i18n.t("officer_view.intelligence", default="Intelligence")
    politics_label = i18n.t("officer_view.politics", default="Politics")
    charisma_label = i18n.t("officer_view.charisma", default="Charisma")

    leadership_bar = render_progress_bar(officer.leadership)
    intelligence_bar = render_progress_bar(officer.intelligence)
    politics_bar = render_progress_bar(officer.politics)
    charisma_bar = render_progress_bar(officer.charisma)

    lines.append(f"  {leadership_label:13} [{leadership_bar}] {officer.leadership:3}/100")
    lines.append(f"  {intelligence_label:13} [{intelligence_bar}] {officer.intelligence:3}/100")
    lines.append(f"  {politics_label:13} [{politics_bar}] {officer.politics:3}/100")
    lines.append(f"  {charisma_label:13} [{charisma_bar}] {officer.charisma:3}/100")
    lines.append("")

    # Condition section
    condition_title = i18n.t("officer_view.condition_title", default="Condition:")
    lines.append(condition_title)

    energy_label = i18n.t("officer_view.energy", default="Energy")
    loyalty_label = i18n.t("officer_view.loyalty", default="Loyalty")

    energy_bar = render_progress_bar(officer.energy)
    loyalty_bar = render_progress_bar(officer.loyalty)

    lines.append(f"  {energy_label:13} [{energy_bar}] {officer.energy:3}/100")
    lines.append(f"  {loyalty_label:13} [{loyalty_bar}] {officer.loyalty:3}/100")
    lines.append("")

    # Traits section
    traits_title = i18n.t("officer_view.traits_title", default="Traits:")
    lines.append(traits_title)

    if officer.traits:
        for trait in officer.traits:
            # Get trait description from i18n
            trait_desc = i18n.t(f"traits.{trait.lower()}", default=trait)
            lines.append(f"  • {trait_desc}")
    else:
        no_traits = i18n.t("officer_view.no_traits", default="  (No special traits)")
        lines.append(no_traits)

    lines.append("")

    # Relationships section (placeholder for Phase 3)
    relationships_title = i18n.t("officer_view.relationships_title", default="Relationships:")
    lines.append(relationships_title)

    relationships_placeholder = i18n.t("officer_view.relationships_placeholder",
                                       default="  (Relationship system coming in Phase 3)")
    lines.append(relationships_placeholder)
    lines.append("")

    # Current location and status
    if officer.city:
        location_label = i18n.t("officer_view.location", default="Location")
        lines.append(f"{location_label}: {officer.city}")

        if officer.busy and officer.task:
            task_label = i18n.t(f"tasks.{officer.task}", default=officer.task)
            status = i18n.t("officer_view.status_busy",
                          task=task_label,
                          default=f"Currently working: {task_label}")
            lines.append(status)
        else:
            status = i18n.t("officer_view.status_idle", default="Currently idle")
            lines.append(status)
        lines.append("")

    return "\n".join(lines)
