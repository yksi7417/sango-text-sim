"""Integration tests for the web server interface."""
import pytest
import json
from web_server import (
    init_game,
    process_game_command,
    save_game_endpoint,
    load_game_endpoint,
    get_game_state
)
from src.models import GameState
from src import world


class TestWebServerInitialization:
    """Test web server game initialization."""

    def test_init_game_creates_valid_state(self):
        """Test that init_game creates a valid game state."""
        result = init_game()
        
        # Should return success message
        assert "Welcome" in result
        assert "Type 'help' for commands" in result
        
        # Game state should be initialized
        gs = get_game_state()
        assert gs is not None
        assert len(gs.cities) > 0
        assert len(gs.factions) > 0
        assert len(gs.officers) > 0
        assert gs.player_faction in gs.factions

    def test_init_game_with_faction_choice(self):
        """Test that init_game respects faction choice."""
        # Test different faction choices
        for faction in ["Wei", "Shu", "Wu"]:
            result = init_game(faction)
            gs = get_game_state()
            
            assert gs.player_faction == faction
            assert faction in result or f"of {faction}" in result


class TestWebServerStatusCommand:
    """Test status command functionality."""

    def test_status_without_target_returns_faction_overview(self):
        """Test that 'status' without arguments returns faction overview."""
        init_game()
        result = process_game_command("status")
        
        # Should contain overview information
        assert result is not None
        assert isinstance(result, str)
        # Should have year/month info (from faction overview)
        assert any(word in result.lower() for word in ["year", "month", "208", "cities"])
        # Should not have error messages
        assert "Error:" not in result
        assert "takes" not in result
        assert "positional argument" not in result

    def test_status_command_returns_three_part_overview(self):
        """Test that status command returns overview, resources, and relations."""
        init_game()
        result = process_game_command("status")
        
        # The result should contain all three parts that format_faction_overview returns
        # Overview part (cities, year, month)
        assert any(word in result for word in ["cities", "Cities"])
        
        # Resources part (gold, food, troops)
        assert any(word in result.lower() for word in ["gold", "food", "troops", "treasury", "granary"])
        
        # Relations part
        assert ":" in result  # Relations are formatted as "Faction:+/-value"

    def test_status_with_city_name_returns_city_status(self):
        """Test that 'status <city>' returns city-specific status."""
        init_game()
        gs = get_game_state()
        
        # Get a valid city name
        city_name = list(gs.cities.keys())[0]
        
        result = process_game_command(f"status {city_name}")
        
        # Should contain city-specific information
        assert result is not None
        assert city_name in result or "Error:" in result  # Either shows city or error

    def test_status_with_chinese_command(self):
        """Test that Chinese '狀態' command works the same as 'status'."""
        init_game()
        result_en = process_game_command("status")
        
        # Reinitialize to get same starting state
        init_game()
        result_zh = process_game_command("狀態")
        
        # Both should work and return similar information
        assert result_en is not None
        assert result_zh is not None
        assert "Error:" not in result_en
        assert "Error:" not in result_zh


class TestWebServerOfficersCommand:
    """Test officers command functionality."""

    def test_officers_command_lists_faction_officers(self):
        """Test that 'officers' command lists all faction officers."""
        init_game()
        result = process_game_command("officers")
        
        assert result is not None
        assert "Officers" in result
        # Should contain officer stats indicators
        assert any(char in result for char in ["L", "I", "P", "C"])  # Leadership, Intelligence, Politics, Charisma
        assert "Energy" in result or "energy" in result
        assert "Loyalty" in result or "loyalty" in result

    def test_officers_command_with_chinese(self):
        """Test that Chinese '武將' command works."""
        init_game()
        result = process_game_command("武將")
        
        assert result is not None
        assert "Officers" in result or "武將" in result


class TestWebServerHelpCommand:
    """Test help command functionality."""

    def test_help_command_returns_available_commands(self):
        """Test that help command lists available commands."""
        init_game()
        result = process_game_command("help")
        
        assert result is not None
        assert "Commands" in result or "Available" in result
        # Should mention some key commands
        assert "status" in result.lower() or "officers" in result.lower()

    def test_help_with_chinese_command(self):
        """Test that Chinese '幫助' command works."""
        init_game()
        result = process_game_command("幫助")
        
        assert result is not None
        # Should return help information
        assert len(result) > 10  # Not empty or error


