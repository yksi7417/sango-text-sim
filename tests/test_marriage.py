"""Tests for marriage and hostage system."""
import pytest
from unittest.mock import patch
from src.models import GameState, Faction, Officer, RelationshipType
from src.systems.marriage import (
    propose_marriage, send_hostage, return_hostage, list_hostages,
    MARRIAGE_RELATION_BOOST, MARRIAGE_LOYALTY_BOOST, HOSTAGE_RETURN_BOOST,
)


def _make_state():
    gs = GameState()
    gs.player_faction = "Shu"
    gs.factions = {
        "Wei": Faction(name="Wei", cities=["Xuchang"],
                       officers=["CaoCao"], relations={"Shu": 20, "Wu": 0, "Wei": 0}),
        "Shu": Faction(name="Shu", cities=["Chengdu"],
                       officers=["LiuBei", "ZhangFei"], relations={"Wei": 20, "Wu": 30, "Shu": 0}),
        "Wu": Faction(name="Wu", cities=["Jianye"],
                      officers=["SunQuan"], relations={"Wei": 0, "Shu": 30, "Wu": 0}),
    }
    gs.officers = {
        "LiuBei": Officer(name="LiuBei", faction="Shu", leadership=86,
                          intelligence=80, politics=88, charisma=96, city="Chengdu"),
        "ZhangFei": Officer(name="ZhangFei", faction="Shu", leadership=97,
                            intelligence=65, politics=60, charisma=82, city="Chengdu"),
        "CaoCao": Officer(name="CaoCao", faction="Wei", leadership=92,
                          intelligence=94, politics=96, charisma=90, city="Xuchang"),
        "SunQuan": Officer(name="SunQuan", faction="Wu", leadership=86,
                           intelligence=80, politics=85, charisma=92, city="Jianye"),
    }
    gs.hostages = {}
    return gs


class TestProposeMarriage:
    @patch("src.systems.marriage.random.random", return_value=0.0)
    def test_successful_marriage(self, mock_rand):
        gs = _make_state()
        result = propose_marriage(gs, "LiuBei", "Wei")
        assert result["success"] is True

    @patch("src.systems.marriage.random.random", return_value=0.0)
    def test_creates_spouse_relationship(self, mock_rand):
        gs = _make_state()
        propose_marriage(gs, "LiuBei", "Wei")
        assert gs.officers["LiuBei"].relationships.get("CaoCao") == RelationshipType.SPOUSE.value

    @patch("src.systems.marriage.random.random", return_value=0.0)
    def test_boosts_relations(self, mock_rand):
        gs = _make_state()
        before = gs.factions["Shu"].relations["Wei"]
        propose_marriage(gs, "LiuBei", "Wei")
        after = gs.factions["Shu"].relations["Wei"]
        assert after == before + MARRIAGE_RELATION_BOOST

    @patch("src.systems.marriage.random.random", return_value=0.0)
    def test_boosts_loyalty(self, mock_rand):
        gs = _make_state()
        before = gs.officers["LiuBei"].loyalty
        propose_marriage(gs, "LiuBei", "Wei")
        assert gs.officers["LiuBei"].loyalty == min(100, before + MARRIAGE_LOYALTY_BOOST)

    @patch("src.systems.marriage.random.random", return_value=0.99)
    def test_rejected(self, mock_rand):
        gs = _make_state()
        result = propose_marriage(gs, "LiuBei", "Wei")
        assert result["success"] is False

    @patch("src.systems.marriage.random.random", return_value=0.0)
    def test_already_married(self, mock_rand):
        gs = _make_state()
        propose_marriage(gs, "LiuBei", "Wei")
        result = propose_marriage(gs, "LiuBei", "Wu")
        assert result["success"] is False

    def test_invalid_officer(self):
        gs = _make_state()
        result = propose_marriage(gs, "Nobody", "Wei")
        assert result["success"] is False

    def test_enemy_officer(self):
        gs = _make_state()
        result = propose_marriage(gs, "CaoCao", "Wu")
        assert result["success"] is False

    def test_same_faction(self):
        gs = _make_state()
        result = propose_marriage(gs, "LiuBei", "Shu")
        assert result["success"] is False


class TestSendHostage:
    def test_send_hostage(self):
        gs = _make_state()
        result = send_hostage(gs, "ZhangFei", "Wei")
        assert result["success"] is True
        assert "ZhangFei" in gs.hostages

    def test_hostage_removed_from_duty(self):
        gs = _make_state()
        send_hostage(gs, "ZhangFei", "Wei")
        assert gs.officers["ZhangFei"].city is None

    def test_hostage_boosts_relations(self):
        gs = _make_state()
        before = gs.factions["Shu"].relations["Wei"]
        send_hostage(gs, "ZhangFei", "Wei")
        assert gs.factions["Shu"].relations["Wei"] > before

    def test_invalid_officer(self):
        gs = _make_state()
        result = send_hostage(gs, "Nobody", "Wei")
        assert result["success"] is False

    def test_same_faction(self):
        gs = _make_state()
        result = send_hostage(gs, "LiuBei", "Shu")
        assert result["success"] is False


class TestReturnHostage:
    def test_return_hostage(self):
        gs = _make_state()
        send_hostage(gs, "ZhangFei", "Wei")
        result = return_hostage(gs, "ZhangFei")
        assert result["success"] is True
        assert "ZhangFei" not in gs.hostages

    def test_return_boosts_relations(self):
        gs = _make_state()
        send_hostage(gs, "ZhangFei", "Wei")
        before = gs.factions["Shu"].relations["Shu"]
        return_hostage(gs, "ZhangFei")
        # Relations with hostage's home faction improve
        assert gs.factions["Shu"].relations.get("Shu", 0) >= before

    def test_not_hostage(self):
        gs = _make_state()
        result = return_hostage(gs, "LiuBei")
        assert result["success"] is False


class TestListHostages:
    def test_list_hostages(self):
        gs = _make_state()
        send_hostage(gs, "ZhangFei", "Wei")
        result = list_hostages(gs)
        assert len(result) == 1
        assert result[0]["officer"] == "ZhangFei"

    def test_empty_list(self):
        gs = _make_state()
        assert list_hostages(gs) == []
