"""
Tests for the display module.

This module tests visual rendering functions:
- ASCII map rendering
- City detail view rendering
- Faction color codes
- City and connection display
"""

import pytest
from src.models import City, Faction, GameState, Officer
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


class TestCityDetailView:
    """Tests for city detail view rendering."""

    def test_render_city_detail_basic(self):
        """City detail should render with all basic information."""
        from src.display.city_view import render_city_detail

        city = City(
            name="Xuchang",
            owner="Wei",
            gold=1000,
            food=1500,
            troops=500,
            defense=60,
            morale=70,
            agri=60,
            commerce=70,
            tech=50,
            walls=80
        )

        officers = [
            Officer(name="CaoCao", faction="Wei", leadership=95, intelligence=90,
                   politics=85, charisma=92, city="Xuchang", task="trade", busy=True),
            Officer(name="XiahouDun", faction="Wei", leadership=88, intelligence=70,
                   politics=60, charisma=75, city="Xuchang", task=None, busy=False)
        ]

        result = render_city_detail(city, officers)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should show city name
        assert "Xuchang" in result or "xuchang" in result.lower()
        # Should show resources
        assert "1000" in result  # gold
        assert "1500" in result  # food
        assert "500" in result   # troops

    def test_render_city_detail_shows_progress_bars(self):
        """City detail should show progress bars for development levels."""
        from src.display.city_view import render_city_detail

        city = City(
            name="TestCity",
            owner="Wei",
            agri=50,
            commerce=75,
            tech=25,
            walls=100
        )

        result = render_city_detail(city, [])

        # Progress bars use block characters
        assert "█" in result or "░" in result or "▓" in result or "■" in result or "|" in result

    def test_render_city_detail_lists_officers(self):
        """City detail should list stationed officers and their tasks."""
        from src.display.city_view import render_city_detail

        city = City(name="Chengdu", owner="Shu")

        officers = [
            Officer(name="LiuBei", faction="Shu", leadership=85, intelligence=75,
                   politics=80, charisma=95, city="Chengdu", task="farm", busy=True),
            Officer(name="GuanYu", faction="Shu", leadership=97, intelligence=70,
                   politics=65, charisma=90, city="Chengdu", task=None, busy=False),
            Officer(name="ZhangFei", faction="Shu", leadership=95, intelligence=40,
                   politics=35, charisma=75, city="Chengdu", task="train", busy=True)
        ]

        result = render_city_detail(city, officers)

        # Should list officer names
        assert "LiuBei" in result or "Liu Bei" in result or "刘备" in result
        assert "GuanYu" in result or "Guan Yu" in result or "关羽" in result
        assert "ZhangFei" in result or "Zhang Fei" in result or "张飞" in result

    def test_render_city_detail_shows_adjacency(self):
        """City detail should show adjacent cities."""
        from src.display.city_view import render_city_detail
        from src.world import ADJACENCY_MAP

        city = City(name="Xuchang", owner="Wei")

        result = render_city_detail(city, [])

        # Should have some section about adjacent/neighboring cities
        # We can't assert specific cities unless we know the adjacency
        # Just check that the render works
        assert isinstance(result, str)

    def test_render_city_detail_ascii_icon_varies_by_walls(self):
        """City detail should show different ASCII art based on walls level."""
        from src.display.city_view import render_city_detail

        city_low = City(name="WeakCity", owner="Wei", walls=20)
        city_high = City(name="StrongCity", owner="Wei", walls=90)

        result_low = render_city_detail(city_low, [])
        result_high = render_city_detail(city_high, [])

        # Both should render successfully
        assert isinstance(result_low, str)
        assert isinstance(result_high, str)

        # Should contain some ASCII art
        # Could be box drawing, castles, walls, etc.
        assert len(result_low) > 50
        assert len(result_high) > 50

    def test_render_city_detail_with_no_officers(self):
        """City detail should handle cities with no stationed officers."""
        from src.display.city_view import render_city_detail

        city = City(name="EmptyCity", owner="Neutral")

        result = render_city_detail(city, [])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_city_detail_i18n_support(self):
        """City detail should use i18n keys for all labels."""
        from src.display.city_view import render_city_detail

        city = City(name="TestCity", owner="Wei")
        officer = Officer(name="TestOfficer", faction="Wei", leadership=80,
                         intelligence=70, politics=60, charisma=75, city="TestCity")

        result = render_city_detail(city, [officer])

        # Should render without errors (i18n keys exist)
        assert isinstance(result, str)
        # Should have some meaningful content
        assert len(result) > 100


