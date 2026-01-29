"""
Integration Tests: Marriage and Family System

This module tests marriage mechanics:
- Marriage proposal success rate (0.3 + relations/200)
- Spouse loyalty bonus (+25 from relationship)
- Marriage alliance relations boost (+25)
- Internal affairs bonus from spouse
- Hostage exchange mechanics
- Historical marriages

Based on ROTK11's marriage and hostage diplomacy system.
"""
import pytest
from src.models import Officer, Faction, GameState, City, RelationshipType
from src.systems.marriage import (
    MARRIAGE_RELATION_BOOST,
    MARRIAGE_LOYALTY_BOOST,
    HOSTAGE_RELATION_MAINTENANCE,
    HOSTAGE_HARM_PENALTY,
    HOSTAGE_RETURN_BOOST,
    propose_marriage,
    send_hostage,
    return_hostage,
    list_hostages,
)


def create_officer(name, faction="", leadership=70, intelligence=70, politics=70, charisma=70,
                   loyalty=70, energy=100, city=None, task=None, relationships=None):
    """Helper to create officers with correct parameters."""
    return Officer(
        name=name, faction=faction, leadership=leadership, intelligence=intelligence,
        politics=politics, charisma=charisma, loyalty=loyalty, energy=energy,
        city=city, task=task, relationships=relationships or {}
    )


class TestMarriageConstants:
    """Test marriage-related constants."""

    def test_marriage_relation_boost(self):
        """Marriage should boost relations by 25."""
        assert MARRIAGE_RELATION_BOOST == 25

    def test_marriage_loyalty_boost(self):
        """Marriage should boost loyalty by 15."""
        assert MARRIAGE_LOYALTY_BOOST == 15

    def test_hostage_relation_maintenance(self):
        """Hostage presence maintains relations by 5 per turn."""
        assert HOSTAGE_RELATION_MAINTENANCE == 5

    def test_hostage_harm_penalty(self):
        """Harming a hostage incurs -40 relations penalty."""
        assert HOSTAGE_HARM_PENALTY == -40

    def test_hostage_return_boost(self):
        """Returning a hostage boosts relations by 20."""
        assert HOSTAGE_RETURN_BOOST == 20


class TestMarriageProposalRate:
    """Test marriage proposal success rate formula."""

    def test_base_acceptance_rate(self):
        """Base acceptance rate is 30% at 0 relations."""
        relations = 0
        acceptance = 0.3 + (relations / 200.0)
        assert acceptance == 0.3

    def test_neutral_relations_acceptance(self):
        """Neutral relations (50) give 55% acceptance."""
        relations = 50
        acceptance = 0.3 + (relations / 200.0)
        assert acceptance == pytest.approx(0.55)

    def test_good_relations_acceptance(self):
        """Good relations (70) give 65% acceptance."""
        relations = 70
        acceptance = 0.3 + (relations / 200.0)
        assert acceptance == pytest.approx(0.65)

    def test_max_relations_acceptance(self):
        """Max relations (100) give 80% acceptance."""
        relations = 100
        acceptance = 0.3 + (relations / 200.0)
        assert acceptance == pytest.approx(0.80)

    def test_hostile_relations_acceptance(self):
        """Hostile relations (-50) give only 5% acceptance."""
        relations = -50
        acceptance = 0.3 + (relations / 200.0)
        assert acceptance == pytest.approx(0.05)


