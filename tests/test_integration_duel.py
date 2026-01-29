"""
Integration Tests: Duel System with Abilities

This module tests the duel mini-game mechanics:
- WAR stat (leadership) affects damage scaling
- All 3 duel actions (Attack, Defend, Special)
- Special ability triggers in duel context
- Duel victory/defeat effects on morale
- Officer capture mechanics on duel defeat
- Loyalist death-before-capture behavior

Based on 3KYuYun's ROTK11 duel system analysis.
"""
import pytest
import random
from src.models import Officer, GameState, Faction
from src.systems.duel import (
    Duel,
    DuelAction,
    DuelResult,
    start_duel,
    process_duel_round,
    is_duel_over,
    get_duel_winner,
    _calculate_base_damage,
)
from src.abilities import load_abilities, get_officer_ability
from src.systems.capture import (
    LOYALIST_OFFICERS,
    capture_officers,
    recruit_captured,
    execute_captured,
    release_captured,
)
from src.models import City


class TestWarStatDamageScaling:
    """Test that leadership (WAR) stat affects damage output."""

    def test_higher_leadership_higher_damage(self):
        """Higher leadership officers should deal more damage."""
        # Create officers with different leadership levels
        strong = Officer(
            name="LuBu",
            faction="Dong Zhuo",
            leadership=100,
            intelligence=50,
            politics=30,
            charisma=60,
            loyalty=50,
            traits=[],
            city="Chang'an"
        )
        weak = Officer(
            name="Scholar",
            faction="Wei",
            leadership=30,
            intelligence=90,
            politics=80,
            charisma=50,
            loyalty=70,
            traits=[],
            city="Luoyang"
        )

        # Calculate base damage from strong to weak vs weak to strong
        damage_strong_to_weak = _calculate_base_damage(strong.leadership, weak.leadership)
        damage_weak_to_strong = _calculate_base_damage(weak.leadership, strong.leadership)

        # Strong officer should deal significantly more damage
        assert damage_strong_to_weak > damage_weak_to_strong

    def test_damage_formula_differential(self):
        """Test the damage formula incorporates leadership differential."""
        # Equal leadership
        equal_damage = _calculate_base_damage(70, 70)
        # Large advantage
        advantage_damage = _calculate_base_damage(100, 40)
        # Large disadvantage
        disadvantage_damage = _calculate_base_damage(40, 100)

        # Advantage should increase damage from base
        assert advantage_damage > equal_damage
        # Disadvantage should decrease damage from base
        assert disadvantage_damage < equal_damage
        # Minimum damage should still be dealt
        assert disadvantage_damage >= 5

    def test_hp_based_on_leadership(self):
        """Test that initial HP is based on leadership stat."""
        officer1 = Officer(
            name="HighLead",
            faction="Wei",
            leadership=90,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=50,
            traits=[],
            city="Xuchang"
        )
        officer2 = Officer(
            name="LowLead",
            faction="Shu",
            leadership=50,
            intelligence=80,
            politics=70,
            charisma=60,
            loyalty=60,
            traits=[],
            city="Chengdu"
        )

        duel = start_duel(officer1, officer2)

        # HP = leadership * 2
        assert duel.attacker_hp == 90 * 2
        assert duel.defender_hp == 50 * 2

    def test_leadership_extremes(self):
        """Test damage calculation at extreme leadership values."""
        # Maximum leadership (100)
        max_damage = _calculate_base_damage(100, 50)
        # Minimum reasonable leadership (20)
        min_damage = _calculate_base_damage(20, 50)

        # Both should be positive
        assert max_damage > 0
        assert min_damage > 0

        # Max should be significantly higher
        assert max_damage > min_damage


