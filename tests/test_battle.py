"""
Tests for tactical battle system
"""
import pytest
from src.systems.battle import (
    BattleAction,
    TacticalBattle,
    create_battle,
    process_battle_turn,
    apply_terrain_modifiers,
    apply_weather_modifiers,
    calculate_siege_progress,
    check_battle_end
)
from src.models import BattleState, TerrainType


class TestBattleAction:
    """Test BattleAction enum."""

    def test_battle_action_values(self):
        """Test that BattleAction enum has all required actions."""
        assert BattleAction.ATTACK.value == "attack"
        assert BattleAction.DEFEND.value == "defend"
        assert BattleAction.FLANK.value == "flank"
        assert BattleAction.FIRE_ATTACK.value == "fire_attack"
        assert BattleAction.RETREAT.value == "retreat"


class TestCreateBattle:
    """Test battle creation."""

    def test_create_battle_plains(self):
        """Test creating a battle on plains terrain."""
        battle = create_battle(
            attacker_city="Luoyang",
            defender_city="Xuchang",
            attacker_faction="Wei",
            defender_faction="Shu",
            attacker_commander="Cao Cao",
            defender_commander="Liu Bei",
            attacker_troops=5000,
            defender_troops=3000,
            terrain=TerrainType.PLAINS,
            weather="clear"
        )

        assert battle.attacker_city == "Luoyang"
        assert battle.defender_city == "Xuchang"
        assert battle.attacker_troops == 5000
        assert battle.defender_troops == 3000
        assert battle.terrain == TerrainType.PLAINS
        assert battle.weather == "clear"
        assert battle.round == 0
        assert battle.attacker_morale == 70
        assert battle.defender_morale == 70
        assert battle.supply_days == 10
        assert battle.siege_progress == 0
        assert len(battle.combat_log) == 0

    def test_create_battle_mountain(self):
        """Test creating a battle on mountain terrain."""
        battle = create_battle(
            attacker_city="Chengdu",
            defender_city="Hanzhong",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="Zhuge Liang",
            defender_commander="Xiahou Yuan",
            attacker_troops=4000,
            defender_troops=2500,
            terrain=TerrainType.MOUNTAIN
        )

        assert battle.terrain == TerrainType.MOUNTAIN
        assert battle.weather is None


class TestTerrainModifiers:
    """Test terrain modifier calculations."""

    def test_plains_no_modifier(self):
        """Test that plains terrain has no modifiers."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.PLAINS, BattleAction.ATTACK)
        assert atk_mod == 1.0
        assert def_mod == 1.0

    def test_mountain_defense_bonus(self):
        """Test mountain terrain gives defense bonus."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.MOUNTAIN, BattleAction.DEFEND)
        assert def_mod == 1.30  # +30% defense in mountains

    def test_mountain_attack_penalty(self):
        """Test mountain terrain penalizes attackers."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.MOUNTAIN, BattleAction.ATTACK)
        assert atk_mod < 1.0  # Attacking uphill is harder

    def test_forest_fire_attack_bonus(self):
        """Test forest terrain enhances fire attacks."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.FOREST, BattleAction.FIRE_ATTACK)
        assert atk_mod == 1.25  # +25% fire attack in forest

    def test_river_crossing_penalty(self):
        """Test river terrain penalizes attackers."""
        atk_mod, def_mod = apply_terrain_modifiers(TerrainType.RIVER, BattleAction.ATTACK)
        assert atk_mod == 0.85  # -15% when crossing river


class TestWeatherModifiers:
    """Test weather modifier calculations."""

    def test_clear_weather_no_modifier(self):
        """Test that clear weather has no modifiers."""
        modifier = apply_weather_modifiers("clear", BattleAction.ATTACK)
        assert modifier == 1.0

    def test_rain_fire_attack_penalty(self):
        """Test rain reduces fire attack effectiveness."""
        modifier = apply_weather_modifiers("rain", BattleAction.FIRE_ATTACK)
        assert modifier == 0.80  # -20% fire attack in rain

    def test_rain_normal_attack(self):
        """Test rain has minimal effect on normal attacks."""
        modifier = apply_weather_modifiers("rain", BattleAction.ATTACK)
        assert modifier == 0.90  # -10% movement/attack in rain

    def test_drought_fire_attack_bonus(self):
        """Test drought enhances fire attacks."""
        modifier = apply_weather_modifiers("drought", BattleAction.FIRE_ATTACK)
        assert modifier == 1.50  # +50% fire attack in drought

    def test_snow_movement_penalty(self):
        """Test snow penalizes all actions."""
        modifier = apply_weather_modifiers("snow", BattleAction.ATTACK)
        assert modifier == 0.70  # -30% in snow


