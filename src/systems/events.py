"""
Random Event System

Events trigger based on game state conditions (season, weather, morale).
Each event offers player choices that affect gameplay.
"""
import json
import os
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from ..models import GameState, get_current_season
from i18n import i18n


@dataclass
class EventChoice:
    """A choice the player can make for an event."""
    label_key: str
    effects: Dict[str, int] = field(default_factory=dict)


@dataclass
class GameEvent:
    """A random event that can occur during gameplay."""
    id: str
    event_type: str  # positive, negative, neutral
    probability: float
    conditions: Dict[str, Any]
    title_key: str
    description_key: str
    choices: List[EventChoice] = field(default_factory=list)


def load_random_events() -> List[GameEvent]:
    """Load random events from JSON data file."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "events", "random.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        events = []
        for e in data["events"]:
            choices = [EventChoice(label_key=c["label_key"], effects=c["effects"])
                       for c in e.get("choices", [])]
            events.append(GameEvent(
                id=e["id"],
                event_type=e["type"],
                probability=e["probability"],
                conditions=e.get("conditions", {}),
                title_key=e["title_key"],
                description_key=e["description_key"],
                choices=choices
            ))
        return events
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def _check_conditions(event: GameEvent, game_state: GameState, city_name: str) -> bool:
    """Check if event conditions are met."""
    conditions = event.conditions

    if "season" in conditions:
        current_season = get_current_season(game_state.month)
        if current_season.value != conditions["season"]:
            return False

    if "weather" in conditions:
        if game_state.weather.value != conditions["weather"]:
            return False

    if "morale_below" in conditions:
        city = game_state.cities.get(city_name)
        if city and city.morale >= conditions["morale_below"]:
            return False

    return True


def check_event_triggers(game_state: GameState) -> Optional[Dict[str, Any]]:
    """
    Check if any random event should trigger this turn.

    Args:
        game_state: Current game state

    Returns:
        Dict with event details and target city, or None
    """
    events = load_random_events()
    if not events:
        return None

    faction = game_state.factions.get(game_state.player_faction)
    if not faction or not faction.cities:
        return None

    # Pick a random city from player's faction
    target_city = random.choice(faction.cities)

    # Check each event
    for event in events:
        if random.random() < event.probability:
            if _check_conditions(event, game_state, target_city):
                return {
                    "event": event,
                    "city": target_city
                }

    return None


def apply_event_choice(game_state: GameState, event: GameEvent,
                       choice_index: int, city_name: str) -> Dict[str, Any]:
    """
    Apply the effects of a player's event choice.

    Args:
        game_state: Current game state
        event: The triggered event
        choice_index: Index of chosen option (0-based)
        city_name: City affected

    Returns:
        Dict describing applied effects
    """
    if choice_index < 0 or choice_index >= len(event.choices):
        return {"error": "Invalid choice"}

    choice = event.choices[choice_index]
    city = game_state.cities.get(city_name)
    if not city:
        return {"error": "City not found"}

    applied = {}
    for stat, value in choice.effects.items():
        if hasattr(city, stat):
            current = getattr(city, stat)
            new_val = max(0, current + value)
            setattr(city, stat, new_val)
            applied[stat] = value

    return {"applied": applied, "city": city_name}
