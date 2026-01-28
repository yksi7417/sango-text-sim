"""
Espionage System - Spy missions with various outcomes.

Missions:
- scout: Detailed intelligence on target city
- sabotage: Damage target city (food/gold/defense)
- incite: Lower loyalty of target officers
- steal: Steal gold from target city
"""
import random
from typing import Dict, Any
from ..models import GameState, Officer
from i18n import i18n


MISSION_COSTS = {
    "scout": 50,
    "sabotage": 100,
    "incite": 150,
    "steal": 80,
}

MISSION_COOLDOWN = 2  # turns between missions


def execute_spy_mission(game_state: GameState, officer_name: str,
                        target_city: str, mission: str) -> Dict[str, Any]:
    """
    Execute a spy mission.

    Args:
        game_state: Current game state
        officer_name: Name of officer performing espionage
        target_city: Target city name
        mission: Mission type (scout, sabotage, incite, steal)

    Returns:
        Dict with success, message, and details
    """
    if mission not in MISSION_COSTS:
        return {"success": False, "message": i18n.t("espionage.invalid_mission",
                default="Invalid mission. Options: scout, sabotage, incite, steal")}

    officer = game_state.officers.get(officer_name)
    if not officer:
        return {"success": False, "message": i18n.t("errors.no_officer")}

    faction = game_state.factions.get(game_state.player_faction)
    if not faction or officer_name not in faction.officers:
        return {"success": False, "message": i18n.t("errors.not_your_officer")}

    if officer.energy < 20:
        return {"success": False, "message": i18n.t("errors.officer_tired", name=officer.name)}

    city = game_state.cities.get(target_city)
    if not city:
        return {"success": False, "message": i18n.t("errors.no_city")}

    if city.owner == game_state.player_faction:
        return {"success": False, "message": i18n.t("espionage.own_city",
                default="Cannot spy on your own city")}

    cost = MISSION_COSTS[mission]
    # Find a player city with enough gold
    source_city = None
    for cn in faction.cities:
        c = game_state.cities.get(cn)
        if c and c.gold >= cost:
            source_city = c
            break

    if not source_city:
        return {"success": False, "message": i18n.t("errors.need_gold", amount=cost)}

    # Deduct gold and energy
    source_city.gold -= cost
    officer.energy -= 20

    # Calculate success chance based on INT
    base_chance = 0.5 + (officer.intelligence - 50) * 0.005
    success_roll = random.random()
    success = success_roll < base_chance

    if mission == "scout":
        return _scout_mission(city, target_city, success)
    elif mission == "sabotage":
        return _sabotage_mission(city, target_city, success, game_state)
    elif mission == "incite":
        return _incite_mission(city, target_city, success, game_state)
    elif mission == "steal":
        return _steal_mission(city, target_city, success, source_city)

    return {"success": False, "message": "Unknown mission"}


def _scout_mission(city, city_name: str, success: bool) -> Dict[str, Any]:
    """Scout mission - get detailed intelligence."""
    if success:
        report = i18n.t("spy.report",
                        name=city_name, owner=city.owner,
                        troops=city.troops, defense=city.defense,
                        morale=city.morale, agri=city.agri,
                        commerce=city.commerce, tech=city.tech,
                        walls=city.walls)
        return {"success": True, "message": report, "mission": "scout"}
    else:
        return {"success": False, "message": i18n.t("espionage.caught",
                default="Your spy was caught! Diplomatic relations worsen."),
                "mission": "scout", "caught": True}


def _sabotage_mission(city, city_name: str, success: bool, game_state: GameState) -> Dict[str, Any]:
    """Sabotage mission - damage target city."""
    if success:
        damage_food = random.randint(50, 150)
        damage_defense = random.randint(3, 8)
        city.food = max(0, city.food - damage_food)
        city.defense = max(0, city.defense - damage_defense)
        msg = i18n.t("espionage.sabotage_success",
                     city=city_name, food=damage_food, defense=damage_defense,
                     default=f"Sabotage successful! {city_name}: -{damage_food} food, -{damage_defense} defense")
        return {"success": True, "message": msg, "mission": "sabotage"}
    else:
        _apply_caught_penalty(game_state, city.owner)
        return {"success": False, "message": i18n.t("espionage.caught",
                default="Your spy was caught! Diplomatic relations worsen."),
                "mission": "sabotage", "caught": True}


def _incite_mission(city, city_name: str, success: bool, game_state: GameState) -> Dict[str, Any]:
    """Incite mission - lower loyalty of target officers."""
    if success:
        affected = []
        target_faction = game_state.factions.get(city.owner)
        if target_faction:
            for off_name in target_faction.officers:
                off = game_state.officers.get(off_name)
                if off and off.city == city_name:
                    drop = random.randint(5, 15)
                    off.loyalty = max(0, off.loyalty - drop)
                    affected.append(off.name)
        msg = i18n.t("espionage.incite_success",
                     city=city_name, count=len(affected),
                     default=f"Incitement successful! {len(affected)} officers in {city_name} have lowered loyalty.")
        return {"success": True, "message": msg, "mission": "incite"}
    else:
        _apply_caught_penalty(game_state, city.owner)
        return {"success": False, "message": i18n.t("espionage.caught",
                default="Your spy was caught! Diplomatic relations worsen."),
                "mission": "incite", "caught": True}


def _steal_mission(city, city_name: str, success: bool, source_city) -> Dict[str, Any]:
    """Steal mission - steal gold from target city."""
    if success:
        stolen = min(city.gold, random.randint(50, 200))
        city.gold -= stolen
        source_city.gold += stolen
        msg = i18n.t("espionage.steal_success",
                     city=city_name, gold=stolen,
                     default=f"Theft successful! Stole {stolen} gold from {city_name}.")
        return {"success": True, "message": msg, "mission": "steal"}
    else:
        return {"success": False, "message": i18n.t("espionage.caught",
                default="Your spy was caught! Diplomatic relations worsen."),
                "mission": "steal", "caught": True}


def _apply_caught_penalty(game_state: GameState, target_faction_name: str) -> None:
    """Apply diplomatic penalty when spy is caught."""
    player_faction = game_state.factions.get(game_state.player_faction)
    target_faction = game_state.factions.get(target_faction_name)
    if player_faction and target_faction:
        player_faction.relations[target_faction_name] = max(
            -100, player_faction.relations.get(target_faction_name, 0) - 15)
        target_faction.relations[game_state.player_faction] = max(
            -100, target_faction.relations.get(game_state.player_faction, 0) - 15)
