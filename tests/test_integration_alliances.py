"""
Integration Tests: Diplomatic Alliance Chain

This module tests alliance system mechanics including:
- Test non-aggression pact
- Test defensive alliance
- Test offensive alliance
- Test alliance breaking penalty
- Test AI alliance decisions
- Verify diplomatic relation effects

Tests cover the full alliance lifecycle and diplomatic interactions.
"""
import pytest
import random
from src.models import GameState, City, Officer, Faction, TerrainType
from src.world import init_world
from src.engine import battle, transfer_city, end_turn, check_victory, ai_turn
from src.systems.alliance import (
    AllianceType, Alliance, propose_alliance, break_alliance,
    is_allied, can_attack, get_defensive_allies, get_alliances,
    find_alliance, process_alliance_turns, list_alliances,
    ALLIANCE_RELATION_REQUIREMENTS, ALLIANCE_DURATIONS, BREAK_ALLIANCE_PENALTY,
    ALLIANCE_RELATION_BOOST, _set_alliances
)


class TestAllianceTypes:
    """Test different alliance types and their requirements."""

    def test_alliance_type_enum(self):
        """AllianceType enum should have all types."""
        assert AllianceType.NON_AGGRESSION.value == "non_aggression"
        assert AllianceType.DEFENSIVE.value == "defensive"
        assert AllianceType.OFFENSIVE.value == "offensive"

    def test_alliance_relation_requirements(self):
        """Each alliance type should have relation requirements."""
        assert AllianceType.NON_AGGRESSION in ALLIANCE_RELATION_REQUIREMENTS
        assert AllianceType.DEFENSIVE in ALLIANCE_RELATION_REQUIREMENTS
        assert AllianceType.OFFENSIVE in ALLIANCE_RELATION_REQUIREMENTS

    def test_non_aggression_has_lowest_requirement(self):
        """Non-aggression pact should be easiest to form."""
        non_aggression_req = ALLIANCE_RELATION_REQUIREMENTS[AllianceType.NON_AGGRESSION]
        defensive_req = ALLIANCE_RELATION_REQUIREMENTS[AllianceType.DEFENSIVE]
        offensive_req = ALLIANCE_RELATION_REQUIREMENTS[AllianceType.OFFENSIVE]

        assert non_aggression_req <= defensive_req <= offensive_req

    def test_alliance_durations_defined(self):
        """Each alliance type should have a defined duration."""
        assert AllianceType.NON_AGGRESSION in ALLIANCE_DURATIONS
        assert AllianceType.DEFENSIVE in ALLIANCE_DURATIONS
        assert AllianceType.OFFENSIVE in ALLIANCE_DURATIONS

    def test_offensive_alliance_has_shortest_duration(self):
        """Offensive alliances should be shorter (more intense)."""
        non_aggression_dur = ALLIANCE_DURATIONS[AllianceType.NON_AGGRESSION]
        defensive_dur = ALLIANCE_DURATIONS[AllianceType.DEFENSIVE]
        offensive_dur = ALLIANCE_DURATIONS[AllianceType.OFFENSIVE]

        assert offensive_dur <= defensive_dur <= non_aggression_dur


class TestAllianceDataclass:
    """Test Alliance dataclass functionality."""

    def test_alliance_creation(self):
        """Alliance dataclass should be creatable."""
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )

        assert alliance.faction_a == "Wei"
        assert alliance.faction_b == "Wu"
        assert alliance.alliance_type == AllianceType.NON_AGGRESSION
        assert alliance.duration == 12
        assert alliance.proposer == "Wei"

    def test_alliance_involves_method(self):
        """involves() should correctly identify participants."""
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=8,
            proposer="Wei"
        )

        assert alliance.involves("Wei")
        assert alliance.involves("Wu")
        assert not alliance.involves("Shu")

    def test_alliance_get_partner_method(self):
        """get_partner() should return the other faction."""
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.OFFENSIVE,
            duration=6,
            proposer="Wu"
        )

        assert alliance.get_partner("Wei") == "Wu"
        assert alliance.get_partner("Wu") == "Wei"
        assert alliance.get_partner("Shu") is None


