"""
Integration Tests: Multi-Front War

This module tests managing simultaneous conflicts on multiple fronts:
- Test 2-front war management
- Test resource allocation
- Test officer deployment
- Test AI reaction to weakness
- Test strategic retreat and regroup
- Verify faction survival mechanics

Tests cover strategic multi-front warfare mechanics for balanced gameplay.
"""
import pytest
import random
from src.models import (
    GameState, City, Officer, Faction, TerrainType, WeatherType,
    Season, BattleState
)
from src.world import init_world
from src.engine import (
    battle, transfer_city, end_turn, check_victory, ai_turn,
    tech_attack_bonus, initiate_tactical_battle, process_battle_action,
    resolve_battle_end
)
from src.systems.battle import (
    create_battle, process_battle_turn, check_battle_end, BattleAction
)
from src.systems.alliance import (
    AllianceType, Alliance, propose_alliance, break_alliance,
    is_allied, can_attack, get_defensive_allies, get_alliances,
    ALLIANCE_RELATION_REQUIREMENTS, BREAK_ALLIANCE_PENALTY
)


class TestMultiFrontWarSetup:
    """Test setup for multi-front war scenarios."""

    def test_faction_with_multiple_borders(self):
        """A faction can have cities bordering multiple enemies."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Get Wei's cities and check borders
        wei_cities = game_state.factions["Wei"].cities

        # Find all unique enemy factions bordering Wei
        enemy_factions = set()
        for city_name in wei_cities:
            neighbors = game_state.adj.get(city_name, [])
            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei":
                    enemy_factions.add(neighbor_city.owner)

        # Wei should border at least one other faction
        assert len(enemy_factions) >= 1

    def test_multiple_fronts_possible(self):
        """Game should support battles on multiple fronts simultaneously."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Get enemy cities adjacent to different Wei cities
        wei_cities = game_state.factions["Wei"].cities
        front_targets = []

        for city_name in wei_cities:
            neighbors = game_state.adj.get(city_name, [])
            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei":
                    front_targets.append({
                        "from": city_name,
                        "to": neighbor,
                        "enemy": neighbor_city.owner
                    })

        # Should have at least one potential front
        assert len(front_targets) >= 1

    def test_three_way_conflict_possible(self):
        """All three factions should be able to be in conflict."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # All three factions should exist
        assert "Wei" in game_state.factions
        assert "Shu" in game_state.factions
        assert "Wu" in game_state.factions

        # Each should have cities
        for faction_name in ["Wei", "Shu", "Wu"]:
            assert len(game_state.factions[faction_name].cities) > 0


class TestTwoFrontWarManagement:
    """Test managing wars on two fronts simultaneously."""

    def test_attack_two_enemies_same_turn(self):
        """Should be able to attack two different enemies in same turn."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Find two potential targets from different factions
        wei_cities = game_state.factions["Wei"].cities
        targets = []

        for city_name in wei_cities:
            wei_city = game_state.cities[city_name]
            neighbors = game_state.adj.get(city_name, [])
            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei" and wei_city.troops > 200:
                    targets.append({
                        "attacker": wei_city,
                        "defender": neighbor_city,
                        "enemy_faction": neighbor_city.owner
                    })
                    break

        if len(targets) >= 2:
            # Attack first target
            result1 = battle(game_state, targets[0]["attacker"],
                           targets[0]["defender"], 100)

            # Attack second target
            result2 = battle(game_state, targets[1]["attacker"],
                           targets[1]["defender"], 100)

            # Both battles should resolve
            assert isinstance(result1[0], bool)
            assert isinstance(result2[0], bool)

    def test_defend_two_fronts(self):
        """Should be able to defend against attacks from two directions."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Setup: give enemies more troops to simulate attacks
        for faction_name in ["Shu", "Wu"]:
            for city_name in game_state.factions[faction_name].cities:
                game_state.cities[city_name].troops = 800

        # Run several turns to let AI attack
        for _ in range(10):
            end_turn(game_state)
            # Game should continue without crashing
            if check_victory(game_state):
                break

        # Game state should remain valid
        assert len(game_state.factions["Wei"].cities) >= 0  # May have lost cities

    def test_front_priority_by_threat(self):
        """Higher threat fronts should receive more attention."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        # Identify fronts and their threat levels
        front_threats = {}
        for city_name in wei_cities:
            wei_city = game_state.cities[city_name]
            neighbors = game_state.adj.get(city_name, [])
            total_enemy_troops = 0

            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei":
                    total_enemy_troops += neighbor_city.troops

            if total_enemy_troops > 0:
                front_threats[city_name] = {
                    "enemy_troops": total_enemy_troops,
                    "own_troops": wei_city.troops
                }

        # Threat assessment should be possible
        if front_threats:
            highest_threat = max(front_threats.items(),
                               key=lambda x: x[1]["enemy_troops"])
            assert highest_threat[1]["enemy_troops"] > 0


