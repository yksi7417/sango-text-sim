"""
Tests for data loading from JSON files.

Verifies that JSON schemas are valid and data can be loaded correctly.
"""

import json
import pytest
from pathlib import Path


class TestMapDataLoading:
    """Test loading map data from JSON files."""

    def test_china_208_json_exists(self):
        """Verify china_208.json exists."""
        map_path = Path("src/data/maps/china_208.json")
        assert map_path.exists(), "china_208.json file should exist"

    def test_china_208_json_valid(self):
        """Verify china_208.json is valid JSON."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), "Map data should be a dictionary"

    def test_china_208_has_metadata(self):
        """Verify metadata section exists and is complete."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        metadata = data["metadata"]

        required_fields = ["name", "scenario_id", "year", "month", "description", "version"]
        for field in required_fields:
            assert field in metadata, f"Metadata should have {field}"

        assert metadata["scenario_id"] == "china_208"
        assert metadata["year"] == 208
        assert metadata["month"] == 1

    def test_china_208_has_provinces(self):
        """Verify provinces section exists."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "provinces" in data
        assert isinstance(data["provinces"], list)
        assert len(data["provinces"]) > 0

        # Check province structure
        for province in data["provinces"]:
            assert "id" in province
            assert "name" in province
            assert "region" in province

    def test_china_208_has_cities(self):
        """Verify cities section exists with correct count."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "cities" in data
        assert isinstance(data["cities"], list)
        assert len(data["cities"]) == 6, "Should have 6 cities"

    def test_city_structure(self):
        """Verify each city has required fields."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_fields = [
            "id", "province", "terrain", "coordinates",
            "is_capital", "owner", "resources", "development",
            "military", "adjacency"
        ]

        for city in data["cities"]:
            for field in required_fields:
                assert field in city, f"City {city.get('id', 'unknown')} should have {field}"

    def test_city_coordinates(self):
        """Verify city coordinates are valid."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for city in data["cities"]:
            coords = city["coordinates"]
            assert "x" in coords and "y" in coords
            assert 0 <= coords["x"] <= 10, f"X coordinate for {city['id']} should be 0-10"
            assert 0 <= coords["y"] <= 10, f"Y coordinate for {city['id']} should be 0-10"

    def test_city_terrain_types(self):
        """Verify terrain types are valid."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        valid_terrains = ["plains", "mountain", "coastal", "forest", "river"]

        for city in data["cities"]:
            assert city["terrain"] in valid_terrains, \
                f"City {city['id']} has invalid terrain: {city['terrain']}"

    def test_city_resources(self):
        """Verify resource structure."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for city in data["cities"]:
            resources = city["resources"]
            assert "gold" in resources
            assert "food" in resources
            assert "troops" in resources
            assert all(isinstance(v, (int, float)) and v >= 0
                      for v in resources.values())

    def test_city_development(self):
        """Verify development structure and ranges."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for city in data["cities"]:
            dev = city["development"]
            assert "agriculture" in dev
            assert "commerce" in dev
            assert "technology" in dev
            assert "walls" in dev

            # All development values should be 0-100
            for key, value in dev.items():
                assert 0 <= value <= 100, \
                    f"City {city['id']} {key} should be 0-100, got {value}"

    def test_city_military(self):
        """Verify military structure and ranges."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for city in data["cities"]:
            military = city["military"]
            assert "defense" in military
            assert "morale" in military

            # Military values should be 0-100
            for key, value in military.items():
                assert 0 <= value <= 100, \
                    f"City {city['id']} {key} should be 0-100, got {value}"

    def test_adjacency_bidirectional(self):
        """Verify adjacency relationships are bidirectional."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Build city ID set and adjacency map
        city_ids = {city["id"] for city in data["cities"]}
        adjacency_map = {city["id"]: city["adjacency"] for city in data["cities"]}

        # Check bidirectionality
        for city_id, neighbors in adjacency_map.items():
            for neighbor in neighbors:
                assert neighbor in city_ids, \
                    f"City {city_id} references non-existent neighbor {neighbor}"
                assert city_id in adjacency_map[neighbor], \
                    f"Adjacency not bidirectional: {city_id} -> {neighbor}"

    def test_capital_cities(self):
        """Verify each faction has one capital."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        capitals_by_faction = {}
        for city in data["cities"]:
            if city["is_capital"]:
                faction = city["owner"]
                assert faction not in capitals_by_faction, \
                    f"Faction {faction} has multiple capitals"
                capitals_by_faction[faction] = city["id"]

        # Each faction should have a capital
        factions = {city["owner"] for city in data["cities"]}
        assert factions == set(capitals_by_faction.keys()), \
            "Each faction should have exactly one capital"

    def test_province_references(self):
        """Verify all city province references are valid."""
        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        province_ids = {p["id"] for p in data["provinces"]}

        for city in data["cities"]:
            assert city["province"] in province_ids, \
                f"City {city['id']} references non-existent province {city['province']}"

    def test_city_data_matches_existing(self):
        """Verify JSON data matches existing CITY_DATA for backward compatibility."""
        from src.world import CITY_DATA

        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        json_cities = {city["id"]: city for city in data["cities"]}

        # Check all existing cities are present
        for city_name in CITY_DATA.keys():
            assert city_name in json_cities, f"JSON missing city {city_name}"

            city_json = json_cities[city_name]
            city_old = CITY_DATA[city_name]

            # Verify key values match
            assert city_json["owner"] == city_old["owner"]
            assert city_json["resources"]["gold"] == city_old["gold"]
            assert city_json["resources"]["food"] == city_old["food"]
            assert city_json["resources"]["troops"] == city_old["troops"]
            assert city_json["development"]["agriculture"] == city_old["agri"]
            assert city_json["development"]["commerce"] == city_old["commerce"]
            assert city_json["development"]["technology"] == city_old["tech"]
            assert city_json["development"]["walls"] == city_old["walls"]
            assert city_json["military"]["defense"] == city_old["defense"]
            assert city_json["military"]["morale"] == city_old["morale"]

    def test_adjacency_matches_existing(self):
        """Verify JSON adjacency matches existing ADJACENCY_MAP."""
        from src.world import ADJACENCY_MAP

        map_path = Path("src/data/maps/china_208.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        json_adjacency = {city["id"]: set(city["adjacency"])
                         for city in data["cities"]}

        for city_name, neighbors in ADJACENCY_MAP.items():
            assert city_name in json_adjacency
            assert json_adjacency[city_name] == set(neighbors), \
                f"Adjacency mismatch for {city_name}"


