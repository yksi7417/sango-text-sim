"""
Building System - Loading and managing city buildings.
"""
import json
import os
from typing import List, Optional
from .models import Building


def load_buildings() -> List[Building]:
    """Load all buildings from JSON data file."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "buildings.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        buildings = []
        for b in data["buildings"]:
            buildings.append(Building(
                id=b["id"],
                name_key=b["name_key"],
                cost=b["cost"],
                turns=b["turns"],
                effects=b.get("effects", {})
            ))
        return buildings
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def get_building(building_id: str) -> Optional[Building]:
    """Get a specific building by ID."""
    for b in load_buildings():
        if b.id == building_id:
            return b
    return None


def get_available_buildings(city_buildings: List[str]) -> List[Building]:
    """Get buildings not yet built in a city."""
    all_buildings = load_buildings()
    return [b for b in all_buildings if b.id not in city_buildings]
