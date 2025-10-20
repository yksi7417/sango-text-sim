"""
Tests for the persistence module.

This module tests save/load functionality including:
- Saving game state to JSON
- Loading game state from JSON
- Error handling for missing/corrupted files
- Data integrity after save/load cycle
"""

import pytest
import json
import os
import tempfile
from src.models import Officer, City, Faction, GameState
from src import persistence, world


class TestSaveGame:
    """Tests for saving game state."""
    
    def test_save_game_creates_file(self, populated_game_state, tmp_path):
        """Saving game should create a JSON file."""
        filepath = tmp_path / "test_save.json"
        
        result = persistence.save_game(populated_game_state, str(filepath))
        
        assert result is True
        assert filepath.exists()
    
    def test_save_game_creates_valid_json(self, populated_game_state, tmp_path):
        """Saved file should contain valid JSON."""
        filepath = tmp_path / "test_save.json"
        
        persistence.save_game(populated_game_state, str(filepath))
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
    
    def test_save_game_includes_metadata(self, populated_game_state, tmp_path):
        """Saved data should include game metadata."""
        filepath = tmp_path / "test_save.json"
        
        persistence.save_game(populated_game_state, str(filepath))
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "year" in data
        assert "month" in data
        assert "player_faction" in data
        assert "player_ruler" in data
        assert "difficulty" in data
    
    def test_save_game_includes_cities(self, populated_game_state, tmp_path):
        """Saved data should include all cities."""
        filepath = tmp_path / "test_save.json"
        
        persistence.save_game(populated_game_state, str(filepath))
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "cities" in data
        assert len(data["cities"]) == len(populated_game_state.cities)
    
    def test_save_game_includes_factions(self, populated_game_state, tmp_path):
        """Saved data should include all factions."""
        filepath = tmp_path / "test_save.json"
        
        persistence.save_game(populated_game_state, str(filepath))
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "factions" in data
        assert len(data["factions"]) == len(populated_game_state.factions)
    
    def test_save_game_includes_officers(self, populated_game_state, tmp_path):
        """Saved data should include all officers."""
        filepath = tmp_path / "test_save.json"
        
        persistence.save_game(populated_game_state, str(filepath))
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "officers" in data
        assert len(data["officers"]) == len(populated_game_state.officers)
    
    def test_save_game_includes_adjacency(self, populated_game_state, tmp_path):
        """Saved data should include map adjacency."""
        filepath = tmp_path / "test_save.json"
        
        persistence.save_game(populated_game_state, str(filepath))
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "adj" in data
    
    def test_save_game_handles_chinese_characters(self, tmp_path):
        """Save should handle officer IDs correctly."""
        game_state = GameState()
        world.init_world(game_state)  # Contains officer IDs like "LiuBei"
        
        filepath = tmp_path / "test_save_chinese.json"
        
        result = persistence.save_game(game_state, str(filepath))
        
        assert result is True
        
        # Verify officer IDs are saved
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            assert "LiuBei" in content  # Internal officer ID
    
    def test_save_game_invalid_path(self, populated_game_state):
        """Save with invalid path should return False."""
        invalid_path = "/nonexistent/directory/save.json"
        
        result = persistence.save_game(populated_game_state, invalid_path)
        
        assert result is False


