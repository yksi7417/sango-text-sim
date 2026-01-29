"""
Integration Tests: City Defense Mechanics

This module tests defensive city mechanics:
- Wall defense bonuses
- Mountain terrain defense advantages
- Siege progress mechanics
- Supply attrition during siege
- Defender morale vs attacker
- Strong defensive position validation

Based on 3KYuYun's "easy to defend, hard to attack" city analysis from ROTK11.
"""
import pytest
from src.models import City, Officer, BattleState, TerrainType, GameState, Faction
from src.constants import (
    DEFAULT_CITY_DEFENSE,
    DEFAULT_WALLS,
    MAX_DEFENSE,
    MIN_DEFENSE,
    MOUNTAIN_DEFENSE_BONUS,
    MOUNTAIN_CAVALRY_PENALTY,
    COASTAL_NAVAL_DEFENSE_BONUS,
    WALL_DEFENSE_DIVISOR,
    ENGINEER_TRAIT_DEFENSE_BONUS,
)
from src.systems.battle import (
    create_battle,
    calculate_siege_progress,
    apply_terrain_modifiers,
    apply_weather_modifiers,
    BattleAction,
)


class TestWallDefenseBonus:
    """Test city wall defense mechanics."""

    def test_default_wall_value(self):
        """Cities should have default wall values."""
        assert DEFAULT_WALLS == 50
        assert DEFAULT_CITY_DEFENSE == 50

    def test_city_has_walls(self):
        """Cities should track wall level."""
        city = City(
            name="Luoyang",
            owner="Wei",
            troops=5000,
            walls=70
        )

        assert city.walls == 70

    def test_wall_defense_calculation(self):
        """Wall level should contribute to defense."""
        # Defense formula uses walls
        walls = 80
        base_troops = 5000

        # Wall contribution to defense (simplified)
        wall_factor = walls / WALL_DEFENSE_DIVISOR
        defensive_power = base_troops * (1 + wall_factor)

        # 5000 * (1 + 80/400) = 5000 * 1.2 = 6000
        assert defensive_power == pytest.approx(6000)

    def test_high_walls_strong_defense(self):
        """High wall cities should be significantly harder to attack."""
        troops = 5000

        # Low walls (30)
        low_wall_factor = 30 / WALL_DEFENSE_DIVISOR
        low_wall_defense = troops * (1 + low_wall_factor)

        # High walls (90)
        high_wall_factor = 90 / WALL_DEFENSE_DIVISOR
        high_wall_defense = troops * (1 + high_wall_factor)

        # High walls should provide much more defense
        assert high_wall_defense > low_wall_defense
        assert high_wall_defense / low_wall_defense > 1.1

    def test_wall_defense_range(self):
        """Wall-based defense should be within reasonable range."""
        # MIN_DEFENSE should be achievable with low walls
        # MAX_DEFENSE should require high walls
        assert MIN_DEFENSE == 40
        assert MAX_DEFENSE == 95


