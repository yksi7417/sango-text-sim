"""Tests for the unit types system (p2-10)."""
import pytest
from src.models import UnitType, City
from src.constants import UNIT_TYPE_ADVANTAGE, UNIT_TYPE_DISADVANTAGE, UNIT_ADVANTAGE_MAP


class TestUnitTypeEnum:
    """Test UnitType enum."""

    def test_all_unit_types(self):
        assert UnitType.INFANTRY.value == "infantry"
        assert UnitType.CAVALRY.value == "cavalry"
        assert UnitType.ARCHER.value == "archer"

    def test_unit_type_count(self):
        assert len(UnitType) == 3


class TestCityUnitComposition:
    """Test City unit composition."""

    def test_default_composition_from_troops(self):
        city = City(name="Test", owner="Wei", troops=300)
        assert city.unit_composition["infantry"] == 150  # 50%
        assert city.unit_composition["cavalry"] == 75    # 25%
        assert city.unit_composition["archer"] == 75     # 25%

    def test_custom_composition(self):
        city = City(name="Test", owner="Wei", troops=300,
                    unit_composition={"infantry": 100, "cavalry": 100, "archer": 100})
        assert city.unit_composition["infantry"] == 100
        assert city.unit_composition["cavalry"] == 100
        assert city.unit_composition["archer"] == 100

    def test_zero_troops_no_composition(self):
        city = City(name="Test", owner="Wei", troops=0)
        assert sum(city.unit_composition.values()) == 0

    def test_get_units(self):
        city = City(name="Test", owner="Wei", troops=300)
        assert city.get_units(UnitType.INFANTRY) == 150
        assert city.get_units(UnitType.CAVALRY) == 75
        assert city.get_units(UnitType.ARCHER) == 75

    def test_sync_troops(self):
        city = City(name="Test", owner="Wei", troops=300,
                    unit_composition={"infantry": 200, "cavalry": 100, "archer": 50})
        city.sync_troops()
        assert city.troops == 350

    def test_backward_compatible_no_composition(self):
        """Cities without unit_composition should auto-generate it."""
        city = City(name="Test", owner="Wei", troops=400)
        total = sum(city.unit_composition.values())
        assert total == 400


class TestUnitCombatConstants:
    """Test unit type combat constants."""

    def test_advantage_modifier(self):
        assert UNIT_TYPE_ADVANTAGE == 1.20

    def test_disadvantage_modifier(self):
        assert UNIT_TYPE_DISADVANTAGE == 0.80

    def test_advantage_map_completeness(self):
        assert "cavalry" in UNIT_ADVANTAGE_MAP
        assert "archer" in UNIT_ADVANTAGE_MAP
        assert "infantry" in UNIT_ADVANTAGE_MAP

    def test_rock_paper_scissors(self):
        assert UNIT_ADVANTAGE_MAP["cavalry"] == "archer"
        assert UNIT_ADVANTAGE_MAP["archer"] == "infantry"
        assert UNIT_ADVANTAGE_MAP["infantry"] == "cavalry"


class TestUnitI18n:
    """Test unit type i18n keys."""

    def test_locale_keys_exist(self):
        import json
        with open('locales/en.json', encoding='utf-8') as f:
            en = json.load(f)
        with open('locales/zh.json', encoding='utf-8') as f:
            zh = json.load(f)

        assert 'units' in en
        assert 'units' in zh

        for ut in UnitType:
            assert ut.value in en['units']
            assert ut.value in zh['units']

        assert 'advantage' in en['units']
        assert 'advantage' in zh['units']


class TestTrainingUnitTypes:
    """Test that training produces unit types."""

    def test_train_adds_to_composition(self):
        from unittest.mock import patch
        from src.models import GameState, Officer
        from src.world import init_world
        from src.engine import process_assignments

        gs = GameState()
        init_world(gs)

        # Find a city with an officer
        city_name = list(gs.cities.keys())[0]
        city = gs.cities[city_name]
        initial_troops = city.troops

        # Find officer in this city
        officer = None
        for off in gs.officers.values():
            if off.city == city_name:
                officer = off
                break

        if officer:
            officer.task = "train"
            officer.task_city = city_name
            officer.busy = True

            with patch('src.engine.random.choice', return_value="infantry"):
                process_assignments(gs)

            assert city.troops == initial_troops + 10
            assert city.unit_composition["infantry"] > 0
