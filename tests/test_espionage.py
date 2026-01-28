"""Tests for the espionage system."""
import pytest
import random
from src.models import GameState, City, Faction, Officer
from src.systems.espionage import execute_spy_mission, MISSION_COSTS


def _make_state():
    gs = GameState()
    gs.player_faction = "Shu"
    gs.cities["Chengdu"] = City(name="Chengdu", owner="Shu", gold=500, food=500, troops=300)
    gs.cities["Luoyang"] = City(name="Luoyang", owner="Wei", gold=500, food=500, troops=300, defense=50)
    gs.factions["Shu"] = Faction(name="Shu", cities=["Chengdu"],
                                  officers=["ZhugeLiang"],
                                  relations={"Wei": 0})
    gs.factions["Wei"] = Faction(name="Wei", cities=["Luoyang"],
                                  officers=["SimaYi"],
                                  relations={"Shu": 0})
    gs.officers["ZhugeLiang"] = Officer(name="ZhugeLiang", faction="Shu",
                                         leadership=65, intelligence=95, politics=90, charisma=85,
                                         energy=100, city="Chengdu")
    gs.officers["SimaYi"] = Officer(name="SimaYi", faction="Wei",
                                     leadership=80, intelligence=90, politics=80, charisma=70,
                                     energy=100, loyalty=75, city="Luoyang")
    return gs


class TestExecuteSpyMission:
    def test_invalid_mission(self):
        gs = _make_state()
        result = execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "invalid")
        assert result["success"] is False

    def test_officer_not_found(self):
        gs = _make_state()
        result = execute_spy_mission(gs, "NonExistent", "Luoyang", "scout")
        assert result["success"] is False

    def test_not_your_officer(self):
        gs = _make_state()
        result = execute_spy_mission(gs, "SimaYi", "Luoyang", "scout")
        assert result["success"] is False

    def test_officer_tired(self):
        gs = _make_state()
        gs.officers["ZhugeLiang"].energy = 5
        result = execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "scout")
        assert result["success"] is False

    def test_city_not_found(self):
        gs = _make_state()
        result = execute_spy_mission(gs, "ZhugeLiang", "Nowhere", "scout")
        assert result["success"] is False

    def test_own_city(self):
        gs = _make_state()
        result = execute_spy_mission(gs, "ZhugeLiang", "Chengdu", "scout")
        assert result["success"] is False

    def test_insufficient_gold(self):
        gs = _make_state()
        gs.cities["Chengdu"].gold = 0
        result = execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "scout")
        assert result["success"] is False

    def test_scout_deducts_gold_and_energy(self):
        gs = _make_state()
        initial_gold = gs.cities["Chengdu"].gold
        initial_energy = gs.officers["ZhugeLiang"].energy
        random.seed(42)  # Ensure consistent result
        execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "scout")
        assert gs.cities["Chengdu"].gold == initial_gold - MISSION_COSTS["scout"]
        assert gs.officers["ZhugeLiang"].energy == initial_energy - 20

    def test_scout_success(self):
        gs = _make_state()
        random.seed(1)  # High intelligence should succeed often
        result = execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "scout")
        # With INT 95, base_chance = 0.5 + 45*0.005 = 0.725
        assert "mission" in result

    def test_sabotage_success(self):
        gs = _make_state()
        random.seed(1)
        result = execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "sabotage")
        assert "mission" in result

    def test_steal_success(self):
        gs = _make_state()
        random.seed(1)
        result = execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "steal")
        assert "mission" in result

    def test_incite_success(self):
        gs = _make_state()
        random.seed(1)
        result = execute_spy_mission(gs, "ZhugeLiang", "Luoyang", "incite")
        assert "mission" in result
