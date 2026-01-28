"""
Achievement System - Track and award player achievements.
"""
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models import GameState
from i18n import i18n


@dataclass
class Achievement:
    """An achievement that can be earned."""
    id: str
    category: str
    name_key: str
    condition: Dict[str, Any] = field(default_factory=dict)


def load_achievements() -> List[Achievement]:
    """Load all achievements from JSON data file."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "achievements.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [Achievement(
            id=a["id"],
            category=a["category"],
            name_key=a["name_key"],
            condition=a.get("condition", {})
        ) for a in data["achievements"]]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def _check_achievement_condition(achievement: Achievement, game_state: GameState) -> bool:
    """Check if an achievement's condition is met."""
    cond = achievement.condition
    faction = game_state.factions.get(game_state.player_faction)
    if not faction:
        return False

    player_cities = [game_state.cities[cn] for cn in faction.cities if cn in game_state.cities]

    if "cities_owned" in cond:
        if len(faction.cities) < cond["cities_owned"]:
            return False

    if "all_cities" in cond and cond["all_cities"]:
        if len(faction.cities) < len(game_state.cities):
            return False

    if "total_troops" in cond:
        total = sum(c.troops for c in player_cities)
        if total < cond["total_troops"]:
            return False

    if "total_gold" in cond:
        total = sum(c.gold for c in player_cities)
        if total < cond["total_gold"]:
            return False

    if "total_food" in cond:
        total = sum(c.food for c in player_cities)
        if total < cond["total_food"]:
            return False

    if "max_defense" in cond:
        if not player_cities or max(c.defense for c in player_cities) < cond["max_defense"]:
            return False

    if "max_commerce" in cond:
        if not player_cities or max(c.commerce for c in player_cities) < cond["max_commerce"]:
            return False

    if "max_agri" in cond:
        if not player_cities or max(c.agri for c in player_cities) < cond["max_agri"]:
            return False

    if "max_tech" in cond:
        if not player_cities or max(c.tech for c in player_cities) < cond["max_tech"]:
            return False

    if "max_relations" in cond:
        if not faction.relations:
            return False
        if max(faction.relations.values()) < cond["max_relations"]:
            return False

    if "min_relations" in cond:
        if not faction.relations:
            return False
        if min(faction.relations.values()) > cond["min_relations"]:
            return False

    if "officers_count" in cond:
        if len(faction.officers) < cond["officers_count"]:
            return False

    if "all_loyalty_above" in cond:
        threshold = cond["all_loyalty_above"]
        for name in faction.officers:
            off = game_state.officers.get(name)
            if off and off.loyalty < threshold:
                return False

    if "officers_in_faction" in cond:
        for name in cond["officers_in_faction"]:
            if name not in faction.officers:
                return False

    if "techs_researched" in cond:
        if len(faction.technologies) < cond["techs_researched"]:
            return False

    if "turns_survived" in cond:
        turns_played = (game_state.year - 208) * 12 + game_state.month
        if turns_played < cond["turns_survived"]:
            return False

    if "all_morale_above" in cond:
        threshold = cond["all_morale_above"]
        for c in player_cities:
            if c.morale < threshold:
                return False

    if "buildings_built" in cond:
        total_buildings = sum(len(c.buildings) for c in player_cities)
        if total_buildings < cond["buildings_built"]:
            return False

    # battles_won and duels_won are tracked separately via game state counters
    # Skip these for now as they require stat tracking
    if "battles_won" in cond or "duels_won" in cond:
        return False  # Will be implemented when stat tracking is added

    return True


def check_achievements(game_state: GameState, earned_ids: List[str]) -> List[Achievement]:
    """
    Check which achievements have been newly earned.

    Args:
        game_state: Current game state
        earned_ids: List of already earned achievement IDs

    Returns:
        List of newly earned Achievement objects
    """
    achievements = load_achievements()
    newly_earned = []

    for ach in achievements:
        if ach.id in earned_ids:
            continue
        if _check_achievement_condition(ach, game_state):
            newly_earned.append(ach)

    return newly_earned
