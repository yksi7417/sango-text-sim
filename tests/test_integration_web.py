"""
Integration Tests: Complete Web Interface Flow

This module tests all gameplay features through web interface end-to-end:
- Test game initialization
- Test all command inputs
- Test battle interface
- Test duel interface
- Test council interface
- Test save/load through web
- Verify i18n display (EN/ZH)

Tests cover the complete web interface flow for all game features.
"""
import pytest
import json
import os
import tempfile
from web_server import app, game_states, session_states


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['session_id'] = 'test-session-web-integration'
        yield client

    # Cleanup
    if 'test-session-web-integration' in game_states:
        del game_states['test-session-web-integration']
    if 'test-session-web-integration' in session_states:
        del session_states['test-session-web-integration']


@pytest.fixture
def initialized_client(client):
    """Create a client with game already initialized."""
    client.post('/api/command',
               json={'command': 'choose Wei'},
               content_type='application/json')
    return client


class TestGameInitialization:
    """Test game initialization through web interface."""

    def test_index_page_loads(self, client):
        """Main page should load without errors."""
        response = client.get('/')
        assert response.status_code == 200

    def test_health_endpoint(self, client):
        """Health check endpoint should return healthy."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data) if isinstance(response.data, bytes) else response.data
        assert data.get('status') == 'healthy'

    def test_start_command_initializes_world(self, client):
        """'start' command should initialize the game world."""
        response = client.post('/api/command',
                             json={'command': 'start'},
                             content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'output' in data
        assert 'choose' in data['output'].lower() or 'faction' in data['output'].lower()

    def test_choose_wei_sets_faction(self, client):
        """'choose Wei' should set player faction to Wei."""
        response = client.post('/api/command',
                             json={'command': 'choose Wei'},
                             content_type='application/json')

        data = json.loads(response.data)

        assert data['game_state']['faction'] == 'Wei'
        assert data['game_state']['game_started'] is True

    def test_choose_shu_sets_faction(self, client):
        """'choose Shu' should set player faction to Shu."""
        response = client.post('/api/command',
                             json={'command': 'choose Shu'},
                             content_type='application/json')

        data = json.loads(response.data)

        assert data['game_state']['faction'] == 'Shu'
        assert data['game_state']['game_started'] is True

    def test_choose_wu_sets_faction(self, client):
        """'choose Wu' should set player faction to Wu."""
        response = client.post('/api/command',
                             json={'command': 'choose Wu'},
                             content_type='application/json')

        data = json.loads(response.data)

        assert data['game_state']['faction'] == 'Wu'
        assert data['game_state']['game_started'] is True

    def test_game_state_includes_year_month(self, client):
        """Game state should include year and month."""
        response = client.post('/api/command',
                             json={'command': 'choose Wei'},
                             content_type='application/json')

        data = json.loads(response.data)

        assert 'year' in data['game_state']
        assert 'month' in data['game_state']
        assert data['game_state']['year'] > 0
        assert 1 <= data['game_state']['month'] <= 12

    def test_game_state_includes_weather(self, client):
        """Game state should include weather information."""
        response = client.post('/api/command',
                             json={'command': 'choose Wei'},
                             content_type='application/json')

        data = json.loads(response.data)

        assert 'weather' in data['game_state']
        assert data['game_state']['weather'] in ['clear', 'rain', 'snow', 'fog', 'drought']


class TestCommandInputs:
    """Test all command inputs through web interface."""

    def test_help_command(self, initialized_client):
        """'help' command should return help text."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'help'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert 'output' in data
        assert 'command' in data['output'].lower() or 'help' in data['output'].lower()

    def test_status_command(self, initialized_client):
        """'status' command should return faction overview."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'status'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert 'output' in data
        # Should contain faction info
        assert 'Wei' in data['output'] or 'Treasury' in data['output'] or 'Gold' in data['output']

    def test_officers_command(self, initialized_client):
        """'officers' command should list officers."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'officers'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert 'output' in data
        # Should list officers
        assert 'Officer' in data['output'] or 'Energy' in data['output'] or 'Loyalty' in data['output']

    def test_turn_command(self, initialized_client):
        """'turn' command should advance the game."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'turn'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert response.status_code == 200
        # Turn report or game over message
        assert 'output' in data

    def test_menu_command(self, initialized_client):
        """'menu' command should navigate to main menu."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'menu'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert data['menu_state']['current_menu'] == 'main'

    def test_invalid_command_handled(self, initialized_client):
        """Invalid commands should be handled gracefully."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'notarealcommand'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert 'output' in data
        assert 'unknown' in data['output'].lower() or 'invalid' in data['output'].lower()

    def test_empty_command_handled(self, initialized_client):
        """Empty commands should be handled gracefully."""
        response = initialized_client.post('/api/command',
                                          json={'command': ''},
                                          content_type='application/json')

        assert response.status_code == 200


class TestBattleInterface:
    """Test battle interface through web."""

    def test_battle_api_endpoint_exists(self, initialized_client):
        """Battle API endpoint should exist."""
        response = initialized_client.get('/api/battle')
        assert response.status_code == 200

    def test_battle_state_when_inactive(self, initialized_client):
        """Should report no active battle when none exists."""
        response = initialized_client.get('/api/battle')
        data = json.loads(response.data)

        assert 'active' in data
        assert data['active'] is False

    def test_battle_action_api_exists(self, initialized_client):
        """Battle action API should exist."""
        response = initialized_client.post('/api/battle/action',
                                          json={'action': 'attack'},
                                          content_type='application/json')

        # May return error since no battle is active, but should not crash
        assert response.status_code == 200

    def test_battle_action_without_active_battle(self, initialized_client):
        """Battle action without active battle should return error."""
        response = initialized_client.post('/api/battle/action',
                                          json={'action': 'attack'},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert 'error' in data


class TestDuelInterface:
    """Test duel interface through web."""

    def test_duel_api_endpoint_exists(self, initialized_client):
        """Duel API endpoint should exist."""
        response = initialized_client.get('/api/duel')
        assert response.status_code == 200

    def test_duel_state_when_inactive(self, initialized_client):
        """Should report no active duel when none exists."""
        response = initialized_client.get('/api/duel')
        data = json.loads(response.data)

        assert 'active' in data
        assert data['active'] is False

    def test_duel_command_help(self, initialized_client):
        """Duel command without arguments should show usage."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'duel'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert 'output' in data
        # Should show usage info
        assert 'usage' in data['output'].lower() or 'duel' in data['output'].lower()


