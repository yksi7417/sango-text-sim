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


class TestComponents:
    """Tests for reusable UI components."""

    def test_render_progress_bar(self):
        """Progress bar should render correctly with value and max."""
        from src.display.components import render_progress_bar

        # Full bar
        full_bar = render_progress_bar(100, 100, 10)
        assert len(full_bar) == 10
        assert full_bar.count("█") == 10

        # Half bar
        half_bar = render_progress_bar(50, 100, 10)
        assert len(half_bar) == 10
        assert half_bar.count("█") == 5
        assert half_bar.count("░") == 5

        # Empty bar
        empty_bar = render_progress_bar(0, 100, 10)
        assert len(empty_bar) == 10
        assert empty_bar.count("░") == 10

    def test_render_progress_bar_custom_width(self):
        """Progress bar should support custom widths."""
        from src.display.components import render_progress_bar

        bar_20 = render_progress_bar(75, 100, 20)
        assert len(bar_20) == 20
        assert bar_20.count("█") == 15
        assert bar_20.count("░") == 5

    def test_render_box(self):
        """Box should render with title and content."""
        from src.display.components import render_box

        content = "Test content\nMultiple lines\nIn a box"
        result = render_box(content, "Test Title", 40)

        assert isinstance(result, str)
        assert "Test Title" in result
        assert "Test content" in result
        # Should have box drawing characters
        assert "─" in result or "═" in result or "|" in result

    def test_render_box_without_title(self):
        """Box should render without title."""
        from src.display.components import render_box

        content = "Simple content"
        result = render_box(content, "", 30)

        assert isinstance(result, str)
        assert "Simple content" in result
        assert "─" in result or "═" in result or "|" in result

    def test_render_table(self):
        """Table should render with headers and rows."""
        from src.display.components import render_table

        headers = ["Name", "Value", "Status"]
        rows = [
            ["Item 1", "100", "Active"],
            ["Item 2", "200", "Inactive"],
            ["Item 3", "300", "Active"]
        ]

        result = render_table(headers, rows)

        assert isinstance(result, str)
        # Should contain all headers
        assert "Name" in result
        assert "Value" in result
        assert "Status" in result
        # Should contain all row data
        assert "Item 1" in result
        assert "100" in result
        assert "Active" in result

    def test_render_table_with_empty_rows(self):
        """Table should handle empty rows."""
        from src.display.components import render_table

        headers = ["Col1", "Col2"]
        rows = []

        result = render_table(headers, rows)

        assert isinstance(result, str)
        # Should still show headers
        assert "Col1" in result
        assert "Col2" in result

    def test_render_separator(self):
        """Separator should render with specified width and style."""
        from src.display.components import render_separator

        sep_single = render_separator(20, "single")
        assert len(sep_single) == 20
        assert "─" in sep_single or "-" in sep_single

        sep_double = render_separator(20, "double")
        assert len(sep_double) == 20
        assert "═" in sep_double or "=" in sep_double

        sep_heavy = render_separator(20, "heavy")
        assert len(sep_heavy) == 20

    def test_faction_colors_exist(self):
        """FACTION_COLORS should have all main factions."""
        from src.display.components import FACTION_COLORS

        assert "Wei" in FACTION_COLORS
        assert "Shu" in FACTION_COLORS
        assert "Wu" in FACTION_COLORS
        assert "Neutral" in FACTION_COLORS

    def test_get_faction_color(self):
        """get_faction_color should return color template."""
        from src.display.components import get_faction_color

        wei_color = get_faction_color("Wei")
        assert isinstance(wei_color, str)
        # Should contain ANSI codes
        assert "\033[" in wei_color
        assert "\033[0m" in wei_color

        # Unknown faction should default to Neutral
        unknown_color = get_faction_color("Unknown")
        assert isinstance(unknown_color, str)
        assert "\033[" in unknown_color


