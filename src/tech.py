"""
Technology System - Loading and querying tech tree.
"""
import json
import os
from typing import List, Optional
from .models import Technology


def load_technologies() -> List[Technology]:
    """Load all technologies from JSON data file."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "technologies.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        techs = []
        for t in data["technologies"]:
            techs.append(Technology(
                id=t["id"],
                category=t["category"],
                name_key=t["name_key"],
                cost=t["cost"],
                turns=t["turns"],
                prerequisites=t.get("prerequisites", []),
                effects=t.get("effects", {})
            ))
        return techs
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def get_technology(tech_id: str) -> Optional[Technology]:
    """Get a specific technology by ID."""
    for tech in load_technologies():
        if tech.id == tech_id:
            return tech
    return None


def get_available_techs(researched: List[str]) -> List[Technology]:
    """Get technologies available for research (prerequisites met, not yet researched)."""
    all_techs = load_technologies()
    available = []
    for tech in all_techs:
        if tech.id in researched:
            continue
        if all(prereq in researched for prereq in tech.prerequisites):
            available.append(tech)
    return available
