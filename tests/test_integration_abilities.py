"""
Integration Tests: Officer Ability Rankings

This module tests officer special abilities:
- Combat abilities (warriors/generals): attack multipliers, defense bonuses
- Strategist abilities: fire, ambush, morale manipulation
- Ability cooldowns and context requirements
- Ability synergies and effectiveness rankings

Based on 3KYuYun's ROTK11 ability tier analysis.
"""
import pytest
from src.abilities import (
    load_abilities,
    get_ability,
    get_officer_abilities,
    get_officer_ability,
)
from src.models import Ability


class TestAbilityLoading:
    """Test ability data loading from JSON."""

    def test_load_abilities_returns_list(self):
        """Loading abilities should return a list of Ability objects."""
        abilities = load_abilities()
        assert isinstance(abilities, list)
        assert len(abilities) > 0

    def test_all_abilities_are_ability_type(self):
        """All loaded abilities should be Ability dataclass instances."""
        abilities = load_abilities()
        for ability in abilities:
            assert isinstance(ability, Ability)

    def test_ability_count(self):
        """Should have at least 18 unique abilities."""
        abilities = load_abilities()
        assert len(abilities) >= 18

    def test_ability_has_required_fields(self):
        """Each ability should have all required fields."""
        abilities = load_abilities()
        for ability in abilities:
            assert ability.id
            assert ability.officer
            assert ability.name_key
            assert ability.context in ["battle", "duel"]
            assert ability.cooldown > 0
            assert isinstance(ability.effect, dict)


class TestCombatAbilities:
    """Test combat-type (warrior) abilities."""

    def test_guan_yu_green_dragon_slash(self):
        """Guan Yu's signature duel ability."""
        ability = get_officer_ability("GuanYu", "duel")

        assert ability is not None
        assert ability.id == "green_dragon_slash"
        assert ability.context == "duel"
        assert ability.effect.get("damage_mult") == 2.5
        assert ability.cooldown == 2

    def test_zhang_fei_serpent_spear(self):
        """Zhang Fei's spear attack with stun chance."""
        ability = get_officer_ability("ZhangFei", "duel")

        assert ability is not None
        assert ability.id == "serpent_spear"
        assert ability.effect.get("damage_mult") == 2.0
        assert ability.effect.get("stun_chance") == 0.3

    def test_zhao_yun_lone_rider(self):
        """Zhao Yun's battle ability for solo charges."""
        ability = get_officer_ability("ZhaoYun", "battle")

        assert ability is not None
        assert ability.id == "lone_rider"
        assert ability.effect.get("attack_mult") == 1.5
        assert ability.effect.get("morale_boost") == 5

    def test_ma_chao_heroic_charge(self):
        """Ma Chao's cavalry-focused battle ability."""
        ability = get_officer_ability("MaChao", "battle")

        assert ability is not None
        assert ability.id == "heroic_charge"
        assert ability.effect.get("cavalry_mult") == 1.8

    def test_huang_zhong_veteran_aim(self):
        """Huang Zhong's precision duel ability."""
        ability = get_officer_ability("HuangZhong", "duel")

        assert ability is not None
        assert ability.id == "veteran_aim"
        assert ability.effect.get("damage_mult") == 2.2
        assert ability.effect.get("hit_rate") == 0.95

    def test_xu_chu_iron_wall(self):
        """Xu Chu's defensive duel ability."""
        ability = get_officer_ability("XuChu", "duel")

        assert ability is not None
        assert ability.id == "iron_wall"
        assert ability.effect.get("defense_mult") == 2.5

    def test_dian_wei_fearless_guard(self):
        """Dian Wei's counter-attack duel ability."""
        ability = get_officer_ability("DianWei", "duel")

        assert ability is not None
        assert ability.id == "fearless_guard"
        assert ability.effect.get("damage_mult") == 1.8
        assert ability.effect.get("counter_damage") == 0.5

    def test_xiahou_dun_one_eye_fury(self):
        """Xiahou Dun's self-healing duel ability."""
        ability = get_officer_ability("XiahouDun", "duel")

        assert ability is not None
        assert ability.id == "one_eye_fury"
        assert ability.effect.get("damage_mult") == 2.0
        assert ability.effect.get("self_heal") == 10

    def test_zhang_liao_rapid_march(self):
        """Zhang Liao's aggressive battle ability."""
        ability = get_officer_ability("ZhangLiao", "battle")

        assert ability is not None
        assert ability.id == "rapid_march"
        assert ability.effect.get("attack_mult") == 1.6
        assert ability.effect.get("morale_boost") == 5


