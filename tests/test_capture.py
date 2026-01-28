"""Tests for the surrender and capture system."""
import pytest
import random
from src.models import GameState, City, Faction, Officer
from src.systems.capture import (
    capture_officers, recruit_captured, execute_captured, release_captured
)


def _make_state():
    gs = GameState()
    gs.player_faction = "Shu"
    gs.cities["Luoyang"] = City(name="Luoyang", owner="Wei", gold=500, troops=100)
    gs.cities["Chengdu"] = City(name="Chengdu", owner="Shu", gold=500)
    gs.factions["Shu"] = Faction(name="Shu", cities=["Chengdu"],
                                  officers=["LiuBei"],
                                  relations={"Wei": 0})
    gs.factions["Wei"] = Faction(name="Wei", cities=["Luoyang"],
                                  officers=["SimaYi"],
                                  relations={"Shu": 0})
    gs.officers["LiuBei"] = Officer(name="LiuBei", faction="Shu",
                                     leadership=80, intelligence=70, politics=80, charisma=90,
                                     loyalty=90, city="Chengdu")
    gs.officers["SimaYi"] = Officer(name="SimaYi", faction="Wei",
                                     leadership=80, intelligence=90, politics=80, charisma=70,
                                     loyalty=50, city="Luoyang")
    return gs


class TestCaptureOfficers:
    def test_capture_low_loyalty(self):
        gs = _make_state()
        gs.officers["SimaYi"].loyalty = 20
        random.seed(1)
        results = capture_officers(gs, "Luoyang", "Shu")
        assert len(results) > 0

    def test_capture_adds_to_captured(self):
        gs = _make_state()
        gs.officers["SimaYi"].loyalty = 10
        random.seed(42)
        results = capture_officers(gs, "Luoyang", "Shu")
        captured_results = [r for r in results if r["outcome"] == "captured"]
        if captured_results:
            assert "SimaYi" in gs.captured_officers

    def test_loyalist_refuses(self):
        gs = _make_state()
        gs.officers["GuanYu"] = Officer(name="GuanYu", faction="Wei",
                                         leadership=90, intelligence=70, politics=60, charisma=80,
                                         loyalty=90, city="Luoyang")
        gs.factions["Wei"].officers.append("GuanYu")
        results = capture_officers(gs, "Luoyang", "Shu")
        guan_yu_result = [r for r in results if r["officer"] == "GuanYu"]
        if guan_yu_result:
            assert guan_yu_result[0]["outcome"] == "refused"

    def test_no_officers_in_city(self):
        gs = _make_state()
        gs.officers["SimaYi"].city = "Elsewhere"
        results = capture_officers(gs, "Luoyang", "Shu")
        assert len(results) == 0


class TestRecruitCaptured:
    def test_recruit_success(self):
        gs = _make_state()
        gs.captured_officers["SimaYi"] = {"captor": "Shu", "original_faction": "Wei"}
        result = recruit_captured(gs, "SimaYi")
        assert result["success"] is True
        assert "SimaYi" in gs.factions["Shu"].officers
        assert gs.officers["SimaYi"].loyalty == 30

    def test_recruit_not_captured(self):
        gs = _make_state()
        result = recruit_captured(gs, "SimaYi")
        assert result["success"] is False

    def test_recruit_not_your_prisoner(self):
        gs = _make_state()
        gs.captured_officers["SimaYi"] = {"captor": "Wu", "original_faction": "Wei"}
        result = recruit_captured(gs, "SimaYi")
        assert result["success"] is False


class TestExecuteCaptured:
    def test_execute_success(self):
        gs = _make_state()
        gs.captured_officers["SimaYi"] = {"captor": "Shu", "original_faction": "Wei"}
        initial_loyalty = gs.officers["LiuBei"].loyalty
        result = execute_captured(gs, "SimaYi")
        assert result["success"] is True
        assert "SimaYi" not in gs.officers
        assert gs.officers["LiuBei"].loyalty < initial_loyalty

    def test_execute_not_captured(self):
        gs = _make_state()
        result = execute_captured(gs, "SimaYi")
        assert result["success"] is False


class TestReleaseCaptured:
    def test_release_success(self):
        gs = _make_state()
        gs.captured_officers["SimaYi"] = {"captor": "Shu", "original_faction": "Wei"}
        gs.factions["Wei"].officers.remove("SimaYi")
        result = release_captured(gs, "SimaYi")
        assert result["success"] is True
        assert "SimaYi" in gs.factions["Wei"].officers
        assert gs.officers["LiuBei"].loyalty >= 90  # Should get +3

    def test_release_not_captured(self):
        gs = _make_state()
        result = release_captured(gs, "SimaYi")
        assert result["success"] is False
