"""Tests for difficulty settings system."""
import pytest
from src.models import GameState
from src.systems.difficulty import (
    DifficultyLevel, AIPersonality, get_difficulty, get_modifier,
    get_ai_personality, get_ai_action_weight,
    apply_difficulty_to_income, apply_difficulty_to_combat,
    list_difficulties, get_difficulty_description,
    DIFFICULTY_MODIFIERS, AI_PERSONALITY_WEIGHTS, DEFAULT_AI_PERSONALITIES,
)


def _make_state(difficulty="Normal"):
    gs = GameState()
    gs.difficulty = difficulty
    gs.player_faction = "Shu"
    return gs


class TestDifficultyLevel:
    def test_all_levels_exist(self):
        assert len(DifficultyLevel) == 4

    def test_easy(self):
        assert DifficultyLevel.EASY.value == "Easy"

    def test_very_hard(self):
        assert DifficultyLevel.VERY_HARD.value == "Very Hard"


class TestGetDifficulty:
    def test_normal(self):
        gs = _make_state("Normal")
        assert get_difficulty(gs) == DifficultyLevel.NORMAL

    def test_hard(self):
        gs = _make_state("Hard")
        assert get_difficulty(gs) == DifficultyLevel.HARD

    def test_invalid_defaults_normal(self):
        gs = _make_state("Invalid")
        assert get_difficulty(gs) == DifficultyLevel.NORMAL


class TestGetModifier:
    def test_normal_income(self):
        gs = _make_state("Normal")
        assert get_modifier(gs, "player_income") == 1.0

    def test_easy_player_income(self):
        gs = _make_state("Easy")
        assert get_modifier(gs, "player_income") > 1.0

    def test_hard_ai_income(self):
        gs = _make_state("Hard")
        assert get_modifier(gs, "ai_income") > 1.0

    def test_very_hard_player_combat(self):
        gs = _make_state("Very Hard")
        assert get_modifier(gs, "player_combat") < 1.0

    def test_unknown_key_returns_1(self):
        gs = _make_state("Normal")
        assert get_modifier(gs, "nonexistent") == 1.0


class TestApplyDifficulty:
    def test_easy_player_income_boosted(self):
        gs = _make_state("Easy")
        result = apply_difficulty_to_income(gs, "Shu", 100)
        assert result > 100

    def test_easy_ai_income_reduced(self):
        gs = _make_state("Easy")
        result = apply_difficulty_to_income(gs, "Wei", 100)
        assert result < 100

    def test_normal_no_change(self):
        gs = _make_state("Normal")
        assert apply_difficulty_to_income(gs, "Shu", 100) == 100
        assert apply_difficulty_to_income(gs, "Wei", 100) == 100

    def test_hard_ai_combat_boosted(self):
        gs = _make_state("Hard")
        result = apply_difficulty_to_combat(gs, "Wei", 100.0)
        assert result > 100.0

    def test_very_hard_ai_income(self):
        gs = _make_state("Very Hard")
        result = apply_difficulty_to_income(gs, "Wei", 100)
        assert result == 150  # 1.5x


class TestAIPersonality:
    def test_wei_aggressive(self):
        assert get_ai_personality("Wei") == AIPersonality.AGGRESSIVE

    def test_shu_defensive(self):
        assert get_ai_personality("Shu") == AIPersonality.DEFENSIVE

    def test_wu_economic(self):
        assert get_ai_personality("Wu") == AIPersonality.ECONOMIC

    def test_unknown_defaults_defensive(self):
        assert get_ai_personality("Unknown") == AIPersonality.DEFENSIVE


class TestAIActionWeights:
    def test_aggressive_attack_weight(self):
        w = get_ai_action_weight("Wei", "attack")
        assert w > 1.0

    def test_defensive_fortify_weight(self):
        w = get_ai_action_weight("Shu", "fortify")
        assert w > 1.0

    def test_economic_trade_weight(self):
        w = get_ai_action_weight("Wu", "trade")
        assert w > 1.0

    def test_aggressive_farm_low(self):
        w = get_ai_action_weight("Wei", "farm")
        assert w < 1.0

    def test_unknown_action_returns_1(self):
        w = get_ai_action_weight("Wei", "unknown_action")
        assert w == 1.0


class TestListDifficulties:
    def test_list(self):
        result = list_difficulties()
        assert len(result) == 4
        names = [d["id"] for d in result]
        assert "Easy" in names
        assert "Very Hard" in names


class TestModifierConsistency:
    def test_all_levels_have_modifiers(self):
        for level in DifficultyLevel:
            assert level in DIFFICULTY_MODIFIERS

    def test_all_personalities_have_weights(self):
        for p in AIPersonality:
            assert p in AI_PERSONALITY_WEIGHTS
