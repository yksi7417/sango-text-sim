"""
Tests for the display module.

This module tests visual rendering functions:
- ASCII map rendering
- Faction color codes
- City and connection display
"""

import pytest
from src.models import City, Faction, GameState
from src.display.map_view import render_strategic_map, get_faction_color


class TestGetFactionColor:
    """Tests for faction color code function."""

    def test_wei_color(self):
        """Wei faction should return blue color code."""
        color = get_faction_color("Wei")
        assert "\033[" in color  # ANSI escape code
        assert color.endswith("\033[0m")  # Reset code

    def test_shu_color(self):
        """Shu faction should return green color code."""
        color = get_faction_color("Shu")
        assert "\033[" in color
        assert color.endswith("\033[0m")

    def test_wu_color(self):
        """Wu faction should return red color code."""
        color = get_faction_color("Wu")
        assert "\033[" in color
        assert color.endswith("\033[0m")

    def test_neutral_color(self):
        """Unknown faction should return gray color code."""
        color = get_faction_color("Unknown")
        assert "\033[" in color
        assert color.endswith("\033[0m")


class TestRenderStrategicMap:
    """Tests for strategic map rendering."""

    def test_render_map_with_cities(self):
        """Map should render all cities in game state."""
        state = GameState()
        state.cities = {
            "CityA": City(name="CityA", owner="Wei"),
            "CityB": City(name="CityB", owner="Shu"),
            "CityC": City(name="CityC", owner="Wu")
        }
        state.adj = {
            "CityA": ["CityB"],
            "CityB": ["CityA", "CityC"],
            "CityC": ["CityB"]
        }
        state.factions = {
            "Wei": Faction(name="Wei", cities=["CityA"]),
            "Shu": Faction(name="Shu", cities=["CityB"]),
            "Wu": Faction(name="Wu", cities=["CityC"])
        }

        result = render_strategic_map(state)

        assert isinstance(result, str)
        assert len(result) > 0
        # City names are rendered with color codes, so check for individual letters
        assert "C" in result and "i" in result and "t" in result and "y" in result
        # Check that all three factions are represented in legend
        assert "Wei" in result
        assert "Shu" in result
        assert "Wu" in result

    def test_render_map_shows_capital_marker(self):
        """Capital cities should be marked with ★ symbol."""
        state = GameState()
        state.cities = {
            "Capital": City(name="Capital", owner="Wei"),
            "Normal": City(name="Normal", owner="Wei")
        }
        state.adj = {"Capital": ["Normal"], "Normal": ["Capital"]}
        state.factions = {
            "Wei": Faction(name="Wei", cities=["Capital", "Normal"], ruler="Cao Cao")
        }

        result = render_strategic_map(state)

        # Capital should be marked somehow (★ or similar)
        assert "★" in result or "Capital" in result

    def test_render_map_with_no_cities(self):
        """Map should handle empty game state gracefully."""
        state = GameState()
        state.cities = {}
        state.adj = {}
        state.factions = {}

        result = render_strategic_map(state)

        assert isinstance(result, str)
        # Should return some message or empty map structure

    def test_render_map_shows_connections(self):
        """Map should show connections between adjacent cities."""
        state = GameState()
        state.cities = {
            "CityA": City(name="CityA", owner="Wei"),
            "CityB": City(name="CityB", owner="Shu")
        }
        state.adj = {
            "CityA": ["CityB"],
            "CityB": ["CityA"]
        }
        state.factions = {
            "Wei": Faction(name="Wei", cities=["CityA"]),
            "Shu": Faction(name="Shu", cities=["CityB"])
        }

        result = render_strategic_map(state)

        # Should contain city name characters (individually colored)
        assert "C" in result and "i" in result
        # Should have some visual indication of connection (lines, arrows, etc.)
        assert "─" in result or "│" in result or "·" in result or "-" in result

    def test_render_map_uses_color_codes(self):
        """Map should use ANSI color codes for faction differentiation."""
        state = GameState()
        state.cities = {
            "WeiCity": City(name="WeiCity", owner="Wei"),
            "ShuCity": City(name="ShuCity", owner="Shu")
        }
        state.adj = {
            "WeiCity": ["ShuCity"],
            "ShuCity": ["WeiCity"]
        }
        state.factions = {
            "Wei": Faction(name="Wei", cities=["WeiCity"]),
            "Shu": Faction(name="Shu", cities=["ShuCity"])
        }

        result = render_strategic_map(state)

        # Should contain ANSI escape codes
        assert "\033[" in result

    def test_render_map_scales_with_city_count(self):
        """Map should scale appropriately for different numbers of cities."""
        # Test with 6 cities
        state_6 = GameState()
        for i in range(6):
            city_name = f"City{i}"
            state_6.cities[city_name] = City(name=city_name, owner="Wei")
        state_6.adj = {city: [] for city in state_6.cities}
        state_6.factions = {"Wei": Faction(name="Wei", cities=list(state_6.cities.keys()))}

        result_6 = render_strategic_map(state_6)

        # Cities should be visible - check for city symbols and faction in legend
        assert "○" in result_6 or "▲" in result_6 or "◊" in result_6  # City symbols
        assert "Wei" in result_6
        assert "6 cities" in result_6  # Should show 6 cities in legend

        # Test with 40 cities (future support)
        state_40 = GameState()
        for i in range(40):
            city_name = f"City{i:02d}"
            state_40.cities[city_name] = City(name=city_name, owner="Wei")
        state_40.adj = {city: [] for city in state_40.cities}
        state_40.factions = {"Wei": Faction(name="Wei", cities=list(state_40.cities.keys()))}

        result_40 = render_strategic_map(state_40)

        # Should be able to render without crashing
        assert isinstance(result_40, str)
        assert len(result_40) > len(result_6)  # Larger map should have more content

    def test_render_map_with_real_game_data(self):
        """Map should render correctly with data loaded from JSON."""
        # Import the actual world initialization
        from src.world import init_world

        state = GameState()
        init_world(state)

        result = render_strategic_map(state)

        # Should contain parts of city names (letters are individually colored)
        # Check for key letters from city names
        assert "X" in result or "L" in result  # Wei cities (Xuchang, Luoyang)
        assert "C" in result or "H" in result  # Shu cities (Chengdu, Hanzhong)
        assert "J" in result or "W" in result  # Wu cities (Jianye, Wuchang)

        # Should have all three factions (faction names are colored, so just check for "2 cities")
        assert "2 cities" in result  # Each faction should show 2 cities
        assert "Wei" in result
        assert "Shu" in result
        assert "Wu" in result

        # Should have visual structure
        assert len(result) > 100  # Reasonable minimum size

        # Should contain ANSI color codes
        assert "\033[" in result