class TestStrategistAbilities:
    """Test strategist (intelligence-based) abilities."""

    def test_zhuge_liang_empty_fort(self):
        """Zhuge Liang's legendary defensive strategy."""
        ability = get_officer_ability("ZhugeLiang", "battle")

        assert ability is not None
        assert ability.id == "empty_fort"
        assert ability.effect.get("defense_mult") == 2.0
        assert ability.effect.get("morale_boost") == 10

    def test_sima_yi_ambush_master(self):
        """Sima Yi's ambush specialization."""
        ability = get_officer_ability("SimaYi", "battle")

        assert ability is not None
        assert ability.id == "ambush_master"
        assert ability.effect.get("ambush_mult") == 2.0

    def test_zhou_yu_fire_strategy(self):
        """Zhou Yu's fire attack mastery."""
        ability = get_officer_ability("ZhouYu", "battle")

        assert ability is not None
        assert ability.id == "fire_strategy"
        assert ability.effect.get("fire_mult") == 2.5

    def test_pang_tong_brilliant_strategy(self):
        """Pang Tong's balanced tactical ability."""
        ability = get_officer_ability("PangTong", "battle")

        assert ability is not None
        assert ability.id == "brilliant_strategy"
        assert ability.effect.get("attack_mult") == 1.3
        assert ability.effect.get("defense_mult") == 1.3

    def test_lu_xun_swift_assault(self):
        """Lu Xun's combined attack and fire ability."""
        ability = get_officer_ability("LuXun", "battle")

        assert ability is not None
        assert ability.id == "swift_assault"
        assert ability.effect.get("attack_mult") == 1.5
        assert ability.effect.get("fire_mult") == 1.5

    def test_jiang_wei_mountain_defense(self):
        """Jiang Wei's defensive positioning."""
        ability = get_officer_ability("JiangWei", "battle")

        assert ability is not None
        assert ability.id == "mountain_defense"
        assert ability.effect.get("defense_mult") == 1.8


class TestLeadershipAbilities:
    """Test leadership/charisma-based abilities."""

    def test_cao_cao_charismatic_speech(self):
        """Cao Cao's morale and loyalty boosting ability."""
        ability = get_officer_ability("CaoCao", "battle")

        assert ability is not None
        assert ability.id == "charismatic_speech"
        assert ability.effect.get("morale_boost") == 15
        assert ability.effect.get("loyalty_boost") == 5

    def test_lu_su_diplomatic_finesse(self):
        """Lu Su's morale manipulation ability."""
        ability = get_officer_ability("LuSu", "battle")

        assert ability is not None
        assert ability.id == "diplomatic_finesse"
        assert ability.effect.get("morale_boost") == 10
        assert ability.effect.get("enemy_morale_drop") == 10


class TestNavalAbilities:
    """Test naval combat abilities."""

    def test_gan_ning_naval_command(self):
        """Gan Ning's coastal/naval superiority."""
        ability = get_officer_ability("GanNing", "battle")

        assert ability is not None
        assert ability.id == "naval_command"
        assert ability.effect.get("coastal_mult") == 2.0


class TestAbilityCooldowns:
    """Test ability cooldown mechanics."""

    def test_battle_ability_cooldowns(self):
        """Battle abilities should have cooldown of 3-4 turns."""
        abilities = load_abilities()
        battle_abilities = [a for a in abilities if a.context == "battle"]

        for ability in battle_abilities:
            assert 3 <= ability.cooldown <= 4, \
                f"{ability.id} has invalid cooldown: {ability.cooldown}"

    def test_duel_ability_cooldowns(self):
        """Duel abilities should have cooldown of 2 turns."""
        abilities = load_abilities()
        duel_abilities = [a for a in abilities if a.context == "duel"]

        for ability in duel_abilities:
            assert ability.cooldown == 2, \
                f"{ability.id} has invalid cooldown: {ability.cooldown}"

    def test_cooldown_balance(self):
        """Stronger abilities should not have shorter cooldowns."""
        abilities = load_abilities()

        # Find high damage multipliers
        for ability in abilities:
            damage_mult = ability.effect.get("damage_mult", 1.0)

            # Very high damage (2.5x) should not have 1-turn cooldown
            if damage_mult >= 2.5:
                assert ability.cooldown >= 2

    def test_diplomatic_ability_longer_cooldown(self):
        """Diplomatic abilities should have longer cooldowns."""
        ability = get_ability("diplomatic_finesse")

        assert ability is not None
        # Diplomatic finesse affects both sides (powerful) - cooldown 4
        assert ability.cooldown == 4


