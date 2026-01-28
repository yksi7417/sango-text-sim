"""
Supply Line System - Army supply management and logistics.

Armies on campaign consume supplies. Supply lines run through owned territory.
Cut supply lines cause attrition. Friendly cities provide foraging.
"""
from typing import Dict, Any, List, Optional
from ..models import GameState, City
from i18n import i18n


# Supply constants
SUPPLY_PER_TROOP = 0.1  # Food consumed per troop per turn
BASE_SUPPLY_DAYS = 10  # Default supply days for armies
FORAGING_RECOVERY = 3  # Supply days recovered when foraging in friendly city
ATTRITION_RATE = 0.05  # 5% troop loss per turn when out of supplies
SUPPLY_LINE_CUT_ATTRITION = 0.03  # 3% troop loss when supply line is cut


def calculate_supply_consumption(troops: int) -> int:
    """Calculate food consumed by an army per turn."""
    return max(1, int(troops * SUPPLY_PER_TROOP))


def check_supply_line(game_state: GameState, from_city: str, to_city: str,
                      faction: str) -> Dict[str, Any]:
    """
    Check if supply line between cities is intact.
    Supply line is intact if there's a path through owned/allied territory.

    Args:
        game_state: Current game state
        from_city: Supply source city
        to_city: Army location city
        faction: Faction needing supplies

    Returns:
        Dict with intact bool and path info
    """
    if from_city == to_city:
        return {"intact": True, "path": [from_city]}

    # BFS through adjacency, only through owned territory
    visited = set()
    queue = [[from_city]]

    while queue:
        path = queue.pop(0)
        current = path[-1]

        if current == to_city:
            return {"intact": True, "path": path}

        if current in visited:
            continue
        visited.add(current)

        for neighbor in game_state.adj.get(current, []):
            if neighbor in visited:
                continue
            city = game_state.cities.get(neighbor)
            if city and city.owner == faction:
                queue.append(path + [neighbor])

    return {"intact": False, "path": []}


def apply_supply_attrition(troops: int, has_supply: bool) -> Dict[str, Any]:
    """
    Apply attrition based on supply status.

    Args:
        troops: Current troop count
        has_supply: Whether supply line is intact

    Returns:
        Dict with new troop count and losses
    """
    if has_supply:
        return {"troops": troops, "losses": 0, "message": ""}

    losses = max(1, int(troops * ATTRITION_RATE))
    new_troops = max(0, troops - losses)

    return {
        "troops": new_troops,
        "losses": losses,
        "message": i18n.t("supply.attrition", losses=losses,
                          default=f"Supply shortage! {losses} troops lost to attrition.")
    }


def forage_supplies(game_state: GameState, city_name: str, faction: str) -> Dict[str, Any]:
    """
    Forage for supplies in a friendly city.

    Args:
        game_state: Current game state
        city_name: City to forage in
        faction: Faction doing the foraging

    Returns:
        Dict with success and supply recovery info
    """
    city = game_state.cities.get(city_name)
    if not city:
        return {"success": False, "message": i18n.t("errors.no_city")}

    if city.owner != faction:
        return {"success": False, "message": i18n.t("supply.enemy_territory",
                default="Cannot forage in enemy territory.")}

    # Forage consumes some city food
    forage_amount = min(city.food, calculate_supply_consumption(100))
    city.food -= forage_amount

    return {
        "success": True,
        "recovery": FORAGING_RECOVERY,
        "food_consumed": forage_amount,
        "message": i18n.t("supply.foraged", days=FORAGING_RECOVERY, city=city_name,
                          default=f"Foraging in {city_name} recovered {FORAGING_RECOVERY} supply days.")
    }


def get_supply_status(game_state: GameState, city_name: str,
                      faction: str) -> Dict[str, Any]:
    """
    Get supply status for a position.

    Returns supply line status and nearby friendly cities for foraging.
    """
    faction_obj = game_state.factions.get(faction)
    if not faction_obj:
        return {"has_supply": False, "nearby_friendly": []}

    # Check supply from any owned city
    has_supply = False
    for owned_city in faction_obj.cities:
        result = check_supply_line(game_state, owned_city, city_name, faction)
        if result["intact"]:
            has_supply = True
            break

    # Find nearby friendly cities for foraging
    nearby = []
    for neighbor in game_state.adj.get(city_name, []):
        city = game_state.cities.get(neighbor)
        if city and city.owner == faction:
            nearby.append(neighbor)

    return {
        "has_supply": has_supply,
        "nearby_friendly": nearby,
    }
