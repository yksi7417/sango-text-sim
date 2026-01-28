"""
Naval Combat System - Ships, naval transport, and water combat.

Coastal and river cities can build ships. Ships provide:
- Transport capacity for crossing water routes
- Combat bonuses on coastal/river terrain
- Fire attack effectiveness on water
- Zhou Yu's special naval abilities
"""
import random
from typing import Dict, Any, List
from ..models import GameState, City, TerrainType, Officer
from i18n import i18n
from ..constants import (
    SHIP_BUILD_COST_GOLD,
    SHIP_BUILD_COST_FOOD,
    SHIP_TRANSPORT_CAPACITY,
    NAVAL_FIRE_ATTACK_BONUS,
    NAVAL_COMBAT_BONUS,
    NAVAL_DEFENSE_BONUS,
    NO_SHIPS_WATER_PENALTY,
    NAVAL_TERRAIN_TYPES,
)


def can_build_ships(city: City) -> bool:
    """Check if a city can build ships (must be coastal or river terrain)."""
    return city.terrain.value in NAVAL_TERRAIN_TYPES


def build_ships(game_state: GameState, city_name: str, count: int = 1) -> Dict[str, Any]:
    """
    Build ships in a coastal/river city.

    Args:
        game_state: Current game state
        city_name: City to build ships in
        count: Number of ships to build

    Returns:
        Dict with success status and message
    """
    city = game_state.cities.get(city_name)
    if not city:
        return {"success": False, "message": i18n.t("errors.no_city")}

    if city.owner != game_state.player_faction:
        return {"success": False, "message": i18n.t("errors.not_your_city",
                default="This is not your city.")}

    if not can_build_ships(city):
        return {"success": False, "message": i18n.t("naval.not_coastal",
                default="Ships can only be built in coastal or river cities.")}

    total_gold = SHIP_BUILD_COST_GOLD * count
    total_food = SHIP_BUILD_COST_FOOD * count

    if city.gold < total_gold:
        return {"success": False, "message": i18n.t("errors.need_gold", amount=total_gold)}

    if city.food < total_food:
        return {"success": False, "message": i18n.t("naval.need_food",
                default=f"Need {total_food} food to build {count} ships.")}

    city.gold -= total_gold
    city.food -= total_food
    city.ships += count

    return {"success": True, "message": i18n.t("naval.built",
            city=city_name, count=count,
            default=f"Built {count} ship(s) in {city_name}. Total: {city.ships}")}


def get_transport_capacity(city: City) -> int:
    """Get the troop transport capacity based on ships."""
    return city.ships * SHIP_TRANSPORT_CAPACITY


def check_naval_route(game_state: GameState, from_city: str, to_city: str) -> bool:
    """
    Check if a route between cities requires naval transport.

    A route requires naval transport if the destination city is
    coastal or river terrain.
    """
    dest = game_state.cities.get(to_city)
    if not dest:
        return False
    return dest.terrain.value in NAVAL_TERRAIN_TYPES


def can_transport_troops(game_state: GameState, from_city: str, to_city: str, troops: int) -> Dict[str, Any]:
    """
    Check if troops can be transported via naval route.

    Args:
        game_state: Current game state
        from_city: Source city
        to_city: Destination city
        troops: Number of troops to transport

    Returns:
        Dict with can_transport bool and message
    """
    source = game_state.cities.get(from_city)
    dest = game_state.cities.get(to_city)

    if not source or not dest:
        return {"can_transport": False, "message": i18n.t("errors.no_city")}

    # If destination doesn't require naval, always OK
    if dest.terrain.value not in NAVAL_TERRAIN_TYPES:
        return {"can_transport": True, "message": ""}

    # Check if source has enough ships
    capacity = get_transport_capacity(source)
    if capacity >= troops:
        return {"can_transport": True, "message": ""}

    return {"can_transport": False, "message": i18n.t("naval.insufficient_ships",
            needed=troops, capacity=capacity,
            default=f"Need to transport {troops} troops but only have capacity for {capacity}. Build more ships!")}


def get_naval_combat_modifier(city: City, attacker_ships: int, is_fire_attack: bool = False,
                               officer: Officer = None) -> float:
    """
    Get combat modifier for naval engagement.

    Args:
        city: The battle location city
        attacker_ships: Number of ships the attacker has
        is_fire_attack: Whether using fire attack
        officer: Attacking officer (for special abilities)

    Returns:
        Combat modifier (multiplier)
    """
    # Only applies on water terrain
    if city.terrain.value not in NAVAL_TERRAIN_TYPES:
        return 1.0

    modifier = 1.0

    if attacker_ships > 0:
        modifier *= NAVAL_COMBAT_BONUS
    else:
        modifier *= NO_SHIPS_WATER_PENALTY

    # Fire attack bonus on water
    if is_fire_attack and attacker_ships > 0:
        modifier *= NAVAL_FIRE_ATTACK_BONUS

    # Zhou Yu special naval ability
    if officer and "Engineer" in officer.traits:
        modifier *= 1.15  # +15% bonus for naval tacticians

    return modifier


def get_naval_defense_modifier(city: City) -> float:
    """Get defensive modifier for a city with ships."""
    if city.terrain.value not in NAVAL_TERRAIN_TYPES:
        return 1.0

    if city.ships > 0:
        return NAVAL_DEFENSE_BONUS
    return 1.0


def get_fleet_status(game_state: GameState, faction: str) -> List[Dict[str, Any]]:
    """
    Get fleet status for a faction.

    Returns list of cities with ships and their capacity.
    """
    fleet = []
    faction_obj = game_state.factions.get(faction)
    if not faction_obj:
        return fleet

    for city_name in faction_obj.cities:
        city = game_state.cities.get(city_name)
        if city and city.ships > 0:
            fleet.append({
                "city": city_name,
                "ships": city.ships,
                "capacity": get_transport_capacity(city),
                "terrain": city.terrain.value
            })
    return fleet