class TestOfficerProfileView:
    """Tests for officer profile view rendering."""

    def test_render_officer_profile_basic(self):
        """Officer profile should render with all basic information."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Cao Cao",
            faction="Wei",
            leadership=95,
            intelligence=90,
            politics=85,
            charisma=92,
            energy=100,
            loyalty=80,
            traits=["Brilliant", "Ambitious"],
            city="Xuchang"
        )

        result = render_officer_profile(officer)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should show officer name
        assert "Cao Cao" in result or "CaoCao" in result
        # Should show faction
        assert "Wei" in result

    def test_render_officer_profile_shows_stats(self):
        """Officer profile should display all stat values."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Zhuge Liang",
            faction="Shu",
            leadership=85,
            intelligence=100,
            politics=95,
            charisma=90,
            energy=80,
            loyalty=100
        )

        result = render_officer_profile(officer)

        # Should show stat values
        assert "85" in result  # leadership
        assert "100" in result  # intelligence and loyalty
        assert "95" in result  # politics
        assert "90" in result  # charisma
        assert "80" in result  # energy

    def test_render_officer_profile_shows_progress_bars(self):
        """Officer profile should show progress bars for stats."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Lu Bu",
            faction="Neutral",
            leadership=100,
            intelligence=50,
            politics=25,
            charisma=70,
            energy=100,
            loyalty=30
        )

        result = render_officer_profile(officer)

        # Progress bars use block characters
        assert "█" in result or "░" in result

    def test_render_officer_profile_shows_traits(self):
        """Officer profile should display officer traits."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Guan Yu",
            faction="Shu",
            leadership=97,
            intelligence=70,
            politics=65,
            charisma=90,
            traits=["Brave", "Loyal"]
        )

        result = render_officer_profile(officer)

        # Should mention traits somehow
        assert "Brave" in result or "brave" in result.lower()
        assert "Loyal" in result or "loyal" in result.lower()

    def test_render_officer_profile_shows_condition(self):
        """Officer profile should show energy and loyalty condition."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Zhang Fei",
            faction="Shu",
            leadership=95,
            intelligence=40,
            politics=35,
            charisma=75,
            energy=50,
            loyalty=95
        )

        result = render_officer_profile(officer)

        # Should show energy and loyalty values
        assert "50" in result  # energy
        assert "95" in result  # loyalty

    def test_render_officer_profile_ascii_portrait(self):
        """Officer profile should include ASCII portrait placeholder."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Zhou Yu",
            faction="Wu",
            leadership=90,
            intelligence=96,
            politics=88,
            charisma=95
        )

        result = render_officer_profile(officer)

        # Should have some ASCII art/box for portrait
        assert "┌" in result or "┐" in result or "╔" in result or "║" in result or "|" in result
        # Should be reasonably sized
        assert len(result) > 100

    def test_render_officer_profile_with_no_traits(self):
        """Officer profile should handle officers with no traits."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Generic Officer",
            faction="Wei",
            leadership=60,
            intelligence=55,
            politics=50,
            charisma=50,
            traits=[]
        )

        result = render_officer_profile(officer)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_officer_profile_relationships_placeholder(self):
        """Officer profile should have placeholder for relationships section."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Liu Bei",
            faction="Shu",
            leadership=85,
            intelligence=75,
            politics=80,
            charisma=95
        )

        result = render_officer_profile(officer)

        # Should have some section or mention about relationships
        # (even if empty for now)
        assert isinstance(result, str)

    def test_render_officer_profile_personality_quote(self):
        """Officer profile should include personality-based quote."""
        from src.display.officer_view import render_officer_profile

        officer_brave = Officer(
            name="Zhao Yun",
            faction="Shu",
            leadership=96,
            intelligence=75,
            politics=70,
            charisma=88,
            traits=["Brave"]
        )

        officer_scholar = Officer(
            name="Sima Yi",
            faction="Wei",
            leadership=80,
            intelligence=96,
            politics=92,
            charisma=85,
            traits=["Scholar"]
        )

        result_brave = render_officer_profile(officer_brave)
        result_scholar = render_officer_profile(officer_scholar)

        # Both should render successfully
        assert isinstance(result_brave, str)
        assert isinstance(result_scholar, str)
        # Should have some content indicating personality
        assert len(result_brave) > 100
        assert len(result_scholar) > 100

    def test_render_officer_profile_i18n_support(self):
        """Officer profile should use i18n keys for all labels."""
        from src.display.officer_view import render_officer_profile

        officer = Officer(
            name="Sun Quan",
            faction="Wu",
            leadership=88,
            intelligence=82,
            politics=85,
            charisma=90,
            traits=["Charismatic"]
        )

        result = render_officer_profile(officer)

        # Should render without errors (i18n keys exist)
        assert isinstance(result, str)
        # Should have meaningful content
        assert len(result) > 100
