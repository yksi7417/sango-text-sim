"""
Battle View Renderer

This module provides rendering functions for tactical battle maps,
displaying terrain, unit positions, siege progress, weather, and combat state.
"""

from typing import Optional
from i18n import i18n
from src.models import BattleState, TerrainType
from src.display.components import render_box, render_progress_bar, get_faction_color, FACTION_COLORS, COLOR_RESET


def _get_terrain_icon(terrain: TerrainType) -> str:
    """
    Get ASCII icon representing terrain type.

    Args:
        terrain: The terrain type

    Returns:
        ASCII character(s) representing the terrain
    """
    terrain_icons = {
        TerrainType.PLAINS: "═",
        TerrainType.MOUNTAIN: "▲",
        TerrainType.FOREST: "♠",
        TerrainType.COASTAL: "≈",
        TerrainType.RIVER: "~"
    }
    return terrain_icons.get(terrain, "═")


def _format_number(num: int) -> str:
    """
    Format a number with comma separators for readability.

    Args:
        num: Number to format

    Returns:
        Formatted string (e.g., "1000" -> "1,000")
    """
    return f"{num:,}"


def _render_unit_box(commander: str, troops: int, faction: str, morale: int, is_attacker: bool = True) -> str:
    """
    Render a unit information box.

    Args:
        commander: Name of the commanding officer
        troops: Number of troops
        faction: Faction name
        morale: Current morale (0-100)
        is_attacker: Whether this is the attacking unit

    Returns:
        Formatted unit box string
    """
    role = i18n.t("battle.attacker") if is_attacker else i18n.t("battle.defender")
    faction_color = get_faction_color(faction)

    lines = []
    lines.append(f"╔{'═' * 28}╗")
    lines.append(f"║ {role:<26} ║")
    lines.append(f"║ {faction_color.format(faction):<26} ║")
    lines.append(f"║ {'─' * 28} ║")
    lines.append(f"║ {i18n.t('battle.commander')}: {commander:<14} ║")
    lines.append(f"║ {i18n.t('battle.troops')}: {_format_number(troops):<18} ║")

    # Morale bar
    morale_bar = render_progress_bar(morale, 100, 10)
    lines.append(f"║ {i18n.t('battle.morale')}: {morale_bar} {morale:>3}% ║")
    lines.append(f"╚{'═' * 28}╝")

    return "\n".join(lines)


def _render_terrain_zone(terrain: TerrainType, width: int = 40) -> str:
    """
    Render the terrain zone display.

    Args:
        terrain: Terrain type of the battlefield
        width: Width of the terrain display

    Returns:
        Formatted terrain zone string
    """
    icon = _get_terrain_icon(terrain)
    terrain_name = i18n.t(f"terrain.{terrain.value}")

    # Create a visual representation of the terrain
    terrain_line = icon * width

    lines = []
    lines.append(f"┌{'─' * width}┐")
    lines.append(f"│{terrain_line}│")
    lines.append(f"│{terrain_name.center(width)}│")
    lines.append(f"│{terrain_line}│")
    lines.append(f"└{'─' * width}┘")

    return "\n".join(lines)


def _render_battle_status(battle: BattleState) -> str:
    """
    Render battle status information (supply, weather, siege progress).

    Args:
        battle: Current battle state

    Returns:
        Formatted battle status string
    """
    lines = []
    lines.append(f"╔{'═' * 38}╗")
    lines.append(f"║ {i18n.t('battle.status').center(36)} ║")
    lines.append(f"║ {'─' * 38} ║")

    # Round number
    lines.append(f"║ {i18n.t('battle.round')}: {battle.round:<30} ║")

    # Supply days
    supply_status = i18n.t("battle.supply_days", days=battle.supply_days)
    lines.append(f"║ {supply_status:<36} ║")

    # Weather (if present)
    if battle.weather:
        weather_status = i18n.t("battle.weather_current", weather=battle.weather)
        lines.append(f"║ {weather_status:<36} ║")

    # Siege progress (if applicable)
    if battle.siege_progress > 0:
        siege_bar = render_progress_bar(battle.siege_progress, 100, 10)
        siege_label = i18n.t("battle.siege_progress")
        lines.append(f"║ {siege_label}: {siege_bar} {battle.siege_progress:>3}% ║")

    lines.append(f"╚{'═' * 38}╝")

    return "\n".join(lines)


