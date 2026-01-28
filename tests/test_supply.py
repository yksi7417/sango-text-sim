"""Tests for supply line system."""
import pytest
from src.models import GameState, City, Faction, TerrainType
from src.systems.supply import (
    calculate_supply_consumption, check_supply_line,
    apply_supply_attrition, forage_supplies, get_supply_status,
    SUPPLY_PER_TROOP, ATTRITION_RATE, FORAGING_RECOVERY,
)


def _make_state():
    gs = GameState()
    gs.player_faction = "Shu"
    gs.cities = {
        "Chengdu": City(name="Chengdu", owner="Shu", gold=500, food=500),
        "Hanzhong": City(name="Hanzhong", owner="Shu", gold=300, food=300),
        "Luoyang": City(name="Luoyang", owner="Wei", gold=500, food=500),
        "Xuchang": City(name="Xuchang", owner="Wei", gold=500, food=500),
    }
    gs.adj = {
        "Chengdu": ["Hanzhong"],
        "Hanzhong": ["Chengdu", "Luoyang"],
        "Luoyang": ["Hanzhong", "Xuchang"],
        "Xuchang": ["Luoyang"],
    }
    gs.factions = {
        "Shu": Faction(name="Shu", cities=["Chengdu", "Hanzhong"]),
        "Wei": Faction(name="Wei", cities=["Luoyang", "Xuchang"]),
    }
    return gs


class TestSupplyConsumption:
    def test_basic_consumption(self):
        result = calculate_supply_consumption(100)
        assert result == int(100 * SUPPLY_PER_TROOP)

    def test_minimum_one(self):
        result = calculate_supply_consumption(1)
        assert result >= 1

    def test_zero_troops(self):
        result = calculate_supply_consumption(0)
        assert result >= 1


class TestCheckSupplyLine:
    def test_same_city(self):
        gs = _make_state()
        result = check_supply_line(gs, "Chengdu", "Chengdu", "Shu")
        assert result["intact"] is True

    def test_adjacent_owned(self):
        gs = _make_state()
        result = check_supply_line(gs, "Chengdu", "Hanzhong", "Shu")
        assert result["intact"] is True

    def test_blocked_by_enemy(self):
        gs = _make_state()
        result = check_supply_line(gs, "Chengdu", "Luoyang", "Shu")
        assert result["intact"] is False

    def test_enemy_supply_line(self):
        gs = _make_state()
        result = check_supply_line(gs, "Xuchang", "Luoyang", "Wei")
        assert result["intact"] is True

    def test_path_returned(self):
        gs = _make_state()
        result = check_supply_line(gs, "Chengdu", "Hanzhong", "Shu")
        assert "Chengdu" in result["path"]
        assert "Hanzhong" in result["path"]


class TestSupplyAttrition:
    def test_no_attrition_with_supply(self):
        result = apply_supply_attrition(100, has_supply=True)
        assert result["losses"] == 0
        assert result["troops"] == 100

    def test_attrition_without_supply(self):
        result = apply_supply_attrition(100, has_supply=False)
        assert result["losses"] > 0
        assert result["troops"] < 100

    def test_minimum_loss(self):
        result = apply_supply_attrition(10, has_supply=False)
        assert result["losses"] >= 1


class TestForage:
    def test_forage_friendly_city(self):
        gs = _make_state()
        result = forage_supplies(gs, "Chengdu", "Shu")
        assert result["success"] is True
        assert result["recovery"] == FORAGING_RECOVERY

    def test_forage_enemy_city(self):
        gs = _make_state()
        result = forage_supplies(gs, "Luoyang", "Shu")
        assert result["success"] is False

    def test_forage_consumes_food(self):
        gs = _make_state()
        food_before = gs.cities["Chengdu"].food
        forage_supplies(gs, "Chengdu", "Shu")
        assert gs.cities["Chengdu"].food < food_before

    def test_forage_invalid_city(self):
        gs = _make_state()
        result = forage_supplies(gs, "Nowhere", "Shu")
        assert result["success"] is False


class TestGetSupplyStatus:
    def test_has_supply_in_owned_territory(self):
        gs = _make_state()
        status = get_supply_status(gs, "Hanzhong", "Shu")
        assert status["has_supply"] is True

    def test_no_supply_in_enemy_territory(self):
        gs = _make_state()
        status = get_supply_status(gs, "Xuchang", "Shu")
        assert status["has_supply"] is False

    def test_nearby_friendly(self):
        gs = _make_state()
        status = get_supply_status(gs, "Hanzhong", "Shu")
        assert "Chengdu" in status["nearby_friendly"]
