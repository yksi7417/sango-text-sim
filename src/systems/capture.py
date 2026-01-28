"""
Capture System - Officer capture, recruitment, execution, and release.

After battles, defeated officers can be captured. Players can then:
- Recruit: Add captured officer to their faction
- Execute: Kill the officer (loyalty impact on own officers)
- Release: Free the officer (reputation boost)
"""
import random
from typing import Dict, Any, List
from ..models import GameState, Officer
from i18n import i18n


# Officers who refuse to surrender (die rather than be captured)
LOYALIST_OFFICERS = ["GuanYu", "ZhangFei", "DianWei"]


def capture_officers(game_state: GameState, city_name: str,
                     victor_faction: str) -> List[Dict[str, Any]]:
    """
    Attempt to capture officers in a conquered city.

    Args:
        game_state: Current game state
        city_name: The conquered city
        victor_faction: The conquering faction

    Returns:
        List of capture results
    """
    results = []
    city = game_state.cities.get(city_name)
    if not city:
        return results

    loser_faction_name = city.owner
    loser_faction = game_state.factions.get(loser_faction_name)
    if not loser_faction:
        return results

    officers_in_city = [
        name for name in loser_faction.officers
        if game_state.officers.get(name) and game_state.officers[name].city == city_name
    ]

    for off_name in officers_in_city:
        officer = game_state.officers[off_name]

        # Loyalists refuse capture
        if off_name in LOYALIST_OFFICERS and officer.loyalty >= 80:
            results.append({
                "officer": off_name,
                "outcome": "refused",
                "message": i18n.t("capture.refused", officer=off_name,
                                   default=f"{off_name} fights to the death rather than surrender!")
            })
            continue

        # Capture chance based on loyalty (lower loyalty = easier capture)
        capture_chance = 0.8 - (officer.loyalty / 200.0)
        if random.random() < capture_chance:
            # Add to captured list
            if not hasattr(game_state, 'captured_officers'):
                game_state.captured_officers = {}
            game_state.captured_officers[off_name] = {
                "captor": victor_faction,
                "original_faction": loser_faction_name
            }
            # Remove from original faction
            if off_name in loser_faction.officers:
                loser_faction.officers.remove(off_name)
            officer.city = None
            officer.task = None
            officer.busy = False

            results.append({
                "officer": off_name,
                "outcome": "captured",
                "message": i18n.t("capture.captured", officer=off_name,
                                   default=f"{off_name} has been captured!")
            })
        else:
            results.append({
                "officer": off_name,
                "outcome": "escaped",
                "message": i18n.t("capture.escaped", officer=off_name,
                                   default=f"{off_name} escaped during the chaos.")
            })

    return results


def recruit_captured(game_state: GameState, officer_name: str) -> Dict[str, Any]:
    """Recruit a captured officer into the player's faction."""
    captured = getattr(game_state, 'captured_officers', {})
    if officer_name not in captured:
        return {"success": False, "message": i18n.t("capture.not_captured",
                default="Officer is not captured.")}

    info = captured[officer_name]
    if info["captor"] != game_state.player_faction:
        return {"success": False, "message": i18n.t("capture.not_yours",
                default="This prisoner is not yours.")}

    officer = game_state.officers.get(officer_name)
    if not officer:
        return {"success": False, "message": i18n.t("errors.no_officer")}

    # Recruit
    faction = game_state.factions[game_state.player_faction]
    officer.faction = game_state.player_faction
    officer.loyalty = 30  # Starts with low loyalty
    officer.energy = 50
    if faction.cities:
        officer.city = faction.cities[0]
    faction.officers.append(officer_name)
    del captured[officer_name]

    return {"success": True, "message": i18n.t("capture.recruited", officer=officer_name,
            default=f"{officer_name} joins your faction!")}


def execute_captured(game_state: GameState, officer_name: str) -> Dict[str, Any]:
    """Execute a captured officer (affects morale of own officers)."""
    captured = getattr(game_state, 'captured_officers', {})
    if officer_name not in captured:
        return {"success": False, "message": i18n.t("capture.not_captured",
                default="Officer is not captured.")}

    info = captured[officer_name]
    if info["captor"] != game_state.player_faction:
        return {"success": False, "message": i18n.t("capture.not_yours",
                default="This prisoner is not yours.")}

    # Execute - loyalty drop for own officers
    faction = game_state.factions[game_state.player_faction]
    for off_name in faction.officers:
        off = game_state.officers.get(off_name)
        if off:
            off.loyalty = max(0, off.loyalty - 5)

    # Remove officer from game
    del game_state.officers[officer_name]
    del captured[officer_name]

    return {"success": True, "message": i18n.t("capture.executed", officer=officer_name,
            default=f"{officer_name} has been executed. Your officers are disturbed.")}


def release_captured(game_state: GameState, officer_name: str) -> Dict[str, Any]:
    """Release a captured officer (reputation boost)."""
    captured = getattr(game_state, 'captured_officers', {})
    if officer_name not in captured:
        return {"success": False, "message": i18n.t("capture.not_captured",
                default="Officer is not captured.")}

    info = captured[officer_name]
    if info["captor"] != game_state.player_faction:
        return {"success": False, "message": i18n.t("capture.not_yours",
                default="This prisoner is not yours.")}

    officer = game_state.officers.get(officer_name)
    original_faction = game_state.factions.get(info["original_faction"])

    # Return to original faction
    if officer and original_faction:
        officer.faction = info["original_faction"]
        officer.loyalty = min(100, officer.loyalty + 10)
        if original_faction.cities:
            officer.city = original_faction.cities[0]
        original_faction.officers.append(officer_name)

    # Improve relations
    player_faction = game_state.factions.get(game_state.player_faction)
    if player_faction and info["original_faction"] in player_faction.relations:
        player_faction.relations[info["original_faction"]] = min(100,
            player_faction.relations[info["original_faction"]] + 10)

    # Loyalty boost for own officers (benevolent act)
    for off_name in game_state.factions[game_state.player_faction].officers:
        off = game_state.officers.get(off_name)
        if off:
            off.loyalty = min(100, off.loyalty + 3)

    del captured[officer_name]
    return {"success": True, "message": i18n.t("capture.released", officer=officer_name,
            default=f"{officer_name} has been released. Your reputation improves.")}
