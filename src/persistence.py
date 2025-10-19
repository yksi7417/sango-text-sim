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
from .models import Officer, City, Faction, GameState


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
        data["cities"] = {k: asdict(v) for k, v in game_state.cities.items()}
        data["factions"] = {
            k: {
                "name": f.name,
                "relations": f.relations,
                "cities": f.cities,
                "officers": f.officers,
                "ruler": f.ruler
            }
            for k, f in game_state.factions.items()
        }
        data["officers"] = {k: asdict(v) for k, v in game_state.officers.items()}
        
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
        game_state.cities = {k: City(**v) for k, v in data["cities"].items()}
        
        # Restore factions
        game_state.factions = {}
        for k, fv in data["factions"].items():
            game_state.factions[k] = Faction(
                name=fv["name"],
                relations=fv["relations"],
                cities=fv["cities"],
                officers=fv.get("officers", []),
                ruler=fv.get("ruler", "")
            )
        
        # Restore officers
        game_state.officers = {k: Officer(**v) for k, v in data["officers"].items()}
        
        # Restore map adjacency
        game_state.adj = {k: v for k, v in data["adj"].items()}
        
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