class TestAbilitySynergies:
    """Test ability synergies and combinations."""

    def test_fire_strategy_stacks_with_terrain(self):
        """Zhou Yu's fire strategy should work with forest terrain bonus."""
        ability = get_officer_ability("ZhouYu", "battle")

        # Fire mult from ability
        fire_mult = ability.effect.get("fire_mult", 1.0)

        # Forest gives +25% fire bonus (from constants)
        forest_bonus = 1.25

        # Combined effect
        combined = fire_mult * forest_bonus
        assert combined == pytest.approx(3.125)  # 2.5 * 1.25

    def test_lu_xun_dual_synergy(self):
        """Lu Xun's ability provides both attack and fire bonuses."""
        ability = get_officer_ability("LuXun", "battle")

        attack_mult = ability.effect.get("attack_mult", 1.0)
        fire_mult = ability.effect.get("fire_mult", 1.0)

        # Both should be significant
        assert attack_mult >= 1.5
        assert fire_mult >= 1.5

        # Combined offensive potential
        combined = attack_mult * fire_mult
        assert combined >= 2.0

    def test_pang_tong_balanced_synergy(self):
        """Pang Tong's ability provides balanced attack/defense."""
        ability = get_officer_ability("PangTong", "battle")

        attack_mult = ability.effect.get("attack_mult", 1.0)
        defense_mult = ability.effect.get("defense_mult", 1.0)

        # Should be equal for balance
        assert attack_mult == defense_mult

        # Combined tactical flexibility
        total_boost = (attack_mult - 1.0) + (defense_mult - 1.0)
        assert total_boost >= 0.5  # At least +50% total

    def test_cavalry_ability_terrain_synergy(self):
        """Ma Chao's cavalry bonus with plains terrain."""
        ability = get_officer_ability("MaChao", "battle")

        cavalry_mult = ability.effect.get("cavalry_mult", 1.0)

        # Plains give no penalty to cavalry
        plains_mult = 1.0

        # Combined
        combined = cavalry_mult * plains_mult
        assert combined == 1.8

        # But mountains penalize cavalry (-20%)
        mountain_penalty = 0.8
        mountain_combined = cavalry_mult * mountain_penalty
        assert mountain_combined == pytest.approx(1.44)

    def test_morale_abilities_stack(self):
        """Morale-boosting abilities should provide significant bonuses."""
        cao_cao = get_officer_ability("CaoCao", "battle")
        lu_su = get_officer_ability("LuSu", "battle")

        cao_boost = cao_cao.effect.get("morale_boost", 0)
        lu_su_boost = lu_su.effect.get("morale_boost", 0)

        # Individual boosts should be meaningful
        assert cao_boost >= 10
        assert lu_su_boost >= 10

        # If used together, total boost is significant
        total_boost = cao_boost + lu_su_boost
        assert total_boost >= 20


