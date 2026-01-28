"""
Persistence - Save and load game state to/from JSON files.

This module handles game state serialization and deserialization:
- Save game state to JSON files
- Load game state from JSON files
- Handle file errors gracefully
"""

import json
import os
from dataclasses import asdict
from typing import Optional
from .models import Officer, City, Faction, GameState, TerrainType, BattleState, WeatherType


def save_game(game_state: GameState, filepath: str) -> bool:
    """
    Save the current game state to a JSON file.
    
    Serializes all game data including:
    - Game metadata (year, month, faction, ruler, difficulty)
    - All cities with resources and stats
    - All factions with relations and territories
    - All officers with stats and assignments
    - Map adjacency data
    
    Args:
        game_state: Current game state to save
        filepath: Path to save file
    
    Returns:
        True if save successful, False otherwise
    """
    try:
        # Prepare serializable data
        data = asdict(game_state)

        # Convert complex objects to dictionaries
        data["cities"] = {}
        for k, v in game_state.cities.items():
            city_data = asdict(v)
            # Convert TerrainType enum to string
            if isinstance(city_data.get('terrain'), TerrainType):
                city_data['terrain'] = city_data['terrain'].value
            data["cities"][k] = city_data

        data["factions"] = {
            k: {
                "name": f.name,
                "relations": f.relations,
                "cities": f.cities,
                "officers": f.officers,
                "ruler": f.ruler,
                "technologies": f.technologies
            }
            for k, f in game_state.factions.items()
        }
        data["officers"] = {k: asdict(v) for k, v in game_state.officers.items()}

        # Convert WeatherType enum to string
        if isinstance(data.get('weather'), WeatherType):
            data['weather'] = data['weather'].value

        # Save active battle state
        if game_state.active_battle:
            battle_data = asdict(game_state.active_battle)
            # Convert TerrainType enum to string
            if isinstance(battle_data.get('terrain'), TerrainType):
                battle_data['terrain'] = battle_data['terrain'].value
            data["active_battle"] = battle_data
        else:
            data["active_battle"] = None

        # Write to file with UTF-8 encoding to support Chinese characters
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True
    
    except (IOError, OSError, ValueError) as e:
        # Handle file I/O errors
        return False


def load_game(game_state: GameState, filepath: str) -> Optional[str]:
    """
    Load game state from a JSON file.
    
    Deserializes saved game data and updates the game state.
    
    Args:
        game_state: Game state to update
        filepath: Path to save file
    
    Returns:
        None if successful, error message string if failed
    """
    # Check if file exists
    if not os.path.exists(filepath):
        return "errors.file_missing"
    
    try:
        # Read from file
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Restore game metadata
        game_state.year = data["year"]
        game_state.month = data["month"]
        game_state.player_faction = data["player_faction"]
        game_state.player_ruler = data["player_ruler"]
        game_state.difficulty = data.get("difficulty", "Normal")
        game_state.messages = []  # Clear messages on load
        
        # Restore cities
        game_state.cities = {}
        for k, v in data["cities"].items():
            # Convert terrain string back to TerrainType enum
            if 'terrain' in v and isinstance(v['terrain'], str):
                v['terrain'] = TerrainType(v['terrain'])
            game_state.cities[k] = City(**v)
        
        # Restore factions
        game_state.factions = {}
        for k, fv in data["factions"].items():
            game_state.factions[k] = Faction(
                name=fv["name"],
                relations=fv["relations"],
                cities=fv["cities"],
                officers=fv.get("officers", []),
                ruler=fv.get("ruler", ""),
                technologies=fv.get("technologies", [])
            )
        
        # Restore officers
        game_state.officers = {k: Officer(**v) for k, v in data["officers"].items()}
        
        # Restore map adjacency
        game_state.adj = {k: v for k, v in data["adj"].items()}

        # Restore weather
        weather_str = data.get("weather", "clear")
        if isinstance(weather_str, str):
            game_state.weather = WeatherType(weather_str)
        game_state.weather_turns_remaining = data.get("weather_turns_remaining", 0)

        # Restore research and construction
        game_state.research_progress = data.get("research_progress", {})
        game_state.construction_queue = data.get("construction_queue", {})

        # Restore active battle state
        if data.get("active_battle"):
            battle_data = data["active_battle"]
            # Convert terrain string back to TerrainType enum
            if 'terrain' in battle_data and isinstance(battle_data['terrain'], str):
                battle_data['terrain'] = TerrainType(battle_data['terrain'])
            game_state.active_battle = BattleState(**battle_data)
        else:
            game_state.active_battle = None

        return None  # Success
    
    except (IOError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        # Handle file I/O, JSON parsing, or data validation errors
        return "errors.load_failed"


def get_default_save_path() -> str:
    """
    Get the default save game file path.
    
    Returns:
        Default save file path
    """
    return "savegame.json"
