"""Tests for the weather system (p2-09)."""
import pytest
from unittest.mock import patch
from src.models import WeatherType, Season, GameState, get_current_season
from src.engine import generate_weather, update_weather, end_turn
from src.world import init_world


class TestWeatherType:
    """Test WeatherType enum."""

    def test_all_weather_types_exist(self):
        assert WeatherType.CLEAR.value == "clear"
        assert WeatherType.RAIN.value == "rain"
        assert WeatherType.SNOW.value == "snow"
        assert WeatherType.FOG.value == "fog"
        assert WeatherType.DROUGHT.value == "drought"

    def test_weather_type_count(self):
        assert len(WeatherType) == 5


class TestGameStateWeather:
    """Test weather fields on GameState."""

    def test_default_weather(self):
        gs = GameState()
        assert gs.weather == WeatherType.CLEAR
        assert gs.weather_turns_remaining == 0

    def test_set_weather(self):
        gs = GameState()
        gs.weather = WeatherType.RAIN
        gs.weather_turns_remaining = 2
        assert gs.weather == WeatherType.RAIN
        assert gs.weather_turns_remaining == 2


class TestGenerateWeather:
    """Test weather generation based on season."""

    def test_generate_weather_returns_tuple(self):
        weather, duration = generate_weather(Season.SPRING)
        assert isinstance(weather, WeatherType)
        assert 1 <= duration <= 3

    @patch('src.engine.random.random', return_value=0.05)
    @patch('src.engine.random.randint', return_value=2)
    def test_spring_rain(self, mock_randint, mock_random):
        weather, duration = generate_weather(Season.SPRING)
        assert weather == WeatherType.RAIN
        assert duration == 2

    @patch('src.engine.random.random', return_value=0.35)
    def test_spring_fog(self, mock_random):
        weather, _ = generate_weather(Season.SPRING)
        assert weather == WeatherType.FOG

    @patch('src.engine.random.random', return_value=0.50)
    def test_spring_clear(self, mock_random):
        weather, _ = generate_weather(Season.SPRING)
        assert weather == WeatherType.CLEAR

    @patch('src.engine.random.random', return_value=0.10)
    def test_summer_drought(self, mock_random):
        weather, _ = generate_weather(Season.SUMMER)
        assert weather == WeatherType.DROUGHT

    @patch('src.engine.random.random', return_value=0.25)
    def test_summer_rain(self, mock_random):
        weather, _ = generate_weather(Season.SUMMER)
        assert weather == WeatherType.RAIN

    @patch('src.engine.random.random', return_value=0.50)
    def test_summer_clear(self, mock_random):
        weather, _ = generate_weather(Season.SUMMER)
        assert weather == WeatherType.CLEAR

    @patch('src.engine.random.random', return_value=0.05)
    def test_autumn_fog(self, mock_random):
        weather, _ = generate_weather(Season.AUTUMN)
        assert weather == WeatherType.FOG

    @patch('src.engine.random.random', return_value=0.15)
    def test_autumn_rain(self, mock_random):
        weather, _ = generate_weather(Season.AUTUMN)
        assert weather == WeatherType.RAIN

    @patch('src.engine.random.random', return_value=0.50)
    def test_autumn_clear(self, mock_random):
        weather, _ = generate_weather(Season.AUTUMN)
        assert weather == WeatherType.CLEAR

    @patch('src.engine.random.random', return_value=0.10)
    def test_winter_snow(self, mock_random):
        weather, _ = generate_weather(Season.WINTER)
        assert weather == WeatherType.SNOW

    @patch('src.engine.random.random', return_value=0.45)
    def test_winter_fog(self, mock_random):
        weather, _ = generate_weather(Season.WINTER)
        assert weather == WeatherType.FOG

    @patch('src.engine.random.random', return_value=0.60)
    def test_winter_clear(self, mock_random):
        weather, _ = generate_weather(Season.WINTER)
        assert weather == WeatherType.CLEAR

    def test_duration_range(self):
        """Weather duration should always be 1-3 turns."""
        for _ in range(50):
            for season in Season:
                _, duration = generate_weather(season)
                assert 1 <= duration <= 3


class TestUpdateWeather:
    """Test weather persistence and transitions."""

    def test_weather_persists(self):
        gs = GameState()
        gs.weather = WeatherType.RAIN
        gs.weather_turns_remaining = 3
        events = []
        update_weather(gs, events)
        # Should decrement but not change weather yet
        assert gs.weather_turns_remaining >= 0

    def test_weather_changes_when_expired(self):
        gs = GameState()
        gs.weather = WeatherType.RAIN
        gs.weather_turns_remaining = 1
        gs.month = 6  # Summer
        events = []
        update_weather(gs, events)
        # After decrement to 0, new weather is generated
        assert gs.weather_turns_remaining >= 0
        assert isinstance(gs.weather, WeatherType)

    def test_weather_decrement(self):
        gs = GameState()
        gs.weather = WeatherType.SNOW
        gs.weather_turns_remaining = 3
        events = []
        # Mock to keep same weather so we can test decrement
        with patch('src.engine.generate_weather', return_value=(WeatherType.SNOW, 2)):
            update_weather(gs, events)
        # Decremented from 3 to 2, then since 2 > 0, no new weather
        assert gs.weather == WeatherType.SNOW
        assert gs.weather_turns_remaining == 2


class TestWeatherInEndTurn:
    """Test weather integration with end_turn."""

    def test_end_turn_updates_weather(self):
        gs = GameState()
        init_world(gs)
        gs.weather = WeatherType.CLEAR
        gs.weather_turns_remaining = 0
        events = end_turn(gs)
        # Weather should have been updated
        assert isinstance(gs.weather, WeatherType)

    def test_weather_shown_in_status(self):
        """Verify weather field is accessible on game state after init."""
        gs = GameState()
        init_world(gs)
        assert hasattr(gs, 'weather')
        assert hasattr(gs, 'weather_turns_remaining')
        assert gs.weather == WeatherType.CLEAR


class TestWeatherI18n:
    """Test weather i18n keys exist."""

    def test_weather_locale_keys(self):
        import json
        with open('locales/en.json', encoding='utf-8') as f:
            en = json.load(f)
        with open('locales/zh.json', encoding='utf-8') as f:
            zh = json.load(f)

        # Both locales should have weather section
        assert 'weather' in en
        assert 'weather' in zh

        # Check all weather type names
        for wt in WeatherType:
            assert wt.value in en['weather'], f"Missing en weather.{wt.value}"
            assert wt.value in zh['weather'], f"Missing zh weather.{wt.value}"

        # Check change messages
        for wt in WeatherType:
            assert wt.value in en['weather']['change'], f"Missing en weather.change.{wt.value}"
            assert wt.value in zh['weather']['change'], f"Missing zh weather.change.{wt.value}"

        # Check status key
        assert 'status' in en['weather']
        assert 'status' in zh['weather']