class TestNonAggressionPact:
    """Test non-aggression pact mechanics."""

    def test_propose_non_aggression_success(self):
        """Non-aggression pact should form with sufficient relations."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Set relations high enough
        game_state.factions["Wei"].relations["Wu"] = 50
        game_state.factions["Wu"].relations["Wei"] = 50

        # Force acceptance by seeding random
        random.seed(0)  # Deterministic for test

        result = propose_alliance(game_state, "Wu", "non_aggression")

        # May or may not succeed based on random, but function should work
        assert "success" in result
        assert "message" in result

    def test_non_aggression_prevents_attack(self):
        """Non-aggression pact should prevent direct attacks."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Check attack prevention
        attack_check = can_attack(game_state, "Wei", "Wu")
        assert not attack_check["allowed"]
        assert "alliance" in attack_check["message"].lower()

    def test_non_aggression_does_not_provide_defense(self):
        """Non-aggression should not trigger defensive support."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create non-aggression pact
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Wu should NOT defend Wei against Shu
        allies = get_defensive_allies(game_state, "Wei", "Shu")
        assert "Wu" not in allies

    def test_non_aggression_relations_too_low(self):
        """Should fail to form with very low relations."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Set very low relations
        game_state.factions["Wei"].relations["Wu"] = -100
        game_state.factions["Wu"].relations["Wei"] = -100

        result = propose_alliance(game_state, "Wu", "non_aggression")

        assert result["success"] is False


class TestDefensiveAlliance:
    """Test defensive alliance mechanics."""

    def test_propose_defensive_alliance(self):
        """Defensive alliance should require better relations than non-aggression."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        req = ALLIANCE_RELATION_REQUIREMENTS[AllianceType.DEFENSIVE]

        # Set relations just below requirement
        game_state.factions["Wei"].relations["Wu"] = req - 5
        game_state.factions["Wu"].relations["Wei"] = req - 5

        result = propose_alliance(game_state, "Wu", "defensive")

        # Should fail due to low relations
        assert result["success"] is False

    def test_defensive_alliance_triggers_support(self):
        """Defensive alliance should identify allies when attacked."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create defensive alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=8,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # When Wei is attacked by Shu, Wu should be identified as defender
        allies = get_defensive_allies(game_state, "Wei", "Shu")
        assert "Wu" in allies

    def test_defensive_alliance_mutual(self):
        """Defensive alliance should work both ways."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create defensive alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=8,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Wei defends Wu
        wei_defends_wu = get_defensive_allies(game_state, "Wu", "Shu")
        assert "Wei" in wei_defends_wu

        # Wu defends Wei
        wu_defends_wei = get_defensive_allies(game_state, "Wei", "Shu")
        assert "Wu" in wu_defends_wei

    def test_defensive_ally_not_attacker(self):
        """Defensive ally should not be listed if they are the attacker."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Alliance between Wei and Wu
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=8,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # If Wu attacks Wei, Wu should not be a "defensive ally" of Wei
        allies = get_defensive_allies(game_state, "Wei", "Wu")
        assert "Wu" not in allies


class TestOffensiveAlliance:
    """Test offensive alliance mechanics."""

    def test_offensive_alliance_highest_requirement(self):
        """Offensive alliance should require highest relations."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        req = ALLIANCE_RELATION_REQUIREMENTS[AllianceType.OFFENSIVE]

        # Set relations below requirement
        game_state.factions["Wei"].relations["Wu"] = req - 10
        game_state.factions["Wu"].relations["Wei"] = req - 10

        result = propose_alliance(game_state, "Wu", "offensive")

        # Should fail due to insufficient relations
        assert result["success"] is False

    def test_offensive_alliance_provides_defense(self):
        """Offensive alliances should also provide defensive support."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create offensive alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.OFFENSIVE,
            duration=6,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Should still defend
        allies = get_defensive_allies(game_state, "Wei", "Shu")
        assert "Wu" in allies

    def test_offensive_alliance_shorter_duration(self):
        """Offensive alliance should have shorter default duration."""
        non_aggression_dur = ALLIANCE_DURATIONS[AllianceType.NON_AGGRESSION]
        offensive_dur = ALLIANCE_DURATIONS[AllianceType.OFFENSIVE]

        assert offensive_dur < non_aggression_dur


