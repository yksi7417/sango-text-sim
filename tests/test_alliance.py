"""Tests for alliance system."""
import pytest
from unittest.mock import patch
from src.models import GameState, Faction
from src.systems.alliance import (
    Alliance, AllianceType, propose_alliance, break_alliance,
    is_allied, can_attack, get_defensive_allies,
    process_alliance_turns, find_alliance, list_alliances,
    BREAK_ALLIANCE_PENALTY, ALLIANCE_RELATION_BOOST,
)


def _make_state():
    gs = GameState()
    gs.player_faction = "Shu"
    gs.factions = {
        "Wei": Faction(name="Wei", relations={"Shu": 20, "Wu": -10, "Wei": 0}),
        "Shu": Faction(name="Shu", relations={"Wei": 20, "Wu": 40, "Shu": 0}),
        "Wu": Faction(name="Wu", relations={"Wei": -10, "Shu": 40, "Wu": 0}),
    }
    gs.alliances = []
    return gs


class TestProposeAlliance:
    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_propose_non_aggression(self, mock_rand):
        gs = _make_state()
        result = propose_alliance(gs, "Wei", "non_aggression")
        assert result["success"] is True
        assert is_allied(gs, "Shu", "Wei")

    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_propose_defensive(self, mock_rand):
        gs = _make_state()
        result = propose_alliance(gs, "Wu", "defensive")
        assert result["success"] is True

    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_propose_offensive_requires_high_relations(self, mock_rand):
        gs = _make_state()
        result = propose_alliance(gs, "Wu", "offensive")
        assert result["success"] is True

    def test_propose_offensive_low_relations_fails(self):
        gs = _make_state()
        gs.factions["Shu"].relations["Wei"] = 0
        result = propose_alliance(gs, "Wei", "offensive")
        assert result["success"] is False

    def test_propose_invalid_type(self):
        gs = _make_state()
        result = propose_alliance(gs, "Wei", "invalid")
        assert result["success"] is False

    def test_propose_self(self):
        gs = _make_state()
        result = propose_alliance(gs, "Shu", "non_aggression")
        assert result["success"] is False

    def test_propose_nonexistent_faction(self):
        gs = _make_state()
        result = propose_alliance(gs, "Han", "non_aggression")
        assert result["success"] is False

    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_cannot_propose_if_already_allied(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wei", "non_aggression")
        result = propose_alliance(gs, "Wei", "defensive")
        assert result["success"] is False

    @patch("src.systems.alliance.random.random", return_value=0.99)
    def test_ai_can_reject(self, mock_rand):
        gs = _make_state()
        result = propose_alliance(gs, "Wei", "non_aggression")
        assert result["success"] is False

    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_relations_boosted_on_formation(self, mock_rand):
        gs = _make_state()
        before = gs.factions["Shu"].relations["Wei"]
        propose_alliance(gs, "Wei", "non_aggression")
        after = gs.factions["Shu"].relations["Wei"]
        assert after == before + ALLIANCE_RELATION_BOOST


class TestBreakAlliance:
    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_break_alliance(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wei", "non_aggression")
        result = break_alliance(gs, "Wei")
        assert result["success"] is True
        assert not is_allied(gs, "Shu", "Wei")

    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_break_penalty(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wei", "non_aggression")
        before = gs.factions["Shu"].relations["Wei"]
        break_alliance(gs, "Wei")
        after = gs.factions["Shu"].relations["Wei"]
        assert after == before + BREAK_ALLIANCE_PENALTY

    def test_break_no_alliance(self):
        gs = _make_state()
        result = break_alliance(gs, "Wei")
        assert result["success"] is False


class TestCanAttack:
    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_cannot_attack_ally(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wei", "non_aggression")
        result = can_attack(gs, "Shu", "Wei")
        assert result["allowed"] is False

    def test_can_attack_non_ally(self):
        gs = _make_state()
        result = can_attack(gs, "Shu", "Wei")
        assert result["allowed"] is True


class TestDefensiveAllies:
    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_defensive_allies_join(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wu", "defensive")
        allies = get_defensive_allies(gs, "Shu", "Wei")
        assert "Wu" in allies

    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_non_aggression_does_not_join(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wu", "non_aggression")
        allies = get_defensive_allies(gs, "Shu", "Wei")
        assert "Wu" not in allies


class TestProcessTurns:
    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_alliance_expires(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wei", "non_aggression")
        alliance = find_alliance(gs, "Shu", "Wei")
        alliance.duration = 1
        msgs = process_alliance_turns(gs)
        assert len(msgs) == 1
        assert not is_allied(gs, "Shu", "Wei")

    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_alliance_decrements(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wei", "non_aggression")
        alliance = find_alliance(gs, "Shu", "Wei")
        initial = alliance.duration
        process_alliance_turns(gs)
        assert alliance.duration == initial - 1


class TestListAlliances:
    @patch("src.systems.alliance.random.random", return_value=0.0)
    def test_list(self, mock_rand):
        gs = _make_state()
        propose_alliance(gs, "Wei", "non_aggression")
        result = list_alliances(gs)
        assert len(result) == 1
        assert result[0]["type"] == "non_aggression"

    def test_empty_list(self):
        gs = _make_state()
        gs.alliances = []
        assert list_alliances(gs) == []