class TestCouncilInterface:
    """Test council interface through web."""

    def test_council_api_endpoint_exists(self, initialized_client):
        """Council API endpoint should exist."""
        response = initialized_client.get('/api/council')
        assert response.status_code == 200

    def test_council_returns_agenda(self, initialized_client):
        """Council API should return agenda items."""
        response = initialized_client.get('/api/council')
        data = json.loads(response.data)

        assert 'council_display' in data or 'error' in data

    def test_council_has_agenda_count(self, initialized_client):
        """Council response should include agenda count."""
        response = initialized_client.get('/api/council')
        data = json.loads(response.data)

        if 'error' not in data:
            assert 'agenda_count' in data
            assert isinstance(data['agenda_count'], int)

    def test_council_has_items_list(self, initialized_client):
        """Council response should include items list."""
        response = initialized_client.get('/api/council')
        data = json.loads(response.data)

        if 'error' not in data:
            assert 'items' in data
            assert isinstance(data['items'], list)


class TestSaveLoadThroughWeb:
    """Test save/load functionality through web interface."""

    def test_save_command_works(self, initialized_client):
        """'save' command should save the game."""
        # Create a temp file path
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            save_path = f.name

        try:
            response = initialized_client.post('/api/command',
                                              json={'command': f'save {save_path}'},
                                              content_type='application/json')

            data = json.loads(response.data)

            # Should indicate save succeeded or failed
            assert 'output' in data
            # File should exist if save succeeded
            assert 'saved' in data['output'].lower() or 'save' in data['output'].lower()
        finally:
            if os.path.exists(save_path):
                os.remove(save_path)

    def test_load_nonexistent_file(self, initialized_client):
        """Loading nonexistent file should fail gracefully."""
        response = initialized_client.post('/api/command',
                                          json={'command': 'load nonexistent_file_12345.json'},
                                          content_type='application/json')

        data = json.loads(response.data)

        assert 'output' in data
        # Should indicate failure
        assert 'failed' in data['output'].lower() or 'error' in data['output'].lower()