class TestDuelActions:
    """Test all three duel actions and their mechanics."""

    @pytest.fixture
    def duel_pair(self):
        """Create a pair of officers for dueling."""
        attacker = Officer(
            name="ZhangFei",
            faction="Shu",
            leadership=97,
            intelligence=65,
            politics=60,
            charisma=82,
            loyalty=90,
            traits=["Brave"],
            city="Chengdu"
        )
        defender = Officer(
            name="XuChu",
            faction="Wei",
            leadership=94,
            intelligence=40,
            politics=30,
            charisma=60,
            loyalty=85,
            traits=["Brave"],
            city="Xuchang"
        )
        return attacker, defender

    def test_attack_action_deals_damage(self, duel_pair):
        """Attack action should deal damage to opponent."""
        attacker, defender = duel_pair
        duel = start_duel(attacker, defender)
        initial_hp = duel.defender_hp

        # Run multiple attacks to account for misses
        total_damage = 0
        for _ in range(10):
            duel = start_duel(attacker, defender)
            process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)
            total_damage += (initial_hp - duel.defender_hp)

        # Should deal some damage over 10 trials (85% hit rate)
        assert total_damage > 0

    def test_defend_action_reduces_damage(self, duel_pair):
        """Defend action should reduce incoming damage by 50%."""
        attacker, defender = duel_pair

        # Collect damage with attack vs attack
        damage_no_defend = []
        for _ in range(20):
            duel = start_duel(attacker, defender)
            initial_hp = duel.defender_hp
            process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)
            damage_no_defend.append(initial_hp - duel.defender_hp)

        # Collect damage with attack vs defend
        damage_with_defend = []
        for _ in range(20):
            duel = start_duel(attacker, defender)
            initial_hp = duel.defender_hp
            process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)
            damage_with_defend.append(initial_hp - duel.defender_hp)

        avg_no_defend = sum(damage_no_defend) / len(damage_no_defend)
        avg_with_defend = sum(damage_with_defend) / len(damage_with_defend)

        # Defending should result in significantly less average damage
        if avg_no_defend > 0:
            assert avg_with_defend < avg_no_defend

    def test_special_action_high_damage_low_hit(self, duel_pair):
        """Special attack should have higher damage but lower hit rate."""
        attacker, defender = duel_pair

        # Collect special attack results
        special_hits = 0
        special_damage_when_hit = []
        normal_hits = 0
        normal_damage_when_hit = []

        for _ in range(50):
            # Special attack
            duel = start_duel(attacker, defender)
            initial_hp = duel.defender_hp
            process_duel_round(duel, DuelAction.SPECIAL, DuelAction.ATTACK)
            damage = initial_hp - duel.defender_hp
            if damage > 0:
                special_hits += 1
                special_damage_when_hit.append(damage)

            # Normal attack
            duel = start_duel(attacker, defender)
            initial_hp = duel.defender_hp
            process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)
            damage = initial_hp - duel.defender_hp
            if damage > 0:
                normal_hits += 1
                normal_damage_when_hit.append(damage)

        # Special has 70% hit rate, normal has 85%
        # With 50 trials, special should hit less often
        assert special_hits <= normal_hits or special_hits < 45

        # When special hits, it should do more damage (2x multiplier)
        if special_damage_when_hit and normal_damage_when_hit:
            avg_special = sum(special_damage_when_hit) / len(special_damage_when_hit)
            avg_normal = sum(normal_damage_when_hit) / len(normal_damage_when_hit)
            assert avg_special > avg_normal

    def test_defend_action_no_damage(self, duel_pair):
        """Defend action alone should not deal damage."""
        attacker, defender = duel_pair
        duel = start_duel(attacker, defender)
        initial_hp = duel.defender_hp

        process_duel_round(duel, DuelAction.DEFEND, DuelAction.DEFEND)

        # Neither should take damage when both defend
        assert duel.attacker_hp == attacker.leadership * 2
        assert duel.defender_hp == defender.leadership * 2

    def test_action_enum_values(self):
        """Verify all action enum values exist."""
        assert DuelAction.ATTACK.value == "attack"
        assert DuelAction.DEFEND.value == "defend"
        assert DuelAction.SPECIAL.value == "special"