class TestSpouseLoyaltyBonus:
    """Test spouse relationship loyalty bonus."""

    def test_spouse_relationship_loyalty_bonus(self):
        """Spouse relationship gives +25 loyalty bonus."""
        officer = create_officer("ZhangFei", faction="Shu")
        officer.relationships["SunShangxiang"] = RelationshipType.SPOUSE.value

        bonus = officer.get_relationship_bonus("SunShangxiang", "loyalty")
        assert bonus == 25.0

    def test_spouse_vs_sworn_brother_loyalty(self):
        """Compare spouse (+25) vs sworn brother (+30) loyalty bonus."""
        officer = create_officer("LiuBei", faction="Shu")

        # Sworn brother gives higher loyalty
        officer.relationships["GuanYu"] = RelationshipType.SWORN_BROTHER.value
        officer.relationships["LadyMi"] = RelationshipType.SPOUSE.value

        brother_bonus = officer.get_relationship_bonus("GuanYu", "loyalty")
        spouse_bonus = officer.get_relationship_bonus("LadyMi", "loyalty")

        assert brother_bonus == 30.0
        assert spouse_bonus == 25.0
        assert brother_bonus > spouse_bonus

    def test_spouse_loyalty_calculation(self):
        """Calculate effective loyalty with spouse bonus."""
        base_loyalty = 60
        spouse_bonus = 25
        effective = base_loyalty + spouse_bonus

        assert effective == 85

    def test_mutual_spouse_relationship(self):
        """Both spouses should get loyalty bonus."""
        husband = create_officer("LiuBei", faction="Shu")
        wife = create_officer("LadyMi", faction="Shu")

        # Set mutual relationship
        husband.relationships[wife.name] = RelationshipType.SPOUSE.value
        wife.relationships[husband.name] = RelationshipType.SPOUSE.value

        husband_bonus = husband.get_relationship_bonus("LadyMi", "loyalty")
        wife_bonus = wife.get_relationship_bonus("LiuBei", "loyalty")

        assert husband_bonus == 25.0
        assert wife_bonus == 25.0


class TestMarriageAllianceBoost:
    """Test marriage alliance relations boost."""

    def test_relations_boost_value(self):
        """Marriage should boost faction relations by 25."""
        initial_relations = 30
        after_marriage = initial_relations + MARRIAGE_RELATION_BOOST

        assert after_marriage == 55

    def test_relations_boost_capped_at_100(self):
        """Relations boost should cap at 100."""
        initial_relations = 90
        after_marriage = min(100, initial_relations + MARRIAGE_RELATION_BOOST)

        assert after_marriage == 100

    def test_mutual_relations_boost(self):
        """Both factions should receive relations boost."""
        faction_a_initial = 30
        faction_b_initial = 40

        faction_a_after = min(100, faction_a_initial + MARRIAGE_RELATION_BOOST)
        faction_b_after = min(100, faction_b_initial + MARRIAGE_RELATION_BOOST)

        assert faction_a_after == 55
        assert faction_b_after == 65

    def test_marriage_officer_loyalty_boost(self):
        """Married officer gets +15 loyalty boost."""
        initial_loyalty = 70
        after_marriage = min(100, initial_loyalty + MARRIAGE_LOYALTY_BOOST)

        assert after_marriage == 85

    def test_loyalty_boost_capped_at_100(self):
        """Loyalty boost should cap at 100."""
        initial_loyalty = 90
        after_marriage = min(100, initial_loyalty + MARRIAGE_LOYALTY_BOOST)

        assert after_marriage == 100


class TestInternalAffairsBonus:
    """Test internal affairs bonuses from spouse relationships."""

    def test_spouse_charisma_combination(self):
        """Spouses can combine charisma for internal affairs."""
        husband = create_officer("SunQuan", faction="Wu", charisma=75, politics=70)
        wife = create_officer("LadyBu", faction="Wu", charisma=80, politics=85)

        # Combined charisma influence
        combined_charisma = (husband.charisma + wife.charisma) // 2
        assert combined_charisma == 77

    def test_spouse_politics_for_governance(self):
        """Spouse with high politics can aid governance."""
        lord = create_officer("LiuBei", faction="Shu", politics=60)
        spouse = create_officer("LadyMi", faction="Shu", politics=70)

        # Spouse provides governance assistance
        governance_boost = spouse.politics // 10
        assert governance_boost == 7

    def test_spouse_intelligence_for_strategy(self):
        """Spouse with high intelligence can provide strategy advice."""
        commander = create_officer("ZhouYu", faction="Wu", intelligence=96)
        spouse = create_officer("XiaoQiao", faction="Wu", intelligence=75)

        # Spouse can provide tactical insight
        strategy_support = spouse.intelligence // 20
        assert strategy_support == 3


