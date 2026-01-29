"""
Integration Tests: AI Difficulty Scaling

This module tests AI behavior across difficulty levels:
- Easy AI bonuses/penalties
- Normal balanced play
- Hard AI advantages
- Very Hard AI strength
- AI personality types
- AI decision quality scaling

Based on 3KYuYun's PvP vs PvE analysis for ROTK11.
"""
import pytest
from src.systems.difficulty import (
    DifficultyLevel,
    AIPersonality,
    DIFFICULTY_MODIFIERS,
    AI_PERSONALITY_WEIGHTS,
    DEFAULT_AI_PERSONALITIES,
    get_difficulty,
    get_modifier,
    get_ai_personality,
    get_ai_action_weight,
    apply_difficulty_to_income,
    apply_difficulty_to_combat,
    get_difficulty_description,
    list_difficulties,
)
from src.models import GameState


class TestDifficultyLevelEnum:
    """Test difficulty level enumeration."""

    def test_easy_level_exists(self):
        """Easy difficulty should exist."""
        assert DifficultyLevel.EASY.value == "Easy"

    def test_normal_level_exists(self):
        """Normal difficulty should exist."""
        assert DifficultyLevel.NORMAL.value == "Normal"

    def test_hard_level_exists(self):
        """Hard difficulty should exist."""
        assert DifficultyLevel.HARD.value == "Hard"

    def test_very_hard_level_exists(self):
        """Very Hard difficulty should exist."""
        assert DifficultyLevel.VERY_HARD.value == "Very Hard"

    def test_four_difficulty_levels(self):
        """Should have exactly 4 difficulty levels."""
        levels = list(DifficultyLevel)
        assert len(levels) == 4


class TestEasyDifficultyModifiers:
    """Test Easy difficulty bonuses/penalties."""

    def test_easy_player_income_bonus(self):
        """Easy should give player +30% income."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["player_income"]
        assert modifier == 1.30

    def test_easy_player_combat_bonus(self):
        """Easy should give player +15% combat."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["player_combat"]
        assert modifier == 1.15

    def test_easy_ai_income_penalty(self):
        """Easy should give AI -20% income."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["ai_income"]
        assert modifier == 0.80

    def test_easy_ai_combat_penalty(self):
        """Easy should give AI -15% combat."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["ai_combat"]
        assert modifier == 0.85

    def test_easy_ai_recruitment_penalty(self):
        """Easy should give AI -20% recruitment."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["ai_recruitment"]
        assert modifier == 0.80

    def test_easy_player_advantage(self):
        """Player should have advantage on Easy."""
        player_combat = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["player_combat"]
        ai_combat = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["ai_combat"]

        assert player_combat > ai_combat


class TestNormalDifficultyModifiers:
    """Test Normal balanced play modifiers."""

    def test_normal_player_income(self):
        """Normal should give player standard income."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.NORMAL]["player_income"]
        assert modifier == 1.00

    def test_normal_player_combat(self):
        """Normal should give player standard combat."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.NORMAL]["player_combat"]
        assert modifier == 1.00

    def test_normal_ai_income(self):
        """Normal should give AI standard income."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.NORMAL]["ai_income"]
        assert modifier == 1.00

    def test_normal_ai_combat(self):
        """Normal should give AI standard combat."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.NORMAL]["ai_combat"]
        assert modifier == 1.00

    def test_normal_all_equal(self):
        """Normal should have all modifiers at 1.0."""
        mods = DIFFICULTY_MODIFIERS[DifficultyLevel.NORMAL]
        assert all(v == 1.0 for v in mods.values())


class TestHardDifficultyModifiers:
    """Test Hard AI advantages."""

    def test_hard_ai_income_bonus(self):
        """Hard should give AI +20% income."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["ai_income"]
        assert modifier == 1.20

    def test_hard_ai_combat_bonus(self):
        """Hard should give AI +15% combat."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["ai_combat"]
        assert modifier == 1.15

    def test_hard_ai_recruitment_bonus(self):
        """Hard should give AI +20% recruitment."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["ai_recruitment"]
        assert modifier == 1.20

    def test_hard_player_unchanged(self):
        """Hard should not change player modifiers."""
        player_income = DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["player_income"]
        player_combat = DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["player_combat"]

        assert player_income == 1.00
        assert player_combat == 1.00


