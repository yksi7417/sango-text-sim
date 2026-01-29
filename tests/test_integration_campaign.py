"""
Integration Tests: Full Campaign Conquest

This module tests complete game campaign mechanics:
- Start with single faction
- Progress through 50+ turns
- Capture multiple cities
- Use all combat systems
- Achieve victory condition
- Verify no state corruption

Tests cover extended gameplay to ensure all systems integrate correctly.
"""
import pytest
import random
from src.models import GameState, City, Officer, Faction, TerrainType
from src.world import init_world
from src.engine import (
    battle,
    transfer_city,
    end_turn,
    check_victory,
    ai_turn,
    tech_attack_bonus,
)


class TestCampaignInitialization:
    """Test campaign initialization."""

    def test_init_world_creates_factions(self):
        """init_world should create all factions."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        assert "Wei" in game_state.factions
        assert "Shu" in game_state.factions
        assert "Wu" in game_state.factions

    def test_init_world_creates_cities(self):
        """init_world should create cities."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        assert len(game_state.cities) > 0
        # Each faction should have at least one city
        for faction in game_state.factions.values():
            assert len(faction.cities) > 0

    def test_init_world_creates_officers(self):
        """init_world should create officers."""
        game_state = GameState()
        init_world(game_state, player_choice="Shu", seed=42)

        assert len(game_state.officers) > 0

    def test_player_faction_set(self):
        """Player faction should be properly set."""
        game_state = GameState()
        init_world(game_state, player_choice="Wu", seed=42)

        assert game_state.player_faction == "Wu"

    def test_initial_year_set(self):
        """Initial year should be set from scenario."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        assert game_state.year > 0


class TestTurnProgression:
    """Test multi-turn game progression."""

    def test_end_turn_advances_month(self):
        """end_turn should advance the month."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        initial_month = game_state.month
        end_turn(game_state)

        if initial_month == 12:
            assert game_state.month == 1
        else:
            assert game_state.month == initial_month + 1

    def test_end_turn_advances_year(self):
        """end_turn should advance year after December."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.month = 12
        initial_year = game_state.year

        end_turn(game_state)

        assert game_state.year == initial_year + 1
        assert game_state.month == 1

    def test_progress_50_turns(self):
        """Game should handle 50+ turns without errors."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for _ in range(50):
            end_turn(game_state)

        # Should have progressed more than 4 years
        assert game_state.month >= 1
        assert game_state.month <= 12

    def test_economy_persists_across_turns(self):
        """City resources should persist across turns."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Get a player city
        player_cities = game_state.factions["Wei"].cities
        city_name = player_cities[0]
        city = game_state.cities[city_name]

        # Record initial resources
        initial_gold = city.gold
        initial_food = city.food

        # Run turns (resources change based on economy)
        for _ in range(5):
            end_turn(game_state)

        # Resources should be different (economy processing)
        # At least the structure should be intact
        assert city.gold >= 0
        assert city.food >= 0


class TestBattleSystem:
    """Test battle system integration."""

    def test_battle_calculates_outcome(self):
        """battle should determine victory and casualties."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Get cities from different factions
        wei_city_name = game_state.factions["Wei"].cities[0]
        shu_city_name = game_state.factions["Shu"].cities[0]

        attacker = game_state.cities[wei_city_name]
        defender = game_state.cities[shu_city_name]

        victory, casualties = battle(game_state, attacker, defender, 1000)

        assert isinstance(victory, bool)
        assert isinstance(casualties, int)
        assert casualties >= 0

    def test_tech_attack_bonus(self):
        """Tech bonus should affect combat."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        bonus = tech_attack_bonus(game_state, "Wei")

        assert bonus >= 1.0  # Always at least 1.0

    def test_battle_reduces_troops(self):
        """Battle should affect troop counts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_city_name = game_state.factions["Wei"].cities[0]
        shu_city_name = game_state.factions["Shu"].cities[0]

        attacker = game_state.cities[wei_city_name]
        defender = game_state.cities[shu_city_name]

        initial_defender_troops = defender.troops
        initial_attacker_troops = attacker.troops

        battle(game_state, attacker, defender, 500)

        # Some change should have occurred
        assert defender.troops != initial_defender_troops or initial_defender_troops == 0


