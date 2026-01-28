"""Tests for the building system."""
import pytest
from src.models import GameState, City, Faction, Officer
from src.buildings import load_buildings, get_building, get_available_buildings
from src.engine import start_construction, process_construction, end_turn


class TestBuildingsData:
    """Test loading building data from JSON."""

    def test_load_buildings(self):
        buildings = load_buildings()
        assert len(buildings) == 10

    def test_load_buildings_has_barracks(self):
        buildings = load_buildings()
        ids = [b.id for b in buildings]
        assert "barracks" in ids

    def test_get_building_found(self):
        b = get_building("market")
        assert b is not None
        assert b.id == "market"
        assert b.cost > 0
        assert b.turns > 0

    def test_get_building_not_found(self):
        assert get_building("nonexistent") is None

    def test_get_available_buildings_all(self):
        available = get_available_buildings([])
        assert len(available) == 10

    def test_get_available_buildings_some_built(self):
        available = get_available_buildings(["barracks", "market"])
        ids = [b.id for b in available]
        assert "barracks" not in ids
        assert "market" not in ids
        assert len(available) == 8

    def test_building_effects(self):
        b = get_building("barracks")
        assert "train_speed" in b.effects


class TestStartConstruction:
    """Test starting building construction."""

    def _make_state(self):
        gs = GameState()
        gs.player_faction = "Shu"
        gs.cities["Chengdu"] = City(name="Chengdu", owner="Shu", gold=1000)
        gs.factions["Shu"] = Faction(name="Shu", cities=["Chengdu"])
        return gs

    def test_start_construction_success(self):
        gs = self._make_state()
        result = start_construction(gs, "Chengdu", "barracks")
        assert result["success"] is True
        assert "Chengdu" in gs.construction_queue
        assert gs.construction_queue["Chengdu"]["building_id"] == "barracks"

    def test_start_construction_deducts_gold(self):
        gs = self._make_state()
        initial_gold = gs.cities["Chengdu"].gold
        start_construction(gs, "Chengdu", "barracks")
        barracks = get_building("barracks")
        assert gs.cities["Chengdu"].gold == initial_gold - barracks.cost

    def test_start_construction_unknown_building(self):
        gs = self._make_state()
        result = start_construction(gs, "Chengdu", "nonexistent")
        assert result["success"] is False

    def test_start_construction_insufficient_gold(self):
        gs = self._make_state()
        gs.cities["Chengdu"].gold = 0
        result = start_construction(gs, "Chengdu", "barracks")
        assert result["success"] is False

    def test_start_construction_already_building(self):
        gs = self._make_state()
        start_construction(gs, "Chengdu", "barracks")
        result = start_construction(gs, "Chengdu", "market")
        assert result["success"] is False

    def test_start_construction_already_built(self):
        gs = self._make_state()
        gs.cities["Chengdu"].buildings.append("barracks")
        result = start_construction(gs, "Chengdu", "barracks")
        assert result["success"] is False

    def test_start_construction_not_your_city(self):
        gs = self._make_state()
        gs.cities["Chengdu"].owner = "Wei"
        result = start_construction(gs, "Chengdu", "barracks")
        assert result["success"] is False

    def test_start_construction_city_not_found(self):
        gs = self._make_state()
        result = start_construction(gs, "Nowhere", "barracks")
        assert result["success"] is False


class TestProcessConstruction:
    """Test construction processing during turns."""

    def _make_state(self):
        gs = GameState()
        gs.player_faction = "Shu"
        gs.cities["Chengdu"] = City(name="Chengdu", owner="Shu", gold=1000)
        gs.factions["Shu"] = Faction(name="Shu", cities=["Chengdu"])
        return gs

    def test_process_construction_increments_progress(self):
        gs = self._make_state()
        gs.construction_queue["Chengdu"] = {
            "building_id": "barracks",
            "progress": 0,
            "turns_needed": 3
        }
        events = []
        process_construction(gs, events)
        assert gs.construction_queue["Chengdu"]["progress"] == 1
        assert len(events) == 0  # Not complete yet

    def test_process_construction_completes(self):
        gs = self._make_state()
        gs.construction_queue["Chengdu"] = {
            "building_id": "barracks",
            "progress": 2,
            "turns_needed": 3
        }
        events = []
        process_construction(gs, events)
        assert "Chengdu" not in gs.construction_queue
        assert "barracks" in gs.cities["Chengdu"].buildings
        assert len(events) == 1

    def test_process_construction_empty_queue(self):
        gs = self._make_state()
        events = []
        process_construction(gs, events)
        assert len(events) == 0