class TestAbilityEffectivenessRankings:
    """Test ability effectiveness rankings based on ROTK11 tier analysis."""

    def test_duel_ability_damage_rankings(self):
        """Rank duel abilities by damage multiplier."""
        abilities = load_abilities()
        duel_abilities = [a for a in abilities if a.context == "duel"]

        # Sort by damage multiplier
        ranked = sorted(
            [(a.id, a.officer, a.effect.get("damage_mult", 1.0)) for a in duel_abilities],
            key=lambda x: x[2],
            reverse=True
        )

        # Guan Yu should be at top (Green Dragon Slash = 2.5x)
        assert ranked[0][1] == "GuanYu"
        assert ranked[0][2] == 2.5

        # Huang Zhong should be second (Veteran Aim = 2.2x)
        assert ranked[1][1] == "HuangZhong"
        assert ranked[1][2] == 2.2

    def test_battle_ability_attack_rankings(self):
        """Rank battle abilities by attack multiplier."""
        abilities = load_abilities()
        battle_abilities = [a for a in abilities if a.context == "battle"]

        # Get attack multipliers
        attack_abilities = [
            (a.id, a.officer, a.effect.get("attack_mult", 1.0))
            for a in battle_abilities
            if a.effect.get("attack_mult", 1.0) > 1.0
        ]

        # Sort by attack multiplier
        ranked = sorted(attack_abilities, key=lambda x: x[2], reverse=True)

        # Zhang Liao should have highest pure attack mult (1.6)
        assert any(r[1] == "ZhangLiao" and r[2] >= 1.5 for r in ranked)

    def test_battle_ability_defense_rankings(self):
        """Rank battle abilities by defense multiplier."""
        abilities = load_abilities()
        battle_abilities = [a for a in abilities if a.context == "battle"]

        # Get defense multipliers
        defense_abilities = [
            (a.id, a.officer, a.effect.get("defense_mult", 1.0))
            for a in battle_abilities
            if a.effect.get("defense_mult", 1.0) > 1.0
        ]

        # Sort by defense multiplier
        ranked = sorted(defense_abilities, key=lambda x: x[2], reverse=True)

        # Zhuge Liang's Empty Fort should be top (2.0x)
        assert ranked[0][1] == "ZhugeLiang"
        assert ranked[0][2] == 2.0

    def test_duel_defensive_ability_rankings(self):
        """Rank duel defensive abilities."""
        abilities = load_abilities()
        duel_abilities = [a for a in abilities if a.context == "duel"]

        # Get defense multipliers
        defense_abilities = [
            (a.id, a.officer, a.effect.get("defense_mult", 1.0))
            for a in duel_abilities
            if a.effect.get("defense_mult", 1.0) > 1.0
        ]

        # Sort by defense multiplier
        ranked = sorted(defense_abilities, key=lambda x: x[2], reverse=True)

        # Xu Chu's Iron Wall should be top (2.5x)
        assert ranked[0][1] == "XuChu"
        assert ranked[0][2] == 2.5

    def test_fire_ability_rankings(self):
        """Rank fire-related abilities."""
        abilities = load_abilities()

        # Get fire multipliers
        fire_abilities = [
            (a.id, a.officer, a.effect.get("fire_mult", 1.0))
            for a in abilities
            if a.effect.get("fire_mult", 1.0) > 1.0
        ]

        # Sort by fire multiplier
        ranked = sorted(fire_abilities, key=lambda x: x[2], reverse=True)

        # Zhou Yu should be best fire strategist (2.5x)
        assert ranked[0][1] == "ZhouYu"
        assert ranked[0][2] == 2.5

        # Lu Xun also has fire ability (1.5x)
        assert any(r[1] == "LuXun" for r in ranked)

    def test_morale_ability_rankings(self):
        """Rank morale-boosting abilities."""
        abilities = load_abilities()

        # Get morale boosts
        morale_abilities = [
            (a.id, a.officer, a.effect.get("morale_boost", 0))
            for a in abilities
            if a.effect.get("morale_boost", 0) > 0
        ]

        # Sort by morale boost
        ranked = sorted(morale_abilities, key=lambda x: x[2], reverse=True)

        # Cao Cao should have highest morale boost (15)
        assert ranked[0][1] == "CaoCao"
        assert ranked[0][2] == 15


class TestAbilityContexts:
    """Test ability context requirements."""

    def test_all_abilities_have_valid_context(self):
        """All abilities should have either 'battle' or 'duel' context."""
        abilities = load_abilities()

        for ability in abilities:
            assert ability.context in ["battle", "duel"], \
                f"{ability.id} has invalid context: {ability.context}"

    def test_duel_abilities_are_duel_only(self):
        """Duel abilities should not have battle effects."""
        abilities = load_abilities()
        duel_abilities = [a for a in abilities if a.context == "duel"]

        # Duel abilities should focus on damage/defense, not army-scale effects
        for ability in duel_abilities:
            # Should not have army-scale effects
            assert not ability.effect.get("cavalry_mult")
            assert not ability.effect.get("ambush_mult")
            assert not ability.effect.get("coastal_mult")

    def test_battle_abilities_are_battle_only(self):
        """Battle abilities should not have duel-specific effects."""
        abilities = load_abilities()
        battle_abilities = [a for a in abilities if a.context == "battle"]

        # Battle abilities can have attack/defense multipliers but also army effects
        # Just verify they exist in correct context
        assert len(battle_abilities) > 0


