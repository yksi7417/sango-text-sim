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


@dataclass
class HistoricalEvent:
    """A historical event that triggers based on year and conditions."""
    id: str
    year_range: List[int]
    conditions: Dict[str, Any]
    title_key: str
    description_key: str
    effects: Dict[str, Any] = field(default_factory=dict)
    one_time: bool = True


def load_historical_events() -> List[HistoricalEvent]:
    """Load historical events from JSON data file."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "events", "historical.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        events = []
        for e in data["events"]:
            events.append(HistoricalEvent(
                id=e["id"],
                year_range=e["year_range"],
                conditions=e.get("conditions", {}),
                title_key=e["title_key"],
                description_key=e["description_key"],
                effects=e.get("effects", {}),
                one_time=e.get("one_time", True)
            ))
        return events
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def _check_historical_conditions(event: HistoricalEvent, game_state: GameState) -> bool:
    """Check if historical event conditions are met."""
    if not (event.year_range[0] <= game_state.year <= event.year_range[1]):
        return False

    conditions = event.conditions

    if "officers_in_faction" in conditions:
        faction_name = conditions.get("faction", game_state.player_faction)
        faction = game_state.factions.get(faction_name)
        if not faction:
            return False
        for officer_name in conditions["officers_in_faction"]:
            if officer_name not in faction.officers:
                return False

    if "officer_exists" in conditions:
        if conditions["officer_exists"] not in game_state.officers:
            return False

    if "factions_exist" in conditions:
        for fn in conditions["factions_exist"]:
            if fn not in game_state.factions:
                return False

    if "faction_has_officer" in conditions:
        fho = conditions["faction_has_officer"]
        faction = game_state.factions.get(fho["faction"])
        if not faction or fho["officer"] not in faction.officers:
            return False

    return True


def apply_historical_effects(game_state: GameState, event: HistoricalEvent) -> Dict[str, Any]:
    """Apply the effects of a historical event."""
    effects = event.effects
    applied = {}

    if "relationships" in effects:
        for rel in effects["relationships"]:
            o1 = game_state.officers.get(rel["officer1"])
            o2 = game_state.officers.get(rel["officer2"])
            if o1 and o2:
                o1.relationships[rel["officer2"]] = rel["type"]
                o2.relationships[rel["officer1"]] = rel["type"]
        applied["relationships"] = len(effects["relationships"])

    if "loyalty_boost" in effects:
        for name, boost in effects["loyalty_boost"].items():
            officer = game_state.officers.get(name)
            if officer:
                officer.loyalty = min(100, max(0, officer.loyalty + boost))
        applied["loyalty"] = effects["loyalty_boost"]

    if "morale_boost" in effects:
        for faction_name, boost in effects["morale_boost"].items():
            faction = game_state.factions.get(faction_name)
            if faction:
                for city_name in faction.cities:
                    city = game_state.cities.get(city_name)
                    if city:
                        city.morale = min(100, city.morale + boost)
        applied["morale"] = effects["morale_boost"]

    if "tech_boost" in effects:
        for faction_name, boost in effects["tech_boost"].items():
            faction = game_state.factions.get(faction_name)
            if faction:
                for city_name in faction.cities:
                    city = game_state.cities.get(city_name)
                    if city:
                        city.tech = min(100, city.tech + boost)
        applied["tech"] = effects["tech_boost"]

    if "relations_change" in effects:
        for pair_key, delta in effects["relations_change"].items():
            parts = pair_key.split("_")
            if len(parts) == 2:
                f1, f2 = parts
                if f1 in game_state.factions and f2 in game_state.factions:
                    fac1 = game_state.factions[f1]
                    fac2 = game_state.factions[f2]
                    fac1.relations[f2] = max(-100, min(100, fac1.relations.get(f2, 0) + delta))
                    fac2.relations[f1] = max(-100, min(100, fac2.relations.get(f1, 0) + delta // 2))
        applied["relations"] = effects["relations_change"]

    return applied


def check_historical_events(game_state: GameState, triggered_ids: List[str]) -> Optional[Dict[str, Any]]:
    """
    Check if any historical event should trigger.

    Args:
        game_state: Current game state
        triggered_ids: List of already triggered event IDs

    Returns:
        Dict with event and applied effects, or None
    """
    events = load_historical_events()
    for event in events:
        if event.one_time and event.id in triggered_ids:
            continue
        if _check_historical_conditions(event, game_state):
            applied = apply_historical_effects(game_state, event)
            title = i18n.t(event.title_key, default=event.id)
            desc = i18n.t(event.description_key, default="")
            msg = f"[Historical] {title}: {desc}"
            game_state.log(msg)
            return {
                "event": event,
                "applied": applied,
                "message": msg
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
