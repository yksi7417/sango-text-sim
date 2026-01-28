"""
Event Display Renderer

Renders random events with narrative box, choices, and outcomes.
"""
from ..systems.events import GameEvent
from .components import render_box, render_separator
from i18n import i18n


def render_event(event: GameEvent, city_name: str) -> str:
    """
    Render a random event display.

    Args:
        event: The triggered event
        city_name: City where event occurs

    Returns:
        Formatted string for display
    """
    lines = []

    title = i18n.t(event.title_key, default=event.id)
    desc = i18n.t(event.description_key, default="An event has occurred.")

    # Event type indicator
    if event.event_type == "positive":
        indicator = "[+]"
    elif event.event_type == "negative":
        indicator = "[!]"
    else:
        indicator = "[~]"

    lines.append(render_separator(60, "double"))
    lines.append(f"  {indicator} {title} - {city_name}")
    lines.append(render_separator(60, "single"))
    lines.append(f"  {desc}")
    lines.append("")

    # Choices
    for idx, choice in enumerate(event.choices, 1):
        label = i18n.t(choice.label_key, default=f"Choice {idx}")
        lines.append(f"  {idx}. {label}")

    lines.append("")
    lines.append(render_separator(60, "single"))

    return "\n".join(lines)


def render_event_outcome(effects: dict, city_name: str) -> str:
    """
    Render the outcome of an event choice.

    Args:
        effects: Applied effects dict
        city_name: City affected

    Returns:
        Formatted outcome string
    """
    lines = [f"  Effects on {city_name}:"]
    applied = effects.get("applied", {})
    for stat, value in applied.items():
        sign = "+" if value > 0 else ""
        lines.append(f"    {stat}: {sign}{value}")

    return "\n".join(lines)
