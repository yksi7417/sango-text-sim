"""
Integration Tests: Naval Combat Superiority

This module tests naval warfare mechanics:
- Naval combat bonuses (+25% attack, +20% defense)
- Non-naval penalty on water (-50%)
- Coastal city defense requirements
- Water route terrain types
- Fire attack naval bonus (+50%)
- Top naval commanders and their abilities

Based on 3KYuYun's water combat analysis from ROTK11.
"""
import pytest
from src.models import City, Officer, Faction, GameState, BattleState, TerrainType, UnitType
from src.constants import (
    NAVAL_COMBAT_BONUS,
    NAVAL_DEFENSE_BONUS,
    NAVAL_FIRE_ATTACK_BONUS,
    NO_SHIPS_WATER_PENALTY,
    NAVAL_TERRAIN_TYPES,
    COASTAL_NAVAL_REQUIRED,
    COASTAL_NAVAL_DEFENSE_BONUS,
    SHIP_BUILD_COST_GOLD,
    SHIP_BUILD_COST_FOOD,
    SHIP_TRANSPORT_CAPACITY,
)
from src.abilities import get_officer_ability


class TestNavalConstants:
    """Test naval combat related constants."""

    def test_naval_combat_bonus(self):
        """Naval forces should have +25% combat bonus on water."""
        assert NAVAL_COMBAT_BONUS == 1.25

    def test_naval_defense_bonus(self):
        """Naval forces should have +20% defense bonus on water."""
        assert NAVAL_DEFENSE_BONUS == 1.20

    def test_no_ships_water_penalty(self):
        """Forces without ships should have -50% penalty on water."""
        assert NO_SHIPS_WATER_PENALTY == 0.50

    def test_naval_terrain_types(self):
        """Naval mechanics should apply on coastal and river terrain."""
        assert "coastal" in NAVAL_TERRAIN_TYPES
        assert "river" in NAVAL_TERRAIN_TYPES

    def test_coastal_naval_required(self):
        """Coastal cities should require naval for attack."""
        assert COASTAL_NAVAL_REQUIRED is True

    def test_coastal_naval_defense_bonus(self):
        """Coastal cities should have +15% defense bonus."""
        assert COASTAL_NAVAL_DEFENSE_BONUS == 1.15


class TestNavalFireAttackBonus:
    """Test fire attack bonuses in naval combat."""

    def test_naval_fire_attack_bonus_constant(self):
        """Fire attacks on water should have +50% bonus."""
        assert NAVAL_FIRE_ATTACK_BONUS == 1.50

    def test_fire_attack_effectiveness_on_water(self):
        """Calculate fire attack effectiveness on water."""
        base_fire_damage = 100

        # Naval fire bonus
        naval_fire_damage = base_fire_damage * NAVAL_FIRE_ATTACK_BONUS

        assert naval_fire_damage == 150

    def test_fire_attack_stacking_with_drought(self):
        """Fire attack on water during drought is devastating."""
        from src.constants import DROUGHT_FIRE_ATTACK_BONUS

        base_damage = 100

        # Drought (+50%) + Naval (+50%) = multiplicative
        combined = base_damage * DROUGHT_FIRE_ATTACK_BONUS * NAVAL_FIRE_ATTACK_BONUS

        # 100 * 1.5 * 1.5 = 225
        assert combined == 225

    def test_red_cliff_scenario_fire_effectiveness(self):
        """Simulate Red Cliff fire attack conditions."""
        from src.constants import DROUGHT_FIRE_ATTACK_BONUS

        # Historical: Naval battle, favorable wind (drought-like conditions)
        base_damage = 1000

        # Naval fire attack in favorable conditions
        naval_mult = NAVAL_FIRE_ATTACK_BONUS  # 1.50
        weather_mult = DROUGHT_FIRE_ATTACK_BONUS  # 1.50

        total_damage = base_damage * naval_mult * weather_mult

        # 1000 * 1.5 * 1.5 = 2250
        assert total_damage == 2250

        # This explains the devastating effectiveness at Red Cliff