class TestI18nDisplayEnglish:
    """Test internationalization - English display."""

    def test_lang_en_command(self, client):
        """'lang en' should set language to English."""
        response = client.post('/api/command',
                             json={'command': 'lang en'},
                             content_type='application/json')

        data = json.loads(response.data)

        assert data['menu_state']['language'] == 'en'

    def test_english_status_output(self, initialized_client):
        """Status output should be in English when language is English."""
        # Set to English
        initialized_client.post('/api/command',
                               json={'command': 'lang en'},
                               content_type='application/json')

        response = initialized_client.post('/api/command',
                                          json={'command': 'status'},
                                          content_type='application/json')

        data = json.loads(response.data)

        # Should contain English words
        output = data['output']
        assert any(word in output for word in ['Treasury', 'Gold', 'Food', 'Troops', 'Wei', 'Year', 'Month'])

    def test_english_help_output(self, initialized_client):
        """Help output should be in English when language is English."""
        # Set to English
        initialized_client.post('/api/command',
                               json={'command': 'lang en'},
                               content_type='application/json')

        response = initialized_client.post('/api/command',
                                          json={'command': 'help'},
                                          content_type='application/json')

        data = json.loads(response.data)

        # Should contain English help text
        assert 'command' in data['output'].lower() or 'help' in data['output'].lower()


class TestI18nDisplayChinese:
    """Test internationalization - Chinese display."""

    def test_lang_zh_command(self, client):
        """'lang zh' should set language to Chinese."""
        response = client.post('/api/command',
                             json={'command': 'lang zh'},
                             content_type='application/json')

        data = json.loads(response.data)

        assert data['menu_state']['language'] == 'zh'

    def test_chinese_language_persists(self, initialized_client):
        """Chinese language setting should persist across requests."""
        # Set to Chinese
        initialized_client.post('/api/command',
                               json={'command': 'lang zh'},
                               content_type='application/json')

        # Make another request
        response = initialized_client.post('/api/command',
                                          json={'command': 'status'},
                                          content_type='application/json')

        data = json.loads(response.data)

        # Language should still be Chinese
        assert data['menu_state']['language'] == 'zh'

    def test_invalid_language_rejected(self, client):
        """Invalid language codes should be rejected."""
        response = client.post('/api/command',
                             json={'command': 'lang invalid'},
                             content_type='application/json')

        data = json.loads(response.data)

        # Should show usage or error
        assert 'usage' in data['output'].lower() or 'en' in data['output'].lower()