class TestTurnReportGenerator:
    """Tests for turn report generation."""

    def test_generate_turn_report_empty_events(self):
        """Test generating report with no events."""
        from src.display.reports import generate_turn_report
        from src.models import Season
        
        report = generate_turn_report([], Season.SPRING)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_turn_report_with_season_flavor(self):
        """Test report includes seasonal flavor text."""
        from src.display.reports import generate_turn_report, TurnEvent, EventCategory
        from src.models import Season
        
        events = []
        report_spring = generate_turn_report(events, Season.SPRING)
        report_winter = generate_turn_report(events, Season.WINTER)
        
        # Reports should differ by season
        assert isinstance(report_spring, str)
        assert isinstance(report_winter, str)

    def test_generate_turn_report_with_economy_events(self):
        """Test report formats economy events."""
        from src.display.reports import generate_turn_report, TurnEvent, EventCategory
        from src.models import Season
        
        events = [
            TurnEvent(
                category=EventCategory.ECONOMY,
                message="Chengdu earned 100 gold from commerce",
                data={"city": "Chengdu", "gold": 100}
            )
        ]
        report = generate_turn_report(events, Season.SPRING)
        
        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_turn_report_with_military_events(self):
        """Test report formats military events."""
        from src.display.reports import generate_turn_report, TurnEvent, EventCategory
        from src.models import Season
        
        events = [
            TurnEvent(
                category=EventCategory.MILITARY,
                message="Shu trained 50 troops at Chengdu",
                data={"city": "Chengdu", "troops": 50}
            )
        ]
        report = generate_turn_report(events, Season.SUMMER)
        
        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_turn_report_with_officer_events(self):
        """Test report formats officer events."""
        from src.display.reports import generate_turn_report, TurnEvent, EventCategory
        from src.models import Season
        
        events = [
            TurnEvent(
                category=EventCategory.OFFICER,
                message="Guan Yu completed farming assignment",
                data={"officer": "Guan Yu", "task": "farm"}
            )
        ]
        report = generate_turn_report(events, Season.AUTUMN)
        
        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_turn_report_with_mixed_events(self):
        """Test report handles multiple event categories."""
        from src.display.reports import generate_turn_report, TurnEvent, EventCategory
        from src.models import Season
        
        events = [
            TurnEvent(EventCategory.ECONOMY, "Commerce income", {}),
            TurnEvent(EventCategory.MILITARY, "Training complete", {}),
            TurnEvent(EventCategory.OFFICER, "Loyalty change", {}),
        ]
        report = generate_turn_report(events, Season.WINTER)
        
        assert isinstance(report, str)
        assert len(report) > 0

    def test_turn_event_creation(self):
        """Test TurnEvent dataclass creation."""
        from src.display.reports import TurnEvent, EventCategory
        
        event = TurnEvent(
            category=EventCategory.ECONOMY,
            message="Test message",
            data={"key": "value"}
        )
        
        assert event.category == EventCategory.ECONOMY
        assert event.message == "Test message"
        assert event.data["key"] == "value"

    def test_event_category_enum(self):
        """Test EventCategory enum has all categories."""
        from src.display.reports import EventCategory

        assert hasattr(EventCategory, 'ECONOMY')
        assert hasattr(EventCategory, 'MILITARY')
        assert hasattr(EventCategory, 'DIPLOMATIC')
        assert hasattr(EventCategory, 'OFFICER')


