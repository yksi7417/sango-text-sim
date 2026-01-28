"""
Marriage & Hostage System - Diplomatic marriages and hostage exchanges.

Marriages:
- Create relationship bonds between officers
- Improve faction relations
- Can be proposed to other factions

Hostages:
- Officers sent as guarantee of treaty compliance
- Hostage welfare affects diplomatic relations
- Can be returned or detained
"""
import random
from typing import Dict, Any, List, Optional
from ..models import GameState, Officer, RelationshipType
from i18n import i18n


MARRIAGE_RELATION_BOOST = 25  # Relations boost from marriage
MARRIAGE_LOYALTY_BOOST = 15  # Loyalty boost for married officer
HOSTAGE_RELATION_MAINTENANCE = 5  # Relations maintained per turn while hostage held
HOSTAGE_HARM_PENALTY = -40  # Relations penalty if hostage is harmed
HOSTAGE_RETURN_BOOST = 20  # Relations boost when hostage returned


def propose_marriage(game_state: GameState, officer_name: str,
                     target_faction: str) -> Dict[str, Any]:
    """
    Propose a diplomatic marriage to another faction.

    Args:
        game_state: Current game state
        officer_name: Officer to be married
        target_faction: Faction to propose marriage to

    Returns:
        Dict with success and message
    """
    player = game_state.player_faction
    officer = game_state.officers.get(officer_name)

    if not officer:
        return {"success": False, "message": i18n.t("errors.no_officer")}

    if officer.faction != player:
        return {"success": False, "message": i18n.t("errors.not_your_officer")}

    target = game_state.factions.get(target_faction)
    if not target or target_faction == player:
        return {"success": False, "message": i18n.t("marriage.invalid_target",
                default="Invalid target faction.")}

    # Check if officer already has spouse relationship
    if any(v == RelationshipType.SPOUSE.value for v in officer.relationships.values()):
        return {"success": False, "message": i18n.t("marriage.already_married",
                officer=officer_name,
                default=f"{officer_name} is already married.")}

    # AI acceptance based on relations
    relations = game_state.factions[player].relations.get(target_faction, 0)
    acceptance = 0.3 + (relations / 200.0)

    if random.random() > acceptance:
        return {"success": False, "message": i18n.t("marriage.rejected",
                faction=target_faction,
                default=f"{target_faction} rejects the marriage proposal.")}

    # Find a target officer (pick first available from target faction)
    target_officer = None
    for off_name in target.officers:
        off = game_state.officers.get(off_name)
        if off and not any(v == RelationshipType.SPOUSE.value
                          for v in off.relationships.values()):
            target_officer = off
            break

    if not target_officer:
        return {"success": False, "message": i18n.t("marriage.no_candidate",
                faction=target_faction,
                default=f"No available candidates in {target_faction}.")}

    # Create marriage bonds
    officer.relationships[target_officer.name] = RelationshipType.SPOUSE.value
    target_officer.relationships[officer.name] = RelationshipType.SPOUSE.value

    # Boost relations
    game_state.factions[player].relations[target_faction] = min(100,
        game_state.factions[player].relations.get(target_faction, 0) + MARRIAGE_RELATION_BOOST)
    target.relations[player] = min(100,
        target.relations.get(player, 0) + MARRIAGE_RELATION_BOOST)

    # Loyalty boost
    officer.loyalty = min(100, officer.loyalty + MARRIAGE_LOYALTY_BOOST)

    return {"success": True, "message": i18n.t("marriage.success",
            officer=officer_name, spouse=target_officer.name, faction=target_faction,
            default=f"{officer_name} married {target_officer.name} of {target_faction}! Relations improved.")}


def send_hostage(game_state: GameState, officer_name: str,
                 target_faction: str) -> Dict[str, Any]:
    """
    Send an officer as hostage to another faction.

    Args:
        game_state: Current game state
        officer_name: Officer to send as hostage
        target_faction: Faction to send hostage to

    Returns:
        Dict with success and message
    """
    player = game_state.player_faction
    officer = game_state.officers.get(officer_name)

    if not officer:
        return {"success": False, "message": i18n.t("errors.no_officer")}

    if officer.faction != player:
        return {"success": False, "message": i18n.t("errors.not_your_officer")}

    target = game_state.factions.get(target_faction)
    if not target or target_faction == player:
        return {"success": False, "message": i18n.t("marriage.invalid_target",
                default="Invalid target faction.")}

    # Record hostage
    hostages = getattr(game_state, 'hostages', {})
    hostages[officer_name] = {
        "from_faction": player,
        "to_faction": target_faction,
    }
    game_state.hostages = hostages

    # Remove from active duty
    officer.city = None
    officer.task = None
    officer.busy = False

    # Relations boost
    game_state.factions[player].relations[target_faction] = min(100,
        game_state.factions[player].relations.get(target_faction, 0) + 10)
    target.relations[player] = min(100,
        target.relations.get(player, 0) + 10)

    return {"success": True, "message": i18n.t("hostage.sent",
            officer=officer_name, faction=target_faction,
            default=f"{officer_name} sent as hostage to {target_faction}.")}


def return_hostage(game_state: GameState, officer_name: str) -> Dict[str, Any]:
    """Return a hostage to their faction."""
    hostages = getattr(game_state, 'hostages', {})

    if officer_name not in hostages:
        return {"success": False, "message": i18n.t("hostage.not_hostage",
                default="This officer is not a hostage.")}

    info = hostages[officer_name]
    officer = game_state.officers.get(officer_name)

    if officer:
        # Return to home faction
        home_faction = game_state.factions.get(info["from_faction"])
        if home_faction and home_faction.cities:
            officer.city = home_faction.cities[0]

        # Relations boost
        player = game_state.player_faction
        game_state.factions[player].relations[info["from_faction"]] = min(100,
            game_state.factions[player].relations.get(info["from_faction"], 0) + HOSTAGE_RETURN_BOOST)

    del hostages[officer_name]
    game_state.hostages = hostages

    return {"success": True, "message": i18n.t("hostage.returned",
            officer=officer_name,
            default=f"{officer_name} has been returned. Relations improved.")}


def list_hostages(game_state: GameState) -> List[Dict[str, Any]]:
    """List all current hostages."""
    hostages = getattr(game_state, 'hostages', {})
    result = []
    for name, info in hostages.items():
        result.append({
            "officer": name,
            "from_faction": info["from_faction"],
            "to_faction": info["to_faction"],
        })
    return result