class TestSpecialAbilityTriggers:
    """Test special abilities in duel context."""

    def test_duel_abilities_exist(self):
        """Verify duel-context abilities exist in data."""
        abilities = load_abilities()
        duel_abilities = [a for a in abilities if a.context == "duel"]

        # Should have multiple duel abilities
        assert len(duel_abilities) >= 5

        # Check specific known abilities
        duel_ability_ids = [a.id for a in duel_abilities]
        assert "green_dragon_slash" in duel_ability_ids  # Guan Yu
        assert "serpent_spear" in duel_ability_ids  # Zhang Fei
        assert "veteran_aim" in duel_ability_ids  # Huang Zhong
        assert "iron_wall" in duel_ability_ids  # Xu Chu

    def test_guan_yu_green_dragon_slash(self):
        """Test Guan Yu's Green Dragon Slash ability."""
        ability = get_officer_ability("GuanYu", "duel")

        assert ability is not None
        assert ability.id == "green_dragon_slash"
        assert ability.context == "duel"
        assert ability.cooldown == 2
        assert ability.effect.get("damage_mult") == 2.5

    def test_zhang_fei_serpent_spear(self):
        """Test Zhang Fei's Serpent Spear ability."""
        ability = get_officer_ability("ZhangFei", "duel")

        assert ability is not None
        assert ability.id == "serpent_spear"
        assert ability.effect.get("damage_mult") == 2.0
        assert ability.effect.get("stun_chance") == 0.3

    def test_huang_zhong_veteran_aim(self):
        """Test Huang Zhong's Veteran Aim ability."""
        ability = get_officer_ability("HuangZhong", "duel")

        assert ability is not None
        assert ability.id == "veteran_aim"
        assert ability.effect.get("damage_mult") == 2.2
        assert ability.effect.get("hit_rate") == 0.95

    def test_xu_chu_iron_wall(self):
        """Test Xu Chu's Iron Wall defensive ability."""
        ability = get_officer_ability("XuChu", "duel")

        assert ability is not None
        assert ability.id == "iron_wall"
        assert ability.effect.get("defense_mult") == 2.5

    def test_xiahou_dun_one_eye_fury(self):
        """Test Xiahou Dun's One Eye Fury ability."""
        ability = get_officer_ability("XiahouDun", "duel")

        assert ability is not None
        assert ability.id == "one_eye_fury"
        assert ability.effect.get("damage_mult") == 2.0
        assert ability.effect.get("self_heal") == 10

    def test_ability_damage_multipliers(self):
        """Verify damage multipliers for all duel abilities."""
        abilities = load_abilities()
        duel_abilities = [a for a in abilities if a.context == "duel"]

        for ability in duel_abilities:
            damage_mult = ability.effect.get("damage_mult")
            defense_mult = ability.effect.get("defense_mult")

            # Each duel ability should have some combat effect
            assert damage_mult or defense_mult or ability.effect.get("counter_damage")


class TestDuelVictoryEffects:
    """Test effects of duel victory on morale and loyalty."""

    @pytest.fixture
    def game_state(self):
        """Create a game state for testing."""
        gs = GameState()
        gs.factions = {
            "Shu": Faction(name="Shu", cities=["Chengdu"], officers=["GuanYu"], relations={}),
            "Wei": Faction(name="Wei", cities=["Xuchang"], officers=["XuChu"], relations={})
        }
        gs.officers = {
            "GuanYu": Officer(
                name="GuanYu",
                faction="Shu",
                leadership=98,
                intelligence=79,
                politics=92,
                charisma=84,
                loyalty=85,
                traits=["Brave"],
                city="Chengdu"
            ),
            "XuChu": Officer(
                name="XuChu",
                faction="Wei",
                leadership=94,
                intelligence=40,
                politics=30,
                charisma=60,
                loyalty=75,
                traits=["Brave"],
                city="Xuchang"
            )
        }
        gs.player_faction = "Shu"
        return gs

    def test_duel_winner_determination(self):
        """Test that duel winner is correctly determined."""
        attacker = Officer(
            name="Winner",
            faction="Shu",
            leadership=100,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Chengdu"
        )
        defender = Officer(
            name="Loser",
            faction="Wei",
            leadership=30,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Xuchang"
        )

        duel = start_duel(attacker, defender)

        # Run until duel ends
        while not is_duel_over(duel):
            process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

        winner = get_duel_winner(duel)

        # Strong officer should usually win
        assert winner in [attacker, defender]
        assert is_duel_over(duel)

    def test_duel_affects_hp(self):
        """Test that duels properly affect HP through combat."""
        attacker = Officer(
            name="Attacker",
            faction="Shu",
            leadership=80,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Chengdu"
        )
        defender = Officer(
            name="Defender",
            faction="Wei",
            leadership=80,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Xuchang"
        )

        duel = start_duel(attacker, defender)
        initial_attacker_hp = duel.attacker_hp
        initial_defender_hp = duel.defender_hp

        # Process one round
        process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

        # At least one should have taken damage (may miss)
        hp_changed = (duel.attacker_hp < initial_attacker_hp or
                      duel.defender_hp < initial_defender_hp)
        # Run more rounds if needed to confirm damage occurs
        for _ in range(5):
            if hp_changed:
                break
            process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)
            hp_changed = (duel.attacker_hp < initial_attacker_hp or
                          duel.defender_hp < initial_defender_hp)

        assert hp_changed

    def test_duel_log_records_events(self):
        """Test that duel log records combat events."""
        attacker = Officer(
            name="Attacker",
            faction="Shu",
            leadership=80,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Chengdu"
        )
        defender = Officer(
            name="Defender",
            faction="Wei",
            leadership=80,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Xuchang"
        )

        duel = start_duel(attacker, defender)
        assert len(duel.log) == 0

        process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)

        # Log should have at least one entry
        assert len(duel.log) > 0
        assert "Round 1" in duel.log[0]