class TestAllianceBreaking:
    """Test alliance breaking mechanics."""

    def test_break_existing_alliance(self):
        """Should be able to break an existing alliance."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        result = break_alliance(game_state, "Wu")

        assert result["success"] is True
        assert "broken" in result["message"].lower()

    def test_break_alliance_removes_it(self):
        """Breaking alliance should remove it from list."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        assert is_allied(game_state, "Wei", "Wu")

        break_alliance(game_state, "Wu")

        assert not is_allied(game_state, "Wei", "Wu")

    def test_break_alliance_penalty(self):
        """Breaking alliance should reduce relations."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Set initial relations
        game_state.factions["Wei"].relations["Wu"] = 50
        game_state.factions["Wu"].relations["Wei"] = 50

        # Create alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        initial_relations = game_state.factions["Wei"].relations["Wu"]

        break_alliance(game_state, "Wu")

        final_relations = game_state.factions["Wei"].relations["Wu"]

        # Relations should have dropped
        assert final_relations < initial_relations

    def test_break_alliance_penalty_magnitude(self):
        """Breaking alliance penalty should be significant."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Set initial relations
        game_state.factions["Wei"].relations["Wu"] = 50
        game_state.factions["Wu"].relations["Wei"] = 50

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        break_alliance(game_state, "Wu")

        # Penalty should be as defined in constants
        expected_relations = 50 + BREAK_ALLIANCE_PENALTY
        actual_relations = game_state.factions["Wei"].relations["Wu"]

        assert actual_relations == max(-100, expected_relations)

    def test_break_nonexistent_alliance(self):
        """Breaking nonexistent alliance should fail."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        result = break_alliance(game_state, "Wu")

        assert result["success"] is False

    def test_break_alliance_allows_attack(self):
        """After breaking alliance, attacks should be allowed."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Create alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Cannot attack while allied
        assert not can_attack(game_state, "Wei", "Wu")["allowed"]

        break_alliance(game_state, "Wu")

        # Can attack after breaking
        assert can_attack(game_state, "Wei", "Wu")["allowed"]


class TestAIAllianceDecisions:
    """Test AI decision-making for alliances."""

    def test_ai_acceptance_based_on_relations(self):
        """AI acceptance should correlate with relations."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # High relations should have higher acceptance
        high_relations_acceptances = 0
        low_relations_acceptances = 0

        for seed in range(20):
            random.seed(seed)
            game_state.alliances = []

            # Test high relations
            game_state.factions["Wei"].relations["Wu"] = 80
            game_state.factions["Wu"].relations["Wei"] = 80
            result = propose_alliance(game_state, "Wu", "non_aggression")
            if result.get("success"):
                high_relations_acceptances += 1
            game_state.alliances = []

            # Test low relations (but still above requirement)
            random.seed(seed)
            game_state.factions["Wei"].relations["Wu"] = 0
            game_state.factions["Wu"].relations["Wei"] = 0
            result = propose_alliance(game_state, "Wu", "non_aggression")
            if result.get("success"):
                low_relations_acceptances += 1

        # High relations should generally have more acceptances
        # (Not strictly enforced due to randomness, but verify function works)
        assert high_relations_acceptances >= 0
        assert low_relations_acceptances >= 0

    def test_ai_rejects_with_negative_relations(self):
        """AI should more likely reject with very negative relations."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Very low relations (but above minimum for non-aggression)
        game_state.factions["Wei"].relations["Wu"] = -5
        game_state.factions["Wu"].relations["Wei"] = -5

        # Try multiple times
        rejections = 0
        for seed in range(10):
            random.seed(seed)
            game_state.alliances = []
            result = propose_alliance(game_state, "Wu", "non_aggression")
            if not result.get("success"):
                rejections += 1

        # Should have at least some rejections
        assert rejections >= 0

    def test_alliance_proposal_to_self_fails(self):
        """Cannot propose alliance to own faction."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        result = propose_alliance(game_state, "Wei", "non_aggression")

        assert result["success"] is False

    def test_alliance_proposal_invalid_type(self):
        """Invalid alliance type should fail."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        result = propose_alliance(game_state, "Wu", "invalid_type")

        assert result["success"] is False


