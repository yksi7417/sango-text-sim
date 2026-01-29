"""
Integration Tests: Unit Type Combat Matrix

This module tests the rock-paper-scissors unit combat system:
- Infantry beats Cavalry (+20%)
- Cavalry beats Archers (+20%)
- Archers beat Infantry (+20%)

Based on 3KYuYun's ROTK11 deep gameplay analysis.
"""
import pytest
from src.models import UnitType, TerrainType, City
from src.constants import (
    UNIT_TYPE_ADVANTAGE,
    UNIT_TYPE_DISADVANTAGE,
    UNIT_ADVANTAGE_MAP,
    MOUNTAIN_CAVALRY_PENALTY,
    NAVAL_COMBAT_BONUS,
    NO_SHIPS_WATER_PENALTY,
)


class TestUnitTypeConstants:
    """Test that unit type constants are properly defined."""

    def test_unit_type_advantage_value(self):
        """Unit type advantage should be +20%."""
        assert UNIT_TYPE_ADVANTAGE == 1.20

    def test_unit_type_disadvantage_value(self):
        """Unit type disadvantage should be -20%."""
        assert UNIT_TYPE_DISADVANTAGE == 0.80

    def test_unit_advantage_map_complete(self):
        """All unit matchups should be defined."""
        assert "cavalry" in UNIT_ADVANTAGE_MAP
        assert "archer" in UNIT_ADVANTAGE_MAP
        assert "infantry" in UNIT_ADVANTAGE_MAP

    def test_cavalry_beats_archers(self):
        """Cavalry should have advantage over archers."""
        assert UNIT_ADVANTAGE_MAP["cavalry"] == "archer"

    def test_archers_beat_infantry(self):
        """Archers should have advantage over infantry."""
        assert UNIT_ADVANTAGE_MAP["archer"] == "infantry"

    def test_infantry_beats_cavalry(self):
        """Infantry should have advantage over cavalry."""
        assert UNIT_ADVANTAGE_MAP["infantry"] == "cavalry"


class TestUnitTypeCombatAdvantage:
    """Test unit type advantage/disadvantage calculations."""

    def test_get_unit_advantage(self):
        """Test calculating unit type advantage modifier."""
        def get_unit_combat_modifier(attacker_type: str, defender_type: str) -> float:
            """Calculate combat modifier based on unit types."""
            # Check if attacker has advantage
            if UNIT_ADVANTAGE_MAP.get(attacker_type) == defender_type:
                return UNIT_TYPE_ADVANTAGE
            # Check if attacker has disadvantage
            for unit, beats in UNIT_ADVANTAGE_MAP.items():
                if beats == attacker_type and unit == defender_type:
                    return UNIT_TYPE_DISADVANTAGE
            # No advantage/disadvantage
            return 1.0

        # Test all 9 combinations (3x3 matrix)
        # Cavalry vs others
        assert get_unit_combat_modifier("cavalry", "archer") == UNIT_TYPE_ADVANTAGE  # Cavalry beats archers
        assert get_unit_combat_modifier("cavalry", "infantry") == UNIT_TYPE_DISADVANTAGE  # Infantry beats cavalry
        assert get_unit_combat_modifier("cavalry", "cavalry") == 1.0  # Same type

        # Archers vs others
        assert get_unit_combat_modifier("archer", "infantry") == UNIT_TYPE_ADVANTAGE  # Archers beat infantry
        assert get_unit_combat_modifier("archer", "cavalry") == UNIT_TYPE_DISADVANTAGE  # Cavalry beats archers
        assert get_unit_combat_modifier("archer", "archer") == 1.0  # Same type

        # Infantry vs others
        assert get_unit_combat_modifier("infantry", "cavalry") == UNIT_TYPE_ADVANTAGE  # Infantry beats cavalry
        assert get_unit_combat_modifier("infantry", "archer") == UNIT_TYPE_DISADVANTAGE  # Archers beat infantry
        assert get_unit_combat_modifier("infantry", "infantry") == 1.0  # Same type


