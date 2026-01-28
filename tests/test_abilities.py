"""Tests for the officer abilities system."""
import pytest
from src.models import Ability
from src.abilities import load_abilities, get_ability, get_officer_abilities, get_officer_ability


class TestLoadAbilities:
    def test_load_abilities(self):
        abilities = load_abilities()
        assert len(abilities) >= 15

    def test_ability_has_required_fields(self):
        abilities = load_abilities()
        for a in abilities:
            assert a.id
            assert a.officer
            assert a.name_key
            assert a.context in ("battle", "duel")
            assert a.cooldown > 0

    def test_unique_ids(self):
        abilities = load_abilities()
        ids = [a.id for a in abilities]
        assert len(ids) == len(set(ids))


class TestGetAbility:
    def test_get_existing(self):
        a = get_ability("empty_fort")
        assert a is not None
        assert a.officer == "ZhugeLiang"
        assert a.context == "battle"

    def test_get_nonexistent(self):
        assert get_ability("nonexistent") is None

    def test_green_dragon_slash(self):
        a = get_ability("green_dragon_slash")
        assert a is not None
        assert a.officer == "GuanYu"
        assert a.context == "duel"
        assert "damage_mult" in a.effect

    def test_lone_rider(self):
        a = get_ability("lone_rider")
        assert a is not None
        assert a.officer == "ZhaoYun"


class TestGetOfficerAbilities:
    def test_officer_with_abilities(self):
        abilities = get_officer_abilities("ZhugeLiang")
        assert len(abilities) >= 1
        assert abilities[0].id == "empty_fort"

    def test_officer_without_abilities(self):
        abilities = get_officer_abilities("NonExistent")
        assert len(abilities) == 0


class TestGetOfficerAbility:
    def test_duel_ability(self):
        a = get_officer_ability("GuanYu", "duel")
        assert a is not None
        assert a.id == "green_dragon_slash"

    def test_battle_ability(self):
        a = get_officer_ability("ZhugeLiang", "battle")
        assert a is not None
        assert a.id == "empty_fort"

    def test_no_ability_for_context(self):
        # GuanYu has duel ability but not battle
        a = get_officer_ability("GuanYu", "battle")
        assert a is None

    def test_specific_effects(self):
        a = get_officer_ability("XuChu", "duel")
        assert a is not None
        assert a.effect.get("defense_mult") == 2.5
