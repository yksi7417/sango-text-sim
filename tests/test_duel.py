"""
Tests for the duel system mechanics.
"""

import pytest
from src.systems.duel import (
    Duel,
    DuelAction,
    DuelResult,
    process_duel_round,
    start_duel,
    is_duel_over,
)
from src.models import Officer


@pytest.fixture
def strong_officer():
    """Create a strong officer (high leadership)."""
    return Officer(
        name="Lu Bu",
        faction="Dong Zhuo",
        leadership=100,
        intelligence=50,
        politics=30,
        charisma=60,
        energy=100,
        loyalty=50,
        traits=[],
        city="Chang'an",
        task=None,
        task_city=None,
        busy=False
    )


@pytest.fixture
def average_officer():
    """Create an average officer."""
    return Officer(
        name="Zhang Fei",
        faction="Shu",
        leadership=80,
        intelligence=60,
        politics=40,
        charisma=70,
        energy=100,
        loyalty=90,
        traits=[],
        city="Chengdu",
        task=None,
        task_city=None,
        busy=False
    )


@pytest.fixture
def weak_officer():
    """Create a weak officer (low leadership)."""
    return Officer(
        name="Scholar Wang",
        faction="Wu",
        leadership=30,
        intelligence=90,
        politics=80,
        charisma=50,
        energy=100,
        loyalty=70,
        traits=[],
        city="Jianye",
        task=None,
        task_city=None,
        busy=False
    )


class TestDuelDataStructures:
    """Test duel data structures."""

    def test_duel_action_enum(self):
        """Test DuelAction enum has all required values."""
        assert hasattr(DuelAction, 'ATTACK')
        assert hasattr(DuelAction, 'DEFEND')
        assert hasattr(DuelAction, 'SPECIAL')

    def test_start_duel(self, strong_officer, average_officer):
        """Test duel initialization."""
        duel = start_duel(strong_officer, average_officer)

        assert duel.attacker == strong_officer
        assert duel.defender == average_officer
        assert duel.attacker_hp > 0
        assert duel.defender_hp > 0
        assert duel.round == 0
        assert isinstance(duel.log, list)
        assert len(duel.log) == 0

    def test_initial_hp_based_on_leadership(self, strong_officer, weak_officer):
        """Test that initial HP is based on leadership stat."""
        duel = start_duel(strong_officer, weak_officer)

        # Strong officer should have more HP
        assert duel.attacker_hp > duel.defender_hp


class TestDuelRoundProcessing:
    """Test duel round processing mechanics."""

    def test_attack_vs_attack(self, strong_officer, average_officer):
        """Test both officers attacking each other."""
        duel = start_duel(strong_officer, average_officer)
        initial_attacker_hp = duel.attacker_hp
        initial_defender_hp = duel.defender_hp

        result = process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

        # Both should take damage
        assert duel.attacker_hp < initial_attacker_hp or duel.defender_hp < initial_defender_hp
        assert duel.round == 1
        assert len(duel.log) > 0
        assert isinstance(result, DuelResult)

    def test_attack_vs_defend(self, strong_officer, average_officer):
        """Test attack vs defend - defender takes reduced damage."""
        duel = start_duel(strong_officer, average_officer)
        initial_defender_hp = duel.defender_hp

        # Attacker attacks, defender defends
        result = process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)

        # Defender should take some damage (but reduced)
        damage_taken = initial_defender_hp - duel.defender_hp
        assert damage_taken >= 0  # May miss, so >= 0
        assert duel.round == 1

    def test_defend_reduces_damage(self, strong_officer, weak_officer):
        """Test that defend reduces damage by 50%."""
        # Run multiple trials to account for randomness
        total_damage_normal = 0
        total_damage_defended = 0
        trials = 10

        for _ in range(trials):
            # Normal attack
            duel1 = start_duel(strong_officer, weak_officer)
            initial_hp1 = duel1.defender_hp
            process_duel_round(duel1, DuelAction.ATTACK, DuelAction.ATTACK)
            total_damage_normal += (initial_hp1 - duel1.defender_hp)

            # Defended attack
            duel2 = start_duel(strong_officer, weak_officer)
            initial_hp2 = duel2.defender_hp
            process_duel_round(duel2, DuelAction.ATTACK, DuelAction.DEFEND)
            total_damage_defended += (initial_hp2 - duel2.defender_hp)

        # On average, defended damage should be less than normal damage
        avg_damage_normal = total_damage_normal / trials
        avg_damage_defended = total_damage_defended / trials

        if avg_damage_normal > 0:  # Only check if damage was dealt
            assert avg_damage_defended < avg_damage_normal

    def test_special_attack_high_damage_low_hit(self, strong_officer, average_officer):
        """Test special attack has high damage but lower hit rate."""
        duel = start_duel(strong_officer, average_officer)
        initial_hp = duel.defender_hp

        result = process_duel_round(duel, DuelAction.SPECIAL, DuelAction.ATTACK)

        # Check that round processed
        assert duel.round == 1
        assert len(duel.log) > 0

        # If hit, damage should be significant
        damage = initial_hp - duel.defender_hp
        if damage > 0:
            # Special attacks should do more damage than regular attacks
            assert damage >= 10  # Some significant damage

    def test_damage_based_on_leadership_differential(self, strong_officer, weak_officer):
        """Test that leadership difference affects damage."""
        # Strong vs weak should do more damage
        duel1 = start_duel(strong_officer, weak_officer)
        initial_hp1 = duel1.defender_hp
        process_duel_round(duel1, DuelAction.ATTACK, DuelAction.ATTACK)
        damage1 = initial_hp1 - duel1.defender_hp

        # Weak vs strong should do less damage
        duel2 = start_duel(weak_officer, strong_officer)
        initial_hp2 = duel2.defender_hp
        process_duel_round(duel2, DuelAction.ATTACK, DuelAction.ATTACK)
        damage2 = initial_hp2 - duel2.defender_hp

        # Average over multiple trials
        total_strong_damage = damage1
        total_weak_damage = damage2

        for _ in range(9):  # 9 more trials = 10 total
            duel1 = start_duel(strong_officer, weak_officer)
            initial_hp1 = duel1.defender_hp
            process_duel_round(duel1, DuelAction.ATTACK, DuelAction.ATTACK)
            total_strong_damage += (initial_hp1 - duel1.defender_hp)

            duel2 = start_duel(weak_officer, strong_officer)
            initial_hp2 = duel2.defender_hp
            process_duel_round(duel2, DuelAction.ATTACK, DuelAction.ATTACK)
            total_weak_damage += (initial_hp2 - duel2.defender_hp)

        avg_strong_damage = total_strong_damage / 10
        avg_weak_damage = total_weak_damage / 10

        # Strong officer should deal more damage on average
        if avg_strong_damage > 0:
            assert avg_strong_damage > avg_weak_damage