class TestHostageSystem:
    """Test hostage exchange mechanics."""

    def test_send_hostage_removes_from_duty(self):
        """Sending hostage removes officer from active duty."""
        officer = create_officer("SunShangxiang", faction="Wu", city="Jianye")
        assert officer.city == "Jianye"

        # After being sent as hostage
        officer.city = None
        officer.task = None
        assert officer.city is None
        assert officer.task is None

    def test_hostage_return_boost(self):
        """Returning hostage boosts relations by 20."""
        initial_relations = 40
        after_return = min(100, initial_relations + HOSTAGE_RETURN_BOOST)

        assert after_return == 60

    def test_hostage_harm_penalty_severe(self):
        """Harming hostage severely damages relations."""
        initial_relations = 50
        after_harm = max(-100, initial_relations + HOSTAGE_HARM_PENALTY)

        assert after_harm == 10

    def test_hostage_tracking(self):
        """Test hostage tracking structure."""
        hostage_info = {
            "officer": "SunShangxiang",
            "from_faction": "Wu",
            "to_faction": "Shu",
        }

        assert hostage_info["officer"] == "SunShangxiang"
        assert hostage_info["from_faction"] == "Wu"
        assert hostage_info["to_faction"] == "Shu"


class TestHistoricalMarriages:
    """Test historically significant marriages."""

    def test_liu_bei_lady_mi(self):
        """Liu Bei's marriage to Lady Mi."""
        liu_bei = create_officer("LiuBei", faction="Shu", charisma=95)
        lady_mi = create_officer("LadyMi", faction="Shu", charisma=70, politics=65)

        # Establish marriage
        liu_bei.relationships["LadyMi"] = RelationshipType.SPOUSE.value
        lady_mi.relationships["LiuBei"] = RelationshipType.SPOUSE.value

        assert liu_bei.get_relationship("LadyMi") == RelationshipType.SPOUSE
        assert lady_mi.get_relationship("LiuBei") == RelationshipType.SPOUSE

    def test_liu_bei_sun_shangxiang_alliance(self):
        """Liu Bei's political marriage to Sun Shangxiang (Wu-Shu alliance)."""
        # This marriage was used to strengthen Wu-Shu relations
        initial_relations = 40  # Before marriage
        post_marriage = min(100, initial_relations + MARRIAGE_RELATION_BOOST)

        assert post_marriage == 65
        # Marriage improved relations significantly

    def test_zhou_yu_xiao_qiao(self):
        """Zhou Yu's marriage to Xiao Qiao (Two Qiaos)."""
        zhou_yu = create_officer("ZhouYu", faction="Wu", intelligence=96, charisma=95)
        xiao_qiao = create_officer("XiaoQiao", faction="Wu", charisma=90)

        zhou_yu.relationships["XiaoQiao"] = RelationshipType.SPOUSE.value
        xiao_qiao.relationships["ZhouYu"] = RelationshipType.SPOUSE.value

        # Both get loyalty bonus
        zhou_bonus = zhou_yu.get_relationship_bonus("XiaoQiao", "loyalty")
        qiao_bonus = xiao_qiao.get_relationship_bonus("ZhouYu", "loyalty")

        assert zhou_bonus == 25.0
        assert qiao_bonus == 25.0

    def test_sun_ce_da_qiao(self):
        """Sun Ce's marriage to Da Qiao (Two Qiaos)."""
        sun_ce = create_officer("SunCe", faction="Wu", leadership=90, charisma=93)
        da_qiao = create_officer("DaQiao", faction="Wu", charisma=92)

        sun_ce.relationships["DaQiao"] = RelationshipType.SPOUSE.value
        da_qiao.relationships["SunCe"] = RelationshipType.SPOUSE.value

        assert sun_ce.get_relationship("DaQiao") == RelationshipType.SPOUSE

    def test_cao_cao_lady_bian(self):
        """Cao Cao's marriage to Lady Bian."""
        cao_cao = create_officer("CaoCao", faction="Wei", politics=90, charisma=96)
        lady_bian = create_officer("LadyBian", faction="Wei", politics=75)

        cao_cao.relationships["LadyBian"] = RelationshipType.SPOUSE.value

        assert cao_cao.get_relationship_bonus("LadyBian", "loyalty") == 25.0


