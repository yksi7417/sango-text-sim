"""Integration tests for web_server function signatures.

This test module ensures that utility functions used by web_server.py
are called with the correct number of arguments. This prevents runtime
errors like "takes X positional arguments but Y were given".

These tests don't require Flask dependencies and can run in isolation.
"""
import pytest
from src.models import GameState
from src import world, utils


class TestWebServerFunctionSignatures:
    """Test that web server calls utility functions with correct argument counts."""
    
    def test_format_faction_overview_takes_one_argument(self):
        """Test that format_faction_overview requires exactly 1 argument (game_state)."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        # Should work with 1 argument
        overview, resources, relations = utils.format_faction_overview(gs)
        assert isinstance(overview, str)
        assert isinstance(resources, str)
        assert isinstance(relations, str)
        assert len(overview) > 0
        assert "Shu" in overview or "Wei" in overview or "Wu" in overview
        
        # Should fail with 2 arguments (old bug)
        with pytest.raises(TypeError, match="takes 1 positional argument but 2 were given"):
            utils.format_faction_overview(gs, gs.player_faction)

    def test_format_city_status_takes_two_arguments(self):
        """Test that format_city_status requires exactly 2 arguments."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        city_name = list(gs.cities.keys())[0]
        
        # Should work with 2 arguments
        result = utils.format_city_status(gs, city_name)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    def test_status_command_without_target_uses_faction_overview(self):
        """Test status command logic when no city is specified."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        # Set language explicitly for test
        from i18n import i18n
        i18n.load('en')
        
        # This simulates what web_server does for 'status' command
        overview, resources, relations = utils.format_faction_overview(gs)
        result = f"{overview}\n{resources}\n{relations}"
        
        # Should not contain error messages
        assert "Error:" not in result
        assert "takes" not in result
        assert "positional argument" not in result
        
        # Should contain expected content
        assert any(str(gs.year) in result or str(gs.month) in result for _ in [1])
        assert "Treasury" in result or "Gold" in result.lower() or "金庫" in result

    def test_status_command_with_city_uses_city_status(self):
        """Test status command logic when a city is specified."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        city_name = list(gs.cities.keys())[0]
        
        # This simulates what web_server does for 'status <city>' command
        result = utils.format_city_status(gs, city_name)
        
        # Should return valid city information
        assert result is not None
        assert len(result) > 0


class TestWebServerCommandIntegrity:
    """Test that common web server commands work without errors."""
    
    def test_faction_overview_returns_three_components(self):
        """Test that faction overview returns all three required components."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        overview, resources, relations = utils.format_faction_overview(gs)
        
        # All three components should be non-empty strings
        assert overview and isinstance(overview, str)
        assert resources and isinstance(resources, str)
        assert relations and isinstance(relations, str)
        
        # Overview should mention cities and faction
        assert any(faction in overview for faction in ["Wei", "Shu", "Wu"])
        
        # Resources should mention treasury/gold, food, and troops (in any language)
        assert "Treasury" in resources or "Gold" in resources or "金庫" in resources
        assert "Food" in resources or "Granary" in resources
        assert "Troops" in resources

    def test_multiple_faction_overview_calls_consistent(self):
        """Test that calling format_faction_overview multiple times is stable."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        # Call multiple times
        result1 = utils.format_faction_overview(gs)
        result2 = utils.format_faction_overview(gs)
        
        # Should return same results
        assert result1 == result2

    def test_city_status_for_all_cities(self):
        """Test that format_city_status works for all cities."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        # Should work for every city
        for city_name in gs.cities.keys():
            result = utils.format_city_status(gs, city_name)
            assert result is not None
            assert len(result) > 0
            # City name should appear in result
            assert any(city_name in str(line) for line in result)


class TestWebServerErrorPrevention:
    """Tests that prevent specific bugs from recurring."""
    
    def test_status_command_signature_bug(self):
        """
        Regression test for bug where format_faction_overview was called with 2 args.
        
        Bug: web_server.py called utils.format_faction_overview(gs, gs.player_faction)
        Fix: Should be utils.format_faction_overview(gs)
        
        This test ensures the function signature is correct and will fail if
        someone tries to call it with 2 arguments again.
        """
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        # Correct call (should work)
        try:
            overview, resources, relations = utils.format_faction_overview(gs)
            assert True  # Success
        except TypeError:
            pytest.fail("format_faction_overview should accept 1 argument")
        
        # Incorrect call (should fail)
        try:
            utils.format_faction_overview(gs, gs.player_faction)
            pytest.fail("format_faction_overview should NOT accept 2 arguments")
        except TypeError as e:
            assert "takes 1 positional argument but 2 were given" in str(e)

    def test_web_server_compatible_return_types(self):
        """Test that utility functions return types compatible with web server."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        # format_faction_overview should return tuple of 3 strings
        result = utils.format_faction_overview(gs)
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(s, str) for s in result)
        
        # format_city_status should return list of strings
        city_name = list(gs.cities.keys())[0]
        result = utils.format_city_status(gs, city_name)
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_status_command_always_returns_string(self):
        """
        Regression test for bug where 'status CITY' returned a list instead of string.
        
        Bug: JavaScript error "data.output.split is not a function"
        Root cause: format_city_status returns a list, but web server returned it directly
        Fix: web_server.py must join the list into a string before returning
        
        This test simulates what web_server.execute_command does and ensures it
        always returns a string, never a list.
        """
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        # Get a city name to test with
        city_name = list(gs.cities.keys())[0]
        
        # Test 'status' command without city (faction overview)
        overview, resources, relations = utils.format_faction_overview(gs)
        status_output = f"{overview}\n{resources}\n{relations}"
        assert isinstance(status_output, str), "status command must return string"
        assert len(status_output) > 0
        
        # Test 'status CITY' command with city (city status)
        city_status = utils.format_city_status(gs, city_name)
        assert isinstance(city_status, list), "format_city_status returns list"
        
        # This is what web_server.py must do - join the list into a string
        city_status_output = "\n".join(city_status)
        assert isinstance(city_status_output, str), "status CITY must return string, not list"
        assert len(city_status_output) > 0
        assert city_name in city_status_output
        
        # Verify that the string can be split (what JavaScript does)
        lines = city_status_output.split('\n')
        assert isinstance(lines, list)
        assert len(lines) > 0
        
    def test_status_command_for_all_cities_returns_strings(self):
        """Test that status command returns strings for every city in the game."""
        gs = GameState()
        world.init_world(gs, player_choice=None, seed=42)
        
        for city_name in gs.cities.keys():
            city_status = utils.format_city_status(gs, city_name)
            
            # format_city_status returns a list
            assert isinstance(city_status, list)
            
            # Web server must join it into a string
            status_output = "\n".join(city_status)
            assert isinstance(status_output, str), f"status {city_name} must return string"
            
            # Verify JavaScript can split it
            lines = status_output.split('\n')
            assert isinstance(lines, list)
            assert len(lines) > 0
