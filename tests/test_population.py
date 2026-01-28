"""Tests for population system."""
import pytest
from src.models import GameState, City, Faction
from src.systems.population import (
    get_max_recruitment, get_production_modifier, calculate_growth,
    process_population, apply_war_losses, process_migration,
    RECRUITMENT_POPULATION_RATIO, MIN_POPULATION, MAX_POPULATION,
    FAMINE_THRESHOLD, WAR_POPULATION_LOSS,
)


def _make_state():
    gs = GameState()
    gs.player_faction = "Shu"
    gs.cities = {
        "Chengdu": City(name="Chengdu", owner="Shu", food=500, commerce=60,
                        morale=70, population=15000),
        "Hanzhong": City(name="Hanzhong", owner="Shu", food=300, commerce=40,
                         morale=40, population=8000),
        "Xuchang": City(name="Xuchang", owner="Wei", food=500, commerce=65,
                         morale=75, population=20000),
    }
    gs.factions = {
        "Shu": Faction(name="Shu", cities=["Chengdu", "Hanzhong"]),
        "Wei": Faction(name="Wei", cities=["Xuchang"]),
    }
    return gs


class TestMaxRecruitment:
    def test_basic(self):
        city = City(name="A", owner="X", population=10000)
        assert get_max_recruitment(city) == int(10000 * RECRUITMENT_POPULATION_RATIO)

    def test_low_population(self):
        city = City(name="A", owner="X", population=1000)
        assert get_max_recruitment(city) == 100


class TestProductionModifier:
    def test_base_population(self):
        city = City(name="A", owner="X", population=10000)
        assert get_production_modifier(city) == 1.0

    def test_high_population(self):
        city = City(name="A", owner="X", population=20000)
        assert get_production_modifier(city) == 2.0

    def test_low_population(self):
        city = City(name="A", owner="X", population=5000)
        assert get_production_modifier(city) == 0.5

    def test_capped_high(self):
        city = City(name="A", owner="X", population=50000)
        assert get_production_modifier(city) == 2.0


class TestCalculateGrowth:
    def test_normal_growth(self):
        city = City(name="A", owner="X", food=500, commerce=60, morale=70, population=10000)
        growth = calculate_growth(city)
        assert growth > 0

    def test_famine_decline(self):
        city = City(name="A", owner="X", food=50, commerce=60, morale=70, population=10000)
        growth = calculate_growth(city)
        assert growth < 0

    def test_low_morale_penalty(self):
        city_high = City(name="A", owner="X", food=500, commerce=60, morale=70, population=10000)
        city_low = City(name="B", owner="X", food=500, commerce=60, morale=20, population=10000)
        assert calculate_growth(city_high) > calculate_growth(city_low)


class TestProcessPopulation:
    def test_growth_events(self):
        gs = _make_state()
        events = process_population(gs)
        assert len(events) > 0

    def test_famine_event(self):
        gs = _make_state()
        gs.cities["Hanzhong"].food = 50
        events = process_population(gs)
        famine_events = [e for e in events if e["type"] == "famine"]
        assert len(famine_events) > 0

    def test_population_bounded(self):
        gs = _make_state()
        gs.cities["Chengdu"].population = MAX_POPULATION
        process_population(gs)
        assert gs.cities["Chengdu"].population <= MAX_POPULATION

    def test_population_min_bounded(self):
        gs = _make_state()
        gs.cities["Hanzhong"].population = MIN_POPULATION
        gs.cities["Hanzhong"].food = 50
        process_population(gs)
        assert gs.cities["Hanzhong"].population >= MIN_POPULATION


class TestWarLosses:
    def test_war_losses(self):
        city = City(name="A", owner="X", population=10000)
        losses = apply_war_losses(city)
        assert losses == int(10000 * WAR_POPULATION_LOSS)
        assert city.population == 10000 - losses

    def test_min_population_after_war(self):
        city = City(name="A", owner="X", population=MIN_POPULATION)
        apply_war_losses(city)
        assert city.population >= MIN_POPULATION


class TestMigration:
    def test_migration_occurs(self):
        gs = _make_state()
        gs.cities["Chengdu"].morale = 90
        gs.cities["Hanzhong"].morale = 30
        events = process_migration(gs)
        assert len(events) > 0
        assert events[0]["from"] == "Hanzhong"
        assert events[0]["to"] == "Chengdu"

    def test_no_migration_similar_morale(self):
        gs = _make_state()
        gs.cities["Chengdu"].morale = 60
        gs.cities["Hanzhong"].morale = 55
        events = process_migration(gs)
        assert len(events) == 0

    def test_single_city_no_migration(self):
        gs = _make_state()
        events = process_migration(gs)
        # Wei has only 1 city, no migration for Wei
        wei_events = [e for e in events if "Xuchang" in str(e)]
        assert len(wei_events) == 0