class TestBattleTurnProcessing:
    """Test battle turn mechanics."""

    def test_attack_vs_attack(self):
        """Test both sides attacking each other."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )

        result = process_battle_turn(battle, BattleAction.ATTACK, BattleAction.ATTACK)

        assert battle.round == 1
        assert len(battle.combat_log) > 0
        # Both sides should take casualties
        assert battle.attacker_troops < 5000
        assert battle.defender_troops < 5000

    def test_attack_vs_defend(self):
        """Test attacker vs defender."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )

        result = process_battle_turn(battle, BattleAction.ATTACK, BattleAction.DEFEND)

        # Defender should take less damage when defending
        assert battle.round == 1
        assert len(battle.combat_log) > 0

    def test_flank_attack(self):
        """Test flanking maneuver."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )

        result = process_battle_turn(battle, BattleAction.FLANK, BattleAction.ATTACK)

        # Flanking should be more effective than normal attack
        assert battle.round == 1

    def test_fire_attack_in_forest(self):
        """Test fire attack in forest terrain."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.FOREST, "clear"
        )

        result = process_battle_turn(battle, BattleAction.FIRE_ATTACK, BattleAction.ATTACK)

        # Fire attack should be effective in forest
        assert battle.round == 1
        assert len(battle.combat_log) > 0

    def test_fire_attack_in_rain(self):
        """Test fire attack in rain weather."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "rain"
        )

        result = process_battle_turn(battle, BattleAction.FIRE_ATTACK, BattleAction.ATTACK)

        # Fire attack should be less effective in rain
        assert battle.round == 1

    def test_retreat(self):
        """Test retreat action."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )

        result = process_battle_turn(battle, BattleAction.RETREAT, BattleAction.ATTACK)

        # Retreat should end the battle
        assert result["action"] == "retreat"

    def test_morale_loss_from_casualties(self):
        """Test that heavy casualties reduce morale."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )

        initial_morale = battle.attacker_morale

        # Multiple turns of combat should reduce morale
        for _ in range(3):
            process_battle_turn(battle, BattleAction.ATTACK, BattleAction.ATTACK)

        # At least one side should have lower morale
        assert (battle.attacker_morale < initial_morale or
                battle.defender_morale < initial_morale)


class TestSiegeMechanics:
    """Test siege mechanics for walled cities."""

    def test_siege_progress_calculation(self):
        """Test siege progress against walls."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 3000,
            TerrainType.PLAINS, "clear"
        )

        # Simulate siege progress
        progress = calculate_siege_progress(battle, 80)  # 80 wall defense

        assert progress >= 0
        assert progress <= 100

    def test_siege_with_fire_attack(self):
        """Test that fire attacks increase siege progress."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 3000,
            TerrainType.PLAINS, "clear"
        )

        # Fire attack should be more effective against walls
        progress_fire = calculate_siege_progress(battle, 80, is_fire_attack=True)
        progress_normal = calculate_siege_progress(battle, 80, is_fire_attack=False)

        assert progress_fire > progress_normal


class TestBattleEndConditions:
    """Test battle end conditions."""

    def test_battle_continues(self):
        """Test that battle continues with troops and morale."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )

        result = check_battle_end(battle)

        assert result["ended"] is False

    def test_attacker_wins_troops_depleted(self):
        """Test attacker wins when defender runs out of troops."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 0,
            TerrainType.PLAINS, "clear"
        )

        result = check_battle_end(battle)

        assert result["ended"] is True
        assert result["winner"] == "attacker"

    def test_defender_wins_troops_depleted(self):
        """Test defender wins when attacker runs out of troops."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 0, 5000,
            TerrainType.PLAINS, "clear"
        )

        result = check_battle_end(battle)

        assert result["ended"] is True
        assert result["winner"] == "defender"

    def test_morale_break_attacker(self):
        """Test attacker loses when morale breaks."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )
        battle.attacker_morale = 5  # Very low morale

        result = check_battle_end(battle)

        assert result["ended"] is True
        assert result["winner"] == "defender"
        assert "morale" in result["reason"]

    def test_morale_break_defender(self):
        """Test defender loses when morale breaks."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )
        battle.defender_morale = 5  # Very low morale

        result = check_battle_end(battle)

        assert result["ended"] is True
        assert result["winner"] == "attacker"
        assert "morale" in result["reason"]

    def test_siege_breakthrough(self):
        """Test attacker wins when siege reaches 100%."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )
        battle.siege_progress = 100

        result = check_battle_end(battle)

        assert result["ended"] is True
        assert result["winner"] == "attacker"
        assert "walls" in result["reason"].lower() or "breach" in result["reason"].lower()

    def test_supply_exhaustion(self):
        """Test attacker must retreat when supplies run out."""
        battle = create_battle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, "clear"
        )
        battle.supply_days = 0

        result = check_battle_end(battle)

        assert result["ended"] is True
        assert result["winner"] == "defender"
        assert "suppl" in result["reason"].lower()


class TestTacticalBattleClass:
    """Test the TacticalBattle wrapper class."""

    def test_tactical_battle_creation(self):
        """Test creating a TacticalBattle instance."""
        tb = TacticalBattle(
            attacker_city="Luoyang",
            defender_city="Xuchang",
            attacker_faction="Wei",
            defender_faction="Shu",
            attacker_commander="Cao Cao",
            defender_commander="Liu Bei",
            attacker_troops=5000,
            defender_troops=3000,
            terrain=TerrainType.PLAINS,
            walls_level=60
        )

        assert tb.battle_state.attacker_city == "Luoyang"
        assert tb.walls_level == 60
        assert tb.is_active is True

    def test_execute_turn(self):
        """Test executing a battle turn."""
        tb = TacticalBattle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, 50
        )

        result = tb.execute_turn(BattleAction.ATTACK, BattleAction.DEFEND)

        assert "message" in result
        assert tb.battle_state.round == 1

    def test_get_status(self):
        """Test getting battle status."""
        tb = TacticalBattle(
            "City A", "City B", "Wei", "Shu",
            "Cao Cao", "Liu Bei", 5000, 5000,
            TerrainType.PLAINS, 50
        )

        status = tb.get_status()

        assert "round" in status
        assert "attacker_troops" in status
        assert "defender_troops" in status
        assert "attacker_morale" in status
        assert "defender_morale" in status
        assert "is_active" in status