class TestVeryHardDifficultyModifiers:
    """Test Very Hard AI strength."""

    def test_very_hard_player_income_penalty(self):
        """Very Hard should give player -15% income."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["player_income"]
        assert modifier == 0.85

    def test_very_hard_player_combat_penalty(self):
        """Very Hard should give player -5% combat."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["player_combat"]
        assert modifier == 0.95

    def test_very_hard_ai_income_bonus(self):
        """Very Hard should give AI +50% income."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["ai_income"]
        assert modifier == 1.50

    def test_very_hard_ai_combat_bonus(self):
        """Very Hard should give AI +30% combat."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["ai_combat"]
        assert modifier == 1.30

    def test_very_hard_ai_recruitment_bonus(self):
        """Very Hard should give AI +50% recruitment."""
        modifier = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["ai_recruitment"]
        assert modifier == 1.50

    def test_very_hard_significant_ai_advantage(self):
        """Very Hard AI should have significant advantage."""
        player_combat = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["player_combat"]
        ai_combat = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["ai_combat"]

        # AI has 35% effective combat advantage
        advantage = ai_combat / player_combat
        assert advantage > 1.3


class TestAIPersonalityEnum:
    """Test AI personality enumeration."""

    def test_aggressive_personality(self):
        """Aggressive personality should exist."""
        assert AIPersonality.AGGRESSIVE.value == "aggressive"

    def test_defensive_personality(self):
        """Defensive personality should exist."""
        assert AIPersonality.DEFENSIVE.value == "defensive"

    def test_economic_personality(self):
        """Economic personality should exist."""
        assert AIPersonality.ECONOMIC.value == "economic"

    def test_three_personality_types(self):
        """Should have exactly 3 personality types."""
        personalities = list(AIPersonality)
        assert len(personalities) == 3


class TestAIPersonalityWeights:
    """Test AI personality action weights."""

    def test_aggressive_attack_weight(self):
        """Aggressive AI should prefer attacking."""
        weight = AI_PERSONALITY_WEIGHTS[AIPersonality.AGGRESSIVE]["attack"]
        assert weight == 2.0

    def test_aggressive_farm_low_weight(self):
        """Aggressive AI should deprioritize farming."""
        weight = AI_PERSONALITY_WEIGHTS[AIPersonality.AGGRESSIVE]["farm"]
        assert weight == 0.7

    def test_defensive_fortify_weight(self):
        """Defensive AI should prefer fortifying."""
        weight = AI_PERSONALITY_WEIGHTS[AIPersonality.DEFENSIVE]["fortify"]
        assert weight == 2.0

    def test_defensive_attack_low_weight(self):
        """Defensive AI should avoid attacking."""
        weight = AI_PERSONALITY_WEIGHTS[AIPersonality.DEFENSIVE]["attack"]
        assert weight == 0.5

    def test_economic_trade_weight(self):
        """Economic AI should prefer trading."""
        weight = AI_PERSONALITY_WEIGHTS[AIPersonality.ECONOMIC]["trade"]
        assert weight == 2.0

    def test_economic_farm_weight(self):
        """Economic AI should prefer farming."""
        weight = AI_PERSONALITY_WEIGHTS[AIPersonality.ECONOMIC]["farm"]
        assert weight == 1.8

    def test_economic_attack_low_weight(self):
        """Economic AI should avoid attacking."""
        weight = AI_PERSONALITY_WEIGHTS[AIPersonality.ECONOMIC]["attack"]
        assert weight == 0.5


class TestDefaultAIPersonalities:
    """Test default faction AI personalities."""

    def test_wei_aggressive(self):
        """Wei should be aggressive by default."""
        personality = DEFAULT_AI_PERSONALITIES["Wei"]
        assert personality == AIPersonality.AGGRESSIVE

    def test_shu_defensive(self):
        """Shu should be defensive by default."""
        personality = DEFAULT_AI_PERSONALITIES["Shu"]
        assert personality == AIPersonality.DEFENSIVE

    def test_wu_economic(self):
        """Wu should be economic by default."""
        personality = DEFAULT_AI_PERSONALITIES["Wu"]
        assert personality == AIPersonality.ECONOMIC


class TestGetDifficultyFunction:
    """Test get_difficulty function."""

    def test_get_normal_difficulty(self):
        """Should return Normal for default state."""
        game_state = GameState()
        game_state.difficulty = "Normal"

        difficulty = get_difficulty(game_state)
        assert difficulty == DifficultyLevel.NORMAL

    def test_get_easy_difficulty(self):
        """Should return Easy when set."""
        game_state = GameState()
        game_state.difficulty = "Easy"

        difficulty = get_difficulty(game_state)
        assert difficulty == DifficultyLevel.EASY

    def test_get_hard_difficulty(self):
        """Should return Hard when set."""
        game_state = GameState()
        game_state.difficulty = "Hard"

        difficulty = get_difficulty(game_state)
        assert difficulty == DifficultyLevel.HARD

    def test_default_to_normal(self):
        """Should default to Normal for invalid value."""
        game_state = GameState()
        game_state.difficulty = "Invalid"

        difficulty = get_difficulty(game_state)
        assert difficulty == DifficultyLevel.NORMAL


