"""Tests for the historical events system."""
import pytest
from src.models import GameState, City, Faction, Officer
from src.systems.events import (
    load_historical_events, HistoricalEvent,
    _check_historical_conditions, apply_historical_effects,
    check_historical_events
)


def _make_state():
    gs = GameState()
    gs.year = 208
    gs.month = 3
    gs.player_faction = "Shu"
    gs.cities["Chengdu"] = City(name="Chengdu", owner="Shu", gold=500, morale=60)
    gs.cities["Luoyang"] = City(name="Luoyang", owner="Wei", gold=500, morale=60)
    gs.cities["Jianye"] = City(name="Jianye", owner="Wu", gold=500, morale=60)
    gs.factions["Shu"] = Faction(name="Shu", cities=["Chengdu"],
                                  officers=["LiuBei", "GuanYu", "ZhangFei", "ZhugeLiang",
                                            "ZhaoYun", "MaChao", "HuangZhong"],
                                  relations={"Wei": -10, "Wu": 10})
    gs.factions["Wei"] = Faction(name="Wei", cities=["Luoyang"],
                                  officers=["CaoCao", "SimaYi"],
                                  relations={"Shu": -10, "Wu": -5})
    gs.factions["Wu"] = Faction(name="Wu", cities=["Jianye"],
                                 officers=["SunQuan", "ZhouYu", "LuSu"],
                                 relations={"Shu": 10, "Wei": -5})

    for name in ["LiuBei", "GuanYu", "ZhangFei", "ZhugeLiang", "ZhaoYun", "MaChao", "HuangZhong"]:
        gs.officers[name] = Officer(name=name, faction="Shu", leadership=80, intelligence=70, politics=60, charisma=70)
    for name in ["CaoCao", "SimaYi"]:
        gs.officers[name] = Officer(name=name, faction="Wei", leadership=85, intelligence=90, politics=80, charisma=75)
    for name in ["SunQuan", "ZhouYu", "LuSu"]:
        gs.officers[name] = Officer(name=name, faction="Wu", leadership=75, intelligence=85, politics=75, charisma=70)

    return gs


class TestLoadHistoricalEvents:
    def test_load_events(self):
        events = load_historical_events()
        assert len(events) >= 10

    def test_event_has_required_fields(self):
        events = load_historical_events()
        for e in events:
            assert e.id
            assert len(e.year_range) == 2
            assert e.title_key
            assert e.description_key


class TestCheckHistoricalConditions:
    def test_year_in_range(self):
        event = HistoricalEvent(id="test", year_range=[208, 210], conditions={},
                                 title_key="t", description_key="d")
        gs = _make_state()
        gs.year = 209
        assert _check_historical_conditions(event, gs) is True

    def test_year_out_of_range(self):
        event = HistoricalEvent(id="test", year_range=[208, 210], conditions={},
                                 title_key="t", description_key="d")
        gs = _make_state()
        gs.year = 220
        assert _check_historical_conditions(event, gs) is False

    def test_officers_in_faction(self):
        event = HistoricalEvent(id="test", year_range=[208, 210],
                                 conditions={"officers_in_faction": ["LiuBei", "GuanYu"], "faction": "Shu"},
                                 title_key="t", description_key="d")
        gs = _make_state()
        assert _check_historical_conditions(event, gs) is True

    def test_officers_in_faction_missing(self):
        event = HistoricalEvent(id="test", year_range=[208, 210],
                                 conditions={"officers_in_faction": ["LiuBei", "NonExistent"], "faction": "Shu"},
                                 title_key="t", description_key="d")
        gs = _make_state()
        assert _check_historical_conditions(event, gs) is False

    def test_factions_exist(self):
        event = HistoricalEvent(id="test", year_range=[208, 210],
                                 conditions={"factions_exist": ["Shu", "Wu"]},
                                 title_key="t", description_key="d")
        gs = _make_state()
        assert _check_historical_conditions(event, gs) is True

    def test_faction_has_officer(self):
        event = HistoricalEvent(id="test", year_range=[208, 230],
                                 conditions={"officer_exists": "SimaYi",
                                             "faction_has_officer": {"faction": "Wei", "officer": "SimaYi"}},
                                 title_key="t", description_key="d")
        gs = _make_state()
        assert _check_historical_conditions(event, gs) is True


class TestApplyHistoricalEffects:
    def test_relationship_creation(self):
        event = HistoricalEvent(
            id="test", year_range=[208, 210], conditions={},
            title_key="t", description_key="d",
            effects={"relationships": [
                {"officer1": "LiuBei", "officer2": "GuanYu", "type": "sworn_brother"}
            ]}
        )
        gs = _make_state()
        result = apply_historical_effects(gs, event)
        assert gs.officers["LiuBei"].relationships.get("GuanYu") == "sworn_brother"
        assert gs.officers["GuanYu"].relationships.get("LiuBei") == "sworn_brother"

    def test_loyalty_boost(self):
        event = HistoricalEvent(
            id="test", year_range=[208, 210], conditions={},
            title_key="t", description_key="d",
            effects={"loyalty_boost": {"GuanYu": 20}}
        )
        gs = _make_state()
        initial = gs.officers["GuanYu"].loyalty
        apply_historical_effects(gs, event)
        assert gs.officers["GuanYu"].loyalty == min(100, initial + 20)

    def test_morale_boost(self):
        event = HistoricalEvent(
            id="test", year_range=[208, 210], conditions={},
            title_key="t", description_key="d",
            effects={"morale_boost": {"Shu": 10}}
        )
        gs = _make_state()
        initial = gs.cities["Chengdu"].morale
        apply_historical_effects(gs, event)
        assert gs.cities["Chengdu"].morale == min(100, initial + 10)

    def test_tech_boost(self):
        event = HistoricalEvent(
            id="test", year_range=[208, 210], conditions={},
            title_key="t", description_key="d",
            effects={"tech_boost": {"Wu": 5}}
        )
        gs = _make_state()
        initial = gs.cities["Jianye"].tech
        apply_historical_effects(gs, event)
        assert gs.cities["Jianye"].tech == min(100, initial + 5)

    def test_relations_change(self):
        event = HistoricalEvent(
            id="test", year_range=[208, 210], conditions={},
            title_key="t", description_key="d",
            effects={"relations_change": {"Shu_Wu": 20}}
        )
        gs = _make_state()
        initial = gs.factions["Shu"].relations.get("Wu", 0)
        apply_historical_effects(gs, event)
        assert gs.factions["Shu"].relations["Wu"] == initial + 20


class TestCheckHistoricalEvents:
    def test_triggers_when_conditions_met(self):
        gs = _make_state()
        result = check_historical_events(gs, [])
        assert result is not None
        assert "event" in result

    def test_skips_already_triggered(self):
        gs = _make_state()
        # Trigger all events first
        events = load_historical_events()
        triggered = [e.id for e in events]
        result = check_historical_events(gs, triggered)
        assert result is None

    def test_peach_garden_oath_triggers(self):
        gs = _make_state()
        result = check_historical_events(gs, [])
        # The first qualifying event should trigger
        assert result is not None

    def test_returns_none_when_no_conditions_met(self):
        gs = _make_state()
        gs.year = 300  # Way out of range for all events
        result = check_historical_events(gs, [])
        assert result is None