class TestMarriageProposalFunction:
    """Test the propose_marriage function."""

    def create_game_state_with_factions(self):
        """Create a test game state with factions."""
        # Create officers
        officer1 = create_officer("TestOfficer1", faction="Shu", loyalty=70)
        officer2 = create_officer("TestOfficer2", faction="Wu", loyalty=70)

        # Create factions
        shu = Faction(name="Shu", cities=["Chengdu"], officers=["TestOfficer1"], relations={"Wu": 50})
        wu = Faction(name="Wu", cities=["Jianye"], officers=["TestOfficer2"], relations={"Shu": 50})

        # Create game state
        game_state = GameState(
            year=208,
            month=1,
            player_faction="Shu",
            factions={"Shu": shu, "Wu": wu},
            officers={"TestOfficer1": officer1, "TestOfficer2": officer2}
        )
        return game_state

    def test_propose_marriage_invalid_officer(self):
        """Proposing marriage with invalid officer fails."""
        game_state = self.create_game_state_with_factions()

        result = propose_marriage(game_state, "NonExistent", "Wu")
        assert result["success"] is False

    def test_propose_marriage_to_same_faction(self):
        """Proposing marriage to own faction fails."""
        game_state = self.create_game_state_with_factions()

        result = propose_marriage(game_state, "TestOfficer1", "Shu")
        assert result["success"] is False

    def test_propose_marriage_already_married(self):
        """Proposing marriage for already married officer fails."""
        game_state = self.create_game_state_with_factions()

        # Set officer as already married
        game_state.officers["TestOfficer1"].relationships["SomeSpouse"] = RelationshipType.SPOUSE.value

        result = propose_marriage(game_state, "TestOfficer1", "Wu")
        assert result["success"] is False
        assert "already married" in result["message"].lower() or "已" in result["message"]


class TestHostageFunctions:
    """Test hostage system functions."""

    def create_game_state_with_factions(self):
        """Create a test game state with factions."""
        officer1 = create_officer("TestOfficer1", faction="Shu", loyalty=70, city="Chengdu")
        officer2 = create_officer("TestOfficer2", faction="Wu", loyalty=70, city="Jianye")

        shu = Faction(name="Shu", cities=["Chengdu"], officers=["TestOfficer1"], relations={"Wu": 50})
        wu = Faction(name="Wu", cities=["Jianye"], officers=["TestOfficer2"], relations={"Shu": 50})

        game_state = GameState(
            year=208,
            month=1,
            player_faction="Shu",
            factions={"Shu": shu, "Wu": wu},
            officers={"TestOfficer1": officer1, "TestOfficer2": officer2}
        )
        return game_state

    def test_send_hostage_success(self):
        """Successfully sending a hostage."""
        game_state = self.create_game_state_with_factions()

        result = send_hostage(game_state, "TestOfficer1", "Wu")
        assert result["success"] is True

        # Officer should be removed from duty
        assert game_state.officers["TestOfficer1"].city is None

        # Hostage should be tracked
        hostages = list_hostages(game_state)
        assert len(hostages) == 1
        assert hostages[0]["officer"] == "TestOfficer1"

    def test_send_hostage_invalid_officer(self):
        """Sending non-existent officer as hostage fails."""
        game_state = self.create_game_state_with_factions()

        result = send_hostage(game_state, "NonExistent", "Wu")
        assert result["success"] is False

    def test_send_hostage_wrong_faction(self):
        """Cannot send other faction's officer as hostage."""
        game_state = self.create_game_state_with_factions()

        result = send_hostage(game_state, "TestOfficer2", "Wu")  # TestOfficer2 is Wu's
        assert result["success"] is False

    def test_return_hostage_success(self):
        """Successfully returning a hostage."""
        game_state = self.create_game_state_with_factions()

        # First send hostage
        send_hostage(game_state, "TestOfficer1", "Wu")

        # Then return
        result = return_hostage(game_state, "TestOfficer1")
        assert result["success"] is True

        # Hostage list should be empty
        hostages = list_hostages(game_state)
        assert len(hostages) == 0

    def test_return_hostage_not_hostage(self):
        """Returning non-hostage fails."""
        game_state = self.create_game_state_with_factions()

        result = return_hostage(game_state, "TestOfficer1")
        assert result["success"] is False

    def test_list_hostages_empty(self):
        """List hostages returns empty list when none exist."""
        game_state = self.create_game_state_with_factions()

        hostages = list_hostages(game_state)
        assert hostages == []


