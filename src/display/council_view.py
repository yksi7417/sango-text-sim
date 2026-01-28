"""
Council Display Renderer

Renders council meeting view with agenda items, advisor presentations,
and action choices.
"""
from typing import List
from ..systems.council import Council, AgendaItem, AgendaCategory
from .components import render_box, render_separator
from i18n import i18n


CATEGORY_ICONS = {
    AgendaCategory.ECONOMIC: "$",
    AgendaCategory.MILITARY: "!",
    AgendaCategory.DIPLOMATIC: "&",
    AgendaCategory.PERSONNEL: "@",
}


def render_council(council: Council) -> str:
    """
    Render a council meeting display.

    Args:
        council: Council object with agenda items

    Returns:
        Formatted string for display
    """
    lines = []
    title = i18n.t("council.title")
    lines.append(render_separator(60, "double"))
    lines.append(f"  {title} - {council.year}-{council.month:02d}")
    lines.append(render_separator(60, "double"))
    lines.append("")

    if not council.agenda:
        lines.append(f"  {i18n.t('council.no_agenda')}")
        lines.append("")
        return "\n".join(lines)

    for idx, item in enumerate(council.agenda, 1):
        icon = CATEGORY_ICONS.get(item.category, "?")
        lines.append(f"  [{icon}] {idx}. {item.title}")
        lines.append(f"      {i18n.t('council.presenter_label', default='Presenter')}: {item.presenter}")
        lines.append(f"      {item.recommendation}")
        lines.append("")

    lines.append(render_separator(60, "single"))
    return "\n".join(lines)


def render_agenda_item(item: AgendaItem, index: int) -> str:
    """
    Render a single agenda item in detail.

    Args:
        item: AgendaItem to render
        index: Item number (1-based)

    Returns:
        Formatted string
    """
    icon = CATEGORY_ICONS.get(item.category, "?")
    lines = [
        render_box(
            f"{item.title}\n\n"
            f"{item.presenter}: {item.recommendation}",
            title=f"[{icon}] Item {index}"
        )
    ]
    return "\n".join(lines)