class TestLoadScenario:
    """Test load_scenario function."""

    def test_load_scenario_default(self):
        """Verify load_scenario loads china_208 by default."""
        from src.world import load_scenario

        data = load_scenario()
        assert "metadata" in data
        assert "cities" in data
        assert "provinces" in data

    def test_load_scenario_specific(self):
        """Verify load_scenario can load specific scenario."""
        from src.world import load_scenario

        data = load_scenario("china_208")
        assert data["metadata"]["scenario_id"] == "china_208"

    def test_load_scenario_nonexistent(self):
        """Verify load_scenario raises error for missing file."""
        from src.world import load_scenario
        import pytest

        with pytest.raises(FileNotFoundError):
            load_scenario("nonexistent")

    def test_world_loads_from_json(self):
        """Verify world.py actually loads data from JSON."""
        from src.world import CITY_DATA, load_scenario

        # Load JSON directly
        scenario_data = load_scenario("china_208")

        # Verify CITY_DATA was populated from JSON
        for city in scenario_data["cities"]:
            city_id = city["id"]
            assert city_id in CITY_DATA
            assert CITY_DATA[city_id]["owner"] == city["owner"]
            assert CITY_DATA[city_id]["gold"] == city["resources"]["gold"]

    def test_init_world_with_json_data(self):
        """Verify init_world works with JSON-loaded data."""
        from src.models import GameState
        from src.world import init_world

        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Verify cities were created
        assert len(game_state.cities) == 6

        # Verify all expected cities exist
        expected_cities = ["Xuchang", "Luoyang", "Chengdu", "Hanzhong", "Jianye", "Wuchang"]
        for city_name in expected_cities:
            assert city_name in game_state.cities