def _render_combat_log(combat_log: list, max_entries: int = 3) -> str:
    """
    Render recent combat log entries.

    Args:
        combat_log: List of combat event strings
        max_entries: Maximum number of recent entries to show

    Returns:
        Formatted combat log string
    """
    if not combat_log:
        return ""

    recent_log = combat_log[-max_entries:]

    lines = []
    lines.append(f"╔{'═' * 58}╗")
    lines.append(f"║ {i18n.t('battle.combat_log').center(56)} ║")
    lines.append(f"║ {'─' * 58} ║")

    for entry in recent_log:
        # Truncate long entries to fit
        if len(entry) > 56:
            entry = entry[:53] + "..."
        lines.append(f"║ {entry:<56} ║")

    # Add empty lines if fewer than max_entries
    for _ in range(max_entries - len(recent_log)):
        lines.append(f"║{' ' * 58}║")

    lines.append(f"╚{'═' * 58}╝")

    return "\n".join(lines)


def render_battle_map(battle: BattleState) -> str:
    """
    Render a complete tactical battle map.

    This function creates a comprehensive ASCII visualization of the current
    battle state, including:
    - City being attacked/defended
    - Terrain type with visual representation
    - Unit boxes showing commanders, troops, and morale for both sides
    - Battle status (round, supply, weather, siege progress)
    - Recent combat log entries

    Args:
        battle: The current battle state

    Returns:
        Multi-line ASCII art string representing the battle map

    Examples:
        >>> from src.models import BattleState, TerrainType
        >>> battle = BattleState(
        ...     attacker_city="Chengdu",
        ...     defender_city="Changan",
        ...     attacker_faction="Shu",
        ...     defender_faction="Wei",
        ...     attacker_commander="Zhao Yun",
        ...     defender_commander="Cao Ren",
        ...     attacker_troops=5000,
        ...     defender_troops=4000,
        ...     terrain=TerrainType.PLAINS
        ... )
        >>> map_str = render_battle_map(battle)
        >>> "Zhao Yun" in map_str
        True
        >>> "Cao Ren" in map_str
        True
    """
    lines = []

    # Title: Battle location
    title = i18n.t("battle.title",
                   attacker_city=battle.attacker_city,
                   defender_city=battle.defender_city)
    lines.append("")
    lines.append("=" * 60)
    lines.append(title.center(60))
    lines.append("=" * 60)
    lines.append("")

    # Terrain display
    terrain_display = _render_terrain_zone(battle.terrain, 40)
    lines.append(terrain_display)
    lines.append("")

    # Unit displays - side by side if possible, or stacked
    attacker_box = _render_unit_box(
        battle.attacker_commander,
        battle.attacker_troops,
        battle.attacker_faction,
        battle.attacker_morale,
        is_attacker=True
    )

    defender_box = _render_unit_box(
        battle.defender_commander,
        battle.defender_troops,
        battle.defender_faction,
        battle.defender_morale,
        is_attacker=False
    )

    # Display units side by side
    attacker_lines = attacker_box.split("\n")
    defender_lines = defender_box.split("\n")

    for att_line, def_line in zip(attacker_lines, defender_lines):
        lines.append(f"{att_line}    {def_line}")

    lines.append("")

    # Battle status
    status_display = _render_battle_status(battle)
    lines.append(status_display)
    lines.append("")

    # Combat log (if any)
    if battle.combat_log:
        log_display = _render_combat_log(battle.combat_log)
        lines.append(log_display)
        lines.append("")

    return "\n".join(lines)