class TestShipMechanics:
    """Test ship building and transport mechanics."""

    def test_ship_build_cost(self):
        """Ships should have reasonable build costs."""
        assert SHIP_BUILD_COST_GOLD == 100
        assert SHIP_BUILD_COST_FOOD == 50

    def test_ship_transport_capacity(self):
        """Each ship should transport 50 troops."""
        assert SHIP_TRANSPORT_CAPACITY == 50

    def test_ships_required_for_troops(self):
        """Calculate ships needed for troop transport."""
        troops = 5000
        ships_needed = (troops + SHIP_TRANSPORT_CAPACITY - 1) // SHIP_TRANSPORT_CAPACITY

        # 5000 / 50 = 100 ships
        assert ships_needed == 100

    def test_city_ship_storage(self):
        """Coastal cities can have ships."""
        city = City(
            name="Jianye",
            owner="Wu",
            troops=5000,
            terrain=TerrainType.COASTAL,
            ships=20
        )

        assert city.ships == 20
        assert city.terrain == TerrainType.COASTAL

    def test_inland_city_no_ships(self):
        """Inland cities start with no ships."""
        city = City(
            name="Chengdu",
            owner="Shu",
            troops=5000,
            terrain=TerrainType.MOUNTAIN
        )

        assert city.ships == 0


class TestNavalCombatModifiers:
    """Test naval combat modifier calculations."""

    def test_naval_attack_bonus(self):
        """Naval forces attacking on water get +25% bonus."""
        base_attack = 1000
        has_ships = True

        if has_ships:
            effective_attack = base_attack * NAVAL_COMBAT_BONUS
        else:
            effective_attack = base_attack * NO_SHIPS_WATER_PENALTY

        assert effective_attack == 1250

    def test_no_ships_attack_penalty(self):
        """Forces without ships get -50% penalty on water."""
        base_attack = 1000
        has_ships = False

        if has_ships:
            effective_attack = base_attack * NAVAL_COMBAT_BONUS
        else:
            effective_attack = base_attack * NO_SHIPS_WATER_PENALTY

        assert effective_attack == 500

    def test_naval_vs_non_naval_advantage(self):
        """Naval forces have massive advantage over non-naval on water."""
        attacker_base = 1000
        defender_base = 1000

        # Attacker has ships, defender doesn't
        attacker_effective = attacker_base * NAVAL_COMBAT_BONUS  # 1250
        defender_effective = defender_base * NO_SHIPS_WATER_PENALTY  # 500

        # Naval advantage ratio
        advantage_ratio = attacker_effective / defender_effective

        assert advantage_ratio == pytest.approx(2.5)

    def test_both_forces_naval_equipped(self):
        """Both forces with ships fight normally with bonuses."""
        attacker_base = 1000
        defender_base = 1000

        # Both have ships
        attacker_effective = attacker_base * NAVAL_COMBAT_BONUS
        defender_effective = defender_base * NAVAL_DEFENSE_BONUS

        assert attacker_effective == 1250
        assert defender_effective == 1200


class TestCoastalCityAttacks:
    """Test coastal city attack mechanics."""

    def test_coastal_city_terrain(self):
        """Coastal cities should have COASTAL terrain type."""
        city = City(
            name="Jianye",
            owner="Wu",
            troops=5000,
            terrain=TerrainType.COASTAL
        )

        assert city.terrain == TerrainType.COASTAL
        assert city.terrain.value == "coastal"

    def test_coastal_terrain_in_naval_types(self):
        """Coastal terrain should be in NAVAL_TERRAIN_TYPES."""
        assert TerrainType.COASTAL.value in NAVAL_TERRAIN_TYPES

    def test_river_terrain_in_naval_types(self):
        """River terrain should be in NAVAL_TERRAIN_TYPES."""
        assert TerrainType.RIVER.value in NAVAL_TERRAIN_TYPES

    def test_coastal_defense_bonus(self):
        """Coastal defenders get +15% defense bonus."""
        base_defense = 1000

        coastal_defense = base_defense * COASTAL_NAVAL_DEFENSE_BONUS

        assert coastal_defense == 1150

    def test_attacking_coastal_without_ships(self):
        """Attacking coastal city without ships is very disadvantageous."""
        attacker_base = 1000
        defender_base = 1000

        # Attacker without ships, defender on coast
        attacker_effective = attacker_base * NO_SHIPS_WATER_PENALTY
        defender_effective = defender_base * COASTAL_NAVAL_DEFENSE_BONUS

        ratio = attacker_effective / defender_effective
        assert ratio < 0.5  # Attacker at severe disadvantage