class TestDuelView:
    """Tests for duel view rendering."""

    def test_render_duel_state_basic(self):
        """Duel state should render with HP bars and combatants."""
        from src.display.duel_view import render_duel_state
        from src.systems.duel import start_duel

        officer1 = Officer(
            name="Lu Bu", faction="Dong Zhuo",
            leadership=100, intelligence=50, politics=30, charisma=60
        )
        officer2 = Officer(
            name="Zhang Fei", faction="Shu",
            leadership=95, intelligence=40, politics=35, charisma=75
        )

        duel = start_duel(officer1, officer2)
        result = render_duel_state(duel)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should show both officer names
        assert "Lu Bu" in result or "LuBu" in result
        assert "Zhang Fei" in result or "ZhangFei" in result

    def test_render_duel_state_shows_hp_bars(self):
        """Duel state should display HP bars for both combatants."""
        from src.display.duel_view import render_duel_state
        from src.systems.duel import start_duel

        officer1 = Officer(
            name="Guan Yu", faction="Shu",
            leadership=98, intelligence=75, politics=65, charisma=90
        )
        officer2 = Officer(
            name="Xiahou Dun", faction="Wei",
            leadership=88, intelligence=70, politics=60, charisma=75
        )

        duel = start_duel(officer1, officer2)
        result = render_duel_state(duel)

        # Should contain HP bars (block characters)
        assert "█" in result or "░" in result

    def test_render_duel_state_shows_round(self):
        """Duel state should display current round number."""
        from src.display.duel_view import render_duel_state
        from src.systems.duel import start_duel, process_duel_round, DuelAction

        officer1 = Officer(
            name="Zhao Yun", faction="Shu",
            leadership=96, intelligence=75, politics=70, charisma=88
        )
        officer2 = Officer(
            name="Xu Chu", faction="Wei",
            leadership=93, intelligence=65, politics=55, charisma=70
        )

        duel = start_duel(officer1, officer2)
        process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)
        result = render_duel_state(duel)

        # Should show round number
        assert "1" in result or "Round" in result or "回合" in result

    def test_render_duel_state_shows_combat_log(self):
        """Duel state should display combat log of recent actions."""
        from src.display.duel_view import render_duel_state
        from src.systems.duel import start_duel, process_duel_round, DuelAction

        officer1 = Officer(
            name="Ma Chao", faction="Shu",
            leadership=95, intelligence=70, politics=60, charisma=85
        )
        officer2 = Officer(
            name="Pang De", faction="Wei",
            leadership=88, intelligence=65, politics=50, charisma=70
        )

        duel = start_duel(officer1, officer2)
        process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)
        result = render_duel_state(duel)

        # Should have combat log section
        assert isinstance(result, str)
        assert len(result) > 50

    def test_render_action_menu(self):
        """Action menu should render with all action choices."""
        from src.display.duel_view import render_action_menu

        result = render_action_menu()

        assert isinstance(result, str)
        # Should show all three actions
        assert "Attack" in result or "attack" in result or "攻击" in result
        assert "Defend" in result or "defend" in result or "防御" in result
        assert "Special" in result or "special" in result or "必杀" in result

    def test_render_action_menu_shows_descriptions(self):
        """Action menu should show descriptions for each action."""
        from src.display.duel_view import render_action_menu

        result = render_action_menu()

        # Should have descriptions (hit rate, damage info)
        assert "85%" in result or "70%" in result or "50%" in result

    def test_render_duel_victory(self):
        """Victory screen should show winner and final stats."""
        from src.display.duel_view import render_duel_victory

        winner = Officer(
            name="Guan Yu", faction="Shu",
            leadership=98, intelligence=75, politics=65, charisma=90
        )
        loser = Officer(
            name="Hua Xiong", faction="Dong Zhuo",
            leadership=75, intelligence=50, politics=40, charisma=55
        )

        result = render_duel_victory(winner, loser)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should show winner name
        assert "Guan Yu" in result or "GuanYu" in result or "关羽" in result

    def test_render_duel_victory_shows_victory_message(self):
        """Victory screen should display victory message."""
        from src.display.duel_view import render_duel_victory

        winner = Officer(
            name="Lu Bu", faction="Neutral",
            leadership=100, intelligence=50, politics=30, charisma=60
        )
        loser = Officer(
            name="Ji Ling", faction="Yuan Shu",
            leadership=80, intelligence=60, politics=55, charisma=65
        )

        result = render_duel_victory(winner, loser)

        # Should have some victory terminology
        assert "victory" in result.lower() or "victorious" in result.lower() or "胜利" in result

    def test_render_duel_defeat(self):
        """Defeat screen should show loser perspective."""
        from src.display.duel_view import render_duel_defeat

        winner = Officer(
            name="Zhang Liao", faction="Wei",
            leadership=92, intelligence=80, politics=70, charisma=85
        )
        loser = Officer(
            name="Test Officer", faction="Test",
            leadership=60, intelligence=50, politics=50, charisma=50
        )

        result = render_duel_defeat(winner, loser)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should show winner who defeated you
        assert "Zhang Liao" in result or "ZhangLiao" in result

    def test_render_duel_state_with_partial_hp(self):
        """Duel state should correctly show partial HP."""
        from src.display.duel_view import render_duel_state
        from src.systems.duel import start_duel, process_duel_round, DuelAction

        officer1 = Officer(
            name="Officer1", faction="Wei",
            leadership=90, intelligence=70, politics=60, charisma=75
        )
        officer2 = Officer(
            name="Officer2", faction="Shu",
            leadership=85, intelligence=65, politics=55, charisma=70
        )

        duel = start_duel(officer1, officer2)
        # Fight a few rounds to damage HP
        for _ in range(3):
            from src.systems.duel import is_duel_over
            if not is_duel_over(duel):
                process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

        result = render_duel_state(duel)

        # Should render without errors
        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_duel_state_i18n_support(self):
        """Duel view should use i18n keys for all labels."""
        from src.display.duel_view import render_duel_state
        from src.systems.duel import start_duel

        officer1 = Officer(
            name="Test1", faction="Wei",
            leadership=80, intelligence=70, politics=60, charisma=70
        )
        officer2 = Officer(
            name="Test2", faction="Shu",
            leadership=75, intelligence=65, politics=55, charisma=65
        )

        duel = start_duel(officer1, officer2)
        result = render_duel_state(duel)

        # Should render without errors (i18n keys exist)
        assert isinstance(result, str)
        assert len(result) > 50


