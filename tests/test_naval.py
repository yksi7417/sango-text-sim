"""Tests for naval combat system."""
import pytest
from src.models import GameState, City, Faction, Officer, TerrainType, UnitType
from src.systems.naval import (
    can_build_ships, build_ships, get_transport_capacity,
    check_naval_route, can_transport_troops,
    get_naval_combat_modifier, get_naval_defense_modifier,
    get_fleet_status,
)
from src.constants import SHIP_TRANSPORT_CAPACITY


def _make_state():
    gs = GameState()
    gs.player_faction = "Wu"
    gs.cities = {
        "Jianye": City(name="Jianye", owner="Wu", gold=500, food=500,
                       terrain=TerrainType.COASTAL, ships=0),
        "Wuchang": City(name="Wuchang", owner="Wu", gold=300, food=300,
                        terrain=TerrainType.RIVER, ships=0),
        "Xuchang": City(name="Xuchang", owner="Wei", gold=500, food=500,
                        terrain=TerrainType.PLAINS, ships=0),
    }
    gs.factions = {
        "Wu": Faction(name="Wu", cities=["Jianye", "Wuchang"], officers=["ZhouYu"]),
        "Wei": Faction(name="Wei", cities=["Xuchang"], officers=[]),
    }
    gs.officers = {
        "ZhouYu": Officer(name="ZhouYu", faction="Wu", leadership=90,
                          intelligence=92, politics=88, charisma=88,
                          traits=["Scholar", "Engineer"], city="Jianye"),
    }
    return gs


class TestCanBuildShips:
    def test_coastal_city_can_build(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL)
        assert can_build_ships(city) is True

    def test_river_city_can_build(self):
        city = City(name="Wuchang", owner="Wu", terrain=TerrainType.RIVER)
        assert can_build_ships(city) is True

    def test_plains_city_cannot_build(self):
        city = City(name="Xuchang", owner="Wei", terrain=TerrainType.PLAINS)
        assert can_build_ships(city) is False

    def test_mountain_city_cannot_build(self):
        city = City(name="Chengdu", owner="Shu", terrain=TerrainType.MOUNTAIN)
        assert can_build_ships(city) is False


class TestBuildShips:
    def test_build_one_ship(self):
        gs = _make_state()
        result = build_ships(gs, "Jianye", 1)
        assert result["success"] is True
        assert gs.cities["Jianye"].ships == 1

    def test_build_multiple_ships(self):
        gs = _make_state()
        result = build_ships(gs, "Jianye", 3)
        assert result["success"] is True
        assert gs.cities["Jianye"].ships == 3

    def test_build_deducts_resources(self):
        gs = _make_state()
        gold_before = gs.cities["Jianye"].gold
        food_before = gs.cities["Jianye"].food
        build_ships(gs, "Jianye", 2)
        assert gs.cities["Jianye"].gold < gold_before
        assert gs.cities["Jianye"].food < food_before

    def test_cannot_build_on_plains(self):
        gs = _make_state()
        gs.cities["Xuchang"].owner = "Wu"
        gs.factions["Wu"].cities.append("Xuchang")
        result = build_ships(gs, "Xuchang", 1)
        assert result["success"] is False

    def test_cannot_build_insufficient_gold(self):
        gs = _make_state()
        gs.cities["Jianye"].gold = 10
        result = build_ships(gs, "Jianye", 1)
        assert result["success"] is False

    def test_cannot_build_enemy_city(self):
        gs = _make_state()
        result = build_ships(gs, "Xuchang", 1)
        assert result["success"] is False


class TestTransport:
    def test_transport_capacity(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL, ships=5)
        assert get_transport_capacity(city) == 5 * SHIP_TRANSPORT_CAPACITY

    def test_no_ships_no_capacity(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL, ships=0)
        assert get_transport_capacity(city) == 0

    def test_can_transport_with_ships(self):
        gs = _make_state()
        gs.cities["Jianye"].ships = 5
        result = can_transport_troops(gs, "Jianye", "Wuchang", 200)
        assert result["can_transport"] is True

    def test_cannot_transport_insufficient_ships(self):
        gs = _make_state()
        gs.cities["Jianye"].ships = 1
        result = can_transport_troops(gs, "Jianye", "Wuchang", 200)
        assert result["can_transport"] is False

    def test_no_naval_needed_for_plains(self):
        gs = _make_state()
        result = can_transport_troops(gs, "Jianye", "Xuchang", 200)
        assert result["can_transport"] is True


class TestNavalCombat:
    def test_naval_bonus_with_ships(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL)
        mod = get_naval_combat_modifier(city, attacker_ships=5)
        assert mod > 1.0

    def test_penalty_without_ships_on_water(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL)
        mod = get_naval_combat_modifier(city, attacker_ships=0)
        assert mod < 1.0

    def test_no_modifier_on_plains(self):
        city = City(name="Xuchang", owner="Wei", terrain=TerrainType.PLAINS)
        mod = get_naval_combat_modifier(city, attacker_ships=5)
        assert mod == 1.0

    def test_fire_attack_bonus_on_water(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL)
        mod_normal = get_naval_combat_modifier(city, attacker_ships=5, is_fire_attack=False)
        mod_fire = get_naval_combat_modifier(city, attacker_ships=5, is_fire_attack=True)
        assert mod_fire > mod_normal

    def test_zhou_yu_naval_bonus(self):
        gs = _make_state()
        city = gs.cities["Jianye"]
        officer = gs.officers["ZhouYu"]
        mod_without = get_naval_combat_modifier(city, attacker_ships=5)
        mod_with = get_naval_combat_modifier(city, attacker_ships=5, officer=officer)
        assert mod_with > mod_without

    def test_naval_defense_with_ships(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL, ships=3)
        mod = get_naval_defense_modifier(city)
        assert mod > 1.0

    def test_naval_defense_without_ships(self):
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL, ships=0)
        mod = get_naval_defense_modifier(city)
        assert mod == 1.0

    def test_naval_defense_plains(self):
        city = City(name="Xuchang", owner="Wei", terrain=TerrainType.PLAINS, ships=0)
        mod = get_naval_defense_modifier(city)
        assert mod == 1.0


class TestFleetStatus:
    def test_fleet_status(self):
        gs = _make_state()
        gs.cities["Jianye"].ships = 5
        gs.cities["Wuchang"].ships = 3
        fleet = get_fleet_status(gs, "Wu")
        assert len(fleet) == 2
        assert fleet[0]["ships"] == 5

    def test_empty_fleet(self):
        gs = _make_state()
        fleet = get_fleet_status(gs, "Wu")
        assert len(fleet) == 0

    def test_fleet_has_capacity(self):
        gs = _make_state()
        gs.cities["Jianye"].ships = 4
        fleet = get_fleet_status(gs, "Wu")
        assert fleet[0]["capacity"] == 4 * SHIP_TRANSPORT_CAPACITY


class TestUnitType:
    def test_navy_unit_type_exists(self):
        assert UnitType.NAVY.value == "navy"


class TestNavalRoute:
    def test_coastal_requires_naval(self):
        gs = _make_state()
        assert check_naval_route(gs, "Xuchang", "Jianye") is True

    def test_plains_no_naval(self):
        gs = _make_state()
        assert check_naval_route(gs, "Jianye", "Xuchang") is False