class TestGetModifierFunction:
    """Test get_modifier function."""

    def test_get_player_income_modifier(self):
        """Should return correct player income modifier."""
        game_state = GameState()
        game_state.difficulty = "Easy"

        modifier = get_modifier(game_state, "player_income")
        assert modifier == 1.30

    def test_get_ai_combat_modifier(self):
        """Should return correct AI combat modifier."""
        game_state = GameState()
        game_state.difficulty = "Very Hard"

        modifier = get_modifier(game_state, "ai_combat")
        assert modifier == 1.30

    def test_get_unknown_modifier_default(self):
        """Should return 1.0 for unknown modifier."""
        game_state = GameState()
        game_state.difficulty = "Normal"

        modifier = get_modifier(game_state, "unknown_modifier")
        assert modifier == 1.0


class TestGetAIPersonalityFunction:
    """Test get_ai_personality function."""

    def test_get_wei_personality(self):
        """Should return aggressive for Wei."""
        personality = get_ai_personality("Wei")
        assert personality == AIPersonality.AGGRESSIVE

    def test_get_shu_personality(self):
        """Should return defensive for Shu."""
        personality = get_ai_personality("Shu")
        assert personality == AIPersonality.DEFENSIVE

    def test_get_wu_personality(self):
        """Should return economic for Wu."""
        personality = get_ai_personality("Wu")
        assert personality == AIPersonality.ECONOMIC

    def test_get_unknown_faction_default(self):
        """Should return defensive for unknown faction."""
        personality = get_ai_personality("Unknown")
        assert personality == AIPersonality.DEFENSIVE


class TestGetAIActionWeight:
    """Test get_ai_action_weight function."""

    def test_wei_attack_weight(self):
        """Wei (aggressive) should have high attack weight."""
        weight = get_ai_action_weight("Wei", "attack")
        assert weight == 2.0

    def test_shu_fortify_weight(self):
        """Shu (defensive) should have high fortify weight."""
        weight = get_ai_action_weight("Shu", "fortify")
        assert weight == 2.0

    def test_wu_trade_weight(self):
        """Wu (economic) should have high trade weight."""
        weight = get_ai_action_weight("Wu", "trade")
        assert weight == 2.0

    def test_unknown_action_default(self):
        """Unknown action should return 1.0."""
        weight = get_ai_action_weight("Wei", "unknown_action")
        assert weight == 1.0


class TestApplyDifficultyToIncome:
    """Test apply_difficulty_to_income function."""

    def test_player_income_easy(self):
        """Player should get +30% income on Easy."""
        game_state = GameState()
        game_state.difficulty = "Easy"
        game_state.player_faction = "Wei"

        result = apply_difficulty_to_income(game_state, "Wei", 100)
        assert result == 130

    def test_ai_income_easy(self):
        """AI should get -20% income on Easy."""
        game_state = GameState()
        game_state.difficulty = "Easy"
        game_state.player_faction = "Wei"

        result = apply_difficulty_to_income(game_state, "Shu", 100)
        assert result == 80

    def test_ai_income_very_hard(self):
        """AI should get +50% income on Very Hard."""
        game_state = GameState()
        game_state.difficulty = "Very Hard"
        game_state.player_faction = "Wei"

        result = apply_difficulty_to_income(game_state, "Shu", 100)
        assert result == 150


class TestApplyDifficultyToCombat:
    """Test apply_difficulty_to_combat function."""

    def test_player_combat_easy(self):
        """Player should get +15% combat on Easy."""
        game_state = GameState()
        game_state.difficulty = "Easy"
        game_state.player_faction = "Wei"

        result = apply_difficulty_to_combat(game_state, "Wei", 100.0)
        assert result == pytest.approx(115.0)

    def test_ai_combat_very_hard(self):
        """AI should get +30% combat on Very Hard."""
        game_state = GameState()
        game_state.difficulty = "Very Hard"
        game_state.player_faction = "Wei"

        result = apply_difficulty_to_combat(game_state, "Shu", 100.0)
        assert result == pytest.approx(130.0)

    def test_player_combat_normal(self):
        """Player should get no modifier on Normal."""
        game_state = GameState()
        game_state.difficulty = "Normal"
        game_state.player_faction = "Wei"

        result = apply_difficulty_to_combat(game_state, "Wei", 100.0)
        assert result == pytest.approx(100.0)


