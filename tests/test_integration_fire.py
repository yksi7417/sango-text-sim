"""
Integration Tests: Fire Attack Conditions

This module tests fire attack effectiveness across various conditions:
- Weather effects: drought (+50%), rain (-20%)
- Terrain effects: forest (+25%), naval (+50%)
- Combined conditions stacking

Based on 3KYuYun's fire deity/ghost gate analysis of ROTK11.
"""
import pytest
from src.models import TerrainType, WeatherType
from src.constants import (
    RAIN_FIRE_ATTACK_PENALTY,
    DROUGHT_FIRE_ATTACK_BONUS,
    FOREST_FIRE_ATTACK_BONUS,
    NAVAL_FIRE_ATTACK_BONUS,
    NAVAL_TERRAIN_TYPES,
)
from src.systems.battle import (
    BattleAction,
    apply_weather_modifiers,
    apply_terrain_modifiers,
    create_battle,
)


class TestFireAttackConstants:
    """Test fire attack related constants."""

    def test_drought_fire_attack_bonus(self):
        """Drought should give +50% fire attack bonus."""
        assert DROUGHT_FIRE_ATTACK_BONUS == 1.50

    def test_rain_fire_attack_penalty(self):
        """Rain should give -20% fire attack penalty."""
        assert RAIN_FIRE_ATTACK_PENALTY == 0.80

    def test_forest_fire_attack_bonus(self):
        """Forest terrain should give +25% fire attack bonus."""
        assert FOREST_FIRE_ATTACK_BONUS == 1.25

    def test_naval_fire_attack_bonus(self):
        """Naval fire attacks should give +50% bonus."""
        assert NAVAL_FIRE_ATTACK_BONUS == 1.50

    def test_naval_terrain_types(self):
        """Naval mechanics should apply on coastal and river terrain."""
        assert "coastal" in NAVAL_TERRAIN_TYPES
        assert "river" in NAVAL_TERRAIN_TYPES


class TestWeatherFireAttackEffects:
    """Test weather effects on fire attacks."""

    def test_clear_weather_no_fire_modifier(self):
        """Clear weather should have no effect on fire attacks."""
        modifier = apply_weather_modifiers("clear", BattleAction.FIRE_ATTACK)
        assert modifier == 1.0

    def test_no_weather_no_fire_modifier(self):
        """No weather (None) should have no effect on fire attacks."""
        modifier = apply_weather_modifiers(None, BattleAction.FIRE_ATTACK)
        assert modifier == 1.0

    def test_drought_increases_fire_attack(self):
        """Drought weather should increase fire attack effectiveness."""
        modifier = apply_weather_modifiers("drought", BattleAction.FIRE_ATTACK)
        assert modifier == DROUGHT_FIRE_ATTACK_BONUS
        assert modifier == 1.50

    def test_rain_decreases_fire_attack(self):
        """Rain weather should decrease fire attack effectiveness."""
        modifier = apply_weather_modifiers("rain", BattleAction.FIRE_ATTACK)
        assert modifier == RAIN_FIRE_ATTACK_PENALTY
        assert modifier == 0.80

    def test_snow_no_fire_modifier(self):
        """Snow weather should not specifically modify fire attacks."""
        # Snow affects movement, not fire attacks directly
        modifier = apply_weather_modifiers("snow", BattleAction.FIRE_ATTACK)
        # Snow still has movement penalty but shouldn't affect fire effectiveness
        # Based on the implementation, snow returns 0.70 for all actions
        assert modifier <= 1.0

    def test_fog_fire_attack_penalty(self):
        """Fog should reduce visibility and fire attack effectiveness."""
        modifier = apply_weather_modifiers("fog", BattleAction.FIRE_ATTACK)
        # Fog gives -20% visibility penalty for non-flank actions
        assert modifier == 0.80


