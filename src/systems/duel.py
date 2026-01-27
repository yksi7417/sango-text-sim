"""
Duel system for one-on-one officer combat.

This module provides mechanics for dramatic duels between officers,
with HP-based combat, multiple action choices, and outcome tracking.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import random

from src.models import Officer


class DuelAction(Enum):
    """Actions an officer can take during a duel."""
    ATTACK = "attack"
    DEFEND = "defend"
    SPECIAL = "special"


@dataclass
class DuelResult:
    """Result of a single duel round."""
    attacker_action: DuelAction
    defender_action: DuelAction
    attacker_damage: int  # Damage dealt by attacker
    defender_damage: int  # Damage dealt by defender
    message: str  # Description of what happened


@dataclass
class Duel:
    """
    Represents an ongoing duel between two officers.

    Attributes:
        attacker: The officer who initiated the duel
        defender: The officer defending
        attacker_hp: Current HP of attacker
        defender_hp: Current HP of defender
        round: Current round number
        log: Combat log of events
    """
    attacker: Officer
    defender: Officer
    attacker_hp: int
    defender_hp: int
    round: int = 0
    log: List[str] = field(default_factory=list)


def start_duel(attacker: Officer, defender: Officer) -> Duel:
    """
    Initialize a new duel between two officers.

    HP is based on leadership stat to reflect combat prowess.
    Base HP = leadership * 2

    Args:
        attacker: Officer initiating the duel
        defender: Officer being challenged

    Returns:
        Initialized Duel instance
    """
    attacker_hp = attacker.leadership * 2
    defender_hp = defender.leadership * 2

    return Duel(
        attacker=attacker,
        defender=defender,
        attacker_hp=attacker_hp,
        defender_hp=defender_hp,
        round=0,
        log=[]
    )


def is_duel_over(duel: Duel) -> bool:
    """
    Check if the duel has ended.

    Duel ends when either officer's HP reaches 0 or below.

    Args:
        duel: The duel to check

    Returns:
        True if duel is over, False otherwise
    """
    return duel.attacker_hp <= 0 or duel.defender_hp <= 0


def _calculate_base_damage(attacker_leadership: int, defender_leadership: int) -> int:
    """
    Calculate base damage based on leadership differential.

    Formula: Base = 10 + (attacker_leadership - defender_leadership) / 5
    This creates meaningful differences while keeping combat from being too quick.

    Args:
        attacker_leadership: Attacking officer's leadership stat
        defender_leadership: Defending officer's leadership stat

    Returns:
        Base damage value
    """
    differential = (attacker_leadership - defender_leadership) / 5
    base_damage = max(5, 10 + differential)  # Minimum 5 damage
    return int(base_damage)


def _execute_attack(attacker: Officer, defender: Officer, is_special: bool = False) -> Tuple[int, str]:
    """
    Execute an attack and calculate damage.

    Args:
        attacker: Officer performing the attack
        defender: Officer being attacked
        is_special: Whether this is a special attack

    Returns:
        Tuple of (damage, description)
    """
    base_damage = _calculate_base_damage(attacker.leadership, defender.leadership)

    if is_special:
        # Special attack: higher damage, lower hit rate (70%)
        hit_chance = 0.70
        damage_multiplier = 2.0
    else:
        # Normal attack: standard hit rate (85%)
        hit_chance = 0.85
        damage_multiplier = 1.0

    # Hit check
    if random.random() > hit_chance:
        return (0, f"{attacker.name} attacks but misses!")

    # Calculate final damage with some randomness (±20%)
    variance = random.uniform(0.8, 1.2)
    damage = int(base_damage * damage_multiplier * variance)

    attack_type = "special attack" if is_special else "attack"
    description = f"{attacker.name} {attack_type}s {defender.name} for {damage} damage!"

    return (damage, description)


def process_duel_round(duel: Duel, attacker_action: DuelAction, defender_action: DuelAction) -> DuelResult:
    """
    Process a single round of the duel.

    Action mechanics:
    - ATTACK: Standard damage, 85% hit rate
    - DEFEND: Reduce incoming damage by 50%, cannot deal damage
    - SPECIAL: High damage (2x), lower hit rate (70%)

    Args:
        duel: The ongoing duel
        attacker_action: Action chosen by attacker
        defender_action: Action chosen by defender

    Returns:
        DuelResult with outcome information
    """
    duel.round += 1

    attacker_damage_dealt = 0
    defender_damage_dealt = 0
    messages = []

    # Process attacker's action
    if attacker_action == DuelAction.ATTACK:
        damage, msg = _execute_attack(duel.attacker, duel.defender, is_special=False)
        attacker_damage_dealt = damage
        messages.append(msg)

        # Apply defense reduction if defender is defending
        if defender_action == DuelAction.DEFEND and damage > 0:
            original_damage = damage
            attacker_damage_dealt = damage // 2
            messages.append(f"{duel.defender.name} defends, reducing damage from {original_damage} to {attacker_damage_dealt}!")

        duel.defender_hp -= attacker_damage_dealt

    elif attacker_action == DuelAction.SPECIAL:
        damage, msg = _execute_attack(duel.attacker, duel.defender, is_special=True)
        attacker_damage_dealt = damage
        messages.append(msg)

        # Apply defense reduction if defender is defending
        if defender_action == DuelAction.DEFEND and damage > 0:
            original_damage = damage
            attacker_damage_dealt = damage // 2
            messages.append(f"{duel.defender.name} defends, reducing damage from {original_damage} to {attacker_damage_dealt}!")

        duel.defender_hp -= attacker_damage_dealt

    elif attacker_action == DuelAction.DEFEND:
        messages.append(f"{duel.attacker.name} takes a defensive stance!")

    # Process defender's action (only if not defending)
    if defender_action == DuelAction.ATTACK:
        damage, msg = _execute_attack(duel.defender, duel.attacker, is_special=False)
        defender_damage_dealt = damage
        messages.append(msg)

        # Apply defense reduction if attacker is defending
        if attacker_action == DuelAction.DEFEND and damage > 0:
            original_damage = damage
            defender_damage_dealt = damage // 2
            messages.append(f"{duel.attacker.name} defends, reducing damage from {original_damage} to {defender_damage_dealt}!")

        duel.attacker_hp -= defender_damage_dealt

    elif defender_action == DuelAction.SPECIAL:
        damage, msg = _execute_attack(duel.defender, duel.attacker, is_special=True)
        defender_damage_dealt = damage
        messages.append(msg)

        # Apply defense reduction if attacker is defending
        if attacker_action == DuelAction.DEFEND and damage > 0:
            original_damage = damage
            defender_damage_dealt = damage // 2
            messages.append(f"{duel.attacker.name} defends, reducing damage from {original_damage} to {defender_damage_dealt}!")

        duel.attacker_hp -= defender_damage_dealt

    elif defender_action == DuelAction.DEFEND:
        messages.append(f"{duel.defender.name} takes a defensive stance!")

    # Combine messages
    combined_message = " ".join(messages)

    # Add to combat log
    duel.log.append(f"Round {duel.round}: {combined_message}")

    return DuelResult(
        attacker_action=attacker_action,
        defender_action=defender_action,
        attacker_damage=attacker_damage_dealt,
        defender_damage=defender_damage_dealt,
        message=combined_message
    )


def get_duel_winner(duel: Duel) -> Officer:
    """
    Get the winner of a completed duel.

    Args:
        duel: The completed duel

    Returns:
        The victorious officer

    Raises:
        ValueError: If duel is not over yet
    """
    if not is_duel_over(duel):
        raise ValueError("Duel is not over yet")

    if duel.attacker_hp > 0:
        return duel.attacker
    else:
        return duel.defender