class TestListDifficulties:
    """Test list_difficulties function."""

    def test_returns_all_difficulties(self):
        """Should return all 4 difficulties."""
        difficulties = list_difficulties()
        assert len(difficulties) == 4

    def test_difficulty_format(self):
        """Each difficulty should have id and name."""
        difficulties = list_difficulties()
        for d in difficulties:
            assert "id" in d
            assert "name" in d

    def test_contains_easy(self):
        """Should contain Easy difficulty."""
        difficulties = list_difficulties()
        ids = [d["id"] for d in difficulties]
        assert "Easy" in ids

    def test_contains_very_hard(self):
        """Should contain Very Hard difficulty."""
        difficulties = list_difficulties()
        ids = [d["id"] for d in difficulties]
        assert "Very Hard" in ids


class TestDifficultyScaling:
    """Test difficulty scaling across levels."""

    def test_difficulty_progression_ai_income(self):
        """AI income should increase with difficulty."""
        easy = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["ai_income"]
        normal = DIFFICULTY_MODIFIERS[DifficultyLevel.NORMAL]["ai_income"]
        hard = DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["ai_income"]
        very_hard = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["ai_income"]

        assert easy < normal < hard < very_hard

    def test_difficulty_progression_ai_combat(self):
        """AI combat should increase with difficulty."""
        easy = DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["ai_combat"]
        normal = DIFFICULTY_MODIFIERS[DifficultyLevel.NORMAL]["ai_combat"]
        hard = DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["ai_combat"]
        very_hard = DIFFICULTY_MODIFIERS[DifficultyLevel.VERY_HARD]["ai_combat"]

        assert easy < normal < hard < very_hard

    def test_player_advantage_decreases(self):
        """Player advantage should decrease with difficulty."""
        easy_adv = (
            DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["player_combat"] /
            DIFFICULTY_MODIFIERS[DifficultyLevel.EASY]["ai_combat"]
        )
        hard_adv = (
            DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["player_combat"] /
            DIFFICULTY_MODIFIERS[DifficultyLevel.HARD]["ai_combat"]
        )

        assert easy_adv > hard_adv


class TestAIDecisionQuality:
    """Test AI decision quality based on personality."""

    def test_aggressive_prioritizes_military(self):
        """Aggressive AI should prioritize military actions."""
        attack = AI_PERSONALITY_WEIGHTS[AIPersonality.AGGRESSIVE]["attack"]
        train = AI_PERSONALITY_WEIGHTS[AIPersonality.AGGRESSIVE]["train"]
        trade = AI_PERSONALITY_WEIGHTS[AIPersonality.AGGRESSIVE]["trade"]

        assert attack > trade
        assert train > trade

    def test_defensive_prioritizes_fortification(self):
        """Defensive AI should prioritize fortification."""
        fortify = AI_PERSONALITY_WEIGHTS[AIPersonality.DEFENSIVE]["fortify"]
        attack = AI_PERSONALITY_WEIGHTS[AIPersonality.DEFENSIVE]["attack"]

        assert fortify > attack

    def test_economic_prioritizes_economy(self):
        """Economic AI should prioritize economic actions."""
        trade = AI_PERSONALITY_WEIGHTS[AIPersonality.ECONOMIC]["trade"]
        farm = AI_PERSONALITY_WEIGHTS[AIPersonality.ECONOMIC]["farm"]
        attack = AI_PERSONALITY_WEIGHTS[AIPersonality.ECONOMIC]["attack"]

        assert trade > attack
        assert farm > attack

    def test_all_personalities_have_research(self):
        """All personalities should value research."""
        for personality in AIPersonality:
            weight = AI_PERSONALITY_WEIGHTS[personality]["research"]
            assert weight >= 0.8  # At least 80% priority


class TestFactionStrategyAlignment:
    """Test faction strategies align with personalities."""

    def test_wei_aggressive_strategy(self):
        """Wei's aggressive strategy should emphasize attack."""
        personality = get_ai_personality("Wei")
        attack_weight = AI_PERSONALITY_WEIGHTS[personality]["attack"]

        assert attack_weight >= 2.0

    def test_shu_defensive_strategy(self):
        """Shu's defensive strategy should emphasize fortification."""
        personality = get_ai_personality("Shu")
        fortify_weight = AI_PERSONALITY_WEIGHTS[personality]["fortify"]

        assert fortify_weight >= 2.0

    def test_wu_economic_strategy(self):
        """Wu's economic strategy should emphasize trade."""
        personality = get_ai_personality("Wu")
        trade_weight = AI_PERSONALITY_WEIGHTS[personality]["trade"]

        assert trade_weight >= 2.0