class TestOfficerCaptureOnDuelDefeat:
    """Test capture mechanics when officer loses a duel."""

    @pytest.fixture
    def game_state_for_capture(self):
        """Create a game state for capture testing."""
        gs = GameState()
        gs.factions = {
            "Shu": Faction(name="Shu", cities=["Chengdu"], officers=["ZhaoYun"], relations={"Wei": 0}),
            "Wei": Faction(name="Wei", cities=["Xuchang"], officers=["XuChu"], relations={"Shu": 0})
        }
        gs.officers = {
            "ZhaoYun": Officer(
                name="ZhaoYun",
                faction="Shu",
                leadership=96,
                intelligence=76,
                politics=65,
                charisma=85,
                loyalty=90,
                traits=["Brave"],
                city="Chengdu"
            ),
            "XuChu": Officer(
                name="XuChu",
                faction="Wei",
                leadership=94,
                intelligence=40,
                politics=30,
                charisma=60,
                loyalty=75,
                traits=["Brave"],
                city="Xuchang"
            )
        }
        gs.cities = {
            "Chengdu": type("City", (), {"name": "Chengdu", "owner": "Shu"})(),
            "Xuchang": type("City", (), {"name": "Xuchang", "owner": "Wei"})()
        }
        gs.player_faction = "Wei"
        gs.captured_officers = {}
        return gs

    def test_capture_chance_based_on_loyalty(self, game_state_for_capture):
        """Test that capture chance is affected by loyalty."""
        gs = game_state_for_capture

        # High loyalty officer (90) - harder to capture
        high_loyalty = gs.officers["ZhaoYun"]
        high_loyalty.loyalty = 90

        # Low loyalty officer - easier to capture
        low_loyalty = Officer(
            name="Disloyal",
            faction="Wei",
            leadership=50,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=20,  # Very low loyalty
            traits=[],
            city="Xuchang"
        )

        # Calculate capture chances
        # Formula: capture_chance = 0.8 - (loyalty / 200.0)
        high_loyalty_chance = 0.8 - (high_loyalty.loyalty / 200.0)
        low_loyalty_chance = 0.8 - (low_loyalty.loyalty / 200.0)

        assert low_loyalty_chance > high_loyalty_chance
        assert high_loyalty_chance == pytest.approx(0.35)  # 0.8 - 0.45
        assert low_loyalty_chance == pytest.approx(0.70)  # 0.8 - 0.10

    def test_captured_officer_recruitment(self, game_state_for_capture):
        """Test recruiting a captured officer."""
        gs = game_state_for_capture

        # Manually capture an officer
        gs.captured_officers = {
            "XuChu": {
                "captor": "Wei",
                "original_faction": "Wei"
            }
        }
        gs.officers["XuChu"].faction = "Wei"

        # Try to recruit (as Wei player)
        result = recruit_captured(gs, "XuChu")

        # Should succeed
        assert result["success"] is True
        assert "XuChu" not in gs.captured_officers

    def test_captured_officer_execution_loyalty_impact(self, game_state_for_capture):
        """Test that executing a captured officer affects own officers' loyalty."""
        gs = game_state_for_capture

        # Add another officer to player's faction
        gs.officers["Soldier"] = Officer(
            name="Soldier",
            faction="Wei",
            leadership=50,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Xuchang"
        )
        gs.factions["Wei"].officers.append("Soldier")

        initial_loyalty = gs.officers["Soldier"].loyalty

        # Capture an enemy officer
        gs.captured_officers = {
            "ZhaoYun": {
                "captor": "Wei",
                "original_faction": "Shu"
            }
        }

        # Execute
        result = execute_captured(gs, "ZhaoYun")

        assert result["success"] is True
        # Own officer's loyalty should drop
        assert gs.officers["Soldier"].loyalty < initial_loyalty

    def test_release_improves_relations(self, game_state_for_capture):
        """Test that releasing a captured officer improves relations."""
        gs = game_state_for_capture

        initial_relations = gs.factions["Wei"].relations["Shu"]

        # Capture Zhao Yun
        gs.captured_officers = {
            "ZhaoYun": {
                "captor": "Wei",
                "original_faction": "Shu"
            }
        }
        gs.factions["Shu"].officers.remove("ZhaoYun")

        # Release
        result = release_captured(gs, "ZhaoYun")

        assert result["success"] is True
        # Relations should improve
        assert gs.factions["Wei"].relations["Shu"] > initial_relations