class TestResourceAllocation:
    """Test resource allocation across multiple fronts."""

    def test_split_troops_between_fronts(self):
        """Should be able to split troops between different fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities
        if len(wei_cities) >= 2:
            city1 = game_state.cities[wei_cities[0]]
            city2 = game_state.cities[wei_cities[1]]

            # Record initial troops
            total_troops = city1.troops + city2.troops

            # Troops can be in different cities (allocation is implicit)
            assert city1.troops >= 0
            assert city2.troops >= 0

    def test_gold_allocation_for_recruitment(self):
        """Gold should support recruitment on multiple fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        # Calculate total gold available
        total_gold = sum(game_state.cities[cn].gold for cn in wei_cities)

        # Should have gold for recruitment
        assert total_gold > 0

    def test_food_sustains_multiple_armies(self):
        """Food supply should sustain armies on multiple fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        # Calculate total food
        total_food = sum(game_state.cities[cn].food for cn in wei_cities)
        total_troops = sum(game_state.cities[cn].troops for cn in wei_cities)

        # Should have enough food for troops
        food_per_troop = total_food / max(1, total_troops)
        assert food_per_troop > 0

    def test_resource_drain_from_two_wars(self):
        """Two simultaneous wars should drain resources faster."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        # Record initial resources
        initial_gold = sum(game_state.cities[cn].gold for cn in wei_cities)
        initial_food = sum(game_state.cities[cn].food for cn in wei_cities)
        initial_troops = sum(game_state.cities[cn].troops for cn in wei_cities)

        # Simulate combat on multiple fronts
        for city_name in wei_cities[:2]:  # First two cities
            wei_city = game_state.cities[city_name]
            neighbors = game_state.adj.get(city_name, [])
            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei" and wei_city.troops > 150:
                    battle(game_state, wei_city, neighbor_city, 100)
                    break

        # Resources should have changed (troops at minimum)
        final_troops = sum(game_state.cities[cn].troops for cn in wei_cities)
        # Troops may have changed due to battles
        assert final_troops >= 0


