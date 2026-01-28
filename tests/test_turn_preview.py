"""Tests for the turn preview system."""
import pytest
from src.models import GameState, City, Faction, Officer
from src.display.reports import generate_turn_preview


def _make_state():
    gs = GameState()
    gs.year = 210
    gs.month = 6
    gs.player_faction = "Shu"
    gs.cities["Chengdu"] = City(name="Chengdu", owner="Shu", gold=500, food=500, troops=300)
    gs.cities["Luoyang"] = City(name="Luoyang", owner="Wei", gold=500, food=500, troops=500)
    gs.factions["Shu"] = Faction(name="Shu", cities=["Chengdu"],
                                  officers=["LiuBei"])
    gs.factions["Wei"] = Faction(name="Wei", cities=["Luoyang"])
    gs.officers["LiuBei"] = Officer(name="LiuBei", faction="Shu", leadership=80, intelligence=70, politics=60, charisma=70, loyalty=75)
    gs.adj = {"Chengdu": ["Luoyang"], "Luoyang": ["Chengdu"]}
    return gs


class TestGenerateTurnPreview:
    def test_empty_when_nothing_pending(self):
        gs = _make_state()
        gs.cities["Luoyang"].troops = 50  # Low threat
        preview = generate_turn_preview(gs)
        # May still show enemy threat if troops >= 200
        # With 50 troops, no threat shown
        assert "enemy" not in preview.lower() or preview == ""

    def test_construction_completion(self):
        gs = _make_state()
        gs.construction_queue["Chengdu"] = {"building_id": "barracks", "progress": 2, "turns_needed": 3}
        preview = generate_turn_preview(gs)
        assert "barracks" in preview.lower() or "Barracks" in preview

    def test_research_completion(self):
        gs = _make_state()
        gs.research_progress["Shu"] = {"tech_id": "iron_weapons", "progress": 2, "turns_needed": 3, "officer": "LiuBei", "city": "Chengdu"}
        preview = generate_turn_preview(gs)
        assert len(preview) > 0

    def test_loyalty_warning(self):
        gs = _make_state()
        gs.officers["LiuBei"].loyalty = 30
        preview = generate_turn_preview(gs)
        assert "LiuBei" in preview

    def test_enemy_threat(self):
        gs = _make_state()
        gs.cities["Luoyang"].troops = 500
        preview = generate_turn_preview(gs)
        assert "Chengdu" in preview

    def test_low_food_warning(self):
        gs = _make_state()
        gs.cities["Chengdu"].food = 50
        preview = generate_turn_preview(gs)
        assert "Chengdu" in preview

    def test_low_gold_warning(self):
        gs = _make_state()
        gs.cities["Chengdu"].gold = 20
        preview = generate_turn_preview(gs)
        assert "Chengdu" in preview

    def test_no_faction_returns_empty(self):
        gs = _make_state()
        gs.player_faction = "NonExistent"
        preview = generate_turn_preview(gs)
        assert preview == ""