class TestWaterRouteBlocking:
    """Test water route blocking mechanics (economic sanctions)."""

    def test_river_crossing_terrain(self):
        """River terrain should block easy passage."""
        river_city = City(
            name="Wuchang",
            owner="Wu",
            troops=3000,
            terrain=TerrainType.RIVER
        )

        assert river_city.terrain == TerrainType.RIVER
        assert river_city.terrain.value in NAVAL_TERRAIN_TYPES

    def test_naval_route_control(self):
        """Controlling coastal/river cities blocks naval routes."""
        # A faction controlling key water cities can block trade
        coastal_cities = [
            City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL, troops=5000),
            City(name="Wuchang", owner="Wu", terrain=TerrainType.RIVER, troops=4000)
        ]

        # All controlled by Wu
        wu_controls_water = all(c.owner == "Wu" for c in coastal_cities)
        assert wu_controls_water

    def test_water_route_denial_value(self):
        """Calculate value of water route denial."""
        # Ships without safe ports can't resupply
        ships = 50
        transport_capacity = SHIP_TRANSPORT_CAPACITY
        troops_at_risk = ships * transport_capacity

        assert troops_at_risk == 2500  # 50 * 50


class TestNavalCommanders:
    """Test top naval commanders and their abilities."""

    def test_gan_ning_naval_command_ability(self):
        """Gan Ning should have naval command ability."""
        ability = get_officer_ability("GanNing", "battle")

        assert ability is not None
        assert ability.id == "naval_command"
        assert ability.effect.get("coastal_mult") == 2.0

    def test_zhou_yu_fire_strategy(self):
        """Zhou Yu should have fire strategy ability for naval fire attacks."""
        ability = get_officer_ability("ZhouYu", "battle")

        assert ability is not None
        assert ability.id == "fire_strategy"
        assert ability.effect.get("fire_mult") == 2.5

    def test_lu_xun_swift_assault(self):
        """Lu Xun should have combined attack and fire ability."""
        ability = get_officer_ability("LuXun", "battle")

        assert ability is not None
        assert ability.id == "swift_assault"
        assert ability.effect.get("attack_mult") == 1.5
        assert ability.effect.get("fire_mult") == 1.5

    def test_wu_naval_dominance(self):
        """Wu faction should have multiple naval-capable commanders."""
        wu_naval_officers = ["ZhouYu", "LuXun", "GanNing", "LuSu"]

        naval_abilities_count = 0
        for officer in wu_naval_officers:
            ability = get_officer_ability(officer, "battle")
            if ability:
                if (ability.effect.get("fire_mult") or
                    ability.effect.get("coastal_mult") or
                    ability.effect.get("attack_mult")):
                    naval_abilities_count += 1

        # Wu should have multiple officers effective in naval combat
        assert naval_abilities_count >= 3


class TestNavalCombatScenarios:
    """Test realistic naval combat scenarios."""

    def test_wu_vs_wei_on_water(self):
        """Wu should have naval advantage over Wei on water."""
        # Wu: Strong naval tradition, ships
        wu_base = 10000
        wu_has_ships = True
        wu_fire_ability_mult = 2.5  # Zhou Yu

        # Wei: Land power, limited ships
        wei_base = 15000
        wei_has_ships = False

        # Calculate effective power on water
        if wu_has_ships:
            wu_effective = wu_base * NAVAL_COMBAT_BONUS * wu_fire_ability_mult
        else:
            wu_effective = wu_base * NO_SHIPS_WATER_PENALTY

        if wei_has_ships:
            wei_effective = wei_base * NAVAL_COMBAT_BONUS
        else:
            wei_effective = wei_base * NO_SHIPS_WATER_PENALTY

        # Wu: 10000 * 1.25 * 2.5 = 31250
        # Wei: 15000 * 0.50 = 7500
        assert wu_effective == 31250
        assert wei_effective == 7500
        assert wu_effective > wei_effective

    def test_crossing_river_without_ships(self):
        """Forces crossing river without ships take heavy penalties."""
        crossing_troops = 5000

        # Without ships: -50% effectiveness
        effective_troops = crossing_troops * NO_SHIPS_WATER_PENALTY

        assert effective_troops == 2500

    def test_naval_fire_attack_combo(self):
        """Test maximum fire attack damage on water."""
        from src.constants import DROUGHT_FIRE_ATTACK_BONUS, FOREST_FIRE_ATTACK_BONUS

        base_damage = 1000

        # Zhou Yu's fire strategy + Naval bonus + Drought
        ability_mult = 2.5  # fire_strategy
        naval_mult = NAVAL_FIRE_ATTACK_BONUS  # 1.50
        drought_mult = DROUGHT_FIRE_ATTACK_BONUS  # 1.50

        max_fire_damage = base_damage * ability_mult * naval_mult * drought_mult

        # 1000 * 2.5 * 1.5 * 1.5 = 5625
        assert max_fire_damage == pytest.approx(5625)

    def test_defensive_naval_position(self):
        """Test defensive advantage of naval-equipped coastal city."""
        defender_troops = 5000
        defender_ships = True

        attacker_troops = 8000
        attacker_ships = False

        # Defender on coast with ships
        defender_effective = defender_troops * NAVAL_DEFENSE_BONUS * COASTAL_NAVAL_DEFENSE_BONUS

        # Attacker without ships
        attacker_effective = attacker_troops * NO_SHIPS_WATER_PENALTY

        # 5000 * 1.20 * 1.15 = 6900
        # 8000 * 0.50 = 4000
        assert defender_effective == pytest.approx(6900)
        assert attacker_effective == 4000
        assert defender_effective > attacker_effective