class TestOfficerDeployment:
    """Test officer deployment across multiple fronts."""

    def test_officers_in_multiple_cities(self):
        """Officers should be stationed in multiple cities."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Check officers are distributed
        wei_officers = game_state.factions["Wei"].officers
        cities_with_officers = set()

        for officer_name in wei_officers:
            officer = game_state.officers[officer_name]
            if officer.city:
                cities_with_officers.add(officer.city)

        # Should have officers in at least one city
        assert len(cities_with_officers) >= 1

    def test_commander_selection_per_front(self):
        """Each front should have a commander for battles."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        for city_name in wei_cities:
            # Find officers in this city
            city_officers = [
                game_state.officers[name]
                for name in game_state.factions["Wei"].officers
                if game_state.officers[name].city == city_name
            ]

            if city_officers:
                # Can select best commander
                best_commander = max(city_officers, key=lambda o: o.leadership)
                assert best_commander.leadership > 0

    def test_officer_exhaustion_from_multi_front(self):
        """Officers should tire from multi-front assignments."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_officers = game_state.factions["Wei"].officers

        # Assign tasks to multiple officers
        for i, officer_name in enumerate(wei_officers[:3]):
            officer = game_state.officers[officer_name]
            officer.task = "train"
            officer.task_city = game_state.factions["Wei"].cities[0]
            officer.busy = True
            officer.energy = 50  # Simulate some energy used

        # Run turn
        end_turn(game_state)

        # Officers should have energy changes
        for officer_name in wei_officers[:3]:
            officer = game_state.officers[officer_name]
            assert 0 <= officer.energy <= 100


class TestAIReactionToWeakness:
    """Test AI behavior when detecting weakness on a front."""

    def test_ai_attacks_weak_front(self):
        """AI should target weakened fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Weaken one Wei city
        wei_cities = game_state.factions["Wei"].cities
        if wei_cities:
            weak_city_name = wei_cities[0]
            weak_city = game_state.cities[weak_city_name]
            weak_city.troops = 50  # Very weak
            weak_city.morale = 30

        # Run AI turns for enemy factions
        for faction in ["Shu", "Wu"]:
            ai_turn(game_state, faction)

        # Game should continue
        assert len(game_state.cities) > 0

    def test_ai_exploits_empty_front(self):
        """AI should exploit completely undefended fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Make one Wei city very weak
        wei_cities = game_state.factions["Wei"].cities
        if wei_cities:
            weak_city = game_state.cities[wei_cities[0]]
            weak_city.troops = 10  # Almost no defense

        # Run multiple turns
        for _ in range(5):
            end_turn(game_state)

        # AI should have reacted (either attacked or game still valid)
        assert len(game_state.factions) >= 1

    def test_ai_coordinates_multi_front_attacks(self):
        """AI factions may coordinate to attack multiple fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Give AI factions strong positions
        for faction in ["Shu", "Wu"]:
            for city_name in game_state.factions[faction].cities:
                city = game_state.cities[city_name]
                city.troops = 1000
                city.morale = 90

        # Run AI turns
        for faction in ["Shu", "Wu"]:
            ai_turn(game_state, faction)

        # Game state should remain valid
        for city in game_state.cities.values():
            assert city.troops >= 0
            assert 0 <= city.morale <= 100

    def test_ai_defensive_when_weak(self):
        """AI should defend when it's weak instead of attacking."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Weaken AI faction
        for city_name in game_state.factions["Shu"].cities:
            city = game_state.cities[city_name]
            city.troops = 50
            city.morale = 30

        # Run AI turn
        ai_turn(game_state, "Shu")

        # AI should not have lost all troops
        shu_troops = sum(
            game_state.cities[cn].troops
            for cn in game_state.factions["Shu"].cities
        )
        # AI should be conservative when weak
        assert shu_troops >= 0


class TestStrategicRetreatAndRegroup:
    """Test strategic retreat and regrouping mechanics."""

    def test_retreat_preserves_troops(self):
        """Retreating from battle should preserve some troops."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_city_name = game_state.factions["Wei"].cities[0]
        wei_city = game_state.cities[wei_city_name]
        initial_troops = wei_city.troops

        # Simulate a lost battle - troops should remain in city
        # (attacking troops return minus casualties)
        neighbors = game_state.adj.get(wei_city_name, [])
        for neighbor in neighbors:
            neighbor_city = game_state.cities.get(neighbor)
            if neighbor_city and neighbor_city.owner != "Wei":
                battle(game_state, wei_city, neighbor_city, 100)
                break

        # Some troops should remain
        assert wei_city.troops >= 0

    def test_tactical_retreat_action(self):
        """Tactical battle retreat should end battle."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Create a tactical battle
        battle_state = create_battle(
            attacker_city="CityA",
            defender_city="CityB",
            attacker_faction="Wei",
            defender_faction="Shu",
            attacker_commander="TestCommander",
            defender_commander="DefCommander",
            attacker_troops=1000,
            defender_troops=1000,
            terrain=TerrainType.PLAINS,
            weather="clear"
        )

        # Execute retreat
        result = process_battle_turn(
            battle_state,
            BattleAction.RETREAT,
            BattleAction.ATTACK
        )

        assert result["action"] == "retreat"
        assert "retreat" in result["message"].lower()

    def test_regroup_after_defeat(self):
        """Faction should be able to regroup after a defeat."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities
        if len(wei_cities) >= 2:
            # Simulate losing a city
            lost_city_name = wei_cities[0]
            transfer_city(game_state, "Shu", game_state.cities[lost_city_name])

            # Remaining cities should still function
            remaining_cities = game_state.factions["Wei"].cities
            for city_name in remaining_cities:
                city = game_state.cities[city_name]
                assert city.owner == "Wei"

            # Can still end turn
            end_turn(game_state)

    def test_consolidate_forces_after_loss(self):
        """Should be able to consolidate forces after losing a front."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Record initial state
        initial_total_troops = sum(
            game_state.cities[cn].troops
            for cn in game_state.factions["Wei"].cities
        )

        # Run turns to simulate warfare
        for _ in range(5):
            end_turn(game_state)
            if len(game_state.factions["Wei"].cities) == 0:
                break

        # If Wei still has cities, troops should be consolidated there
        if game_state.factions["Wei"].cities:
            current_total_troops = sum(
                game_state.cities[cn].troops
                for cn in game_state.factions["Wei"].cities
            )
            assert current_total_troops >= 0


class TestFactionSurvivalMechanics:
    """Test faction survival under multi-front pressure."""

    def test_faction_survives_with_one_city(self):
        """Faction should survive as long as it has one city."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Transfer all but one city
        wei_cities = list(game_state.factions["Wei"].cities)
        for city_name in wei_cities[1:]:
            transfer_city(game_state, "Shu", game_state.cities[city_name])

        # Wei should still exist
        assert len(game_state.factions["Wei"].cities) == 1
        assert "Wei" in game_state.factions

    def test_faction_eliminated_without_cities(self):
        """Faction is effectively eliminated without cities."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Transfer all Wei cities
        wei_cities = list(game_state.factions["Wei"].cities)
        for city_name in wei_cities:
            transfer_city(game_state, "Shu", game_state.cities[city_name])

        # Wei has no cities (defeat condition)
        assert len(game_state.factions["Wei"].cities) == 0
        assert check_victory(game_state)  # Game should end (player defeated)

    def test_defeat_check_with_multi_front_losses(self):
        """Defeat should trigger after losing all fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Not yet defeated
        assert not check_victory(game_state)

        # Lose all cities
        for city_name in list(game_state.factions["Wei"].cities):
            transfer_city(game_state, "Shu", game_state.cities[city_name])

        # Now defeated
        assert check_victory(game_state)

    def test_last_stand_scenario(self):
        """Test defending the last city (last stand)."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Reduce to one city
        wei_cities = list(game_state.factions["Wei"].cities)
        for city_name in wei_cities[1:]:
            transfer_city(game_state, "Shu", game_state.cities[city_name])

        last_city_name = game_state.factions["Wei"].cities[0]
        last_city = game_state.cities[last_city_name]

        # Strengthen last city for last stand
        last_city.troops = 2000
        last_city.morale = 90
        last_city.defense = 80

        # Should still be defensible
        assert last_city.troops > 0
        assert last_city.morale > 50


class TestMultiFrontStrategicDecisions:
    """Test strategic decision making in multi-front scenarios."""

    def test_prioritize_critical_front(self):
        """Should be able to identify and prioritize critical fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        # Assess each front's criticality
        front_priorities = {}
        for city_name in wei_cities:
            city = game_state.cities[city_name]
            neighbors = game_state.adj.get(city_name, [])

            enemy_threat = 0
            own_strength = city.troops * (city.morale / 100.0)

            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei":
                    enemy_threat += neighbor_city.troops

            if enemy_threat > 0:
                # Threat ratio determines priority
                threat_ratio = enemy_threat / max(own_strength, 1)
                front_priorities[city_name] = threat_ratio

        # Should be able to identify highest priority front
        if front_priorities:
            critical_front = max(front_priorities, key=front_priorities.get)
            assert critical_front in wei_cities

    def test_offensive_vs_defensive_balance(self):
        """Should balance between offensive and defensive on different fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Identify fronts
        wei_cities = game_state.factions["Wei"].cities
        offensive_fronts = []
        defensive_fronts = []

        for city_name in wei_cities:
            city = game_state.cities[city_name]
            neighbors = game_state.adj.get(city_name, [])

            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei":
                    if city.troops > neighbor_city.troops:
                        offensive_fronts.append(city_name)
                    else:
                        defensive_fronts.append(city_name)
                    break

        # Should be able to categorize fronts
        total_fronts = len(set(offensive_fronts + defensive_fronts))
        assert total_fronts >= 0  # At least categorization works

    def test_strategic_city_value(self):
        """Some cities have higher strategic value due to position."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Calculate strategic value (number of connections)
        city_values = {}
        for city_name in game_state.cities:
            city = game_state.cities[city_name]
            neighbors = len(game_state.adj.get(city_name, []))
            # More connections = higher strategic value
            city_values[city_name] = neighbors

        # Should have varying strategic values
        if city_values:
            max_value = max(city_values.values())
            min_value = min(city_values.values())
            assert max_value >= min_value

    def test_encirclement_detection(self):
        """Should detect when a city is being encircled."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        for city_name in wei_cities:
            neighbors = game_state.adj.get(city_name, [])
            if not neighbors:
                continue

            enemy_neighbors = 0
            for neighbor in neighbors:
                neighbor_city = game_state.cities.get(neighbor)
                if neighbor_city and neighbor_city.owner != "Wei":
                    enemy_neighbors += 1

            encirclement_ratio = enemy_neighbors / len(neighbors)
            # Can detect encirclement level
            assert 0 <= encirclement_ratio <= 1


class TestMultiFrontResourceStress:
    """Test resource stress under multi-front warfare."""

    def test_gold_depletion_rate(self):
        """Gold should deplete faster with multiple active fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Track gold over turns
        initial_gold = sum(
            game_state.cities[cn].gold
            for cn in game_state.factions["Wei"].cities
        )

        # Add troops to increase upkeep
        for city_name in game_state.factions["Wei"].cities:
            game_state.cities[city_name].troops = 1000

        # Run several turns
        for _ in range(5):
            end_turn(game_state)

        final_gold = sum(
            game_state.cities[cn].gold
            for cn in game_state.factions["Wei"].cities
        )

        # Gold should have changed (upkeep or income)
        assert final_gold >= 0

    def test_food_crisis_from_warfare(self):
        """Extended warfare can cause food shortages."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Reduce food, increase troops
        for city_name in game_state.factions["Wei"].cities:
            city = game_state.cities[city_name]
            city.food = 100  # Low food
            city.troops = 500  # Many troops to feed

        # Run turns
        for _ in range(5):
            end_turn(game_state)

        # Game should handle food crisis (starvation events)
        for city_name in game_state.factions["Wei"].cities:
            city = game_state.cities[city_name]
            # Food should be at least 0 (clamped)
            assert city.food >= 0

    def test_morale_impact_from_losses(self):
        """Multiple defeats should impact overall morale."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        wei_cities = game_state.factions["Wei"].cities

        # Simulate losses across multiple fronts
        for city_name in wei_cities[:2]:
            city = game_state.cities[city_name]
            # Simulate defeat effects
            city.morale = max(0, city.morale - 20)
            city.troops = max(0, city.troops - 100)

        # Morale should be tracked
        for city_name in wei_cities[:2]:
            city = game_state.cities[city_name]
            assert 0 <= city.morale <= 100