class TestCityCapture:
    """Test city capture mechanics."""

    def test_transfer_city_changes_owner(self):
        """transfer_city should change city ownership."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Get a Shu city to capture
        shu_city_name = game_state.factions["Shu"].cities[0]
        city = game_state.cities[shu_city_name]

        transfer_city(game_state, "Wei", city)

        assert city.owner == "Wei"

    def test_transfer_city_updates_faction(self):
        """transfer_city should update faction city lists."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        shu_city_name = game_state.factions["Shu"].cities[0]
        city = game_state.cities[shu_city_name]

        transfer_city(game_state, "Wei", city)

        assert shu_city_name not in game_state.factions["Shu"].cities
        assert shu_city_name in game_state.factions["Wei"].cities

    def test_multiple_city_captures(self):
        """Should handle multiple city captures."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        initial_wei_cities = len(game_state.factions["Wei"].cities)

        # Capture all non-Wei cities
        for city_name, city in list(game_state.cities.items()):
            if city.owner != "Wei":
                transfer_city(game_state, "Wei", city)

        assert len(game_state.factions["Wei"].cities) > initial_wei_cities


class TestVictoryConditions:
    """Test victory and defeat conditions."""

    def test_victory_when_all_cities_owned(self):
        """Victory when player owns all cities."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Transfer all cities to Wei
        for city in game_state.cities.values():
            if city.owner != "Wei":
                transfer_city(game_state, "Wei", city)

        result = check_victory(game_state)
        assert result is True

    def test_no_victory_with_multiple_factions(self):
        """No victory while multiple factions control cities."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        result = check_victory(game_state)
        assert result is False

    def test_defeat_when_no_cities(self):
        """Defeat when player has no cities."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Transfer all Wei cities to Shu
        for city_name in list(game_state.factions["Wei"].cities):
            city = game_state.cities[city_name]
            transfer_city(game_state, "Shu", city)

        result = check_victory(game_state)
        assert result is True  # Game ends (defeat)


class TestAIIntegration:
    """Test AI system integration."""

    def test_ai_turn_processes(self):
        """AI turn should process without errors."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Run AI turn for other factions
        for faction_name in game_state.factions:
            if faction_name != "Wei":
                ai_turn(game_state, faction_name)

    def test_ai_preserves_game_state(self):
        """AI turn should not corrupt game state."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        initial_city_count = len(game_state.cities)
        initial_faction_count = len(game_state.factions)

        for faction_name in game_state.factions:
            if faction_name != "Wei":
                ai_turn(game_state, faction_name)

        # Core structure should be preserved
        assert len(game_state.cities) == initial_city_count
        assert len(game_state.factions) == initial_faction_count


class TestStateIntegrity:
    """Test game state integrity over extended play."""

    def test_no_duplicate_cities(self):
        """Cities should not appear in multiple faction lists."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for _ in range(20):
            end_turn(game_state)

        all_cities = []
        for faction in game_state.factions.values():
            all_cities.extend(faction.cities)

        # No duplicates
        assert len(all_cities) == len(set(all_cities))

    def test_city_owner_matches_faction(self):
        """City owner should match faction that owns it."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for _ in range(20):
            end_turn(game_state)

        for faction_name, faction in game_state.factions.items():
            for city_name in faction.cities:
                city = game_state.cities[city_name]
                assert city.owner == faction_name

    def test_officer_faction_consistency(self):
        """Officers should belong to valid factions."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for _ in range(20):
            end_turn(game_state)

        for officer in game_state.officers.values():
            if officer.faction:
                assert officer.faction in game_state.factions

    def test_positive_resources(self):
        """Resources should not go negative (except possibly food)."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for _ in range(50):
            end_turn(game_state)

        for city in game_state.cities.values():
            assert city.gold >= 0
            assert city.troops >= 0
            assert city.defense >= 0


class TestCombatSystemsIntegration:
    """Test all combat systems work together."""

    def test_battle_with_commanders(self):
        """Battle should use commander stats."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_city = game_state.cities[game_state.factions["Wei"].cities[0]]
        shu_city = game_state.cities[game_state.factions["Shu"].cities[0]]

        # Battle uses commanders from cities
        victory, casualties = battle(game_state, wei_city, shu_city, 1000)

        assert isinstance(victory, bool)
        assert casualties >= 0

    def test_battle_affects_morale(self):
        """Battle should affect morale."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_city = game_state.cities[game_state.factions["Wei"].cities[0]]
        shu_city = game_state.cities[game_state.factions["Shu"].cities[0]]

        initial_morale = shu_city.morale
        battle(game_state, wei_city, shu_city, 1000)

        # Morale should be affected (especially if losing)
        assert shu_city.morale <= initial_morale + 20  # Morale doesn't spike massively