class TestMountainTerrainDefense:
    """Test mountain terrain defensive advantages."""

    def test_mountain_defense_bonus_constant(self):
        """Mountain terrain should give +30% defense bonus."""
        assert MOUNTAIN_DEFENSE_BONUS == 1.30

    def test_mountain_cavalry_penalty_constant(self):
        """Mountain terrain should penalize cavalry by -20%."""
        assert MOUNTAIN_CAVALRY_PENALTY == 0.80

    def test_mountain_terrain_modifiers(self):
        """Mountain terrain should boost defense significantly."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.MOUNTAIN, BattleAction.ATTACK)

        # Attackers should be penalized in mountains
        assert atk_mod < 1.0

        # Defenders should get bonus
        assert def_mod == MOUNTAIN_DEFENSE_BONUS
        assert def_mod == 1.30

    def test_mountain_city_defense_calculation(self):
        """Calculate actual defense value in mountain city."""
        base_defense = 5000

        # Mountain defense bonus
        mountain_defense = base_defense * MOUNTAIN_DEFENSE_BONUS

        assert mountain_defense == 6500

    def test_cavalry_in_mountains(self):
        """Cavalry should be severely penalized in mountains."""
        cavalry_base = 2000

        # Cavalry in mountains
        effective_cavalry = cavalry_base * MOUNTAIN_CAVALRY_PENALTY

        assert effective_cavalry == 1600
        assert effective_cavalry < cavalry_base

    def test_combined_mountain_wall_defense(self):
        """Combine mountain terrain with high walls."""
        troops = 5000
        walls = 80

        # Wall bonus
        wall_factor = walls / WALL_DEFENSE_DIVISOR  # 80/400 = 0.2
        wall_defense = troops * (1 + wall_factor)  # 6000

        # Mountain bonus
        total_defense = wall_defense * MOUNTAIN_DEFENSE_BONUS  # 7800

        assert total_defense == pytest.approx(7800)


class TestSiegeProgressMechanics:
    """Test siege progress and breakthrough mechanics."""

    def test_siege_progress_starts_at_zero(self):
        """New battles should start with 0 siege progress."""
        battle = create_battle(
            attacker_city="Chengdu",
            defender_city="Hanzhong",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="XuChu",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.MOUNTAIN
        )

        assert battle.siege_progress == 0

    def test_siege_progress_calculation(self):
        """Test siege progress formula."""
        battle = BattleState(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="CaoRen",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS
        )

        # Calculate siege progress
        walls = 50
        progress = calculate_siege_progress(battle, walls, is_fire_attack=False)

        # Progress should be positive
        assert progress >= 0

    def test_siege_progress_affected_by_walls(self):
        """Higher walls should slow siege progress."""
        battle = BattleState(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="CaoRen",
            attacker_troops=15000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS
        )

        # Low walls
        low_wall_progress = calculate_siege_progress(battle, 30, is_fire_attack=False)

        # High walls
        high_wall_progress = calculate_siege_progress(battle, 90, is_fire_attack=False)

        # Low walls should be faster to breach
        assert low_wall_progress > high_wall_progress

    def test_siege_progress_fire_attack_bonus(self):
        """Fire attacks should accelerate siege progress."""
        battle = BattleState(
            attacker_city="Jianye",
            defender_city="Wuchang",
            attacker_faction="Wu",
            defender_faction="Wei",
            attacker_commander="ZhouYu",
            defender_commander="CaoRen",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS
        )

        # Normal attack
        normal_progress = calculate_siege_progress(battle, 50, is_fire_attack=False)

        # Fire attack
        fire_progress = calculate_siege_progress(battle, 50, is_fire_attack=True)

        # Fire should be faster
        assert fire_progress >= normal_progress

    def test_siege_breakthrough_at_100(self):
        """Siege should succeed when progress reaches 100."""
        battle = BattleState(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="CaoRen",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS,
            siege_progress=100
        )

        # At 100%, walls are breached
        assert battle.siege_progress >= 100


class TestSupplyAttritionDuringSiege:
    """Test supply mechanics during siege warfare."""

    def test_battle_has_supply_days(self):
        """Battles should track supply days."""
        battle = BattleState(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="CaoRen",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS,
            supply_days=10
        )

        assert battle.supply_days == 10

    def test_default_supply_days(self):
        """Default supply should be 10 days."""
        battle = create_battle(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="CaoRen",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS
        )

        assert battle.supply_days == 10

    def test_supply_attrition_concept(self):
        """Running out of supply should cause attrition."""
        initial_troops = 10000
        supply_days = 0

        # Out of supply = attrition
        if supply_days <= 0:
            attrition_rate = 0.10  # 10% attrition per turn
            troops_lost = int(initial_troops * attrition_rate)
            remaining_troops = initial_troops - troops_lost

            assert remaining_troops == 9000

    def test_extended_siege_supply_drain(self):
        """Extended sieges should drain supply."""
        initial_supply = 10
        turns = 5

        # Supply decreases each turn
        supply_per_turn = 1
        remaining_supply = initial_supply - (turns * supply_per_turn)

        assert remaining_supply == 5

    def test_low_supply_forces_retreat(self):
        """Very low supply should encourage retreat."""
        supply_days = 2
        should_consider_retreat = supply_days <= 3

        assert should_consider_retreat is True


class TestDefenderMoraleVsAttacker:
    """Test morale differences between attackers and defenders."""

    def test_battle_tracks_morale(self):
        """Battles should track morale for both sides."""
        battle = BattleState(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="CaoRen",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS,
            attacker_morale=70,
            defender_morale=80
        )

        assert battle.attacker_morale == 70
        assert battle.defender_morale == 80

    def test_default_morale_values(self):
        """Default morale should be 70 for both."""
        battle = create_battle(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="CaoRen",
            attacker_troops=10000,
            defender_troops=5000,
            terrain=TerrainType.PLAINS
        )

        assert battle.attacker_morale == 70
        assert battle.defender_morale == 70

    def test_morale_affects_combat_power(self):
        """Higher morale should increase combat effectiveness."""
        base_power = 1000

        low_morale = 40
        high_morale = 90

        # Morale factor (simplified)
        low_morale_power = base_power * (low_morale / 100)
        high_morale_power = base_power * (high_morale / 100)

        assert high_morale_power > low_morale_power
        assert high_morale_power == 900
        assert low_morale_power == 400

    def test_defender_home_advantage_morale(self):
        """Defenders should have morale advantage on home turf."""
        # Defending home city morale boost concept
        base_morale = 70
        home_defense_bonus = 10

        defender_morale = min(100, base_morale + home_defense_bonus)
        attacker_morale = base_morale

        assert defender_morale > attacker_morale

    def test_low_morale_rout(self):
        """Very low morale should cause rout."""
        morale = 15
        rout_threshold = 20

        should_rout = morale < rout_threshold
        assert should_rout is True


class TestStrongDefensivePositions:
    """Test identification and value of strong defensive positions."""

    def test_mountain_city_is_strong(self):
        """Mountain cities should be strong defensive positions."""
        city = City(
            name="Hanzhong",
            owner="Shu",
            troops=5000,
            terrain=TerrainType.MOUNTAIN,
            walls=70,
            defense=80
        )

        assert city.terrain == TerrainType.MOUNTAIN
        assert city.defense >= 70

    def test_high_wall_city_is_strong(self):
        """High wall cities should be strong defensive positions."""
        city = City(
            name="Luoyang",
            owner="Wei",
            troops=5000,
            walls=90,
            defense=85
        )

        assert city.walls >= 80
        assert city.defense >= 80

    def test_defensive_position_value(self):
        """Calculate defensive value of a position."""
        def calculate_defensive_value(city: City) -> float:
            """Calculate total defensive value."""
            base = city.defense

            # Terrain bonus
            if city.terrain == TerrainType.MOUNTAIN:
                base *= MOUNTAIN_DEFENSE_BONUS
            elif city.terrain == TerrainType.COASTAL:
                base *= COASTAL_NAVAL_DEFENSE_BONUS

            # Wall bonus
            wall_bonus = city.walls / WALL_DEFENSE_DIVISOR
            base *= (1 + wall_bonus)

            return base

        # Mountain city with high walls
        strong_city = City(
            name="Hanzhong",
            owner="Shu",
            troops=5000,
            terrain=TerrainType.MOUNTAIN,
            walls=80,
            defense=70
        )

        # Plains city with low walls
        weak_city = City(
            name="OpenPlains",
            owner="Shu",
            troops=5000,
            terrain=TerrainType.PLAINS,
            walls=30,
            defense=50
        )

        strong_value = calculate_defensive_value(strong_city)
        weak_value = calculate_defensive_value(weak_city)

        # Strong position should be significantly better
        assert strong_value > weak_value
        assert strong_value / weak_value > 1.5

    def test_chokepoint_cities(self):
        """Cities at chokepoints should control strategic routes."""
        # Hanzhong controls access to Shu
        hanzhong = City(
            name="Hanzhong",
            owner="Shu",
            troops=5000,
            terrain=TerrainType.MOUNTAIN,
            walls=75
        )

        # Is a strategic chokepoint
        is_chokepoint = hanzhong.terrain == TerrainType.MOUNTAIN
        has_strong_walls = hanzhong.walls >= 70

        assert is_chokepoint
        assert has_strong_walls


class TestDefenseInBattleScenarios:
    """Test defense mechanics in realistic battle scenarios."""

    def test_siege_of_mountain_fortress(self):
        """Test siege difficulty against mountain fortress."""
        battle = BattleState(
            attacker_city="Xuchang",
            defender_city="Hanzhong",
            attacker_faction="Wei",
            defender_faction="Shu",
            attacker_commander="CaoCao",
            defender_commander="ZhaoYun",
            attacker_troops=50000,
            defender_troops=10000,
            terrain=TerrainType.MOUNTAIN,
            attacker_morale=70,
            defender_morale=80
        )

        # Despite 5:1 numerical advantage, terrain helps defender
        _, def_mod = apply_terrain_modifiers(TerrainType.MOUNTAIN, BattleAction.ATTACK)

        # Defender gets +30% bonus
        effective_defender_troops = battle.defender_troops * def_mod

        assert effective_defender_troops == 13000
        assert battle.attacker_troops / effective_defender_troops < 4  # Reduced ratio

    def test_coastal_city_defense(self):
        """Test coastal city defense requirements."""
        battle = BattleState(
            attacker_city="Luoyang",
            defender_city="Jianye",
            attacker_faction="Wei",
            defender_faction="Wu",
            attacker_commander="ZhangLiao",
            defender_commander="ZhouYu",
            attacker_troops=30000,
            defender_troops=20000,
            terrain=TerrainType.COASTAL
        )

        # Coastal terrain
        assert battle.terrain == TerrainType.COASTAL

        # Coastal defense bonus
        assert COASTAL_NAVAL_DEFENSE_BONUS == 1.15

    def test_prolonged_siege_defender_advantage(self):
        """Defenders should have advantage in prolonged sieges."""
        # Initial state
        attacker_supply = 10
        attacker_morale = 70
        defender_morale = 80

        # After 8 turns of siege
        turns = 8
        attacker_supply_remaining = attacker_supply - turns  # 2 days left

        # Attacker morale drops due to supply concerns
        supply_morale_penalty = (10 - attacker_supply_remaining) * 2  # 16 morale lost
        attacker_morale_after = max(20, attacker_morale - supply_morale_penalty)

        # Defender maintains morale (home advantage)
        defender_morale_after = min(100, defender_morale + 5)  # Slight boost

        assert attacker_supply_remaining <= 3
        assert attacker_morale_after < defender_morale_after

    def test_engineer_officer_siege_advantage(self):
        """Officers with Engineer trait should boost siege capabilities."""
        # Engineer trait bonus for defense building
        engineer_defense_bonus = ENGINEER_TRAIT_DEFENSE_BONUS

        assert engineer_defense_bonus == 1.08

        # Engineer officer defending
        base_defense = 100
        with_engineer = base_defense * engineer_defense_bonus

        assert with_engineer == 108


class TestDefenseConstants:
    """Test defense-related constants are properly defined."""

    def test_defense_range_constants(self):
        """Defense should be bounded by min and max."""
        assert MIN_DEFENSE == 40
        assert MAX_DEFENSE == 95
        assert MIN_DEFENSE < MAX_DEFENSE

    def test_wall_defense_divisor(self):
        """Wall defense divisor should be reasonable."""
        assert WALL_DEFENSE_DIVISOR == 400

    def test_terrain_defense_bonuses(self):
        """Terrain defense bonuses should be significant."""
        # Mountain: +30%
        assert MOUNTAIN_DEFENSE_BONUS == 1.30

        # Coastal: +15%
        assert COASTAL_NAVAL_DEFENSE_BONUS == 1.15

    def test_cavalry_penalty_in_mountains(self):
        """Cavalry should be penalized in mountains."""
        assert MOUNTAIN_CAVALRY_PENALTY == 0.80
        assert MOUNTAIN_CAVALRY_PENALTY < 1.0


class TestDefenseVsAttackRatios:
    """Test defender effectiveness at various force ratios."""

    def test_equal_forces_defender_advantage(self):
        """With equal forces, defender should have advantage."""
        attacker_troops = 10000
        defender_troops = 10000

        # Defender on plains with moderate walls
        wall_bonus = 50 / WALL_DEFENSE_DIVISOR  # 0.125
        defender_effective = defender_troops * (1 + wall_bonus)  # 11250

        # Defender has advantage even on plains
        assert defender_effective > attacker_troops

    def test_3_to_1_ratio_recommended(self):
        """3:1 ratio should be minimum for successful assault."""
        defender_troops = 5000
        defender_walls = 60
        terrain = TerrainType.PLAINS

        # Defender effective strength
        wall_bonus = defender_walls / WALL_DEFENSE_DIVISOR
        defender_effective = defender_troops * (1 + wall_bonus)  # 5750

        # Need 3x to have good chance
        recommended_attackers = defender_effective * 3

        assert recommended_attackers >= 17000

    def test_mountain_requires_5_to_1(self):
        """Mountain cities may require 5:1 or more."""
        defender_troops = 5000
        defender_walls = 70

        # Mountain defense
        wall_bonus = defender_walls / WALL_DEFENSE_DIVISOR  # 0.175
        base_defense = defender_troops * (1 + wall_bonus)  # 5875
        mountain_defense = base_defense * MOUNTAIN_DEFENSE_BONUS  # 7637.5

        # Against mountain fortress
        recommended_attackers = mountain_defense * 5

        assert recommended_attackers >= 35000
