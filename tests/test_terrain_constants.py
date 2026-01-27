"""
Tests for terrain-related constants.
"""
import pytest
from src import constants


class TestTerrainConstants:
    """Tests for terrain effect constants."""

    def test_plains_constants_exist(self):
        """Test that plains terrain constants are defined."""
        assert hasattr(constants, 'PLAINS_COMBAT_MODIFIER')
        assert constants.PLAINS_COMBAT_MODIFIER == 1.0

    def test_mountain_constants_exist(self):
        """Test that mountain terrain constants are defined."""
        assert hasattr(constants, 'MOUNTAIN_DEFENSE_BONUS')
        assert hasattr(constants, 'MOUNTAIN_CAVALRY_PENALTY')
        assert constants.MOUNTAIN_DEFENSE_BONUS == 1.30
        assert constants.MOUNTAIN_CAVALRY_PENALTY == 0.80

    def test_forest_constants_exist(self):
        """Test that forest terrain constants are defined."""
        assert hasattr(constants, 'FOREST_AMBUSH_BONUS')
        assert hasattr(constants, 'FOREST_FIRE_ATTACK_BONUS')
        assert constants.FOREST_AMBUSH_BONUS == 1.20
        assert constants.FOREST_FIRE_ATTACK_BONUS == 1.25

    def test_coastal_constants_exist(self):
        """Test that coastal terrain constants are defined."""
        assert hasattr(constants, 'COASTAL_NAVAL_REQUIRED')
        assert hasattr(constants, 'COASTAL_NAVAL_DEFENSE_BONUS')
        assert constants.COASTAL_NAVAL_REQUIRED is True
        assert constants.COASTAL_NAVAL_DEFENSE_BONUS == 1.15

    def test_river_constants_exist(self):
        """Test that river terrain constants are defined."""
        assert hasattr(constants, 'RIVER_CROSSING_PENALTY')
        assert hasattr(constants, 'RIVER_CROSSING_ATTRITION')
        assert constants.RIVER_CROSSING_PENALTY == 0.85
        assert constants.RIVER_CROSSING_ATTRITION == 0.02

    def test_terrain_modifiers_are_numeric(self):
        """Test that all terrain modifiers are numeric values."""
        terrain_constants = [
            constants.PLAINS_COMBAT_MODIFIER,
            constants.MOUNTAIN_DEFENSE_BONUS,
            constants.MOUNTAIN_CAVALRY_PENALTY,
            constants.FOREST_AMBUSH_BONUS,
            constants.FOREST_FIRE_ATTACK_BONUS,
            constants.COASTAL_NAVAL_DEFENSE_BONUS,
            constants.RIVER_CROSSING_PENALTY,
            constants.RIVER_CROSSING_ATTRITION
        ]

        for const in terrain_constants:
            assert isinstance(const, (int, float)), f"Terrain constant {const} should be numeric"

    def test_terrain_bonuses_reasonable(self):
        """Test that terrain bonuses are in reasonable ranges."""
        # Bonuses should generally be between 0.5 and 2.0
        assert 0.5 <= constants.MOUNTAIN_DEFENSE_BONUS <= 2.0
        assert 0.5 <= constants.MOUNTAIN_CAVALRY_PENALTY <= 2.0
        assert 0.5 <= constants.FOREST_AMBUSH_BONUS <= 2.0
        assert 0.5 <= constants.FOREST_FIRE_ATTACK_BONUS <= 2.0
        assert 0.5 <= constants.COASTAL_NAVAL_DEFENSE_BONUS <= 2.0
        assert 0.5 <= constants.RIVER_CROSSING_PENALTY <= 2.0

        # Attrition should be small (< 10%)
        assert 0 <= constants.RIVER_CROSSING_ATTRITION < 0.1