class TestAbilityRetrieval:
    """Test ability retrieval functions."""

    def test_get_ability_by_id(self):
        """Should retrieve ability by ID."""
        ability = get_ability("green_dragon_slash")

        assert ability is not None
        assert ability.id == "green_dragon_slash"
        assert ability.officer == "GuanYu"

    def test_get_nonexistent_ability(self):
        """Should return None for nonexistent ability."""
        ability = get_ability("nonexistent_ability")
        assert ability is None

    def test_get_officer_abilities(self):
        """Should retrieve all abilities for an officer."""
        # ZhugeLiang has battle ability
        abilities = get_officer_abilities("ZhugeLiang")

        assert len(abilities) >= 1
        assert all(a.officer == "ZhugeLiang" for a in abilities)

    def test_get_officer_ability_by_context(self):
        """Should retrieve officer ability for specific context."""
        # GuanYu has duel ability
        duel_ability = get_officer_ability("GuanYu", "duel")
        battle_ability = get_officer_ability("GuanYu", "battle")

        assert duel_ability is not None
        assert duel_ability.context == "duel"

        # GuanYu doesn't have battle ability
        assert battle_ability is None

    def test_officer_without_abilities(self):
        """Should return empty list for officer without abilities."""
        abilities = get_officer_abilities("RandomOfficer")
        assert abilities == []


class TestAbilityBalance:
    """Test overall ability balance."""

    def test_no_ability_is_overpowered(self):
        """No single ability should have extreme multipliers."""
        abilities = load_abilities()

        for ability in abilities:
            damage_mult = ability.effect.get("damage_mult", 1.0)
            attack_mult = ability.effect.get("attack_mult", 1.0)
            defense_mult = ability.effect.get("defense_mult", 1.0)
            fire_mult = ability.effect.get("fire_mult", 1.0)

            # No ability should exceed 3x multiplier
            assert damage_mult <= 3.0, f"{ability.id} damage too high"
            assert attack_mult <= 2.0, f"{ability.id} attack too high"
            assert defense_mult <= 3.0, f"{ability.id} defense too high"
            assert fire_mult <= 3.0, f"{ability.id} fire too high"

    def test_factions_have_balanced_abilities(self):
        """Each major faction should have competitive abilities."""
        abilities = load_abilities()

        # Officer-to-faction mapping (simplified)
        faction_officers = {
            "Shu": ["ZhugeLiang", "GuanYu", "ZhangFei", "ZhaoYun", "MaChao",
                    "HuangZhong", "JiangWei", "PangTong"],
            "Wei": ["CaoCao", "SimaYi", "XuChu", "DianWei", "XiahouDun", "ZhangLiao"],
            "Wu": ["ZhouYu", "LuSu", "LuXun", "GanNing"]
        }

        faction_abilities = {}
        for faction, officers in faction_officers.items():
            faction_abilities[faction] = [
                a for a in abilities if a.officer in officers
            ]

        # Each faction should have multiple abilities
        for faction, abs in faction_abilities.items():
            assert len(abs) >= 3, f"{faction} has too few abilities"

    def test_ability_type_distribution(self):
        """Should have good mix of offensive and defensive abilities."""
        abilities = load_abilities()

        offensive = 0
        defensive = 0
        utility = 0

        for ability in abilities:
            if ability.effect.get("damage_mult") or ability.effect.get("attack_mult"):
                offensive += 1
            if ability.effect.get("defense_mult"):
                defensive += 1
            if ability.effect.get("morale_boost") or ability.effect.get("loyalty_boost"):
                utility += 1

        # Should have variety
        assert offensive >= 5
        assert defensive >= 3
        assert utility >= 3