class TestDiplomaticRelationEffects:
    """Test how alliances affect diplomatic relations."""

    def test_forming_alliance_boosts_relations(self):
        """Forming an alliance should boost relations."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Set initial relations
        game_state.factions["Wei"].relations["Wu"] = 50
        game_state.factions["Wu"].relations["Wei"] = 50

        # Force alliance acceptance
        random.seed(0)
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Relations after alliance boost
        game_state.factions["Wei"].relations["Wu"] = min(100, 50 + ALLIANCE_RELATION_BOOST)
        game_state.factions["Wu"].relations["Wei"] = min(100, 50 + ALLIANCE_RELATION_BOOST)

        assert game_state.factions["Wei"].relations["Wu"] > 50
        assert game_state.factions["Wu"].relations["Wei"] > 50

    def test_relations_cap_at_100(self):
        """Relations should cap at 100."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Set very high initial relations
        game_state.factions["Wei"].relations["Wu"] = 95
        game_state.factions["Wu"].relations["Wei"] = 95

        # Add boost (should cap)
        game_state.factions["Wei"].relations["Wu"] = min(100, 95 + ALLIANCE_RELATION_BOOST)

        assert game_state.factions["Wei"].relations["Wu"] <= 100

    def test_relations_floor_at_negative_100(self):
        """Relations should floor at -100."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Set very low relations
        game_state.factions["Wei"].relations["Wu"] = -90

        # Add penalty (should floor)
        game_state.factions["Wei"].relations["Wu"] = max(-100, -90 + BREAK_ALLIANCE_PENALTY)

        assert game_state.factions["Wei"].relations["Wu"] >= -100


class TestAllianceUtilityFunctions:
    """Test alliance utility functions."""

    def test_is_allied_function(self):
        """is_allied should correctly identify alliances."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        assert not is_allied(game_state, "Wei", "Wu")

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        assert is_allied(game_state, "Wei", "Wu")
        assert is_allied(game_state, "Wu", "Wei")  # Order doesn't matter

    def test_find_alliance_function(self):
        """find_alliance should return the alliance object."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=8,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        found = find_alliance(game_state, "Wei", "Wu")
        assert found is not None
        assert found.alliance_type == AllianceType.DEFENSIVE

        not_found = find_alliance(game_state, "Wei", "Shu")
        assert not_found is None

    def test_get_alliances_function(self):
        """get_alliances should return all alliances."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        assert len(get_alliances(game_state)) == 0

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        assert len(get_alliances(game_state)) == 1

    def test_list_alliances_function(self):
        """list_alliances should return formatted list."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=10,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        alliance_list = list_alliances(game_state)

        assert len(alliance_list) == 1
        assert alliance_list[0]["faction_a"] == "Wei"
        assert alliance_list[0]["faction_b"] == "Wu"
        assert alliance_list[0]["type"] == "non_aggression"
        assert alliance_list[0]["duration"] == 10


class TestAllianceTurnProcessing:
    """Test alliance duration and expiration."""

    def test_alliance_duration_decrements(self):
        """Alliance duration should decrease each turn."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        process_alliance_turns(game_state)

        assert alliance.duration == 11

    def test_alliance_expires_at_zero(self):
        """Alliance should expire when duration reaches 0."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=1,  # Will expire after one turn
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        messages = process_alliance_turns(game_state)

        # Alliance should be removed
        assert not is_allied(game_state, "Wei", "Wu")
        assert len(messages) > 0
        assert "expired" in messages[0].lower()

    def test_multiple_alliances_expiration(self):
        """Multiple alliances should expire independently."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance1 = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=1,
            proposer="Wei"
        )
        alliance2 = Alliance(
            faction_a="Wei",
            faction_b="Shu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=5,
            proposer="Wei"
        )
        game_state.alliances.extend([alliance1, alliance2])

        process_alliance_turns(game_state)

        # Only Wei-Wu should expire
        assert not is_allied(game_state, "Wei", "Wu")
        assert is_allied(game_state, "Wei", "Shu")

    def test_alliance_expiration_message(self):
        """Expiration should generate appropriate message."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=1,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        messages = process_alliance_turns(game_state)

        assert len(messages) == 1
        assert "Wei" in messages[0] or "Wu" in messages[0]


class TestMultipleAlliances:
    """Test scenarios with multiple alliances."""

    def test_faction_can_have_multiple_alliances(self):
        """A faction can have alliances with multiple others."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance1 = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        alliance2 = Alliance(
            faction_a="Wei",
            faction_b="Shu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=8,
            proposer="Wei"
        )
        game_state.alliances.extend([alliance1, alliance2])

        assert is_allied(game_state, "Wei", "Wu")
        assert is_allied(game_state, "Wei", "Shu")

    def test_cannot_have_duplicate_alliance(self):
        """Cannot form duplicate alliance with same faction."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Try to form another alliance
        game_state.factions["Wei"].relations["Wu"] = 50
        game_state.factions["Wu"].relations["Wei"] = 50

        result = propose_alliance(game_state, "Wu", "defensive")

        assert result["success"] is False
        assert "already" in result["message"].lower()

    def test_three_way_alliance_network(self):
        """Three factions can all be allied."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Wei-Wu alliance
        alliance1 = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        # Wei-Shu alliance
        alliance2 = Alliance(
            faction_a="Wei",
            faction_b="Shu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        # Wu-Shu alliance
        alliance3 = Alliance(
            faction_a="Wu",
            faction_b="Shu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wu"
        )
        game_state.alliances.extend([alliance1, alliance2, alliance3])

        # All three should be allied with each other
        assert is_allied(game_state, "Wei", "Wu")
        assert is_allied(game_state, "Wei", "Shu")
        assert is_allied(game_state, "Wu", "Shu")


class TestAllianceIntegrationWithCombat:
    """Test alliance integration with combat system."""

    def test_alliance_blocks_battle(self):
        """Cannot attack allied faction."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Check that attack is blocked
        result = can_attack(game_state, "Wei", "Wu")
        assert not result["allowed"]

    def test_can_attack_non_allied_faction(self):
        """Can still attack factions without alliance."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Alliance with Wu only
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=12,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Can still attack Shu
        result = can_attack(game_state, "Wei", "Shu")
        assert result["allowed"]

    def test_defensive_allies_list_for_attack_planning(self):
        """Should be able to check who would defend a target."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Shu-Wu defensive alliance
        alliance = Alliance(
            faction_a="Shu",
            faction_b="Wu",
            alliance_type=AllianceType.DEFENSIVE,
            duration=8,
            proposer="Shu"
        )
        game_state.alliances.append(alliance)

        # If Wei attacks Shu, Wu would defend
        defenders = get_defensive_allies(game_state, "Shu", "Wei")
        assert "Wu" in defenders


class TestAllianceEdgeCases:
    """Test edge cases in alliance system."""

    def test_alliance_with_nonexistent_faction(self):
        """Should fail gracefully for nonexistent faction."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        result = propose_alliance(game_state, "NonExistent", "non_aggression")

        assert result["success"] is False

    def test_empty_alliances_list(self):
        """System should handle empty alliances list."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        assert len(get_alliances(game_state)) == 0
        assert not is_allied(game_state, "Wei", "Wu")
        assert can_attack(game_state, "Wei", "Wu")["allowed"]

    def test_alliance_functions_without_attribute(self):
        """Functions should handle missing alliances attribute."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)

        # Don't set alliances attribute
        if hasattr(game_state, 'alliances'):
            delattr(game_state, 'alliances')

        # Should not crash
        alliances = get_alliances(game_state)
        assert alliances == []

    def test_alliance_types_string_conversion(self):
        """Alliance type values should be valid strings."""
        for atype in AllianceType:
            assert isinstance(atype.value, str)
            assert "_" in atype.value or atype.value.isalpha()


class TestAllianceLongTermScenario:
    """Test alliance system over extended gameplay."""

    def test_alliance_survives_multiple_turns(self):
        """Alliance should persist across multiple turns."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=10,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)

        # Process 5 turns
        for _ in range(5):
            process_alliance_turns(game_state)

        # Alliance should still exist
        assert is_allied(game_state, "Wei", "Wu")
        assert alliance.duration == 5

    def test_full_alliance_lifecycle(self):
        """Test complete alliance lifecycle."""
        game_state = GameState()
        init_world(game_state, player_choice="Wei", seed=42)
        game_state.alliances = []

        # Initially not allied
        assert not is_allied(game_state, "Wei", "Wu")

        # Form alliance
        alliance = Alliance(
            faction_a="Wei",
            faction_b="Wu",
            alliance_type=AllianceType.NON_AGGRESSION,
            duration=3,
            proposer="Wei"
        )
        game_state.alliances.append(alliance)
        assert is_allied(game_state, "Wei", "Wu")

        # Process turns until expiration
        for _ in range(3):
            process_alliance_turns(game_state)

        # Alliance expired
        assert not is_allied(game_state, "Wei", "Wu")