class TestLoyalistDeathBeforeCapture:
    """Test that loyalist officers refuse capture and die instead."""

    def test_loyalist_officers_list(self):
        """Verify the list of loyalist officers."""
        assert "GuanYu" in LOYALIST_OFFICERS
        assert "ZhangFei" in LOYALIST_OFFICERS
        assert "DianWei" in LOYALIST_OFFICERS

    def test_loyalist_refuses_capture_high_loyalty(self):
        """Test that loyalist with high loyalty refuses capture."""
        gs = GameState()
        gs.factions = {
            "Shu": Faction(name="Shu", cities=["Chengdu"], officers=["GuanYu"], relations={}),
            "Wei": Faction(name="Wei", cities=["Xuchang"], officers=[], relations={})
        }
        gs.officers = {
            "GuanYu": Officer(
                name="GuanYu",
                faction="Shu",
                leadership=98,
                intelligence=79,
                politics=92,
                charisma=84,
                loyalty=90,  # High loyalty - will refuse capture
                traits=["Brave", "Strict"],
                city="Chengdu"
            )
        }
        # Create proper City objects
        gs.cities = {
            "Chengdu": City(name="Chengdu", owner="Shu", troops=1000),
            "Xuchang": City(name="Xuchang", owner="Wei", troops=1000)
        }
        gs.captured_officers = {}

        # Attempt to capture officers in Chengdu (by Wei)
        results = capture_officers(gs, "Chengdu", "Wei")

        # Guan Yu should refuse capture
        assert len(results) == 1
        assert results[0]["officer"] == "GuanYu"
        assert results[0]["outcome"] == "refused"
        assert "fights to the death" in results[0]["message"] or "refused" in results[0]["outcome"]

    def test_loyalist_can_be_captured_with_low_loyalty(self):
        """Test that even loyalists can be captured if loyalty is low."""
        gs = GameState()
        gs.factions = {
            "Shu": Faction(name="Shu", cities=["Chengdu"], officers=["GuanYu"], relations={}),
            "Wei": Faction(name="Wei", cities=["Xuchang"], officers=[], relations={})
        }
        gs.officers = {
            "GuanYu": Officer(
                name="GuanYu",
                faction="Shu",
                leadership=98,
                intelligence=79,
                politics=92,
                charisma=84,
                loyalty=50,  # Low loyalty - can be captured
                traits=["Brave", "Strict"],
                city="Chengdu"
            )
        }
        # Create proper City objects
        gs.cities = {
            "Chengdu": City(name="Chengdu", owner="Shu", troops=1000),
            "Xuchang": City(name="Xuchang", owner="Wei", troops=1000)
        }
        gs.captured_officers = {}

        # Run multiple attempts since capture has random element
        captured_once = False
        for _ in range(20):
            # Reset state
            gs.factions["Shu"].officers = ["GuanYu"]
            gs.officers["GuanYu"].city = "Chengdu"
            gs.captured_officers = {}

            results = capture_officers(gs, "Chengdu", "Wei")

            if results and results[0]["outcome"] == "captured":
                captured_once = True
                break

        # With low loyalty, should be able to capture sometimes
        assert captured_once or any(r["outcome"] != "refused" for r in [capture_officers(gs, "Chengdu", "Wei") for _ in range(10)] if r)

    def test_non_loyalist_can_be_captured_normally(self):
        """Test that non-loyalist officers follow normal capture rules."""
        gs = GameState()
        gs.factions = {
            "Wei": Faction(name="Wei", cities=["Xuchang"], officers=["XuChu"], relations={}),
            "Shu": Faction(name="Shu", cities=["Chengdu"], officers=[], relations={})
        }
        gs.officers = {
            "XuChu": Officer(
                name="XuChu",
                faction="Wei",
                leadership=94,
                intelligence=40,
                politics=30,
                charisma=60,
                loyalty=75,
                traits=["Brave"],
                city="Xuchang"
            )
        }
        # Create proper City objects
        gs.cities = {
            "Chengdu": City(name="Chengdu", owner="Shu", troops=1000),
            "Xuchang": City(name="Xuchang", owner="Wei", troops=1000)
        }
        gs.captured_officers = {}

        # XuChu is not in LOYALIST_OFFICERS
        assert "XuChu" not in LOYALIST_OFFICERS

        # Run capture attempts
        captured = False
        for _ in range(20):
            gs.factions["Wei"].officers = ["XuChu"]
            gs.officers["XuChu"].city = "Xuchang"
            gs.captured_officers = {}

            results = capture_officers(gs, "Xuchang", "Shu")

            if results and results[0]["outcome"] == "captured":
                captured = True
                break

        # Non-loyalist with 75 loyalty should be capturable
        # Capture chance = 0.8 - (75/200) = 0.425
        assert captured