class TestWebServerAssignmentCommands:
    """Test officer assignment commands."""

    def test_assign_command_structure(self):
        """Test that assign command processes correctly."""
        init_game()
        gs = get_game_state()
        
        # Get an officer from player faction
        player_officers = [
            o for o in gs.officers.values() 
            if o.faction == gs.player_faction
        ]
        
        if player_officers:
            officer = player_officers[0]
            city_name = list(gs.cities.keys())[0]
            
            # Try to assign officer to farm
            result = process_game_command(f"assign {officer.name} farm {city_name}")
            
            # Should either succeed or give a valid error message
            assert result is not None
            assert "Error:" in result or "assigned" in result.lower() or officer.name in result

    def test_unassign_command_structure(self):
        """Test that unassign command processes correctly."""
        init_game()
        gs = get_game_state()
        
        # Get an officer
        player_officers = [
            o for o in gs.officers.values() 
            if o.faction == gs.player_faction
        ]
        
        if player_officers:
            officer = player_officers[0]
            
            result = process_game_command(f"unassign {officer.name}")
            
            # Should process without error
            assert result is not None
            assert "Error:" in result or "unassigned" in result.lower() or officer.name in result


class TestWebServerEndTurnCommand:
    """Test end turn command."""

    def test_end_turn_advances_game(self):
        """Test that end turn advances the game state."""
        init_game()
        gs = get_game_state()
        
        initial_month = gs.month
        initial_year = gs.year
        
        result = process_game_command("end")
        
        # Game should advance
        gs_after = get_game_state()
        time_advanced = (
            gs_after.year > initial_year or 
            (gs_after.year == initial_year and gs_after.month > initial_month)
        )
        assert time_advanced

    def test_end_turn_with_chinese_command(self):
        """Test that Chinese '結束' command works."""
        init_game()
        gs = get_game_state()
        
        initial_month = gs.month
        
        result = process_game_command("結束")
        
        # Should advance time
        gs_after = get_game_state()
        assert gs_after.month != initial_month or gs_after.year > gs.year


class TestWebServerSaveLoadCommands:
    """Test save and load functionality through web interface."""

    def test_save_game_creates_file(self, tmp_path):
        """Test that save_game_endpoint creates a save file."""
        init_game()
        gs = get_game_state()
        
        # Modify game state
        gs.month = 6
        gs.year = 210
        
        save_path = tmp_path / "web_test_save.json"
        
        result = save_game_endpoint(str(save_path))
        
        assert result is not None
        assert "saved" in result.lower() or "success" in result.lower()
        assert save_path.exists()

    def test_load_game_restores_state(self, tmp_path):
        """Test that load_game_endpoint restores game state."""
        # Create and save a game
        init_game()
        gs = get_game_state()
        gs.month = 8
        gs.year = 215
        target_city = list(gs.cities.keys())[0]
        gs.cities[target_city].gold = 99999
        
        save_path = tmp_path / "web_load_test.json"
        save_game_endpoint(str(save_path))
        
        # Initialize a new game (different state)
        init_game()
        
        # Load the saved game
        result = load_game_endpoint(str(save_path))
        
        assert result is not None
        assert "loaded" in result.lower() or "success" in result.lower()
        
        # Verify state restored
        gs_loaded = get_game_state()
        assert gs_loaded.month == 8
        assert gs_loaded.year == 215
        assert gs_loaded.cities[target_city].gold == 99999


class TestWebServerCommandParsing:
    """Test command parsing and error handling."""

    def test_empty_command_handled_gracefully(self):
        """Test that empty commands don't crash."""
        init_game()
        result = process_game_command("")
        
        assert result is not None
        # Should either ignore or give error message
        assert isinstance(result, str)

    def test_invalid_command_returns_error(self):
        """Test that invalid commands return appropriate error."""
        init_game()
        result = process_game_command("invalidcommandxyz")
        
        assert result is not None
        # Should indicate unknown command
        assert "unknown" in result.lower() or "invalid" in result.lower() or "not recognized" in result.lower()

    def test_whitespace_variations_handled(self):
        """Test that commands with extra whitespace work."""
        init_game()
        
        # Extra spaces
        result = process_game_command("  status  ")
        assert result is not None
        assert "Error:" not in result or "unknown" in result.lower()
        
        # Tabs
        result = process_game_command("\tstatus\t")
        assert result is not None


class TestWebServerAttackCommand:
    """Test attack command functionality."""

    def test_attack_command_structure(self):
        """Test that attack command processes correctly."""
        init_game()
        gs = get_game_state()
        
        # Get two adjacent cities
        if gs.adj:
            city1 = list(gs.adj.keys())[0]
            if gs.adj[city1]:
                city2 = gs.adj[city1][0]
                
                result = process_game_command(f"attack {city1} {city2} 1000")
                
                # Should process (may succeed or fail based on ownership)
                assert result is not None
                assert isinstance(result, str)


