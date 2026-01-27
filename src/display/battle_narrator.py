"""
Battle Narrative Generator

This module generates dramatic prose descriptions of battle events,
making combat feel more engaging and immersive.

Features:
- Multiple narrative templates per event type
- Commander names integrated into narratives
- Terrain-aware descriptions
- Weather-aware descriptions
- Casualty-aware intensity
"""
import random
from typing import Dict, Any
from src.models import TerrainType
from i18n import i18n


def _get_terrain_flavor(terrain: TerrainType) -> str:
    """
    Get terrain-specific flavor text.

    Args:
        terrain: Terrain type of battlefield

    Returns:
        Localized terrain flavor text
    """
    if terrain == TerrainType.PLAINS:
        return i18n.t("battle.narrator.terrain.plains")
    elif terrain == TerrainType.MOUNTAIN:
        return i18n.t("battle.narrator.terrain.mountain")
    elif terrain == TerrainType.FOREST:
        return i18n.t("battle.narrator.terrain.forest")
    elif terrain == TerrainType.RIVER:
        return i18n.t("battle.narrator.terrain.river")
    elif terrain == TerrainType.COASTAL:
        return i18n.t("battle.narrator.terrain.coastal")
    return ""


def _get_weather_flavor(weather: str) -> str:
    """
    Get weather-specific flavor text.

    Args:
        weather: Weather condition

    Returns:
        Localized weather flavor text
    """
    if not weather or weather == "clear":
        return ""

    weather_key = f"battle.narrator.weather.{weather}"
    return i18n.t(weather_key)


def _get_casualty_intensity(attacker_casualties: int, defender_casualties: int) -> str:
    """
    Determine battle intensity based on casualties.

    Args:
        attacker_casualties: Number of attacker casualties
        defender_casualties: Number of defender casualties

    Returns:
        Intensity descriptor (light, moderate, heavy, devastating)
    """
    total_casualties = attacker_casualties + defender_casualties

    if total_casualties < 100:
        return "light"
    elif total_casualties < 300:
        return "moderate"
    elif total_casualties < 600:
        return "heavy"
    else:
        return "devastating"


def narrate_battle_event(event: Dict[str, Any]) -> str:
    """
    Generate dramatic narrative for a battle event.

    Args:
        event: Dictionary containing:
            - action_type: Type of action (attack, flank, fire_attack, defend, retreat, victory)
            - attacker: Name of attacking commander
            - defender: Name of defending commander
            - terrain: TerrainType enum
            - weather: Weather condition string
            - attacker_casualties: Number (optional)
            - defender_casualties: Number (optional)
            - winner: "attacker" or "defender" (for victory events)
            - reason: Victory reason (for victory events)

    Returns:
        Dramatic narrative string
    """
    action_type = event.get("action_type", "attack")
    attacker = event.get("attacker", "The attacker")
    defender = event.get("defender", "The defender")
    terrain = event.get("terrain", TerrainType.PLAINS)
    weather = event.get("weather", "clear")

    # Get flavor texts
    terrain_flavor = _get_terrain_flavor(terrain)
    weather_flavor = _get_weather_flavor(weather)

    # Handle different action types
    if action_type == "attack":
        return _narrate_attack(attacker, defender, terrain_flavor, weather_flavor, event)
    elif action_type == "flank":
        return _narrate_flank(attacker, defender, terrain_flavor, weather_flavor, event)
    elif action_type == "fire_attack":
        return _narrate_fire_attack(attacker, defender, terrain_flavor, weather_flavor, event)
    elif action_type == "defend":
        return _narrate_defend(attacker, defender, terrain_flavor, weather_flavor, event)
    elif action_type == "retreat":
        return _narrate_retreat(attacker, defender, terrain_flavor, weather_flavor, event)
    elif action_type == "victory":
        return _narrate_victory(event)
    else:
        # Fallback
        return i18n.t("battle.narrator.generic", attacker=attacker, defender=defender)


def _narrate_attack(attacker: str, defender: str, terrain: str, weather: str, event: Dict[str, Any]) -> str:
    """Generate narrative for standard attack action."""
    attacker_casualties = event.get("attacker_casualties", 0)
    defender_casualties = event.get("defender_casualties", 0)
    intensity = _get_casualty_intensity(attacker_casualties, defender_casualties)

    # Multiple templates for variety
    templates = [
        "battle.narrator.attack.template1",
        "battle.narrator.attack.template2",
        "battle.narrator.attack.template3"
    ]

    template = random.choice(templates)

    narrative = i18n.t(template,
                      attacker=attacker,
                      defender=defender,
                      terrain=terrain,
                      weather=weather,
                      intensity=intensity)

    return narrative


def _narrate_flank(attacker: str, defender: str, terrain: str, weather: str, event: Dict[str, Any]) -> str:
    """Generate narrative for flanking maneuver."""
    attacker_casualties = event.get("attacker_casualties", 0)
    defender_casualties = event.get("defender_casualties", 0)

    templates = [
        "battle.narrator.flank.template1",
        "battle.narrator.flank.template2",
        "battle.narrator.flank.template3"
    ]

    template = random.choice(templates)

    narrative = i18n.t(template,
                      attacker=attacker,
                      defender=defender,
                      terrain=terrain,
                      weather=weather)

    return narrative


def _narrate_fire_attack(attacker: str, defender: str, terrain: str, weather: str, event: Dict[str, Any]) -> str:
    """Generate narrative for fire attack."""
    templates = [
        "battle.narrator.fire.template1",
        "battle.narrator.fire.template2",
        "battle.narrator.fire.template3"
    ]

    template = random.choice(templates)

    narrative = i18n.t(template,
                      attacker=attacker,
                      defender=defender,
                      terrain=terrain,
                      weather=weather)

    return narrative


def _narrate_defend(attacker: str, defender: str, terrain: str, weather: str, event: Dict[str, Any]) -> str:
    """Generate narrative for defensive action."""
    templates = [
        "battle.narrator.defend.template1",
        "battle.narrator.defend.template2",
        "battle.narrator.defend.template3"
    ]

    template = random.choice(templates)

    narrative = i18n.t(template,
                      attacker=attacker,
                      defender=defender,
                      terrain=terrain,
                      weather=weather)

    return narrative


def _narrate_retreat(attacker: str, defender: str, terrain: str, weather: str, event: Dict[str, Any]) -> str:
    """Generate narrative for retreat action."""
    templates = [
        "battle.narrator.retreat.template1",
        "battle.narrator.retreat.template2",
        "battle.narrator.retreat.template3"
    ]

    template = random.choice(templates)

    narrative = i18n.t(template,
                      attacker=attacker,
                      defender=defender,
                      terrain=terrain,
                      weather=weather)

    return narrative


def _narrate_victory(event: Dict[str, Any]) -> str:
    """Generate narrative for battle victory/defeat."""
    winner = event.get("winner", "attacker")
    attacker = event.get("attacker", "The attacker")
    defender = event.get("defender", "The defender")
    reason = event.get("reason", "")

    if winner == "attacker":
        templates = [
            "battle.narrator.victory.attacker_wins1",
            "battle.narrator.victory.attacker_wins2",
            "battle.narrator.victory.attacker_wins3"
        ]
    else:
        templates = [
            "battle.narrator.victory.defender_wins1",
            "battle.narrator.victory.defender_wins2",
            "battle.narrator.victory.defender_wins3"
        ]

    template = random.choice(templates)

    narrative = i18n.t(template,
                      attacker=attacker,
                      defender=defender,
                      reason=reason)

    return narrative