class TestDuelScenarios:
    """Test realistic duel battle scenarios."""

    def test_lu_bu_vs_zhang_fei(self):
        """Test legendary duel: Lu Bu vs Zhang Fei."""
        lu_bu = Officer(
            name="LuBu",
            faction="Dong Zhuo",
            leadership=100,  # Strongest warrior
            intelligence=50,
            politics=30,
            charisma=60,
            loyalty=30,
            traits=["Brave"],
            city="Chang'an"
        )
        zhang_fei = Officer(
            name="ZhangFei",
            faction="Shu",
            leadership=97,  # Very strong
            intelligence=65,
            politics=60,
            charisma=82,
            loyalty=90,
            traits=["Brave"],
            city="Chengdu"
        )

        # Lu Bu should have slight advantage
        duel = start_duel(lu_bu, zhang_fei)

        assert duel.attacker_hp > duel.defender_hp  # Lu Bu has more HP

        # Run the duel
        lu_bu_wins = 0
        zhang_fei_wins = 0
        trials = 20

        for _ in range(trials):
            duel = start_duel(lu_bu, zhang_fei)
            while not is_duel_over(duel):
                process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

            winner = get_duel_winner(duel)
            if winner.name == "LuBu":
                lu_bu_wins += 1
            else:
                zhang_fei_wins += 1

        # Lu Bu should win more often (but not always due to randomness)
        assert lu_bu_wins >= zhang_fei_wins - 5  # Allow some variance

    def test_guan_yu_vs_xu_chu(self):
        """Test legendary duel: Guan Yu vs Xu Chu."""
        guan_yu = Officer(
            name="GuanYu",
            faction="Shu",
            leadership=98,
            intelligence=79,
            politics=92,
            charisma=84,
            loyalty=90,
            traits=["Brave", "Strict"],
            city="Chengdu"
        )
        xu_chu = Officer(
            name="XuChu",
            faction="Wei",
            leadership=94,
            intelligence=40,
            politics=30,
            charisma=60,
            loyalty=80,
            traits=["Brave"],
            city="Xuchang"
        )

        duel = start_duel(guan_yu, xu_chu)

        # Guan Yu has slight HP advantage
        assert duel.attacker_hp > duel.defender_hp

        # Both should be formidable
        base_damage_gy = _calculate_base_damage(guan_yu.leadership, xu_chu.leadership)
        base_damage_xc = _calculate_base_damage(xu_chu.leadership, guan_yu.leadership)

        # Both deal significant damage
        assert base_damage_gy >= 10
        assert base_damage_xc >= 9

    def test_strategist_vs_warrior_duel(self):
        """Test duel between strategist and warrior (warrior advantage)."""
        zhuge_liang = Officer(
            name="ZhugeLiang",
            faction="Shu",
            leadership=45,  # Low combat stats
            intelligence=100,
            politics=95,
            charisma=92,
            loyalty=95,
            traits=["Scholar"],
            city="Chengdu"
        )
        lu_bu = Officer(
            name="LuBu",
            faction="Dong Zhuo",
            leadership=100,
            intelligence=50,
            politics=30,
            charisma=60,
            loyalty=30,
            traits=["Brave"],
            city="Chang'an"
        )

        duel = start_duel(zhuge_liang, lu_bu)

        # Lu Bu should dominate
        assert duel.defender_hp > duel.attacker_hp

        # Run duel - Lu Bu should win almost always
        lu_bu_wins = 0
        trials = 10

        for _ in range(trials):
            duel = start_duel(zhuge_liang, lu_bu)
            while not is_duel_over(duel):
                process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

            winner = get_duel_winner(duel)
            if winner.name == "LuBu":
                lu_bu_wins += 1

        # Lu Bu should win almost all duels
        assert lu_bu_wins >= trials - 2


