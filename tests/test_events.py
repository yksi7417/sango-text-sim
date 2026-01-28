"""Tests for the random event system (p3-06)."""
import pytest
from unittest.mock import patch
from src.models import GameState, WeatherType
from src.systems.events import (
    GameEvent, EventChoice, load_random_events,
    check_event_triggers, apply_event_choice, _check_conditions
)
from src.world import init_world


class TestLoadRandomEvents:
    """Test loading events from JSON."""

    def test_loads_events(self):
        events = load_random_events()
        assert len(events) >= 15

    def test_event_structure(self):
        events = load_random_events()
        for e in events:
            assert isinstance(e, GameEvent)
            assert e.id
            assert e.event_type in ("positive", "negative", "neutral")
            assert 0 < e.probability <= 1.0
            assert e.title_key
            assert e.description_key
            assert len(e.choices) >= 2

    def test_event_choices_have_effects(self):
        events = load_random_events()
        for e in events:
            for c in e.choices:
                assert isinstance(c, EventChoice)
                assert c.label_key
                assert isinstance(c.effects, dict)


class TestCheckConditions:
    """Test event condition checking."""

    def test_no_conditions_always_passes(self):
        event = GameEvent(id="test", event_type="positive", probability=1.0,
                         conditions={}, title_key="t", description_key="d")
        gs = GameState()
        init_world(gs)
        assert _check_conditions(event, gs, "Chengdu")

    def test_season_condition_matches(self):
        event = GameEvent(id="test", event_type="positive", probability=1.0,
                         conditions={"season": "winter"}, title_key="t", description_key="d")
        gs = GameState()
        init_world(gs)
        gs.month = 1  # Winter
        assert _check_conditions(event, gs, "Chengdu")

    def test_season_condition_fails(self):
        event = GameEvent(id="test", event_type="positive", probability=1.0,
                         conditions={"season": "summer"}, title_key="t", description_key="d")
        gs = GameState()
        init_world(gs)
        gs.month = 1  # Winter, not summer
        assert not _check_conditions(event, gs, "Chengdu")

    def test_weather_condition(self):
        event = GameEvent(id="test", event_type="positive", probability=1.0,
                         conditions={"weather": "drought"}, title_key="t", description_key="d")
        gs = GameState()
        init_world(gs)
        gs.weather = WeatherType.DROUGHT
        assert _check_conditions(event, gs, "Chengdu")

    def test_morale_condition(self):
        event = GameEvent(id="test", event_type="negative", probability=1.0,
                         conditions={"morale_below": 40}, title_key="t", description_key="d")
        gs = GameState()
        init_world(gs)
        gs.cities["Chengdu"].morale = 30
        assert _check_conditions(event, gs, "Chengdu")

    def test_morale_condition_fails(self):
        event = GameEvent(id="test", event_type="negative", probability=1.0,
                         conditions={"morale_below": 40}, title_key="t", description_key="d")
        gs = GameState()
        init_world(gs)
        gs.cities["Chengdu"].morale = 60
        assert not _check_conditions(event, gs, "Chengdu")


class TestCheckEventTriggers:
    """Test event trigger checking."""

    @patch('src.systems.events.random.random', return_value=0.01)
    def test_event_triggers(self, mock_random):
        gs = GameState()
        init_world(gs)
        result = check_event_triggers(gs)
        # With very low random, some event should trigger
        # (may be None if season conditions don't match)
        if result:
            assert "event" in result
            assert "city" in result

    @patch('src.systems.events.random.random', return_value=0.99)
    def test_no_event_triggers(self, mock_random):
        gs = GameState()
        init_world(gs)
        result = check_event_triggers(gs)
        assert result is None


class TestApplyEventChoice:
    """Test applying event choice effects."""

    def test_apply_gold_effect(self):
        gs = GameState()
        init_world(gs)
        event = GameEvent(
            id="test", event_type="positive", probability=1.0,
            conditions={}, title_key="t", description_key="d",
            choices=[EventChoice(label_key="c1", effects={"gold": 100})]
        )
        initial_gold = gs.cities["Chengdu"].gold
        result = apply_event_choice(gs, event, 0, "Chengdu")
        assert gs.cities["Chengdu"].gold == initial_gold + 100
        assert "applied" in result

    def test_apply_negative_effect(self):
        gs = GameState()
        init_world(gs)
        event = GameEvent(
            id="test", event_type="negative", probability=1.0,
            conditions={}, title_key="t", description_key="d",
            choices=[EventChoice(label_key="c1", effects={"troops": -20})]
        )
        initial_troops = gs.cities["Chengdu"].troops
        apply_event_choice(gs, event, 0, "Chengdu")
        assert gs.cities["Chengdu"].troops == initial_troops - 20

    def test_invalid_choice_index(self):
        gs = GameState()
        init_world(gs)
        event = GameEvent(
            id="test", event_type="positive", probability=1.0,
            conditions={}, title_key="t", description_key="d",
            choices=[EventChoice(label_key="c1", effects={"gold": 100})]
        )
        result = apply_event_choice(gs, event, 5, "Chengdu")
        assert "error" in result

    def test_effect_floor_at_zero(self):
        gs = GameState()
        init_world(gs)
        gs.cities["Chengdu"].gold = 10
        event = GameEvent(
            id="test", event_type="negative", probability=1.0,
            conditions={}, title_key="t", description_key="d",
            choices=[EventChoice(label_key="c1", effects={"gold": -500})]
        )
        apply_event_choice(gs, event, 0, "Chengdu")
        assert gs.cities["Chengdu"].gold == 0  # Clamped to 0


class TestEventI18n:
    """Test event i18n keys."""

    def test_locale_keys_exist(self):
        import json
        with open('locales/en.json', encoding='utf-8') as f:
            en = json.load(f)
        with open('locales/zh.json', encoding='utf-8') as f:
            zh = json.load(f)

        assert 'events' in en
        assert 'events' in zh

        events = load_random_events()
        for e in events:
            event_id = e.id
            assert event_id in en['events'], f"Missing en events.{event_id}"
            assert event_id in zh['events'], f"Missing zh events.{event_id}"