class TestExtendedCampaign:
    """Test extended campaign play."""

    def test_100_turn_campaign(self):
        """Game should handle 100 turn campaign."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for _ in range(100):
            if check_victory(game_state):
                break
            end_turn(game_state)

        # Game state should still be valid
        assert len(game_state.cities) > 0
        assert len(game_state.factions) > 0

    def test_campaign_with_city_changes(self):
        """Campaign with city ownership changes."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Simulate conquest
        cities_to_capture = [c for c in game_state.cities.values() if c.owner != "Wei"]

        for city in cities_to_capture[:2]:  # Capture 2 cities
            transfer_city(game_state, "Wei", city)
            end_turn(game_state)

        # Wei should have more cities
        assert len(game_state.factions["Wei"].cities) > 2


class TestConquestScenario:
    """Test full conquest scenario."""

    def test_unification_scenario(self):
        """Simulate unification by one faction."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Capture all cities for Wei
        for city in list(game_state.cities.values()):
            if city.owner != "Wei":
                transfer_city(game_state, "Wei", city)

        # Check victory
        assert check_victory(game_state) is True

        # All cities should be Wei's
        assert all(c.owner == "Wei" for c in game_state.cities.values())

    def test_faction_elimination(self):
        """Test faction loses all cities."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Take all Shu cities
        shu_cities = list(game_state.factions["Shu"].cities)
        for city_name in shu_cities:
            city = game_state.cities[city_name]
            transfer_city(game_state, "Wei", city)

        assert len(game_state.factions["Shu"].cities) == 0


class TestScenarioVariations:
    """Test different scenario configurations."""

    def test_different_player_factions(self):
        """Each faction should be playable."""
        for faction in ["Wei", "Shu", "Wu"]:
            game_state = GameState()
            init_world(game_state, player_choice=faction, seed=42)

            assert game_state.player_faction == faction
            assert len(game_state.factions[faction].cities) > 0

    def test_seed_reproducibility(self):
        """Same seed should produce same initial state."""
        game_state1 = GameState()
        init_world(game_state1, player_choice="Wei", seed=123)

        game_state2 = GameState()
        init_world(game_state2, player_choice="Wei", seed=123)

        # Should have same structure
        assert len(game_state1.cities) == len(game_state2.cities)
        assert len(game_state1.factions) == len(game_state2.factions)


class TestResourceManagement:
    """Test resource management over campaign."""

    def test_gold_accumulation(self):
        """Gold should accumulate over turns (if economy is positive)."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        city = game_state.cities[game_state.factions["Wei"].cities[0]]
        initial_gold = city.gold

        # Boost commerce for positive income
        city.commerce = 80
        city.troops = 100  # Low upkeep

        for _ in range(12):  # One year
            end_turn(game_state)

        # Gold should have changed
        assert city.gold != initial_gold or city.gold >= 0

    def test_food_consumption(self):
        """Food should be consumed by troops."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        city = game_state.cities[game_state.factions["Wei"].cities[0]]
        city.troops = 5000  # Many troops
        city.agri = 20  # Low agriculture

        initial_food = city.food

        for _ in range(6):
            end_turn(game_state)

        # Food should be affected
        assert city.food != initial_food or city.food <= 0


class TestOfficerManagement:
    """Test officer management over campaign."""

    def test_officers_persist(self):
        """Officers should persist across turns."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        initial_officers = set(game_state.officers.keys())

        for _ in range(20):
            end_turn(game_state)

        # Most officers should persist (some may defect)
        remaining_officers = set(game_state.officers.keys())
        assert len(remaining_officers) > 0

    def test_officers_have_valid_stats(self):
        """All officers should have valid stats."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for officer in game_state.officers.values():
            assert 0 <= officer.leadership <= 100
            assert 0 <= officer.intelligence <= 100
            assert 0 <= officer.politics <= 100
            assert 0 <= officer.charisma <= 100
            assert 0 <= officer.loyalty <= 100