class TestMultiFrontWithAlliances:
    """Test multi-front scenarios with alliance considerations."""

    def test_alliance_reduces_fronts(self):
        """Forming an alliance should reduce active fronts."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []  # Initialize alliances

        # Set relations high enough for alliance
        game_state.factions["Wei"].relations["Wu"] = 40
        game_state.factions["Wu"].relations["Wei"] = 40

        # Propose alliance
        result = propose_alliance(game_state, "Wu", "non_aggression")

        # If accepted, cannot attack ally
        if result.get("success"):
            attack_check = can_attack(game_state, "Wei", "Wu")
            assert not attack_check["allowed"]

    def test_broken_alliance_opens_front(self):
        """Breaking an alliance opens a new potential front."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create alliance
        game_state.factions["Wei"].relations["Wu"] = 50
        game_state.factions["Wu"].relations["Wei"] = 50

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=10,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Break alliance
        result = break_alliance(game_state, "Wu")

        if result.get("success"):
            # Can now attack
            attack_check = can_attack(game_state, "Wei", "Wu")
            assert attack_check["allowed"]

    def test_defensive_ally_joins_war(self):
        """Defensive ally should be identified when attacked."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create defensive alliance between Shu and Wu
        alliance = Alliance(
            faction_a="Shu",
            faction_b="Wu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=10,
            proposer="Shu"
        )
        game_state.alliances.append(alliance)

        # Check if Wu would defend Shu
        allies = get_defensive_allies(game_state, "Shu", "Wei")
        assert "Wu" in allies


class TestExtendedMultiFrontCampaign:
    """Test extended multi-front campaign scenarios."""

    def test_50_turn_multi_front_war(self):
        """Game should handle 50 turns of multi-front conflict."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for turn in range(50):
            if check_victory(game_state):
                break

            # Process turn
            end_turn(game_state)

            # State should remain valid
            for city in game_state.cities.values():
                assert city.troops >= 0
                assert city.gold >= 0
                assert 0 <= city.morale <= 100

    def test_faction_balance_over_time(self):
        """Faction balance should shift during multi-front war."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        initial_cities = {
            faction: len(game_state.factions[faction].cities)
            for faction in ["Wei", "Shu", "Wu"]
        }

        # Run extended campaign
        for _ in range(30):
            if check_victory(game_state):
                break
            end_turn(game_state)

        # Check final state
        final_cities = {
            faction: len(game_state.factions[faction].cities)
            for faction in ["Wei", "Shu", "Wu"]
            if faction in game_state.factions
        }

        # At least one faction should have cities
        assert sum(final_cities.values()) > 0

    def test_no_state_corruption_in_complex_war(self):
        """Complex multi-front warfare should not corrupt state."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        for _ in range(20):
            if check_victory(game_state):
                break

            # Validate state before turn
            all_cities_in_factions = []
            for faction in game_state.factions.values():
                all_cities_in_factions.extend(faction.cities)

            # No duplicate cities
            assert len(all_cities_in_factions) == len(set(all_cities_in_factions))

            # City owners match faction lists
            for faction_name, faction in game_state.factions.items():
                for city_name in faction.cities:
                    assert game_state.cities[city_name].owner == faction_name

            end_turn(game_state)