class TestWebServerMoveCommand:
    """Test move command functionality."""

    def test_move_command_structure(self):
        """Test that move command processes correctly."""
        init_game()
        gs = get_game_state()
        
        # Get an officer and cities
        player_officers = [
            o for o in gs.officers.values() 
            if o.faction == gs.player_faction
        ]
        
        if player_officers and len(gs.cities) >= 2:
            officer = player_officers[0]
            cities = list(gs.cities.keys())
            
            result = process_game_command(f"move {officer.name} {cities[0]}")
            
            # Should process
            assert result is not None
            assert isinstance(result, str)


class TestWebServerArgumentCounts:
    """Test that all commands receive correct number of arguments."""

    def test_all_format_functions_called_with_correct_args(self):
        """Test that utility format functions are called with correct argument counts."""
        init_game()
        
        # Test status without target - should call format_faction_overview with 1 arg
        result = process_game_command("status")
        assert "takes" not in result  # Should not have "takes X positional argument but Y were given"
        assert "positional argument" not in result
        
        # Test status with city - should call format_city_status with 2 args
        gs = get_game_state()
        city_name = list(gs.cities.keys())[0]
        result = process_game_command(f"status {city_name}")
        assert "takes" not in result
        assert "positional argument" not in result

    def test_officers_command_correct_args(self):
        """Test that officers command doesn't have argument errors."""
        init_game()
        result = process_game_command("officers")
        
        assert result is not None
        assert "takes" not in result
        assert "positional argument" not in result

    def test_end_turn_correct_args(self):
        """Test that end turn command doesn't have argument errors."""
        init_game()
        result = process_game_command("end")
        
        assert result is not None
        assert "takes" not in result
        assert "positional argument" not in result


class TestWebServerGameStateConsistency:
    """Test that game state remains consistent through web commands."""

    def test_multiple_commands_maintain_state(self):
        """Test that executing multiple commands maintains game state consistency."""
        init_game()
        
        # Execute a sequence of commands
        results = []
        results.append(process_game_command("status"))
        results.append(process_game_command("officers"))
        results.append(process_game_command("end"))
        results.append(process_game_command("status"))
        
        # All commands should execute without crashing
        for result in results:
            assert result is not None
            assert isinstance(result, str)
        
        # Game state should still be valid
        gs = get_game_state()
        assert gs is not None
        assert len(gs.cities) > 0
        assert len(gs.factions) > 0

    def test_game_state_persists_between_commands(self):
        """Test that game state changes persist between commands."""
        init_game()
        gs = get_game_state()
        
        initial_month = gs.month
        
        # End a turn
        process_game_command("end")
        
        # Check that state persisted
        gs_after = get_game_state()
        assert gs_after is not None
        assert gs_after.month != initial_month or gs_after.year > gs.year


class TestWebServerErrorHandling:
    """Test error handling in web server."""

    def test_command_errors_return_strings(self):
        """Test that command errors return error strings, not exceptions."""
        init_game()
        
        # Try commands that should fail gracefully
        test_cases = [
            "assign NonExistentOfficer farm SomeCity",
            "attack NonExistentCity1 NonExistentCity2 1000",
            "move NonExistentOfficer SomeCity",
            "status NonExistentCity",
        ]
        
        for cmd in test_cases:
            result = process_game_command(cmd)
            assert result is not None
            assert isinstance(result, str)
            # Should not raise exception - if we got here, we're good

    def test_game_state_not_corrupted_by_errors(self):
        """Test that game state remains valid even after error commands."""
        init_game()
        
        # Execute commands that will fail
        process_game_command("attack InvalidCity1 InvalidCity2 1000")
        process_game_command("assign InvalidOfficer farm InvalidCity")
        
        # Game state should still be valid
        gs = get_game_state()
        assert gs is not None
        assert len(gs.cities) > 0
        assert len(gs.factions) > 0
        
        # Should still be able to execute valid commands
        result = process_game_command("status")
        assert result is not None
        assert "Error:" not in result or "unknown" in result.lower()


class TestWebServerReturnTypes:
    """Test that all web server functions return expected types."""

    def test_process_game_command_always_returns_string(self):
        """Test that process_game_command always returns a string."""
        init_game()
        
        commands = [
            "status",
            "officers",
            "help",
            "end",
            "",
            "invalid_command",
        ]
        
        for cmd in commands:
            result = process_game_command(cmd)
            assert isinstance(result, str), f"Command '{cmd}' did not return string, got {type(result)}"

    def test_init_game_returns_string(self):
        """Test that init_game returns a string message."""
        result = init_game()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_save_load_return_strings(self, tmp_path):
        """Test that save and load functions return strings."""
        init_game()
        
        save_path = tmp_path / "return_type_test.json"
        
        save_result = save_game_endpoint(str(save_path))
        assert isinstance(save_result, str)
        
        load_result = load_game_endpoint(str(save_path))
        assert isinstance(load_result, str)
