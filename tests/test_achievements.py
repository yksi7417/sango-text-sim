"""Tests for the achievement system."""
import pytest
from src.models import GameState, City, Faction, Officer
from src.systems.achievements import load_achievements, check_achievements, _check_achievement_condition, Achievement


def _make_state():
    gs = GameState()
    gs.year = 210
    gs.month = 6
    gs.player_faction = "Shu"
    gs.cities["Chengdu"] = City(name="Chengdu", owner="Shu", gold=1000, food=1500, troops=500, defense=50, morale=70, agri=60, commerce=60, tech=50)
    gs.cities["Hanzhong"] = City(name="Hanzhong", owner="Shu", gold=800, food=1000, troops=400, defense=40, morale=65, agri=55, commerce=50, tech=45)
    gs.cities["Luoyang"] = City(name="Luoyang", owner="Wei", gold=500)
    gs.factions["Shu"] = Faction(name="Shu", cities=["Chengdu", "Hanzhong"],
                                  officers=["LiuBei", "GuanYu", "ZhangFei"],
                                  relations={"Wei": -20, "Wu": 30})
    gs.factions["Wei"] = Faction(name="Wei", cities=["Luoyang"])
    for name in ["LiuBei", "GuanYu", "ZhangFei"]:
        gs.officers[name] = Officer(name=name, faction="Shu", leadership=80, intelligence=70, politics=60, charisma=70, loyalty=75)
    return gs


class TestLoadAchievements:
    def test_load(self):
        achs = load_achievements()
        assert len(achs) >= 25

    def test_has_required_fields(self):
        for a in load_achievements():
            assert a.id
            assert a.category in ("military", "economic", "diplomatic", "collection")
            assert a.name_key

    def test_unique_ids(self):
        achs = load_achievements()
        ids = [a.id for a in achs]
        assert len(ids) == len(set(ids))


class TestCheckConditions:
    def test_cities_owned(self):
        ach = Achievement(id="test", category="military", name_key="t", condition={"cities_owned": 2})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_cities_owned_not_met(self):
        ach = Achievement(id="test", category="military", name_key="t", condition={"cities_owned": 5})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is False

    def test_total_gold(self):
        ach = Achievement(id="test", category="economic", name_key="t", condition={"total_gold": 1500})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_total_food(self):
        ach = Achievement(id="test", category="economic", name_key="t", condition={"total_food": 2000})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_total_troops(self):
        ach = Achievement(id="test", category="military", name_key="t", condition={"total_troops": 800})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_officers_count(self):
        ach = Achievement(id="test", category="collection", name_key="t", condition={"officers_count": 3})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_officers_in_faction(self):
        ach = Achievement(id="test", category="collection", name_key="t",
                         condition={"officers_in_faction": ["LiuBei", "GuanYu"]})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_officers_in_faction_missing(self):
        ach = Achievement(id="test", category="collection", name_key="t",
                         condition={"officers_in_faction": ["LiuBei", "ZhaoYun"]})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is False

    def test_max_relations(self):
        ach = Achievement(id="test", category="diplomatic", name_key="t", condition={"max_relations": 20})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_all_loyalty_above(self):
        ach = Achievement(id="test", category="collection", name_key="t", condition={"all_loyalty_above": 70})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is True

    def test_all_loyalty_above_fail(self):
        ach = Achievement(id="test", category="collection", name_key="t", condition={"all_loyalty_above": 80})
        gs = _make_state()
        assert _check_achievement_condition(ach, gs) is False

    def test_turns_survived(self):
        ach = Achievement(id="test", category="military", name_key="t", condition={"turns_survived": 24})
        gs = _make_state()
        # year 210, month 6 = 30 turns from year 208
        assert _check_achievement_condition(ach, gs) is True


class TestCheckAchievements:
    def test_finds_new_achievements(self):
        gs = _make_state()
        newly = check_achievements(gs, [])
        assert len(newly) > 0

    def test_skips_already_earned(self):
        gs = _make_state()
        newly1 = check_achievements(gs, [])
        earned_ids = [a.id for a in newly1]
        newly2 = check_achievements(gs, earned_ids)
        for a in newly2:
            assert a.id not in earned_ids
