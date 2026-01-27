"""
Tactical Battle System

This module implements the tactical battle mechanics for Sango Text Sim.
Battles are multi-turn engagements with terrain effects, weather conditions,
positioning, and various tactical actions.

Features:
- Multi-turn battles with tactical choices
- Terrain modifiers (Plains, Mountain, Forest, Coastal, River)
- Weather effects (Clear, Rain, Snow, Drought, Fog)
- Battle actions: Attack, Defend, Flank, Fire Attack, Retreat
- Siege mechanics for walled cities
- Morale and supply management
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Tuple
import random

from src.models import BattleState, TerrainType
from src.constants import (
    # Terrain effects
    PLAINS_COMBAT_MODIFIER,
    MOUNTAIN_DEFENSE_BONUS,
    MOUNTAIN_CAVALRY_PENALTY,
    FOREST_AMBUSH_BONUS,
    FOREST_FIRE_ATTACK_BONUS,
    RIVER_CROSSING_PENALTY,
    RIVER_CROSSING_ATTRITION,
    # Weather effects
    RAIN_FIRE_ATTACK_PENALTY,
    RAIN_MOVEMENT_PENALTY,
    DROUGHT_FIRE_ATTACK_BONUS,
    SNOW_MOVEMENT_PENALTY,
    SNOW_ATTRITION_RATE,
    WINTER_ATTRITION_RATE,
)


class BattleAction(Enum):
    """
    Available tactical actions in battle.

    - ATTACK: Standard assault, balanced offense
    - DEFEND: Defensive stance, reduces incoming damage
    - FLANK: Flanking maneuver, bonus damage but riskier
    - FIRE_ATTACK: Fire-based attack, affected by weather/terrain
    - RETREAT: Withdraw from battle
    """
    ATTACK = "attack"
    DEFEND = "defend"
    FLANK = "flank"
    FIRE_ATTACK = "fire_attack"
    RETREAT = "retreat"


def create_battle(
    attacker_city: str,
    defender_city: str,
    attacker_faction: str,
    defender_faction: str,
    attacker_commander: str,
    defender_commander: str,
    attacker_troops: int,
    defender_troops: int,
    terrain: TerrainType,
    weather: str = None
) -> BattleState:
    """
    Create a new battle state.

    Args:
        attacker_city: Name of attacking city
        defender_city: Name of defending city
        attacker_faction: Attacking faction name
        defender_faction: Defending faction name
        attacker_commander: Commanding officer of attackers
        defender_commander: Commanding officer of defenders
        attacker_troops: Number of attacking troops
        defender_troops: Number of defending troops
        terrain: Terrain type of battlefield
        weather: Weather conditions (optional)

    Returns:
        BattleState object ready for tactical combat
    """
    return BattleState(
        attacker_city=attacker_city,
        defender_city=defender_city,
        attacker_faction=attacker_faction,
        defender_faction=defender_faction,
        attacker_commander=attacker_commander,
        defender_commander=defender_commander,
        attacker_troops=attacker_troops,
        defender_troops=defender_troops,
        terrain=terrain,
        weather=weather,
        round=0,
        attacker_morale=70,
        defender_morale=70,
        supply_days=10,
        siege_progress=0,
        combat_log=[]
    )


def apply_terrain_modifiers(
    terrain: TerrainType,
    action: BattleAction
) -> Tuple[float, float]:
    """
    Calculate terrain modifiers for attack and defense.

    Args:
        terrain: Terrain type of battlefield
        action: Battle action being performed

    Returns:
        Tuple of (attacker_modifier, defender_modifier)
    """
    atk_mod = 1.0
    def_mod = 1.0

    if terrain == TerrainType.PLAINS:
        # Plains have no modifiers
        pass

    elif terrain == TerrainType.MOUNTAIN:
        # Mountains favor defenders
        def_mod = MOUNTAIN_DEFENSE_BONUS
        # Attacking uphill is harder
        atk_mod = 0.85
        # Cavalry is less effective
        if action == BattleAction.FLANK:
            atk_mod *= MOUNTAIN_CAVALRY_PENALTY

    elif terrain == TerrainType.FOREST:
        # Forest enhances fire attacks and ambushes
        if action == BattleAction.FIRE_ATTACK:
            atk_mod = FOREST_FIRE_ATTACK_BONUS
        elif action == BattleAction.FLANK:
            atk_mod = FOREST_AMBUSH_BONUS

    elif terrain == TerrainType.RIVER:
        # River crossing penalty for attackers
        atk_mod = RIVER_CROSSING_PENALTY

    elif terrain == TerrainType.COASTAL:
        # Coastal terrain gives defender naval advantage
        def_mod = 1.15

    return atk_mod, def_mod


def apply_weather_modifiers(weather: str, action: BattleAction) -> float:
    """
    Calculate weather modifier for an action.

    Args:
        weather: Weather condition
        action: Battle action being performed

    Returns:
        Modifier for the action (1.0 = no effect)
    """
    if not weather or weather == "clear":
        return 1.0

    if weather == "rain":
        if action == BattleAction.FIRE_ATTACK:
            return RAIN_FIRE_ATTACK_PENALTY
        else:
            return RAIN_MOVEMENT_PENALTY

    elif weather == "drought":
        if action == BattleAction.FIRE_ATTACK:
            return DROUGHT_FIRE_ATTACK_BONUS
        return 1.0

    elif weather == "snow":
        # Snow penalizes all movement and attacks
        return SNOW_MOVEMENT_PENALTY

    elif weather == "fog":
        # Fog reduces ranged effectiveness but helps ambushes
        if action == BattleAction.FLANK:
            return 1.30  # +30% ambush in fog
        else:
            return 0.80  # -20% visibility penalty

    return 1.0


def calculate_damage(
    attacker_troops: int,
    attacker_morale: int,
    defender_troops: int,
    defender_morale: int,
    attacker_action: BattleAction,
    defender_action: BattleAction,
    terrain_atk_mod: float,
    terrain_def_mod: float,
    weather_atk_mod: float,
    weather_def_mod: float
) -> Tuple[int, int]:
    """
    Calculate casualties for both sides in a battle turn.

    Args:
        attacker_troops: Number of attacking troops
        attacker_morale: Attacker morale (0-100)
        defender_troops: Number of defending troops
        defender_morale: Defender morale (0-100)
        attacker_action: Action chosen by attacker
        defender_action: Action chosen by defender
        terrain_atk_mod: Terrain modifier for attacker
        terrain_def_mod: Terrain modifier for defender
        weather_atk_mod: Weather modifier for attacker
        weather_def_mod: Weather modifier for defender

    Returns:
        Tuple of (attacker_casualties, defender_casualties)
    """
    # Base combat power
    atk_power = attacker_troops * (1 + attacker_morale / 100.0)
    def_power = defender_troops * (1 + defender_morale / 100.0)

    # Action modifiers
    atk_action_mod = 1.0
    def_action_mod = 1.0

    if attacker_action == BattleAction.ATTACK:
        atk_action_mod = 1.0
    elif attacker_action == BattleAction.DEFEND:
        atk_action_mod = 0.5  # Defending reduces offensive power
        def_action_mod = 0.5  # But also reduces damage taken
    elif attacker_action == BattleAction.FLANK:
        atk_action_mod = 1.3  # +30% damage
    elif attacker_action == BattleAction.FIRE_ATTACK:
        atk_action_mod = 1.4  # +40% damage base
    elif attacker_action == BattleAction.RETREAT:
        atk_action_mod = 0.0  # No damage when retreating
        def_action_mod = 1.5  # But vulnerable to pursuit

    if defender_action == BattleAction.DEFEND:
        def_action_mod *= 0.5  # Defending halves incoming damage
    elif defender_action == BattleAction.FLANK:
        # Counter-flanking
        def_power *= 1.2
    elif defender_action == BattleAction.FIRE_ATTACK:
        def_power *= 1.2

    # Apply all modifiers
    atk_power *= atk_action_mod * terrain_atk_mod * weather_atk_mod
    def_power *= def_action_mod * terrain_def_mod * weather_def_mod

    # Calculate casualties as percentage of troops
    # More powerful attacks cause more casualties
    atk_casualties = 0
    def_casualties = 0

    if atk_power > 0:
        # Defender takes casualties based on attacker power
        casualty_rate = min(0.25, (atk_power / (def_power + atk_power)) * 0.4)
        def_casualties = int(defender_troops * casualty_rate * random.uniform(0.8, 1.2))

    if def_power > 0 and attacker_action != BattleAction.RETREAT:
        # Attacker takes casualties based on defender power
        casualty_rate = min(0.25, (def_power / (atk_power + def_power)) * 0.4)
        atk_casualties = int(attacker_troops * casualty_rate * random.uniform(0.8, 1.2))

    # Ensure casualties don't exceed troop counts
    atk_casualties = min(atk_casualties, attacker_troops)
    def_casualties = min(def_casualties, defender_troops)

    return atk_casualties, def_casualties


def calculate_siege_progress(
    battle: BattleState,
    walls_level: int,
    is_fire_attack: bool = False
) -> int:
    """
    Calculate siege progress per turn.

    Args:
        battle: Current battle state
        walls_level: Defense level of city walls
        is_fire_attack: Whether fire attack is being used

    Returns:
        Siege progress increase (0-100)
    """
    # Base progress depends on attacker troops vs walls
    base_progress = (battle.attacker_troops / 1000.0) * (100.0 / (walls_level + 10))

    # Fire attacks are more effective against walls
    if is_fire_attack:
        base_progress *= 2.0

    # Weather affects siege
    if battle.weather == "rain":
        base_progress *= 0.7  # Harder to siege in rain
    elif battle.weather == "drought":
        base_progress *= 1.3  # Easier with fire in drought

    # Random variation
    progress = int(base_progress * random.uniform(0.8, 1.2))

    return min(progress, 20)  # Max 20% progress per turn


def process_battle_turn(
    battle: BattleState,
    attacker_action: BattleAction,
    defender_action: BattleAction
) -> Dict[str, Any]:
    """
    Process one turn of tactical battle.

    Args:
        battle: Current battle state (modified in place)
        attacker_action: Action chosen by attacker
        defender_action: Action chosen by defender

    Returns:
        Dictionary with turn results
    """
    battle.round += 1

    # Check for retreat
    if attacker_action == BattleAction.RETREAT:
        battle.combat_log.append(f"Round {battle.round}: {battle.attacker_commander} orders a retreat!")
        return {
            "action": "retreat",
            "message": f"{battle.attacker_commander} retreats from {battle.defender_city}!",
            "attacker_casualties": 0,
            "defender_casualties": 0
        }

    # Apply terrain modifiers
    terrain_atk_mod, terrain_def_mod = apply_terrain_modifiers(battle.terrain, attacker_action)

    # Apply weather modifiers
    weather_atk_mod = apply_weather_modifiers(battle.weather, attacker_action)
    weather_def_mod = apply_weather_modifiers(battle.weather, defender_action)

    # Calculate casualties
    atk_casualties, def_casualties = calculate_damage(
        battle.attacker_troops,
        battle.attacker_morale,
        battle.defender_troops,
        battle.defender_morale,
        attacker_action,
        defender_action,
        terrain_atk_mod,
        terrain_def_mod,
        weather_atk_mod,
        weather_def_mod
    )

    # Apply casualties
    battle.attacker_troops -= atk_casualties
    battle.defender_troops -= def_casualties

    # Calculate morale changes based on casualties
    if battle.attacker_troops > 0:
        atk_casualty_rate = atk_casualties / (battle.attacker_troops + atk_casualties)
        morale_loss = int(atk_casualty_rate * 20)
        battle.attacker_morale = max(0, battle.attacker_morale - morale_loss)

    if battle.defender_troops > 0:
        def_casualty_rate = def_casualties / (battle.defender_troops + def_casualties)
        morale_loss = int(def_casualty_rate * 20)
        battle.defender_morale = max(0, battle.defender_morale - morale_loss)

    # Siege progress (only if attacking, not defending)
    if attacker_action != BattleAction.DEFEND:
        # Note: walls_level would be passed from game state
        # For now, assume moderate walls
        is_fire = attacker_action == BattleAction.FIRE_ATTACK
        progress = calculate_siege_progress(battle, 50, is_fire)
        battle.siege_progress = min(100, battle.siege_progress + progress)

    # Supply consumption
    battle.supply_days -= 1

    # Weather attrition
    if battle.weather == "snow":
        snow_casualties = int(battle.attacker_troops * SNOW_ATTRITION_RATE)
        battle.attacker_troops -= snow_casualties
        atk_casualties += snow_casualties

    # River crossing attrition (first few turns)
    if battle.terrain == TerrainType.RIVER and battle.round <= 2:
        river_casualties = int(battle.attacker_troops * RIVER_CROSSING_ATTRITION)
        battle.attacker_troops -= river_casualties
        atk_casualties += river_casualties

    # Log the turn
    action_desc = {
        BattleAction.ATTACK: "launches an assault",
        BattleAction.DEFEND: "takes a defensive stance",
        BattleAction.FLANK: "attempts a flanking maneuver",
        BattleAction.FIRE_ATTACK: "unleashes fire attack",
        BattleAction.RETREAT: "retreats"
    }

    log_entry = (
        f"Round {battle.round}: {battle.attacker_commander} {action_desc[attacker_action]}, "
        f"{battle.defender_commander} {action_desc[defender_action]}. "
        f"Casualties: Attacker {atk_casualties}, Defender {def_casualties}"
    )
    battle.combat_log.append(log_entry)

    return {
        "action": "combat",
        "message": log_entry,
        "attacker_casualties": atk_casualties,
        "defender_casualties": def_casualties,
        "siege_progress": battle.siege_progress
    }


def check_battle_end(battle: BattleState) -> Dict[str, Any]:
    """
    Check if battle has ended and determine winner.

    Args:
        battle: Current battle state

    Returns:
        Dictionary with 'ended' boolean, 'winner', and 'reason'
    """
    # Check troop depletion
    if battle.attacker_troops <= 0:
        return {
            "ended": True,
            "winner": "defender",
            "reason": "Attacking army eliminated"
        }

    if battle.defender_troops <= 0:
        return {
            "ended": True,
            "winner": "attacker",
            "reason": "Defending army eliminated"
        }

    # Check morale break (below 10)
    if battle.attacker_morale < 10:
        return {
            "ended": True,
            "winner": "defender",
            "reason": "Attacker morale broken"
        }

    if battle.defender_morale < 10:
        return {
            "ended": True,
            "winner": "attacker",
            "reason": "Defender morale broken"
        }

    # Check siege breakthrough
    if battle.siege_progress >= 100:
        return {
            "ended": True,
            "winner": "attacker",
            "reason": "City walls breached"
        }

    # Check supply exhaustion
    if battle.supply_days <= 0:
        return {
            "ended": True,
            "winner": "defender",
            "reason": "Attacker supplies exhausted"
        }

    # Battle continues
    return {
        "ended": False,
        "winner": None,
        "reason": None
    }


class TacticalBattle:
    """
    Wrapper class for managing tactical battles.

    This class provides a higher-level interface for battle management,
    including state tracking and result reporting.
    """

    def __init__(
        self,
        attacker_city: str,
        defender_city: str,
        attacker_faction: str,
        defender_faction: str,
        attacker_commander: str,
        defender_commander: str,
        attacker_troops: int,
        defender_troops: int,
        terrain: TerrainType,
        walls_level: int,
        weather: str = None
    ):
        """
        Initialize a tactical battle.

        Args:
            attacker_city: Name of attacking city
            defender_city: Name of defending city
            attacker_faction: Attacking faction
            defender_faction: Defending faction
            attacker_commander: Attacking commander
            defender_commander: Defending commander
            attacker_troops: Number of attacking troops
            defender_troops: Number of defending troops
            terrain: Terrain type
            walls_level: Defense level of city walls
            weather: Weather conditions
        """
        self.battle_state = create_battle(
            attacker_city,
            defender_city,
            attacker_faction,
            defender_faction,
            attacker_commander,
            defender_commander,
            attacker_troops,
            defender_troops,
            terrain,
            weather
        )
        self.walls_level = walls_level
        self.is_active = True

    def execute_turn(
        self,
        attacker_action: BattleAction,
        defender_action: BattleAction
    ) -> Dict[str, Any]:
        """
        Execute one turn of battle.

        Args:
            attacker_action: Action chosen by attacker
            defender_action: Action chosen by defender

        Returns:
            Dictionary with turn results
        """
        if not self.is_active:
            return {"error": "Battle has already ended"}

        result = process_battle_turn(
            self.battle_state,
            attacker_action,
            defender_action
        )

        # Check if battle ended
        end_check = check_battle_end(self.battle_state)
        if end_check["ended"]:
            self.is_active = False
            result["battle_ended"] = True
            result["winner"] = end_check["winner"]
            result["reason"] = end_check["reason"]

        return result

    def get_status(self) -> Dict[str, Any]:
        """
        Get current battle status.

        Returns:
            Dictionary with current battle state
        """
        return {
            "round": self.battle_state.round,
            "attacker_troops": self.battle_state.attacker_troops,
            "defender_troops": self.battle_state.defender_troops,
            "attacker_morale": self.battle_state.attacker_morale,
            "defender_morale": self.battle_state.defender_morale,
            "siege_progress": self.battle_state.siege_progress,
            "supply_days": self.battle_state.supply_days,
            "is_active": self.is_active,
            "combat_log": self.battle_state.combat_log
        }
