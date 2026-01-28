"""
Ability System - Loading and managing officer special abilities.
"""
import json
import os
from typing import List, Optional, Dict
from .models import Ability


def load_abilities() -> List[Ability]:
    """Load all abilities from JSON data file."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "officers", "abilities.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        abilities = []
        for a in data["abilities"]:
            abilities.append(Ability(
                id=a["id"],
                officer=a["officer"],
                name_key=a["name_key"],
                context=a["context"],
                cooldown=a["cooldown"],
                effect=a.get("effect", {})
            ))
        return abilities
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def get_ability(ability_id: str) -> Optional[Ability]:
    """Get a specific ability by ID."""
    for a in load_abilities():
        if a.id == ability_id:
            return a
    return None


def get_officer_abilities(officer_name: str) -> List[Ability]:
    """Get all abilities for a specific officer."""
    return [a for a in load_abilities() if a.officer == officer_name]


def get_officer_ability(officer_name: str, context: str) -> Optional[Ability]:
    """Get an officer's ability for a specific context (battle/duel)."""
    for a in load_abilities():
        if a.officer == officer_name and a.context == context:
            return a
    return None