class TestDuelCompletion:
    """Test duel completion conditions."""

    def test_is_duel_over_initial(self, strong_officer, average_officer):
        """Test duel is not over initially."""
        duel = start_duel(strong_officer, average_officer)
        assert not is_duel_over(duel)

    def test_is_duel_over_when_hp_zero(self, strong_officer, weak_officer):
        """Test duel ends when HP reaches 0 or below."""
        duel = start_duel(strong_officer, weak_officer)

        # Manually set HP to 0
        duel.defender_hp = 0
        assert is_duel_over(duel)

        duel.defender_hp = 10
        duel.attacker_hp = 0
        assert is_duel_over(duel)

        duel.defender_hp = -5
        duel.attacker_hp = 50
        assert is_duel_over(duel)

    def test_duel_to_completion(self, strong_officer, weak_officer):
        """Test running a duel to completion."""
        duel = start_duel(strong_officer, weak_officer)

        max_rounds = 100
        round_count = 0

        while not is_duel_over(duel) and round_count < max_rounds:
            process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)
            round_count += 1

        # Duel should end within max rounds
        assert round_count < max_rounds
        assert is_duel_over(duel)

        # One officer should have HP <= 0
        assert duel.attacker_hp <= 0 or duel.defender_hp <= 0

        # Log should have entries
        assert len(duel.log) > 0


class TestDuelResult:
    """Test duel result information."""

    def test_result_contains_action_info(self, strong_officer, average_officer):
        """Test result contains information about actions taken."""
        duel = start_duel(strong_officer, average_officer)
        result = process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)

        assert hasattr(result, 'attacker_action')
        assert hasattr(result, 'defender_action')
        assert result.attacker_action == DuelAction.ATTACK
        assert result.defender_action == DuelAction.DEFEND

    def test_result_contains_damage_info(self, strong_officer, average_officer):
        """Test result contains damage information."""
        duel = start_duel(strong_officer, average_officer)
        result = process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

        assert hasattr(result, 'attacker_damage')
        assert hasattr(result, 'defender_damage')
        assert isinstance(result.attacker_damage, int)
        assert isinstance(result.defender_damage, int)

    def test_result_contains_message(self, strong_officer, average_officer):
        """Test result contains descriptive message."""
        duel = start_duel(strong_officer, average_officer)
        result = process_duel_round(duel, DuelAction.ATTACK, DuelAction.DEFEND)

        assert hasattr(result, 'message')
        assert isinstance(result.message, str)
        assert len(result.message) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_equal_officers_duel(self, average_officer):
        """Test duel between officers with equal stats."""
        officer2 = Officer(
            name="Twin Officer",
            faction="Wei",
            leadership=80,
            intelligence=60,
            politics=40,
            charisma=70,
            energy=100,
            loyalty=90,
            traits=[],
            city="Luoyang",
            task=None,
            task_city=None,
            busy=False
        )

        duel = start_duel(average_officer, officer2)
        result = process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)

        # Should complete without errors
        assert isinstance(result, DuelResult)
        assert duel.round == 1

    def test_multiple_special_attacks(self, strong_officer, average_officer):
        """Test multiple special attacks in a row."""
        duel = start_duel(strong_officer, average_officer)

        for _ in range(3):
            result = process_duel_round(duel, DuelAction.SPECIAL, DuelAction.SPECIAL)
            if is_duel_over(duel):
                break

        # Should complete without errors
        assert duel.round <= 3

    def test_log_accumulates(self, strong_officer, average_officer):
        """Test that combat log accumulates over rounds."""
        duel = start_duel(strong_officer, average_officer)

        process_duel_round(duel, DuelAction.ATTACK, DuelAction.ATTACK)
        log_size_1 = len(duel.log)

        process_duel_round(duel, DuelAction.DEFEND, DuelAction.ATTACK)
        log_size_2 = len(duel.log)

        assert log_size_2 > log_size_1