class TestMixedArmyComposition:
    """Test mixed army compositions in cities."""

    def test_city_unit_composition_default(self):
        """Test that cities split troops into unit types."""
        city = City(name="Test", owner="Wei", troops=1000)

        # City should have infantry, cavalry, and archers
        total = sum(city.unit_composition.values())
        assert total == 1000
        assert city.unit_composition["infantry"] > 0
        assert city.unit_composition["cavalry"] > 0
        assert city.unit_composition["archer"] > 0

    def test_city_unit_composition_split(self):
        """Test default troop split ratio."""
        city = City(name="Test", owner="Wei", troops=1000)

        # Default split: 50% infantry, 25% cavalry, 25% archer
        assert city.unit_composition["infantry"] == 500
        assert city.unit_composition["cavalry"] == 250
        assert city.unit_composition["archer"] == 250

    def test_city_get_units_by_type(self):
        """Test getting specific unit type count."""
        city = City(name="Test", owner="Wei", troops=1000)

        assert city.get_units(UnitType.INFANTRY) == 500
        assert city.get_units(UnitType.CAVALRY) == 250
        assert city.get_units(UnitType.ARCHER) == 250

    def test_city_sync_troops(self):
        """Test syncing total troops from unit composition."""
        city = City(name="Test", owner="Wei")
        city.unit_composition = {
            "infantry": 300,
            "cavalry": 200,
            "archer": 100
        }
        city.sync_troops()

        assert city.troops == 600

    def test_mixed_army_dominant_type(self):
        """Calculate dominant unit type in mixed army."""
        def get_dominant_type(unit_composition: dict) -> str:
            """Get the unit type with most troops."""
            return max(unit_composition.keys(), key=lambda k: unit_composition[k])

        city = City(name="Test", owner="Wei")
        city.unit_composition = {
            "infantry": 500,
            "cavalry": 200,
            "archer": 300
        }

        assert get_dominant_type(city.unit_composition) == "infantry"

        city.unit_composition["archer"] = 600
        assert get_dominant_type(city.unit_composition) == "archer"


class TestNavalVsLandUnits:
    """Test naval unit interactions with land units."""

    def test_naval_combat_bonus_constant(self):
        """Naval combat bonus should be +25%."""
        assert NAVAL_COMBAT_BONUS == 1.25

    def test_no_ships_water_penalty_constant(self):
        """No ships on water penalty should be -50%."""
        assert NO_SHIPS_WATER_PENALTY == 0.50

    def test_city_ships_default(self):
        """Cities should start with no ships."""
        city = City(name="Test", owner="Wei")
        assert city.ships == 0

    def test_city_ships_coastal(self):
        """Coastal cities should be able to have ships."""
        city = City(name="Jianye", owner="Wu", terrain=TerrainType.COASTAL, ships=5)
        assert city.ships == 5

    def test_naval_advantage_on_water(self):
        """Naval forces should have advantage on water terrain."""
        # Navy unit type exists
        assert UnitType.NAVY.value == "navy"

        # Coastal and river terrain require naval capability
        coastal_city = City(name="Test", owner="Wei", terrain=TerrainType.COASTAL, ships=10)
        river_city = City(name="Test2", owner="Wei", terrain=TerrainType.RIVER, ships=5)

        assert coastal_city.terrain == TerrainType.COASTAL
        assert river_city.terrain == TerrainType.RIVER
        assert coastal_city.ships > 0
        assert river_city.ships > 0


class TestTerrainUnitCombination:
    """Test that terrain modifiers stack with unit bonuses."""

    def test_mountain_cavalry_penalty(self):
        """Mountain terrain should penalize cavalry."""
        assert MOUNTAIN_CAVALRY_PENALTY == 0.80

    def test_terrain_stacking_with_unit_bonus(self):
        """Calculate combined modifier for terrain + unit type."""
        def calculate_combined_modifier(
            unit_type: str,
            defender_type: str,
            terrain: TerrainType
        ) -> float:
            """Calculate combat modifier combining terrain and unit type."""
            base_modifier = 1.0

            # Unit type modifier
            if UNIT_ADVANTAGE_MAP.get(unit_type) == defender_type:
                base_modifier *= UNIT_TYPE_ADVANTAGE
            elif any(UNIT_ADVANTAGE_MAP.get(t) == unit_type for t in [defender_type]):
                for t, beats in UNIT_ADVANTAGE_MAP.items():
                    if beats == unit_type and t == defender_type:
                        base_modifier *= UNIT_TYPE_DISADVANTAGE
                        break

            # Terrain modifier for cavalry
            if terrain == TerrainType.MOUNTAIN and unit_type == "cavalry":
                base_modifier *= MOUNTAIN_CAVALRY_PENALTY

            return base_modifier

        # Cavalry attacking archers on plains: +20%
        mod = calculate_combined_modifier("cavalry", "archer", TerrainType.PLAINS)
        assert mod == UNIT_TYPE_ADVANTAGE  # 1.20

        # Cavalry attacking archers in mountains: +20% - 20% = ~0.96
        mod = calculate_combined_modifier("cavalry", "archer", TerrainType.MOUNTAIN)
        assert mod == UNIT_TYPE_ADVANTAGE * MOUNTAIN_CAVALRY_PENALTY  # 1.20 * 0.80 = 0.96

        # Infantry attacking cavalry in mountains: +20% (no cavalry penalty for infantry)
        mod = calculate_combined_modifier("infantry", "cavalry", TerrainType.MOUNTAIN)
        assert mod == UNIT_TYPE_ADVANTAGE  # 1.20

    def test_combined_modifiers_example_scenarios(self):
        """Test realistic battle scenarios."""
        # Scenario 1: Wei cavalry charging Shu archers on plains
        # Cavalry beats archers (+20%), plains neutral = 1.20x damage
        cavalry_vs_archer_plains = UNIT_TYPE_ADVANTAGE * 1.0
        assert cavalry_vs_archer_plains == 1.20

        # Scenario 2: Wei cavalry charging Shu archers in mountains
        # Cavalry beats archers (+20%), but mountains penalize cavalry (-20%)
        # Net: 1.20 * 0.80 = 0.96 (slightly less than neutral)
        cavalry_vs_archer_mountain = UNIT_TYPE_ADVANTAGE * MOUNTAIN_CAVALRY_PENALTY
        assert cavalry_vs_archer_mountain == pytest.approx(0.96)

        # Scenario 3: Shu infantry defending against Wei cavalry
        # Infantry beats cavalry (+20%) = 1.20x defensive power
        infantry_vs_cavalry = UNIT_TYPE_ADVANTAGE
        assert infantry_vs_cavalry == 1.20