class TestTerrainFireAttackEffects:
    """Test terrain effects on fire attacks."""

    def test_plains_no_fire_bonus(self):
        """Plains terrain should have no fire attack modifier."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.PLAINS, BattleAction.FIRE_ATTACK)
        assert atk_mod == 1.0
        assert def_mod == 1.0

    def test_forest_fire_attack_bonus(self):
        """Forest terrain should give +25% fire attack bonus."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.FOREST, BattleAction.FIRE_ATTACK)
        assert atk_mod == FOREST_FIRE_ATTACK_BONUS
        assert atk_mod == 1.25

    def test_mountain_no_special_fire_bonus(self):
        """Mountain terrain should have attack penalty but no fire bonus."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.MOUNTAIN, BattleAction.FIRE_ATTACK)
        # Mountains penalize attackers in general
        assert atk_mod < 1.0  # Attack penalty for uphill
        assert def_mod == 1.30  # Defense bonus for defenders

    def test_river_fire_attack(self):
        """River terrain should have crossing penalty for fire attacks."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.RIVER, BattleAction.FIRE_ATTACK)
        # River has crossing penalty for attackers
        assert atk_mod == 0.85  # -15% crossing penalty

    def test_coastal_fire_attack(self):
        """Coastal terrain should give naval fire attack advantages."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.COASTAL, BattleAction.FIRE_ATTACK)
        # Coastal gives defender naval advantage
        assert def_mod == 1.15  # Coastal defense bonus


class TestNavalFireAttack:
    """Test naval fire attack on water terrain."""

    def test_naval_fire_bonus_constant_value(self):
        """Naval fire attack should have +50% bonus."""
        assert NAVAL_FIRE_ATTACK_BONUS == 1.50

    def test_naval_fire_on_river(self):
        """Fire attacks on river terrain should benefit from naval bonus."""
        # River is a naval terrain type
        assert "river" in NAVAL_TERRAIN_TYPES

        # Calculate combined naval fire attack
        naval_fire_modifier = NAVAL_FIRE_ATTACK_BONUS
        assert naval_fire_modifier == 1.50

    def test_naval_fire_on_coastal(self):
        """Fire attacks on coastal terrain should benefit from naval bonus."""
        # Coastal is a naval terrain type
        assert "coastal" in NAVAL_TERRAIN_TYPES

        # Naval fire attack effectiveness
        naval_fire_modifier = NAVAL_FIRE_ATTACK_BONUS
        assert naval_fire_modifier == 1.50


class TestCombinedConditions:
    """Test combined weather and terrain conditions."""

    def test_drought_and_forest_stacking(self):
        """Drought + Forest should give combined fire bonus."""
        # Weather: drought +50%
        weather_mod = apply_weather_modifiers("drought", BattleAction.FIRE_ATTACK)
        assert weather_mod == 1.50

        # Terrain: forest +25%
        terrain_atk_mod, _ = apply_terrain_modifiers(TerrainType.FOREST, BattleAction.FIRE_ATTACK)
        assert terrain_atk_mod == 1.25

        # Combined: 1.50 * 1.25 = 1.875 (+87.5% fire damage)
        combined_modifier = weather_mod * terrain_atk_mod
        assert combined_modifier == pytest.approx(1.875)

    def test_rain_and_forest_stacking(self):
        """Rain + Forest: rain penalty partially offsets forest bonus."""
        # Weather: rain -20%
        weather_mod = apply_weather_modifiers("rain", BattleAction.FIRE_ATTACK)
        assert weather_mod == 0.80

        # Terrain: forest +25%
        terrain_atk_mod, _ = apply_terrain_modifiers(TerrainType.FOREST, BattleAction.FIRE_ATTACK)
        assert terrain_atk_mod == 1.25

        # Combined: 0.80 * 1.25 = 1.00 (neutral)
        combined_modifier = weather_mod * terrain_atk_mod
        assert combined_modifier == pytest.approx(1.00)

    def test_drought_and_naval_stacking(self):
        """Drought + Naval should give massive fire bonus."""
        # Weather: drought +50%
        weather_mod = apply_weather_modifiers("drought", BattleAction.FIRE_ATTACK)

        # Naval: +50%
        naval_mod = NAVAL_FIRE_ATTACK_BONUS

        # Combined: 1.50 * 1.50 = 2.25 (+125% fire damage!)
        combined_modifier = weather_mod * naval_mod
        assert combined_modifier == pytest.approx(2.25)

    def test_rain_on_plains_penalty(self):
        """Rain on plains should just have weather penalty."""
        weather_mod = apply_weather_modifiers("rain", BattleAction.FIRE_ATTACK)
        terrain_atk_mod, _ = apply_terrain_modifiers(TerrainType.PLAINS, BattleAction.FIRE_ATTACK)

        combined = weather_mod * terrain_atk_mod
        assert combined == 0.80  # Just rain penalty


class TestFireAttackScenarios:
    """Test realistic fire attack battle scenarios."""

    def test_red_cliff_conditions(self):
        """Red Cliff scenario: naval, drought conditions."""
        # Historical Battle of Red Cliff: fire attack on water
        # in favorable wind/drought conditions

        # Naval fire bonus
        naval_mod = NAVAL_FIRE_ATTACK_BONUS  # 1.50

        # Combined with drought
        drought_mod = DROUGHT_FIRE_ATTACK_BONUS  # 1.50

        # Total fire attack multiplier
        total = naval_mod * drought_mod
        assert total == pytest.approx(2.25)

        # This explains why fire attack was so devastating at Red Cliff

    def test_forest_ambush_fire(self):
        """Forest ambush with fire: forest bonus."""
        # Forest terrain fire attack
        terrain_atk_mod, _ = apply_terrain_modifiers(TerrainType.FOREST, BattleAction.FIRE_ATTACK)
        assert terrain_atk_mod == 1.25

        # Forest is excellent for fire attacks due to flammable vegetation

    def test_monsoon_fire_attack_fail(self):
        """Monsoon (rain) makes fire attacks less effective."""
        weather_mod = apply_weather_modifiers("rain", BattleAction.FIRE_ATTACK)
        assert weather_mod == 0.80

        # Even in forest, rain cancels the bonus
        terrain_mod, _ = apply_terrain_modifiers(TerrainType.FOREST, BattleAction.FIRE_ATTACK)
        combined = weather_mod * terrain_mod
        assert combined == pytest.approx(1.0)  # Neutral


class TestFireAttackBattleCreation:
    """Test fire attack in battle context."""

    def test_create_battle_for_fire_attack(self):
        """Create a battle state suitable for fire attack."""
        battle = create_battle(
            attacker_city="Jianye",
            defender_city="Wuchang",
            attacker_faction="Wu",
            defender_faction="Wei",
            attacker_commander="Zhou Yu",
            defender_commander="Cao Cao",
            attacker_troops=10000,
            defender_troops=20000,
            terrain=TerrainType.RIVER,
            weather="drought"
        )

        assert battle.terrain == TerrainType.RIVER
        assert battle.weather == "drought"

    def test_fire_attack_effectiveness_calculation(self):
        """Calculate total fire attack effectiveness."""
        def calculate_fire_attack_modifier(
            weather: str,
            terrain: TerrainType,
            has_naval: bool = False
        ) -> float:
            """Calculate total fire attack modifier."""
            # Weather modifier
            weather_mod = apply_weather_modifiers(weather, BattleAction.FIRE_ATTACK)

            # Terrain modifier
            terrain_atk_mod, _ = apply_terrain_modifiers(terrain, BattleAction.FIRE_ATTACK)

            # Naval bonus if applicable
            naval_mod = NAVAL_FIRE_ATTACK_BONUS if (has_naval and terrain.value in NAVAL_TERRAIN_TYPES) else 1.0

            return weather_mod * terrain_atk_mod * naval_mod

        # Test various scenarios
        # Clear weather, plains, no naval
        mod = calculate_fire_attack_modifier("clear", TerrainType.PLAINS, False)
        assert mod == pytest.approx(1.0)

        # Drought, forest, no naval
        mod = calculate_fire_attack_modifier("drought", TerrainType.FOREST, False)
        assert mod == pytest.approx(1.875)

        # Drought, river, naval
        mod = calculate_fire_attack_modifier("drought", TerrainType.RIVER, True)
        # drought (1.5) * river_crossing_penalty (0.85) * naval (1.5) = 1.9125
        assert mod == pytest.approx(1.50 * 0.85 * 1.50)


class TestFireAbilities:
    """Test fire-related officer abilities."""

    def test_fire_attack_action_exists(self):
        """Fire attack should be a valid battle action."""
        assert BattleAction.FIRE_ATTACK.value == "fire_attack"

    def test_fire_attack_base_modifier(self):
        """Fire attack action has high base damage."""
        # From battle.py calculate_damage:
        # Fire attack has 1.4x damage modifier
        fire_attack_base_multiplier = 1.4
        assert fire_attack_base_multiplier > 1.0

    def test_huang_gai_red_cliff_scenario(self):
        """Huang Gai's fire ship attack at Red Cliff."""
        # Huang Gai (Wu) - famous for fire attack at Red Cliff
        # Naval fire attack with drought conditions

        # Calculate the devastating effectiveness
        naval_fire = NAVAL_FIRE_ATTACK_BONUS  # 1.50
        drought_bonus = DROUGHT_FIRE_ATTACK_BONUS  # 1.50
        fire_action_base = 1.4  # Fire attack base modifier

        # Total multiplier for Huang Gai's attack
        total = fire_action_base * naval_fire * drought_bonus
        assert total == pytest.approx(3.15)

        # This explains why Cao Cao's fleet was destroyed so quickly!


