"""Basic browser integration tests for Sango Text Sim."""
import pytest

pytestmark = pytest.mark.browser


class TestPageLoad:
    """Tests for basic page loading."""

    def test_page_loads_successfully(self, page, flask_server):
        """Page should load without errors."""
        response = page.goto(flask_server)
        assert response.status == 200

    def test_title_displays(self, game_page):
        """Page title should be visible."""
        title = game_page.locator('h1')
        assert title.is_visible()
        assert '三國志' in title.text_content() or 'TEXT SIM' in title.text_content()

    def test_tabs_visible(self, game_page):
        """All navigation tabs should be visible."""
        tabs = game_page.locator('.tab-btn')
        assert tabs.count() >= 5  # Map, City, Officer, Battle, Duel

        # Check specific tabs exist
        assert game_page.locator('button[data-tab="map"]').is_visible()
        assert game_page.locator('button[data-tab="city"]').is_visible()
        assert game_page.locator('button[data-tab="officer"]').is_visible()
        assert game_page.locator('button[data-tab="battle"]').is_visible()
        assert game_page.locator('button[data-tab="duel"]').is_visible()


class TestCommandInput:
    """Tests for command input functionality."""

    def test_input_exists(self, game_page):
        """Command input field should exist."""
        input_field = game_page.locator('#game-input')
        assert input_field.is_visible()

    def test_send_button_exists(self, game_page):
        """Send button should exist."""
        send_btn = game_page.locator('#send-btn')
        assert send_btn.is_visible()
        assert send_btn.text_content() == 'Send'

    def test_can_type_in_input(self, game_page):
        """Should be able to type commands in the input field."""
        input_field = game_page.locator('#game-input')
        input_field.fill('test command')
        assert input_field.input_value() == 'test command'


class TestGameFlow:
    """Tests for basic game flow."""

    def test_help_command(self, game_page):
        """Help command should display help text."""
        input_field = game_page.locator('#game-input')
        send_btn = game_page.locator('#send-btn')
        output = game_page.locator('#game-output')

        input_field.fill('help')
        send_btn.click()

        # Wait for response
        game_page.wait_for_function(
            "document.getElementById('game-output').textContent.includes('Commands')"
        )

        output_text = output.text_content()
        assert 'Commands' in output_text or 'help' in output_text.lower()

    def test_start_and_choose_faction(self, game_page):
        """Should be able to start game and choose faction."""
        input_field = game_page.locator('#game-input')
        send_btn = game_page.locator('#send-btn')
        output = game_page.locator('#game-output')

        # Choose Wei faction directly
        input_field.fill('choose Wei')
        send_btn.click()

        # Wait for response
        game_page.wait_for_function(
            "document.getElementById('game-output').textContent.includes('Wei')"
        )

        output_text = output.text_content()
        assert 'Wei' in output_text

    def test_status_command_after_start(self, game_page):
        """Status command should work after starting game."""
        input_field = game_page.locator('#game-input')
        send_btn = game_page.locator('#send-btn')
        output = game_page.locator('#game-output')

        # Start and choose faction
        input_field.fill('choose Shu')
        send_btn.click()
        game_page.wait_for_function(
            "document.getElementById('game-output').textContent.includes('Shu')"
        )

        # Check status
        input_field.fill('status')
        send_btn.click()

        # Wait for status response - should contain faction info
        game_page.wait_for_function(
            "!document.getElementById('game-output').textContent.includes('Processing')"
        )

        output_text = output.text_content()
        # Should show faction overview or resources
        assert len(output_text) > 10  # Should have some content


class TestTabNavigation:
    """Tests for tab navigation."""

    def test_map_tab_is_default_active(self, game_page):
        """Map tab should be active by default."""
        map_tab = game_page.locator('button[data-tab="map"]')
        assert 'active' in map_tab.get_attribute('class')

    def test_clicking_tab_changes_active_state(self, game_page):
        """Clicking a tab should make it active and deactivate others."""
        map_tab = game_page.locator('button[data-tab="map"]')
        city_tab = game_page.locator('button[data-tab="city"]')

        # Initially map is active
        assert 'active' in map_tab.get_attribute('class')

        # Click city tab
        city_tab.click()

        # Now city should be active, map should not
        assert 'active' in city_tab.get_attribute('class')
        assert 'active' not in map_tab.get_attribute('class')