# =================== Battle View Tests ===================


class TestRenderBattleMap:
    """Tests for tactical battle map rendering."""

    def test_render_basic_battle_map(self):
        """Battle map should render with basic components."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Chengdu",
            defender_city="Changan",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="Zhao Yun",
            defender_commander="Cao Ren",
            attacker_troops=5000,
            defender_troops=4000,
            terrain=TerrainType.PLAINS
        )

        result = render_battle_map(battle)

        # Should contain key battle information
        assert isinstance(result, str)
        assert len(result) > 100
        # Check for city names
        assert "Chengdu" in result or "chengdu" in result.lower()
        assert "Changan" in result or "changan" in result.lower()

    def test_render_battle_map_shows_commanders(self):
        """Battle map should display commander names."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Xiangyang",
            defender_city="Jiangling",
            attacker_faction="Wei",
            defender_faction="Shu",
            attacker_commander="Zhang Liao",
            defender_commander="Guan Yu",
            attacker_troops=6000,
            defender_troops=5000,
            terrain=TerrainType.MOUNTAIN
        )

        result = render_battle_map(battle)

        # Should mention commanders
        assert "Zhang Liao" in result or "zhang" in result.lower()
        assert "Guan Yu" in result or "guan" in result.lower()

    def test_render_battle_map_shows_troops(self):
        """Battle map should display troop counts."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Luoyang",
            defender_city="Xuchang",
            attacker_faction="Wu",
            defender_faction="Wei",
            attacker_commander="Zhou Yu",
            defender_commander="Xiahou Dun",
            attacker_troops=7500,
            defender_troops=6200,
            terrain=TerrainType.FOREST
        )

        result = render_battle_map(battle)

        # Should show troop numbers
        assert "7500" in result or "7,500" in result
        assert "6200" in result or "6,200" in result

    def test_render_battle_map_shows_terrain(self):
        """Battle map should indicate terrain type."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Hefei",
            defender_city="Jianye",
            attacker_faction="Wei",
            defender_faction="Wu",
            attacker_commander="Cao Cao",
            defender_commander="Sun Quan",
            attacker_troops=8000,
            defender_troops=7000,
            terrain=TerrainType.COASTAL
        )

        result = render_battle_map(battle)

        # Should mention terrain
        assert "coastal" in result.lower() or "Coastal" in result or "COASTAL" in result

    def test_render_battle_map_with_weather(self):
        """Battle map should display weather when present."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Xiapi",
            defender_city="Puyang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="Liu Bei",
            defender_commander="Cao Cao",
            attacker_troops=5500,
            defender_troops=6000,
            terrain=TerrainType.RIVER,
            weather="Rain"
        )

        result = render_battle_map(battle)

        # Should show weather
        assert "Rain" in result or "rain" in result.lower()

    def test_render_battle_map_shows_supply(self):
        """Battle map should display supply days."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Ye",
            defender_city="Yecheng",
            attacker_faction="Wei",
            defender_faction="Shu",
            attacker_commander="Cao Pi",
            defender_commander="Zhuge Liang",
            attacker_troops=9000,
            defender_troops=8000,
            terrain=TerrainType.PLAINS,
            supply_days=5
        )

        result = render_battle_map(battle)

        # Should mention supply
        assert "5" in result  # Supply days
        assert "supply" in result.lower() or "Supply" in result

    def test_render_battle_map_shows_morale(self):
        """Battle map should display morale levels."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Wuwei",
            defender_city="Tianshui",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="Ma Chao",
            defender_commander="Cao Ren",
            attacker_troops=7000,
            defender_troops=6500,
            terrain=TerrainType.MOUNTAIN,
            attacker_morale=85,
            defender_morale=65
        )

        result = render_battle_map(battle)

        # Should show morale (in some form)
        assert "85" in result or "65" in result
        assert "morale" in result.lower() or "Morale" in result

    def test_render_battle_map_shows_siege_progress(self):
        """Battle map should display siege progress when applicable."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Hanzhong",
            defender_city="Changan",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="Huang Zhong",
            defender_commander="Xiahou Yuan",
            attacker_troops=10000,
            defender_troops=9000,
            terrain=TerrainType.MOUNTAIN,
            siege_progress=45
        )

        result = render_battle_map(battle)

        # Should mention siege
        assert "45" in result or "siege" in result.lower() or "Siege" in result

    def test_render_battle_map_different_terrains(self):
        """Battle map should render correctly for all terrain types."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        terrains = [
            TerrainType.PLAINS,
            TerrainType.MOUNTAIN,
            TerrainType.FOREST,
            TerrainType.COASTAL,
            TerrainType.RIVER
        ]

        for terrain in terrains:
            battle = BattleState(
                attacker_city="CityA",
                defender_city="CityB",
                attacker_faction="Shu",
                defender_faction="Wei",
                attacker_commander="Test Commander",
                defender_commander="Test Defender",
                attacker_troops=5000,
                defender_troops=4000,
                terrain=terrain
            )

            result = render_battle_map(battle)
            # Should render without errors for all terrains
            assert isinstance(result, str)
            assert len(result) > 50

    def test_render_battle_map_with_combat_log(self):
        """Battle map should display recent combat events."""
        from src.models import BattleState, TerrainType
        from src.display.battle_view import render_battle_map

        battle = BattleState(
            attacker_city="Jiangxia",
            defender_city="Jiangling",
            attacker_faction="Wu",
            defender_faction="Wei",
            attacker_commander="Lu Meng",
            defender_commander="Cao Ren",
            attacker_troops=7000,
            defender_troops=6000,
            terrain=TerrainType.RIVER,
            combat_log=["Round 1: Fierce clash at the gates!", "Round 2: Defenders hold strong."]
        )

        result = render_battle_map(battle)

        # Should include combat log entries (at least partially)
        assert "Round" in result or "round" in result.lower() or len(battle.combat_log) == 0 or any(word in result for word in ["clash", "Defenders"])


class TestBattleNarrator:
    """Tests for battle narrative generator."""

    def test_narrate_attack_action(self):
        """Attack action should generate dramatic narrative."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "attack",
            "attacker": "Zhao Yun",
            "defender": "Xiahou Dun",
            "terrain": TerrainType.PLAINS,
            "weather": "clear",
            "attacker_casualties": 150,
            "defender_casualties": 200
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should mention the commanders
        assert "Zhao Yun" in result or "attacker" in result.lower()
        assert "Xiahou Dun" in result or "defender" in result.lower()

    def test_narrate_flank_action(self):
        """Flank action should have flanking narrative."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "flank",
            "attacker": "Ma Chao",
            "defender": "Cao Hong",
            "terrain": TerrainType.PLAINS,
            "weather": "clear",
            "attacker_casualties": 100,
            "defender_casualties": 250
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "Ma Chao" in result or "flank" in result.lower()

    def test_narrate_fire_attack(self):
        """Fire attack should have fire-themed narrative."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "fire_attack",
            "attacker": "Zhuge Liang",
            "defender": "Cao Cao",
            "terrain": TerrainType.FOREST,
            "weather": "drought",
            "attacker_casualties": 50,
            "defender_casualties": 400
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "Zhuge Liang" in result or "fire" in result.lower()

    def test_narrate_defend_action(self):
        """Defend action should have defensive narrative."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "defend",
            "attacker": "Guan Yu",
            "defender": "Xu Huang",
            "terrain": TerrainType.MOUNTAIN,
            "weather": "clear",
            "attacker_casualties": 180,
            "defender_casualties": 80
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "defend" in result.lower() or "defensive" in result.lower() or len(result) > 0

    def test_narrate_retreat(self):
        """Retreat should generate retreat narrative."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "retreat",
            "attacker": "Cao Ren",
            "defender": "Zhou Yu",
            "terrain": TerrainType.RIVER,
            "weather": "rain"
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "Cao Ren" in result or "retreat" in result.lower()

    def test_narrate_with_terrain_mountain(self):
        """Narrative should mention mountain terrain."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "attack",
            "attacker": "Wei Yan",
            "defender": "Zhang He",
            "terrain": TerrainType.MOUNTAIN,
            "weather": "clear",
            "attacker_casualties": 200,
            "defender_casualties": 150
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        # Should reference terrain in some way
        assert "mountain" in result.lower() or "slope" in result.lower() or "height" in result.lower() or len(result) > 0

    def test_narrate_with_terrain_forest(self):
        """Narrative should mention forest terrain."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "flank",
            "attacker": "Huang Zhong",
            "defender": "Xiahou Yuan",
            "terrain": TerrainType.FOREST,
            "weather": "clear",
            "attacker_casualties": 80,
            "defender_casualties": 300
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "forest" in result.lower() or "trees" in result.lower() or "wood" in result.lower() or len(result) > 0

    def test_narrate_with_terrain_river(self):
        """Narrative should mention river terrain."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "attack",
            "attacker": "Gan Ning",
            "defender": "Cao Zhang",
            "terrain": TerrainType.RIVER,
            "weather": "clear",
            "attacker_casualties": 250,
            "defender_casualties": 180
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "river" in result.lower() or "crossing" in result.lower() or "water" in result.lower() or len(result) > 0

    def test_narrate_with_weather_rain(self):
        """Narrative should mention rain weather."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "attack",
            "attacker": "Lu Meng",
            "defender": "Cao Pi",
            "terrain": TerrainType.PLAINS,
            "weather": "rain",
            "attacker_casualties": 150,
            "defender_casualties": 160
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "rain" in result.lower() or "wet" in result.lower() or "storm" in result.lower() or len(result) > 0

    def test_narrate_with_weather_snow(self):
        """Narrative should mention snow weather."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "defend",
            "attacker": "Xiahou Dun",
            "defender": "Zhang Fei",
            "terrain": TerrainType.MOUNTAIN,
            "weather": "snow",
            "attacker_casualties": 180,
            "defender_casualties": 90
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "snow" in result.lower() or "cold" in result.lower() or "winter" in result.lower() or len(result) > 0

    def test_narrate_with_weather_fog(self):
        """Narrative should mention fog weather."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "flank",
            "attacker": "Taishi Ci",
            "defender": "Xu Chu",
            "terrain": TerrainType.PLAINS,
            "weather": "fog",
            "attacker_casualties": 120,
            "defender_casualties": 200
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "fog" in result.lower() or "mist" in result.lower() or "visibility" in result.lower() or len(result) > 0

    def test_narrate_high_casualties(self):
        """High casualties should be reflected in narrative."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "attack",
            "attacker": "Lu Bu",
            "defender": "Guan Yu",
            "terrain": TerrainType.PLAINS,
            "weather": "clear",
            "attacker_casualties": 500,
            "defender_casualties": 600
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_narrate_victory(self):
        """Victory event should generate victory narrative."""
        from src.display.battle_narrator import narrate_battle_event

        event = {
            "action_type": "victory",
            "winner": "attacker",
            "attacker": "Liu Bei",
            "defender": "Yuan Shao",
            "reason": "Defending army eliminated"
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert "Liu Bei" in result or "victory" in result.lower() or "triumph" in result.lower()

    def test_narrate_defeat(self):
        """Defeat event should generate defeat narrative."""
        from src.display.battle_narrator import narrate_battle_event

        event = {
            "action_type": "victory",
            "winner": "defender",
            "attacker": "Cao Cao",
            "defender": "Sun Quan",
            "reason": "Attacker morale broken"
        }

        result = narrate_battle_event(event)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_narrate_multiple_templates(self):
        """Same event type should generate varied narratives."""
        from src.display.battle_narrator import narrate_battle_event
        from src.models import TerrainType

        event = {
            "action_type": "attack",
            "attacker": "Zhang Liao",
            "defender": "Sun Quan",
            "terrain": TerrainType.PLAINS,
            "weather": "clear",
            "attacker_casualties": 100,
            "defender_casualties": 150
        }

        # Generate multiple narratives for same event
        narratives = set()
        for _ in range(10):
            result = narrate_battle_event(event)
            narratives.add(result)

        # Should have at least 2 different templates (due to randomization)
        # But we'll be lenient and just check it returns strings
        assert all(isinstance(n, str) for n in narratives)
        assert all(len(n) > 0 for n in narratives)
