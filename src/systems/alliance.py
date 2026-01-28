"""
Alliance System - Formal alliance mechanics between factions.

Alliance types:
- Non-aggression: Cannot attack each other
- Defensive: Join wars when ally is attacked
- Offensive: Coordinate attacks together

Alliances have duration (in turns) and can be broken with reputation penalty.
"""
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from ..models import GameState
from i18n import i18n


class AllianceType(Enum):
    """Types of formal alliances."""
    NON_AGGRESSION = "non_aggression"
    DEFENSIVE = "defensive"
    OFFENSIVE = "offensive"


@dataclass
class Alliance:
    """A formal alliance between two factions."""
    faction_a: str
    faction_b: str
    alliance_type: AllianceType
    duration: int  # Remaining turns
    proposer: str  # Who proposed it

    def involves(self, faction: str) -> bool:
        return faction in (self.faction_a, self.faction_b)

    def get_partner(self, faction: str) -> Optional[str]:
        if faction == self.faction_a:
            return self.faction_b
        elif faction == self.faction_b:
            return self.faction_a
        return None


# Relation requirements to propose alliances
ALLIANCE_RELATION_REQUIREMENTS = {
    AllianceType.NON_AGGRESSION: -10,  # Even slightly hostile factions can agree
    AllianceType.DEFENSIVE: 10,
    AllianceType.OFFENSIVE: 30,
}

ALLIANCE_DURATIONS = {
    AllianceType.NON_AGGRESSION: 12,  # 12 turns (1 year)
    AllianceType.DEFENSIVE: 8,
    AllianceType.OFFENSIVE: 6,
}

BREAK_ALLIANCE_PENALTY = -30  # Relations drop when breaking alliance
ALLIANCE_RELATION_BOOST = 15  # Relations boost when forming alliance


def get_alliances(game_state: GameState) -> List[Alliance]:
    """Get current alliances from game state."""
    return getattr(game_state, 'alliances', [])


def _set_alliances(game_state: GameState, alliances: List[Alliance]) -> None:
    """Set alliances on game state."""
    game_state.alliances = alliances


def find_alliance(game_state: GameState, faction_a: str, faction_b: str) -> Optional[Alliance]:
    """Find existing alliance between two factions."""
    for a in get_alliances(game_state):
        if a.involves(faction_a) and a.involves(faction_b):
            return a
    return None


def propose_alliance(game_state: GameState, target_faction: str,
                     alliance_type_str: str) -> Dict[str, Any]:
    """
    Propose an alliance to another faction.

    Args:
        game_state: Current game state
        target_faction: Faction to propose alliance to
        alliance_type_str: Type of alliance (non_aggression, defensive, offensive)

    Returns:
        Dict with success and message
    """
    try:
        atype = AllianceType(alliance_type_str)
    except ValueError:
        return {"success": False, "message": i18n.t("alliance.invalid_type",
                default="Invalid alliance type. Options: non_aggression, defensive, offensive")}

    player = game_state.player_faction
    if target_faction == player:
        return {"success": False, "message": i18n.t("alliance.self",
                default="Cannot form alliance with yourself.")}

    target = game_state.factions.get(target_faction)
    if not target:
        return {"success": False, "message": i18n.t("alliance.no_faction",
                default="Faction not found.")}

    # Check existing alliance
    existing = find_alliance(game_state, player, target_faction)
    if existing:
        return {"success": False, "message": i18n.t("alliance.already_allied",
                faction=target_faction,
                default=f"Already have an alliance with {target_faction}.")}

    # Check relations
    player_faction = game_state.factions[player]
    relations = player_faction.relations.get(target_faction, 0)
    required = ALLIANCE_RELATION_REQUIREMENTS[atype]

    if relations < required:
        return {"success": False, "message": i18n.t("alliance.relations_too_low",
                faction=target_faction, required=required,
                default=f"Relations with {target_faction} too low. Need {required}, have {relations}.")}

    # AI acceptance check based on relations
    acceptance_chance = 0.3 + (relations / 200.0)
    if random.random() > acceptance_chance:
        return {"success": False, "message": i18n.t("alliance.rejected",
                faction=target_faction,
                default=f"{target_faction} rejects your proposal.")}

    # Create alliance
    alliance = Alliance(
        faction_a=player,
        faction_b=target_faction,
        alliance_type=atype,
        duration=ALLIANCE_DURATIONS[atype],
        proposer=player
    )

    alliances = get_alliances(game_state)
    alliances.append(alliance)
    _set_alliances(game_state, alliances)

    # Boost relations
    player_faction.relations[target_faction] = min(100,
        player_faction.relations.get(target_faction, 0) + ALLIANCE_RELATION_BOOST)
    target.relations[player] = min(100,
        target.relations.get(player, 0) + ALLIANCE_RELATION_BOOST)

    type_name = atype.value.replace("_", " ").title()
    return {"success": True, "message": i18n.t("alliance.formed",
            faction=target_faction, type=type_name,
            default=f"{type_name} alliance formed with {target_faction}!")}