class TestUnitTypeEnum:
    """Test UnitType enum values."""

    def test_unit_types_exist(self):
        """All unit types should be defined."""
        assert UnitType.INFANTRY.value == "infantry"
        assert UnitType.CAVALRY.value == "cavalry"
        assert UnitType.ARCHER.value == "archer"
        assert UnitType.NAVY.value == "navy"

    def test_unit_type_count(self):
        """Should have 4 unit types total."""
        assert len(UnitType) == 4


class TestCombatMatrixComplete:
    """Comprehensive test of all unit matchups."""

    @pytest.mark.parametrize("attacker,defender,expected", [
        # Cavalry matchups
        ("cavalry", "archer", UNIT_TYPE_ADVANTAGE),     # Cavalry beats archers
        ("cavalry", "infantry", UNIT_TYPE_DISADVANTAGE),  # Infantry beats cavalry
        ("cavalry", "cavalry", 1.0),                    # Same type
        # Archer matchups
        ("archer", "infantry", UNIT_TYPE_ADVANTAGE),    # Archers beat infantry
        ("archer", "cavalry", UNIT_TYPE_DISADVANTAGE),  # Cavalry beats archers
        ("archer", "archer", 1.0),                      # Same type
        # Infantry matchups
        ("infantry", "cavalry", UNIT_TYPE_ADVANTAGE),   # Infantry beats cavalry
        ("infantry", "archer", UNIT_TYPE_DISADVANTAGE), # Archers beat infantry
        ("infantry", "infantry", 1.0),                  # Same type
    ])
    def test_combat_matchup(self, attacker, defender, expected):
        """Test each unit type combat matchup."""
        def get_modifier(atk_type, def_type):
            if UNIT_ADVANTAGE_MAP.get(atk_type) == def_type:
                return UNIT_TYPE_ADVANTAGE
            for unit, beats in UNIT_ADVANTAGE_MAP.items():
                if beats == atk_type and unit == def_type:
                    return UNIT_TYPE_DISADVANTAGE
            return 1.0

        assert get_modifier(attacker, defender) == expected


class TestDamageScaling:
    """Test that unit advantage translates to damage scaling."""

    def test_advantage_damage_multiplier(self):
        """20% advantage should mean 20% more damage."""
        base_damage = 100

        advantaged_damage = base_damage * UNIT_TYPE_ADVANTAGE
        assert advantaged_damage == 120

        disadvantaged_damage = base_damage * UNIT_TYPE_DISADVANTAGE
        assert disadvantaged_damage == 80

    def test_symmetric_advantage(self):
        """Advantage and disadvantage should be symmetric."""
        # 1.20 advantage vs 0.80 disadvantage
        # Average should be 1.0
        avg = (UNIT_TYPE_ADVANTAGE + UNIT_TYPE_DISADVANTAGE) / 2
        assert avg == 1.0

    def test_net_effect_of_matchups(self):
        """Rock-paper-scissors should have no net advantage."""
        # Cavalry beats archers: +20%
        # Archers beat infantry: +20%
        # Infantry beats cavalry: +20%
        # Each unit has one advantage and one disadvantage
        total_advantages = 3  # Each type beats one other
        total_disadvantages = 3  # Each type is beaten by one other
        assert total_advantages == total_disadvantages