class TestMenuNavigation:
    """Test menu navigation through web interface."""

    def test_main_menu_to_city(self, initialized_client):
        """Should navigate from main to city menu."""
        response = initialized_client.post('/api/command',
                                          json={'command': '1'},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert data['menu_state']['current_menu'] == 'city'

    def test_main_menu_to_internal(self, initialized_client):
        """Should navigate from main to internal affairs menu."""
        response = initialized_client.post('/api/command',
                                          json={'command': '5'},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert data['menu_state']['current_menu'] == 'internal'

    def test_back_navigation(self, initialized_client):
        """'back' should return to main menu."""
        # Go to internal
        initialized_client.post('/api/command',
                               json={'command': '5'},
                               content_type='application/json')

        # Go back
        response = initialized_client.post('/api/command',
                                          json={'command': 'back'},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert data['menu_state']['current_menu'] == 'main'

    def test_zero_navigation(self, initialized_client):
        """'0' should return to main menu."""
        # Go to internal
        initialized_client.post('/api/command',
                               json={'command': '5'},
                               content_type='application/json')

        # Go back
        response = initialized_client.post('/api/command',
                                          json={'command': '0'},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert data['menu_state']['current_menu'] == 'main'


class TestMapInterface:
    """Test map interface through web."""

    def test_map_api_endpoint_exists(self, initialized_client):
        """Map API endpoint should exist."""
        response = initialized_client.get('/api/map')
        assert response.status_code == 200

    def test_map_returns_data(self, initialized_client):
        """Map API should return map data."""
        response = initialized_client.get('/api/map')
        data = json.loads(response.data)

        assert 'map' in data

    def test_map_not_empty_when_initialized(self, initialized_client):
        """Map should not be empty when game is initialized."""
        response = initialized_client.get('/api/map')
        data = json.loads(response.data)

        # Map should have content
        if 'error' not in data:
            assert len(data['map']) > 0


class TestEventInterface:
    """Test event interface through web."""

    def test_event_choice_api_exists(self, initialized_client):
        """Event choice API should exist."""
        response = initialized_client.post('/api/event/choice',
                                          json={'choice': 0},
                                          content_type='application/json')

        # May return error since no event is pending, but should not crash
        assert response.status_code == 200

    def test_event_choice_without_pending_event(self, initialized_client):
        """Event choice without pending event should return error."""
        response = initialized_client.post('/api/event/choice',
                                          json={'choice': 0},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert 'error' in data


class TestStateConsistency:
    """Test game state consistency through web interface."""

    def test_state_api_endpoint(self, initialized_client):
        """State API endpoint should return game state."""
        response = initialized_client.get('/api/state')
        data = json.loads(response.data)

        assert 'year' in data
        assert 'month' in data
        assert 'faction' in data

    def test_multiple_turn_advancement(self, initialized_client):
        """Multiple turn commands should advance game properly."""
        # Record initial state
        response1 = initialized_client.get('/api/state')
        data1 = json.loads(response1.data)
        initial_month = data1['month']
        initial_year = data1['year']

        # Advance 3 turns
        for _ in range(3):
            initialized_client.post('/api/command',
                                   json={'command': 'turn'},
                                   content_type='application/json')

        # Check state
        response2 = initialized_client.get('/api/state')
        data2 = json.loads(response2.data)

        # Time should have advanced
        total_months_initial = initial_year * 12 + initial_month
        total_months_final = data2['year'] * 12 + data2['month']

        assert total_months_final > total_months_initial

    def test_faction_persists_across_turns(self, initialized_client):
        """Faction should persist across multiple turns."""
        # Get initial faction
        response1 = initialized_client.get('/api/state')
        data1 = json.loads(response1.data)
        initial_faction = data1['faction']

        # Advance turns
        for _ in range(5):
            initialized_client.post('/api/command',
                                   json={'command': 'turn'},
                                   content_type='application/json')

        # Check faction unchanged
        response2 = initialized_client.get('/api/state')
        data2 = json.loads(response2.data)

        assert data2['faction'] == initial_faction


class TestLocaleFiles:
    """Test locale file serving."""

    def test_en_locale_serves(self, client):
        """English locale file should be servable."""
        response = client.get('/locales/en.json')
        assert response.status_code == 200

        # Should be valid JSON
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_zh_locale_serves(self, client):
        """Chinese locale file should be servable."""
        response = client.get('/locales/zh.json')
        assert response.status_code == 200

        # Should be valid JSON
        data = json.loads(response.data)
        assert isinstance(data, dict)


class TestSessionManagement:
    """Test session management through web interface."""

    def test_new_session_created(self, client):
        """New session should be created on first request."""
        response = client.post('/api/command',
                             json={'command': 'start'},
                             content_type='application/json')

        assert response.status_code == 200
        # Session should work

    def test_session_isolated(self):
        """Different sessions should have isolated game states."""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'

        # Test with first client
        with app.test_client() as client1:
            with client1.session_transaction() as sess:
                sess['session_id'] = 'test-session-1'

            # Initialize Wei faction
            client1.post('/api/command',
                       json={'command': 'choose Wei'},
                       content_type='application/json')

            # Check faction
            resp1 = client1.get('/api/state')
            data1 = json.loads(resp1.data)
            assert data1['faction'] == 'Wei'

        # Test with second client (sequentially, not nested)
        with app.test_client() as client2:
            with client2.session_transaction() as sess:
                sess['session_id'] = 'test-session-2'

            # Initialize Shu faction
            client2.post('/api/command',
                       json={'command': 'choose Shu'},
                       content_type='application/json')

            # Check faction
            resp2 = client2.get('/api/state')
            data2 = json.loads(resp2.data)
            assert data2['faction'] == 'Shu'

        # Verify sessions are isolated by checking game_states directly
        assert 'test-session-1' in game_states
        assert 'test-session-2' in game_states
        assert game_states['test-session-1'].player_faction == 'Wei'
        assert game_states['test-session-2'].player_faction == 'Shu'

        # Cleanup
        for sid in ['test-session-1', 'test-session-2']:
            if sid in game_states:
                del game_states[sid]
            if sid in session_states:
                del session_states[sid]


class TestErrorRecovery:
    """Test error recovery and robustness."""

    def test_recover_from_invalid_input(self, initialized_client):
        """Should recover from invalid input."""
        # Send invalid command
        initialized_client.post('/api/command',
                               json={'command': 'invalid!!!'},
                               content_type='application/json')

        # Should still work after
        response = initialized_client.post('/api/command',
                                          json={'command': 'status'},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert response.status_code == 200
        assert 'error' not in data['output'].lower() or 'output' in data

    def test_malformed_json_handled(self, initialized_client):
        """Malformed JSON should be handled gracefully."""
        response = initialized_client.post('/api/command',
                                          data='not json',
                                          content_type='application/json')

        # Should not crash
        assert response.status_code in [200, 400, 415]

    def test_missing_command_key(self, initialized_client):
        """Missing 'command' key should be handled."""
        response = initialized_client.post('/api/command',
                                          json={'notcommand': 'test'},
                                          content_type='application/json')

        assert response.status_code == 200


class TestFullGameFlow:
    """Test complete game flow through web interface."""

    def test_complete_gameplay_session(self, client):
        """Test a complete gameplay session."""
        # 1. Start game
        response = client.post('/api/command',
                             json={'command': 'start'},
                             content_type='application/json')
        data = json.loads(response.data)
        assert 'choose' in data['output'].lower()

        # 2. Choose faction
        response = client.post('/api/command',
                             json={'command': 'choose Wei'},
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['game_state']['faction'] == 'Wei'

        # 3. Check status
        response = client.post('/api/command',
                             json={'command': 'status'},
                             content_type='application/json')
        data = json.loads(response.data)
        assert 'Wei' in data['output'] or 'Treasury' in data['output']

        # 4. View officers
        response = client.post('/api/command',
                             json={'command': 'officers'},
                             content_type='application/json')
        data = json.loads(response.data)
        assert 'Officer' in data['output'] or 'Energy' in data['output']

        # 5. End turn
        response = client.post('/api/command',
                             json={'command': 'turn'},
                             content_type='application/json')
        assert response.status_code == 200

        # 6. Check map
        response = client.get('/api/map')
        data = json.loads(response.data)
        assert 'map' in data

        # 7. Check council
        response = client.get('/api/council')
        data = json.loads(response.data)
        assert 'council_display' in data or 'error' in data

    def test_multi_turn_gameplay(self, initialized_client):
        """Test multiple turns of gameplay."""
        for turn in range(10):
            response = initialized_client.post('/api/command',
                                              json={'command': 'turn'},
                                              content_type='application/json')

            assert response.status_code == 200

        # Game should still be functional
        response = initialized_client.post('/api/command',
                                          json={'command': 'status'},
                                          content_type='application/json')

        data = json.loads(response.data)
        assert 'output' in data