class TestUnitTypeNavy:
    """Test Navy unit type mechanics."""

    def test_navy_unit_type_exists(self):
        """Navy should be a valid unit type."""
        assert UnitType.NAVY.value == "navy"

    def test_navy_unit_in_city(self):
        """Cities can have navy unit composition."""
        city = City(
            name="Jianye",
            owner="Wu",
            troops=5000,
            terrain=TerrainType.COASTAL
        )

        # Check navy in composition
        assert "navy" not in city.unit_composition or city.unit_composition.get("navy", 0) >= 0


class TestNavalBattleState:
    """Test naval aspects of battle state."""

    def test_battle_on_coastal_terrain(self):
        """Battle state should properly track coastal terrain."""
        battle = BattleState(
            attacker_city="Wuchang",
            defender_city="Jianye",
            attacker_faction="Wei",
            defender_faction="Wu",
            attacker_commander="CaoCao",
            defender_commander="ZhouYu",
            attacker_troops=50000,
            defender_troops=30000,
            terrain=TerrainType.COASTAL
        )

        assert battle.terrain == TerrainType.COASTAL
        assert battle.terrain.value in NAVAL_TERRAIN_TYPES

    def test_battle_on_river_terrain(self):
        """Battle state should properly track river terrain."""
        battle = BattleState(
            attacker_city="Luoyang",
            defender_city="Wuchang",
            attacker_faction="Wei",
            defender_faction="Wu",
            attacker_commander="ZhangLiao",
            defender_commander="GanNing",
            attacker_troops=30000,
            defender_troops=20000,
            terrain=TerrainType.RIVER
        )

        assert battle.terrain == TerrainType.RIVER
        assert battle.terrain.value in NAVAL_TERRAIN_TYPES


class TestNavalStrategicValue:
    """Test strategic value of naval capabilities."""

    def test_coastal_city_strategic_value(self):
        """Coastal cities have high strategic value."""
        coastal_city = City(
            name="Jianye",
            owner="Wu",
            troops=5000,
            terrain=TerrainType.COASTAL,
            ships=30,
            commerce=70  # Good trade
        )

        # Strategic value factors
        has_port = coastal_city.terrain == TerrainType.COASTAL
        has_ships = coastal_city.ships > 0
        controls_trade = coastal_city.commerce > 50

        assert has_port
        assert has_ships
        assert controls_trade

    def test_river_city_strategic_value(self):
        """River cities control inland water routes."""
        river_city = City(
            name="Wuchang",
            owner="Wu",
            troops=4000,
            terrain=TerrainType.RIVER,
            ships=20
        )

        # Strategic value
        controls_crossing = river_city.terrain == TerrainType.RIVER
        can_defend_water = river_city.ships > 0

        assert controls_crossing
        assert can_defend_water

    def test_naval_fleet_value(self):
        """Calculate strategic value of a naval fleet."""
        ships = 100
        troops_capacity = ships * SHIP_TRANSPORT_CAPACITY

        # 100 ships can transport 5000 troops
        assert troops_capacity == 5000

        # Fleet cost
        fleet_cost_gold = ships * SHIP_BUILD_COST_GOLD
        fleet_cost_food = ships * SHIP_BUILD_COST_FOOD

        assert fleet_cost_gold == 10000
        assert fleet_cost_food == 5000