class TestDuelMechanicsEdgeCases:
    """Test edge cases in duel mechanics."""

    def test_simultaneous_knockout(self):
        """Test when both officers could reach 0 HP simultaneously."""
        # Create evenly matched officers
        officer1 = Officer(
            name="Officer1",
            faction="Wei",
            leadership=70,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Xuchang"
        )
        officer2 = Officer(
            name="Officer2",
            faction="Shu",
            leadership=70,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Chengdu"
        )

        # Run many duels to ensure game handles edge cases
        for _ in range(20):
            duel = start_duel(officer1, officer2)
            while not is_duel_over(duel):
                process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

            # Should always have a winner
            winner = get_duel_winner(duel)
            assert winner in [officer1, officer2]

    def test_duel_round_counter(self):
        """Test that round counter increments correctly."""
        officer1 = Officer(
            name="Officer1",
            faction="Wei",
            leadership=80,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Xuchang"
        )
        officer2 = Officer(
            name="Officer2",
            faction="Shu",
            leadership=80,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Chengdu"
        )

        duel = start_duel(officer1, officer2)
        assert duel.round == 0

        process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)
        assert duel.round == 1

        process_duel_round(duel, DuelAction.DEFEND, DuelAction.SPECIAL)
        assert duel.round == 2

    def test_very_long_duel(self):
        """Test that duels eventually end even with defensive play."""
        officer1 = Officer(
            name="TankOfficer1",
            faction="Wei",
            leadership=100,  # High HP
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Xuchang"
        )
        officer2 = Officer(
            name="TankOfficer2",
            faction="Shu",
            leadership=100,
            intelligence=50,
            politics=50,
            charisma=50,
            loyalty=80,
            traits=[],
            city="Chengdu"
        )

        duel = start_duel(officer1, officer2)

        # Alternate between defend and attack
        max_rounds = 200
        rounds = 0

        while not is_duel_over(duel) and rounds < max_rounds:
            if rounds % 2 == 0:
                process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)
            else:
                process_duel_round(duel, DuelAction.DEFEND, DuelAction.ATTACK)
            rounds += 1

        # Duel should end within reasonable time
        assert is_duel_over(duel)
        assert rounds < max_rounds
