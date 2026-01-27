"""
Duel View Renderer

Renders the duel state with HP bars, combat log, and action choices.
"""

from typing import List
from i18n import i18n
from src.systems.duel import Duel, DuelAction
from src.models import Officer
from src.display.components import render_progress_bar, render_box, render_separator, get_faction_color


def render_duel_state(duel: Duel, max_log_lines: int = 5) -> str:
    """
    Render the current state of a duel.

    Shows both combatants with HP bars, round info, and recent combat log.

    Args:
        duel: The ongoing duel
        max_log_lines: Maximum number of log lines to show

    Returns:
        Formatted duel state string
    """
    lines = []

    # Title
    title = i18n.t("duel.title")
    lines.append(render_separator(60, "double"))
    lines.append(f"  {title}".center(60))
    lines.append(render_separator(60, "double"))
    lines.append("")

    # Round number
    round_text = i18n.t("duel.round", round=duel.round)
    lines.append(f"  {round_text}".center(60))
    lines.append("")

    # Combatants display
    attacker_color = get_faction_color(duel.attacker.faction)
    defender_color = get_faction_color(duel.defender.faction)

    # Attacker info
    attacker_label = i18n.t("duel.attacker")
    attacker_max_hp = duel.attacker.leadership * 2
    attacker_hp_text = i18n.t("duel.current_hp", current=duel.attacker_hp, max=attacker_max_hp)
    attacker_hp_bar = render_progress_bar(duel.attacker_hp, attacker_max_hp, 20)

    lines.append(f"  {attacker_label}: {attacker_color}{duel.attacker.name}")
    lines.append(f"  {i18n.t('duel.hp')}: {attacker_hp_bar} {attacker_hp_text}")
    lines.append("")

    # VS
    vs_text = i18n.t("duel.vs")
    lines.append(f"  {vs_text}".center(60))
    lines.append("")

    # Defender info
    defender_label = i18n.t("duel.defender")
    defender_max_hp = duel.defender.leadership * 2
    defender_hp_text = i18n.t("duel.current_hp", current=duel.defender_hp, max=defender_max_hp)
    defender_hp_bar = render_progress_bar(duel.defender_hp, defender_max_hp, 20)

    lines.append(f"  {defender_label}: {defender_color}{duel.defender.name}")
    lines.append(f"  {i18n.t('duel.hp')}: {defender_hp_bar} {defender_hp_text}")
    lines.append("")

    # Combat log
    if duel.log:
        lines.append(render_separator(60, "single"))
        lines.append(f"  {i18n.t('duel.combat_log')}")
        lines.append(render_separator(60, "single"))

        # Show recent log entries
        recent_log = duel.log[-max_log_lines:]
        for log_entry in recent_log:
            lines.append(f"  {log_entry}")

        lines.append("")

    return "\n".join(lines)


def render_action_menu() -> str:
    """
    Render the action selection menu for a duel.

    Shows available actions with descriptions.

    Returns:
        Formatted action menu string
    """
    lines = []

    lines.append(render_separator(60, "single"))
    lines.append(f"  {i18n.t('duel.actions.title')}")
    lines.append(render_separator(60, "single"))
    lines.append("")

    # Attack
    lines.append(f"  [1] {i18n.t('duel.actions.attack')}")
    lines.append(f"      {i18n.t('duel.actions.attack_desc')}")
    lines.append("")

    # Defend
    lines.append(f"  [2] {i18n.t('duel.actions.defend')}")
    lines.append(f"      {i18n.t('duel.actions.defend_desc')}")
    lines.append("")

    # Special
    lines.append(f"  [3] {i18n.t('duel.actions.special')}")
    lines.append(f"      {i18n.t('duel.actions.special_desc')}")
    lines.append("")

    return "\n".join(lines)


def render_duel_victory(winner: Officer, loser: Officer) -> str:
    """
    Render the victory screen after a duel.

    Args:
        winner: The victorious officer
        loser: The defeated officer

    Returns:
        Formatted victory message
    """
    lines = []

    lines.append("")
    lines.append(render_separator(60, "double"))
    lines.append("")

    winner_color = get_faction_color(winner.faction)
    victory_msg = i18n.t("duel.victory", winner=winner.name)

    lines.append(f"  {winner_color}{victory_msg}".center(70))
    lines.append("")

    defeat_msg = i18n.t("duel.defeat", loser=loser.name)
    lines.append(f"  {defeat_msg}".center(60))
    lines.append("")

    lines.append(render_separator(60, "double"))
    lines.append("")

    return "\n".join(lines)


def render_duel_defeat(winner: Officer, loser: Officer) -> str:
    """
    Render the defeat screen after losing a duel.

    Args:
        winner: The victorious officer (who defeated you)
        loser: The defeated officer (the player's officer)

    Returns:
        Formatted defeat message
    """
    lines = []

    lines.append("")
    lines.append(render_separator(60, "double"))
    lines.append("")

    defeat_msg = i18n.t("duel.defeat", loser=loser.name)
    lines.append(f"  {defeat_msg}".center(60))
    lines.append("")

    winner_color = get_faction_color(winner.faction)
    victory_msg = i18n.t("duel.victory", winner=winner.name)
    lines.append(f"  {winner_color}{victory_msg}".center(70))
    lines.append("")

    lines.append(render_separator(60, "double"))
    lines.append("")

    return "\n".join(lines)