class TestLoadGame:
    """Tests for loading game state."""
    
    def test_load_game_missing_file(self, empty_game_state):
        """Loading missing file should return error."""
        error = persistence.load_game(empty_game_state, "nonexistent.json")
        
        assert error == "errors.file_missing"
    
    def test_load_game_restores_metadata(self, tmp_path):
        """Loading should restore game metadata."""
        # Create and save a game
        original_state = GameState()
        world.init_world(original_state)
        original_state.year = 220
        original_state.month = 5
        
        filepath = tmp_path / "test_load.json"
        persistence.save_game(original_state, str(filepath))
        
        # Load into new state
        loaded_state = GameState()
        error = persistence.load_game(loaded_state, str(filepath))
        
        assert error is None
        assert loaded_state.year == 220
        assert loaded_state.month == 5
        assert loaded_state.player_faction == original_state.player_faction
        assert loaded_state.player_ruler == original_state.player_ruler
    
    def test_load_game_restores_cities(self, tmp_path):
        """Loading should restore all cities."""
        # Create and save a game
        original_state = GameState()
        world.init_world(original_state)
        
        filepath = tmp_path / "test_load.json"
        persistence.save_game(original_state, str(filepath))
        
        # Load into new state
        loaded_state = GameState()
        error = persistence.load_game(loaded_state, str(filepath))
        
        assert error is None
        assert len(loaded_state.cities) == len(original_state.cities)
        
        # Check specific city
        assert "Chengdu" in loaded_state.cities
        assert loaded_state.cities["Chengdu"].owner == original_state.cities["Chengdu"].owner
    
    def test_load_game_restores_factions(self, tmp_path):
        """Loading should restore all factions."""
        # Create and save a game
        original_state = GameState()
        world.init_world(original_state)
        
        filepath = tmp_path / "test_load.json"
        persistence.save_game(original_state, str(filepath))
        
        # Load into new state
        loaded_state = GameState()
        error = persistence.load_game(loaded_state, str(filepath))
        
        assert error is None
        assert len(loaded_state.factions) == len(original_state.factions)
        
        # Check faction data
        assert "Shu" in loaded_state.factions
        assert loaded_state.factions["Shu"].ruler == original_state.factions["Shu"].ruler
    
    def test_load_game_restores_officers(self, tmp_path):
        """Loading should restore all officers."""
        # Create and save a game
        original_state = GameState()
        world.init_world(original_state)
        
        filepath = tmp_path / "test_load.json"
        persistence.save_game(original_state, str(filepath))
        
        # Load into new state
        loaded_state = GameState()
        error = persistence.load_game(loaded_state, str(filepath))
        
        assert error is None
        assert len(loaded_state.officers) == len(original_state.officers)
        
        # Check specific officer
        assert "LiuBei" in loaded_state.officers
        assert loaded_state.officers["LiuBei"].faction == original_state.officers["LiuBei"].faction
    
    def test_load_game_restores_adjacency(self, tmp_path):
        """Loading should restore map adjacency."""
        # Create and save a game
        original_state = GameState()
        world.init_world(original_state)
        
        filepath = tmp_path / "test_load.json"
        persistence.save_game(original_state, str(filepath))
        
        # Load into new state
        loaded_state = GameState()
        error = persistence.load_game(loaded_state, str(filepath))
        
        assert error is None
        assert loaded_state.adj == original_state.adj
    
    def test_load_game_clears_messages(self, tmp_path):
        """Loading should clear existing messages."""
        # Create and save a game
        original_state = GameState()
        world.init_world(original_state)
        
        filepath = tmp_path / "test_load.json"
        persistence.save_game(original_state, str(filepath))
        
        # Load into state with existing messages
        loaded_state = GameState()
        loaded_state.messages = ["Old message 1", "Old message 2"]
        error = persistence.load_game(loaded_state, str(filepath))
        
        assert error is None
        assert loaded_state.messages == []
    
    def test_load_game_invalid_json(self, empty_game_state, tmp_path):
        """Loading invalid JSON should return error."""
        filepath = tmp_path / "invalid.json"
        
        # Create file with invalid JSON
        with open(filepath, "w") as f:
            f.write("{invalid json content")
        
        error = persistence.load_game(empty_game_state, str(filepath))
        
        assert error == "errors.load_failed"
    
    def test_load_game_missing_keys(self, empty_game_state, tmp_path):
        """Loading JSON with missing keys should return error."""
        filepath = tmp_path / "incomplete.json"
        
        # Create file with incomplete data
        with open(filepath, "w") as f:
            json.dump({"year": 208}, f)  # Missing required keys
        
        error = persistence.load_game(empty_game_state, str(filepath))
        
        assert error == "errors.load_failed"


class TestSaveLoadCycle:
    """Tests for save/load data integrity."""
    
    def test_save_load_preserves_game_state(self, tmp_path):
        """Save and load should preserve complete game state."""
        # Create original game
        original = GameState()
        world.init_world(original)
        original.year = 215
        original.month = 8
        
        # Modify some values
        original.cities["Chengdu"].gold = 9999
        original.officers["LiuBei"].loyalty = 95
        
        # Save and load
        filepath = tmp_path / "cycle_test.json"
        persistence.save_game(original, str(filepath))
        
        loaded = GameState()
        persistence.load_game(loaded, str(filepath))
        
        # Verify critical data preserved
        assert loaded.year == 215
        assert loaded.month == 8
        assert loaded.cities["Chengdu"].gold == 9999
        assert loaded.officers["LiuBei"].loyalty == 95
    
    def test_multiple_save_load_cycles(self, tmp_path):
        """Multiple save/load cycles should preserve data."""
        filepath = tmp_path / "multi_cycle.json"
        
        # Initial state
        state1 = GameState()
        world.init_world(state1)
        persistence.save_game(state1, str(filepath))
        
        # First load and modify
        state2 = GameState()
        persistence.load_game(state2, str(filepath))
        state2.year = 210
        persistence.save_game(state2, str(filepath))
        
        # Second load and verify
        state3 = GameState()
        persistence.load_game(state3, str(filepath))
        
        assert state3.year == 210


class TestHelpers:
    """Tests for helper functions."""
    
    def test_get_default_save_path(self):
        """Default save path should be 'savegame.json'."""
        path = persistence.get_default_save_path()
        
        assert path == "savegame.json"