def break_alliance(game_state: GameState, target_faction: str) -> Dict[str, Any]:
    """
    Break an existing alliance.

    Args:
        game_state: Current game state
        target_faction: Faction to break alliance with

    Returns:
        Dict with success and message
    """
    player = game_state.player_faction
    alliance = find_alliance(game_state, player, target_faction)

    if not alliance:
        return {"success": False, "message": i18n.t("alliance.no_alliance",
                faction=target_faction,
                default=f"No alliance exists with {target_faction}.")}

    # Remove alliance
    alliances = get_alliances(game_state)
    alliances.remove(alliance)
    _set_alliances(game_state, alliances)

    # Penalty
    player_faction = game_state.factions[player]
    target = game_state.factions.get(target_faction)

    player_faction.relations[target_faction] = max(-100,
        player_faction.relations.get(target_faction, 0) + BREAK_ALLIANCE_PENALTY)
    if target:
        target.relations[player] = max(-100,
            target.relations.get(player, 0) + BREAK_ALLIANCE_PENALTY)

    return {"success": True, "message": i18n.t("alliance.broken",
            faction=target_faction,
            default=f"Alliance with {target_faction} broken! Reputation suffers.")}


def is_allied(game_state: GameState, faction_a: str, faction_b: str) -> bool:
    """Check if two factions have any alliance."""
    return find_alliance(game_state, faction_a, faction_b) is not None


def can_attack(game_state: GameState, attacker: str, defender: str) -> Dict[str, Any]:
    """
    Check if an attack is allowed considering alliances.

    Returns dict with allowed bool and message.
    """
    alliance = find_alliance(game_state, attacker, defender)
    if alliance:
        return {"allowed": False, "message": i18n.t("alliance.cannot_attack",
                faction=defender,
                default=f"Cannot attack {defender} - you have an alliance! Break it first.")}
    return {"allowed": True, "message": ""}


def get_defensive_allies(game_state: GameState, defender: str, attacker: str) -> List[str]:
    """Get factions that would join to defend an ally."""
    allies = []
    for a in get_alliances(game_state):
        if not a.involves(defender):
            continue
        if a.alliance_type in (AllianceType.DEFENSIVE, AllianceType.OFFENSIVE):
            partner = a.get_partner(defender)
            if partner and partner != attacker:
                allies.append(partner)
    return allies


def process_alliance_turns(game_state: GameState) -> List[str]:
    """
    Process alliance durations at end of turn.
    Decrements duration and removes expired alliances.

    Returns list of messages about expired alliances.
    """
    messages = []
    alliances = get_alliances(game_state)
    expired = []

    for a in alliances:
        a.duration -= 1
        if a.duration <= 0:
            expired.append(a)
            type_name = a.alliance_type.value.replace("_", " ").title()
            messages.append(i18n.t("alliance.expired",
                            faction_a=a.faction_a, faction_b=a.faction_b, type=type_name,
                            default=f"{type_name} alliance between {a.faction_a} and {a.faction_b} has expired."))

    for a in expired:
        alliances.remove(a)
    _set_alliances(game_state, alliances)

    return messages


def list_alliances(game_state: GameState) -> List[Dict[str, Any]]:
    """List all current alliances for display."""
    result = []
    for a in get_alliances(game_state):
        result.append({
            "faction_a": a.faction_a,
            "faction_b": a.faction_b,
            "type": a.alliance_type.value,
            "duration": a.duration,
        })
    return result