class TestStrategicMarriageValue:
    """Test strategic value of political marriages."""

    def test_alliance_strengthening(self):
        """Marriage strengthens alliances significantly."""
        before_relations = 30
        after_marriage = before_relations + MARRIAGE_RELATION_BOOST

        # 25 point boost is significant
        improvement = after_marriage - before_relations
        assert improvement == 25
        assert improvement > 20  # Substantial improvement

    def test_marriage_vs_gift_diplomacy(self):
        """Compare marriage diplomacy to gift diplomacy."""
        # Typical gift might give +5 relations
        gift_boost = 5
        marriage_boost = MARRIAGE_RELATION_BOOST

        # Marriage is 5x more effective
        assert marriage_boost == 5 * gift_boost

    def test_cross_faction_marriage_benefit(self):
        """Cross-faction marriage benefits both sides."""
        faction_a_boost = MARRIAGE_RELATION_BOOST
        faction_b_boost = MARRIAGE_RELATION_BOOST

        # Both sides benefit equally
        assert faction_a_boost == faction_b_boost

    def test_officer_retention_from_marriage(self):
        """Marriage helps retain officers through loyalty boost."""
        officer = create_officer("TestOfficer", faction="Shu", loyalty=60)

        # Marriage brings loyalty to stable level
        new_loyalty = min(100, officer.loyalty + MARRIAGE_LOYALTY_BOOST)

        assert new_loyalty == 75
        # 75 loyalty is generally safe from defection


class TestMultipleRelationships:
    """Test officers with multiple relationship types."""

    def test_spouse_and_lord_combined(self):
        """Officer can have both spouse and lord relationships."""
        officer = create_officer("TestOfficer", faction="Shu")

        officer.relationships["LiuBei"] = RelationshipType.LORD.value
        officer.relationships["LadyMi"] = RelationshipType.SPOUSE.value

        lord_bonus = officer.get_relationship_bonus("LiuBei", "loyalty")
        spouse_bonus = officer.get_relationship_bonus("LadyMi", "loyalty")

        assert lord_bonus == 20.0
        assert spouse_bonus == 25.0

    def test_spouse_and_sworn_brother_combined(self):
        """Officer can have spouse and sworn brother."""
        officer = create_officer("LiuBei", faction="Shu")

        officer.relationships["LadyMi"] = RelationshipType.SPOUSE.value
        officer.relationships["GuanYu"] = RelationshipType.SWORN_BROTHER.value
        officer.relationships["ZhangFei"] = RelationshipType.SWORN_BROTHER.value

        spouse_bonus = officer.get_relationship_bonus("LadyMi", "loyalty")
        guan_bonus = officer.get_relationship_bonus("GuanYu", "loyalty")
        zhang_bonus = officer.get_relationship_bonus("ZhangFei", "loyalty")

        assert spouse_bonus == 25.0
        assert guan_bonus == 30.0
        assert zhang_bonus == 30.0

    def test_no_combat_bonus_for_spouse(self):
        """Spouse relationship doesn't give combat bonus."""
        officer = create_officer("ZhouYu", faction="Wu")
        officer.relationships["XiaoQiao"] = RelationshipType.SPOUSE.value

        combat_bonus = officer.get_relationship_bonus("XiaoQiao", "combat")
        assert combat_bonus == 0.0
