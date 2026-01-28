"""
Difficulty Settings System - AI bonuses and personality types.

Difficulty levels:
- Easy: Player gets bonuses, AI gets penalties
- Normal: Balanced gameplay
- Hard: AI gets bonuses
- Very Hard: Significant AI advantages

AI Personality types:
- Aggressive: Prefers military actions, attacks more often
- Defensive: Fortifies cities, builds walls, cautious
- Economic: Focuses on commerce and agriculture
"""
from enum import Enum
from typing import Dict, Any
from ..models import GameState
from i18n import i18n


class DifficultyLevel(Enum):
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"
    VERY_HARD = "Very Hard"


class AIPersonality(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    ECONOMIC = "economic"


# Difficulty modifiers: (player_modifier, ai_modifier)
# Applied to income, combat, recruitment
DIFFICULTY_MODIFIERS = {
    DifficultyLevel.EASY: {
        "player_income": 1.30,
        "player_combat": 1.15,
        "ai_income": 0.80,
        "ai_combat": 0.85,
        "ai_recruitment": 0.80,
    },
    DifficultyLevel.NORMAL: {
        "player_income": 1.00,
        "player_combat": 1.00,
        "ai_income": 1.00,
        "ai_combat": 1.00,
        "ai_recruitment": 1.00,
    },
    DifficultyLevel.HARD: {
        "player_income": 1.00,
        "player_combat": 1.00,
        "ai_income": 1.20,
        "ai_combat": 1.15,
        "ai_recruitment": 1.20,
    },
    DifficultyLevel.VERY_HARD: {
        "player_income": 0.85,
        "player_combat": 0.95,
        "ai_income": 1.50,
        "ai_combat": 1.30,
        "ai_recruitment": 1.50,
    },
}

# AI personality task preferences (weight multipliers for choosing actions)
AI_PERSONALITY_WEIGHTS = {
    AIPersonality.AGGRESSIVE: {
        "attack": 2.0,
        "train": 1.5,
        "recruit": 1.5,
        "farm": 0.7,
        "trade": 0.5,
        "fortify": 0.5,
        "research": 0.8,
    },
    AIPersonality.DEFENSIVE: {
        "attack": 0.5,
        "train": 1.2,
        "recruit": 1.0,
        "farm": 1.0,
        "trade": 0.8,
        "fortify": 2.0,
        "research": 1.5,
    },
    AIPersonality.ECONOMIC: {
        "attack": 0.5,
        "train": 0.8,
        "recruit": 0.8,
        "farm": 1.8,
        "trade": 2.0,
        "fortify": 0.8,
        "research": 1.5,
    },
}

# Default AI personalities for factions
DEFAULT_AI_PERSONALITIES = {
    "Wei": AIPersonality.AGGRESSIVE,
    "Shu": AIPersonality.DEFENSIVE,
    "Wu": AIPersonality.ECONOMIC,
}


def get_difficulty(game_state: GameState) -> DifficultyLevel:
    """Get the current difficulty level."""
    try:
        return DifficultyLevel(game_state.difficulty)
    except ValueError:
        return DifficultyLevel.NORMAL


def get_modifier(game_state: GameState, modifier_key: str) -> float:
    """
    Get a difficulty modifier value.

    Args:
        game_state: Current game state
        modifier_key: Key like 'player_income', 'ai_combat', etc.

    Returns:
        Modifier value (float multiplier)
    """
    difficulty = get_difficulty(game_state)
    return DIFFICULTY_MODIFIERS[difficulty].get(modifier_key, 1.0)


def get_ai_personality(faction_name: str) -> AIPersonality:
    """Get the AI personality for a faction."""
    return DEFAULT_AI_PERSONALITIES.get(faction_name, AIPersonality.DEFENSIVE)


def get_ai_action_weight(faction_name: str, action: str) -> float:
    """
    Get the weight for an AI action based on faction personality.

    Args:
        faction_name: Faction name
        action: Action type (attack, train, farm, etc.)

    Returns:
        Weight multiplier for the action
    """
    personality = get_ai_personality(faction_name)
    return AI_PERSONALITY_WEIGHTS[personality].get(action, 1.0)


def apply_difficulty_to_income(game_state: GameState, faction_name: str,
                                income: int) -> int:
    """Apply difficulty modifier to income."""
    if faction_name == game_state.player_faction:
        modifier = get_modifier(game_state, "player_income")
    else:
        modifier = get_modifier(game_state, "ai_income")
    return int(income * modifier)


def apply_difficulty_to_combat(game_state: GameState, faction_name: str,
                                power: float) -> float:
    """Apply difficulty modifier to combat power."""
    if faction_name == game_state.player_faction:
        modifier = get_modifier(game_state, "player_combat")
    else:
        modifier = get_modifier(game_state, "ai_combat")
    return power * modifier


def get_difficulty_description(difficulty: DifficultyLevel) -> str:
    """Get localized description for a difficulty level."""
    key = f"difficulty.{difficulty.value.lower().replace(' ', '_')}"
    return i18n.t(key, default=difficulty.value)


def list_difficulties() -> list:
    """List all available difficulty levels."""
    return [
        {"id": d.value, "name": d.value}
        for d in DifficultyLevel
    ]
