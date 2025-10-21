"""
End-to-end tests for web server integration.
Tests the full stack: Flask routes, session management, game state, and frontend integration.
"""
import pytest
import json
from web_server import app, game_states, session_states


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session-e2e'
        yield client
    
    # Cleanup
    if 'test-session-e2e' in game_states:
        del game_states['test-session-e2e']
    if 'test-session-e2e' in session_states:
        del session_states['test-session-e2e']


class TestPregameFlow:
    """Test the pregame flow: start game, choose faction."""
    
    def test_start_command_works(self, client):
        """Test that 'start' command initializes the game."""
        response = client.post('/api/command',
                             json={'command': 'start'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return success message
        assert 'choose' in data['output'].lower() or 'faction' in data['output'].lower()
        
        # Menu state should still be pregame (waiting for faction choice)
        assert data['menu_state']['current_menu'] == 'pregame'
        
        # Game creates factions but session flag should be False
        # (game_started flag from session_state is False until 'choose' is called)
        assert data['game_state']['game_started'] == True  # World is initialized
    
    def test_choose_faction_works(self, client):
        """Test that 'choose Wei' command sets up the game."""
        response = client.post('/api/command',
                             json={'command': 'choose Wei'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return success message
        assert 'Wei' in data['output']
        
        # Menu state should change to main
        assert data['menu_state']['current_menu'] == 'main'
        
        # Game should be started
        assert data['game_state']['game_started'] == True
        assert data['game_state']['faction'] == 'Wei'
    
    def test_full_pregame_flow(self, client):
        """Test the complete pregame flow from start to playing."""
        # Step 1: Start game
        response1 = client.post('/api/command',
                               json={'command': 'start'},
                               content_type='application/json')
        data1 = json.loads(response1.data)
        assert data1['menu_state']['current_menu'] == 'pregame'
        # After 'start', world is initialized so game_started is True
        assert data1['game_state']['game_started'] == True
        
        # Step 2: Choose faction
        response2 = client.post('/api/command',
                               json={'command': 'choose Shu'},
                               content_type='application/json')
        data2 = json.loads(response2.data)
        assert data2['menu_state']['current_menu'] == 'main'
        assert data2['game_state']['game_started'] == True
        assert data2['game_state']['faction'] == 'Shu'
        
        # Step 3: Verify we can access game commands
        response3 = client.post('/api/command',
                               json={'command': 'status'},
                               content_type='application/json')
        data3 = json.loads(response3.data)
        assert 'Shu' in data3['output']
        assert 'not initialized' not in data3['output'].lower()


class TestMenuNavigation:
    """Test menu navigation after game starts."""
    
    @pytest.fixture(autouse=True)
    def setup_game(self, client):
        """Setup a game before each test."""
        client.post('/api/command',
                   json={'command': 'choose Wei'},
                   content_type='application/json')
    
    def test_navigate_to_internal_affairs(self, client):
        """Test navigating to internal affairs menu."""
        # Navigate to internal affairs (option 5)
        response = client.post('/api/command',
                             json={'command': '5'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['menu_state']['current_menu'] == 'internal'
    
    def test_navigate_back_to_main(self, client):
        """Test navigating back to main menu."""
        # Go to internal affairs
        client.post('/api/command',
                   json={'command': '5'},
                   content_type='application/json')
        
        # Go back
        response = client.post('/api/command',
                             json={'command': '0'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['menu_state']['current_menu'] == 'main'


class TestGameStateConsistency:
    """Test that game state remains consistent across requests."""
    
    def test_state_persists_across_requests(self, client):
        """Test that choosing a faction persists."""
        # Choose faction
        client.post('/api/command',
                   json={'command': 'choose Wu'},
                   content_type='application/json')
        
        # Make another request
        response = client.post('/api/command',
                             json={'command': 'status'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['game_state']['faction'] == 'Wu'
        assert data['game_state']['game_started'] == True
    
    def test_cannot_access_menus_without_starting(self, client):
        """Test that menu commands are rejected before game starts."""
        # Try to navigate to internal affairs without starting
        response = client.post('/api/command',
                             json={'command': '5'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        # Should stay in pregame or return to pregame
        assert data['menu_state']['current_menu'] == 'pregame'


class TestLanguageSwitching:
    """Test language switching functionality."""
    
    def test_language_switch_english(self, client):
        """Test switching to English."""
        response = client.post('/api/command',
                             json={'command': 'lang en'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['menu_state']['language'] == 'en'
    
    def test_language_switch_chinese(self, client):
        """Test switching to Chinese."""
        response = client.post('/api/command',
                             json={'command': 'lang zh'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['menu_state']['language'] == 'zh'


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_command(self, client):
        """Test handling of invalid commands."""
        client.post('/api/command',
                   json={'command': 'choose Wei'},
                   content_type='application/json')
        
        response = client.post('/api/command',
                             json={'command': 'invalidcommand'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert 'unknown' in data['output'].lower() or 'invalid' in data['output'].lower()
    
    def test_empty_command(self, client):
        """Test handling of empty commands."""
        response = client.post('/api/command',
                             json={'command': ''},
                             content_type='application/json')
        
        assert response.status_code == 200
        # Should not crash


class TestBugPreventionRegression:
    """Tests specifically to prevent the 'not yet implemented' bug from recurring."""
    
    def test_pregame_commands_not_treated_as_menu_navigation(self, client):
        """
        Regression test: Ensure 'start' and 'choose' commands work from pregame state.
        
        Bug: pregame menu was being handled by handle_menu_input() which doesn't
        know about 'start' or 'choose' commands, resulting in "not yet implemented" messages.
        
        Fix: execute_command() now excludes 'pregame' from menu handler routing.
        """
        # This should work, not return "not yet implemented"
        response = client.post('/api/command',
                             json={'command': 'start'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert 'not yet implemented' not in data['output'].lower()
        assert 'not implemented' not in data['output'].lower()
        assert 'choose' in data['output'].lower()
    
    def test_choose_command_not_treated_as_menu_navigation(self, client):
        """
        Regression test: Ensure 'choose Wei' works from pregame state.
        """
        response = client.post('/api/command',
                             json={'command': 'choose Wei'},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert 'not yet implemented' not in data['output'].lower()
        assert 'not implemented' not in data['output'].lower()
        assert data['game_state']['faction'] == 'Wei'
        assert data['game_state']['game_started'] == True
    
    def test_all_factions_choosable(self, client):
        """Test that all three factions can be chosen."""
        for faction in ['Wei', 'Shu', 'Wu']:
            # Cleanup
            if 'test-session-e2e' in game_states:
                del game_states['test-session-e2e']
            if 'test-session-e2e' in session_states:
                del session_states['test-session-e2e']
            
            response = client.post('/api/command',
                                 json={'command': f'choose {faction}'},
                                 content_type='application/json')
            
            data = json.loads(response.data)
            assert 'not yet implemented' not in data['output'].lower()
            assert data['game_state']['faction'] == faction
            assert data['game_state']['game_started'] == True