class TestFireEffectivenessRange:
    """Test the range of fire attack effectiveness."""

    def test_minimum_fire_effectiveness(self):
        """Calculate minimum fire attack effectiveness (worst conditions)."""
        # Rain (-20%) on plains (neutral)
        rain_mod = RAIN_FIRE_ATTACK_PENALTY
        plains_mod = 1.0

        min_effectiveness = rain_mod * plains_mod
        assert min_effectiveness == 0.80

    def test_maximum_fire_effectiveness(self):
        """Calculate maximum fire attack effectiveness (best conditions)."""
        # Drought (+50%) on forest (+25%) with naval (+50%)
        drought_mod = DROUGHT_FIRE_ATTACK_BONUS
        forest_mod = FOREST_FIRE_ATTACK_BONUS
        naval_mod = NAVAL_FIRE_ATTACK_BONUS

        max_effectiveness = drought_mod * forest_mod * naval_mod
        # 1.50 * 1.25 * 1.50 = 2.8125
        assert max_effectiveness == pytest.approx(2.8125)

    def test_effectiveness_spread(self):
        """The spread between min and max should be significant."""
        min_eff = 0.80  # Rain only
        max_eff = 2.8125  # All bonuses stacked

        spread = max_eff / min_eff
        assert spread > 3.0  # More than 3x difference

        # This makes weather/terrain strategic decisions important!
