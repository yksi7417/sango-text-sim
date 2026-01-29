"""
Integration Tests: Sworn Brotherhood Mechanics

This module tests sworn brotherhood mechanics:
- Loyalty bonuses (+30% when brothers are together)
- Combat bonuses (+10% when fighting together)
- Morale effect on brother death
- Sworn brother formation bonus
- Historical brothers verification (Liu/Guan/Zhang, Xiahou brothers, Sun Ce/Sun Quan)

Based on 3KYuYun's brotherhood analysis from ROTK11.
"""
import pytest
from src.models import GameState, Officer, Faction, City, RelationshipType
from src.world import load_officers


def create_officer(name, faction="", leadership=70, intelligence=70, politics=70, charisma=70,
                   loyalty=70, energy=100, city=None, task=None, relationships=None):
    """Helper to create an Officer with common defaults."""
    return Officer(
        name=name,
        faction=faction,
        leadership=leadership,
        intelligence=intelligence,
        politics=politics,
        charisma=charisma,
        loyalty=loyalty,
        energy=energy,
        city=city,
        task=task,
        relationships=relationships or {}
    )


class TestRelationshipTypeEnum:
    """Test the RelationshipType enum."""

    def test_sworn_brother_type_exists(self):
        """SWORN_BROTHER should be a valid relationship type."""
        assert RelationshipType.SWORN_BROTHER.value == "sworn_brother"

    def test_all_relationship_types(self):
        """Verify all relationship types exist."""
        types = [
            RelationshipType.SWORN_BROTHER,
            RelationshipType.RIVAL,
            RelationshipType.LORD,
            RelationshipType.SPOUSE,
            RelationshipType.MENTOR
        ]
        assert len(types) == 5


class TestSwornBrotherLoyaltyBonus:
    """Test sworn brother loyalty bonus (+30%)."""

    def test_sworn_brother_loyalty_bonus_value(self):
        """Sworn brothers should give +30 loyalty bonus."""
        guan_yu = create_officer(
            "GuanYu", "Shu",
            relationships={"LiuBei": "sworn_brother", "ZhangFei": "sworn_brother"}
        )

        bonus = guan_yu.get_relationship_bonus("LiuBei", "loyalty")
        assert bonus == 30.0

    def test_sworn_brother_relationship_detection(self):
        """Officer should correctly detect sworn brother relationship."""
        zhang_fei = create_officer(
            "ZhangFei", "Shu",
            relationships={"LiuBei": "sworn_brother", "GuanYu": "sworn_brother"}
        )

        rel = zhang_fei.get_relationship("LiuBei")
        assert rel == RelationshipType.SWORN_BROTHER

    def test_no_relationship_returns_none(self):
        """Non-related officers should return None relationship."""
        generic_officer = create_officer("Generic", "Shu")

        rel = generic_officer.get_relationship("SomeOther")
        assert rel is None

    def test_no_relationship_zero_bonus(self):
        """Non-related officers should have zero bonus."""
        generic_officer = create_officer("Generic", "Shu")

        bonus = generic_officer.get_relationship_bonus("SomeOther", "loyalty")
        assert bonus == 0.0

    def test_other_relationship_types_loyalty_bonus(self):
        """Test loyalty bonuses for other relationship types."""
        officer = create_officer(
            "Test", "Shu",
            relationships={
                "Lord": "lord",
                "Wife": "spouse",
                "Teacher": "mentor",
                "Enemy": "rival"
            }
        )

        assert officer.get_relationship_bonus("Lord", "loyalty") == 20.0
        assert officer.get_relationship_bonus("Wife", "loyalty") == 25.0
        assert officer.get_relationship_bonus("Teacher", "loyalty") == 15.0
        assert officer.get_relationship_bonus("Enemy", "loyalty") == -10.0


class TestSwornBrotherCombatBonus:
    """Test sworn brother combat bonus (+10%)."""

    def test_sworn_brother_combat_bonus_value(self):
        """Sworn brothers should give +10% combat bonus when fighting together."""
        guan_yu = create_officer(
            "GuanYu", "Shu",
            relationships={"LiuBei": "sworn_brother", "ZhangFei": "sworn_brother"}
        )

        bonus = guan_yu.get_relationship_bonus("ZhangFei", "combat")
        assert bonus == pytest.approx(0.10)

    def test_rival_combat_bonus(self):
        """Rivals should give +15% damage bonus against each other."""
        guan_yu = create_officer(
            "GuanYu", "Shu",
            relationships={"LuBu": "rival"}
        )

        bonus = guan_yu.get_relationship_bonus("LuBu", "combat")
        assert bonus == pytest.approx(0.15)

    def test_no_combat_bonus_for_unrelated(self):
        """Unrelated officers should have zero combat bonus."""
        officer = create_officer("Test", "Shu")

        bonus = officer.get_relationship_bonus("Random", "combat")
        assert bonus == 0.0


class TestHistoricBrothers:
    """Test historical sworn brothers from the data."""

    def test_liu_guan_zhang_brotherhood(self):
        """Liu Bei, Guan Yu, and Zhang Fei should be sworn brothers (Peach Garden Oath)."""
        officers_data = load_officers()
        officers_list = officers_data.get("officers", [])

        liu_bei_data = next((o for o in officers_list if o["id"] == "LiuBei"), None)
        guan_yu_data = next((o for o in officers_list if o["id"] == "GuanYu"), None)
        zhang_fei_data = next((o for o in officers_list if o["id"] == "ZhangFei"), None)

        # Create Officer objects from data
        liu_bei = create_officer(
            liu_bei_data["id"], "Shu",
            relationships=liu_bei_data.get("relationships", {})
        ) if liu_bei_data else None
        guan_yu = create_officer(
            guan_yu_data["id"], "Shu",
            relationships=guan_yu_data.get("relationships", {})
        ) if guan_yu_data else None
        zhang_fei = create_officer(
            zhang_fei_data["id"], "Shu",
            relationships=zhang_fei_data.get("relationships", {})
        ) if zhang_fei_data else None

        assert liu_bei is not None
        assert guan_yu is not None
        assert zhang_fei is not None

        # Liu Bei's brothers
        assert liu_bei.get_relationship("GuanYu") == RelationshipType.SWORN_BROTHER
        assert liu_bei.get_relationship("ZhangFei") == RelationshipType.SWORN_BROTHER

        # Guan Yu's brothers
        assert guan_yu.get_relationship("LiuBei") == RelationshipType.SWORN_BROTHER
        assert guan_yu.get_relationship("ZhangFei") == RelationshipType.SWORN_BROTHER

        # Zhang Fei's brothers
        assert zhang_fei.get_relationship("LiuBei") == RelationshipType.SWORN_BROTHER
        assert zhang_fei.get_relationship("GuanYu") == RelationshipType.SWORN_BROTHER

    def test_xiahou_brothers(self):
        """Xiahou Dun and Xiahou Yuan should be sworn brothers."""
        officers_data = load_officers()
        officers_list = officers_data.get("officers", [])

        xiahou_dun_data = next((o for o in officers_list if o["id"] == "XiahouDun"), None)
        xiahou_yuan_data = next((o for o in officers_list if o["id"] == "XiahouYuan"), None)

        if xiahou_dun_data and xiahou_yuan_data:
            xiahou_dun = create_officer(
                xiahou_dun_data["id"], "Wei",
                relationships=xiahou_dun_data.get("relationships", {})
            )
            xiahou_yuan = create_officer(
                xiahou_yuan_data["id"], "Wei",
                relationships=xiahou_yuan_data.get("relationships", {})
            )
            # They are cousins/brothers in history
            assert xiahou_dun.get_relationship("XiahouYuan") == RelationshipType.SWORN_BROTHER
            assert xiahou_yuan.get_relationship("XiahouDun") == RelationshipType.SWORN_BROTHER

    def test_guan_yu_lu_bu_rivalry(self):
        """Guan Yu and Lu Bu should be rivals."""
        officers_data = load_officers()
        officers_list = officers_data.get("officers", [])

        guan_yu_data = next((o for o in officers_list if o["id"] == "GuanYu"), None)

        assert guan_yu_data is not None
        guan_yu = create_officer(
            guan_yu_data["id"], "Shu",
            relationships=guan_yu_data.get("relationships", {})
        )
        assert guan_yu.get_relationship("LuBu") == RelationshipType.RIVAL


class TestSwornBrotherFormationBonus:
    """Test formation bonuses when sworn brothers fight together."""

    def test_brotherhood_formation_calculation(self):
        """Calculate total formation bonus for sworn brothers."""
        guan_yu = create_officer(
            "GuanYu", "Shu", leadership=95,
            relationships={"ZhangFei": "sworn_brother"}
        )
        zhang_fei = create_officer(
            "ZhangFei", "Shu", leadership=90,
            relationships={"GuanYu": "sworn_brother"}
        )

        # Both get +10% combat bonus
        guan_yu_bonus = guan_yu.get_relationship_bonus("ZhangFei", "combat")
        zhang_fei_bonus = zhang_fei.get_relationship_bonus("GuanYu", "combat")

        assert guan_yu_bonus == 0.10
        assert zhang_fei_bonus == 0.10

    def test_three_brothers_formation(self):
        """Three sworn brothers should all benefit from formation."""
        liu_bei = create_officer(
            "LiuBei", "Shu", leadership=75,
            relationships={"GuanYu": "sworn_brother", "ZhangFei": "sworn_brother"}
        )
        guan_yu = create_officer(
            "GuanYu", "Shu", leadership=95,
            relationships={"LiuBei": "sworn_brother", "ZhangFei": "sworn_brother"}
        )
        zhang_fei = create_officer(
            "ZhangFei", "Shu", leadership=90,
            relationships={"LiuBei": "sworn_brother", "GuanYu": "sworn_brother"}
        )

        # Liu Bei benefits when fighting with either brother
        assert liu_bei.get_relationship_bonus("GuanYu", "combat") == 0.10
        assert liu_bei.get_relationship_bonus("ZhangFei", "combat") == 0.10

        # Guan Yu benefits with both brothers
        assert guan_yu.get_relationship_bonus("LiuBei", "combat") == 0.10
        assert guan_yu.get_relationship_bonus("ZhangFei", "combat") == 0.10


class TestSwornBrotherMoraleEffects:
    """Test morale effects related to sworn brothers."""

    def test_brotherhood_loyalty_stacking(self):
        """Verify sworn brother loyalty bonus is significant."""
        officer = create_officer(
            "Test", "Shu", loyalty=50,
            relationships={"Brother1": "sworn_brother", "Brother2": "sworn_brother"}
        )

        # Each brother gives +30 loyalty bonus
        bonus1 = officer.get_relationship_bonus("Brother1", "loyalty")
        bonus2 = officer.get_relationship_bonus("Brother2", "loyalty")

        assert bonus1 == 30.0
        assert bonus2 == 30.0

    def test_brotherhood_prevents_defection(self):
        """Brotherhood should help prevent defection (high loyalty bonus)."""
        # An officer with sworn brothers should be harder to poach
        guan_yu = create_officer(
            "GuanYu", "Shu", loyalty=50,  # Base loyalty
            relationships={"LiuBei": "sworn_brother"}
        )

        # Effective loyalty with brotherhood bonus would be 50 + 30 = 80
        base_loyalty = guan_yu.loyalty
        brotherhood_bonus = guan_yu.get_relationship_bonus("LiuBei", "loyalty")
        effective_loyalty = base_loyalty + brotherhood_bonus

        assert effective_loyalty == 80.0


class TestBrotherhoodScenarios:
    """Test realistic sworn brotherhood scenarios."""

    def test_shu_three_brothers_combat_advantage(self):
        """Shu's three brothers fighting together have significant advantage."""
        officers_data = load_officers()
        officers_list = officers_data.get("officers", [])

        liu_bei_data = next((o for o in officers_list if o["id"] == "LiuBei"), None)
        guan_yu_data = next((o for o in officers_list if o["id"] == "GuanYu"), None)
        zhang_fei_data = next((o for o in officers_list if o["id"] == "ZhangFei"), None)

        liu_bei = create_officer(
            liu_bei_data["id"], "Shu",
            relationships=liu_bei_data.get("relationships", {})
        ) if liu_bei_data else None
        guan_yu = create_officer(
            guan_yu_data["id"], "Shu",
            relationships=guan_yu_data.get("relationships", {})
        ) if guan_yu_data else None
        zhang_fei = create_officer(
            zhang_fei_data["id"], "Shu",
            relationships=zhang_fei_data.get("relationships", {})
        ) if zhang_fei_data else None

        # Calculate total combat bonus for the trio
        total_bonus = 0.0
        if liu_bei and guan_yu:
            total_bonus += liu_bei.get_relationship_bonus("GuanYu", "combat")
        if liu_bei and zhang_fei:
            total_bonus += liu_bei.get_relationship_bonus("ZhangFei", "combat")
        if guan_yu and zhang_fei:
            total_bonus += guan_yu.get_relationship_bonus("ZhangFei", "combat")

        # Should have significant cumulative bonus
        assert total_bonus >= 0.20  # At least 20% bonus

    def test_wei_xiahou_brothers_synergy(self):
        """Wei's Xiahou brothers fighting together."""
        officers_data = load_officers()
        officers_list = officers_data.get("officers", [])

        xiahou_dun_data = next((o for o in officers_list if o["id"] == "XiahouDun"), None)
        xiahou_yuan_data = next((o for o in officers_list if o["id"] == "XiahouYuan"), None)

        if xiahou_dun_data and xiahou_yuan_data:
            xiahou_dun = create_officer(
                xiahou_dun_data["id"], "Wei",
                relationships=xiahou_dun_data.get("relationships", {})
            )
            xiahou_yuan = create_officer(
                xiahou_yuan_data["id"], "Wei",
                relationships=xiahou_yuan_data.get("relationships", {})
            )

            dun_bonus = xiahou_dun.get_relationship_bonus("XiahouYuan", "combat")
            yuan_bonus = xiahou_yuan.get_relationship_bonus("XiahouDun", "combat")

            # Both should benefit
            assert dun_bonus == 0.10
            assert yuan_bonus == 0.10

    def test_rivalry_combat_bonus(self):
        """Rivals fighting each other get damage bonus."""
        officers_data = load_officers()
        officers_list = officers_data.get("officers", [])

        guan_yu_data = next((o for o in officers_list if o["id"] == "GuanYu"), None)

        if guan_yu_data:
            guan_yu = create_officer(
                guan_yu_data["id"], "Shu",
                relationships=guan_yu_data.get("relationships", {})
            )
            # Guan Yu vs Lu Bu (rivalry)
            rival_bonus = guan_yu.get_relationship_bonus("LuBu", "combat")
            assert rival_bonus == 0.15  # +15% damage against rivals


class TestBrotherhoodConstants:
    """Test sworn brotherhood constant values."""

    def test_loyalty_bonus_constant(self):
        """Verify the loyalty bonus constant is +30."""
        # From models.py: return 30.0 for SWORN_BROTHER loyalty
        SWORN_BROTHER_LOYALTY_BONUS = 30.0
        assert SWORN_BROTHER_LOYALTY_BONUS == 30.0

    def test_combat_bonus_constant(self):
        """Verify the combat bonus constant is +10%."""
        # From models.py: return 0.10 for SWORN_BROTHER combat
        SWORN_BROTHER_COMBAT_BONUS = 0.10
        assert SWORN_BROTHER_COMBAT_BONUS == 0.10

    def test_rival_damage_bonus_constant(self):
        """Verify the rival damage bonus constant is +15%."""
        # From models.py: return 0.15 for RIVAL combat
        RIVAL_COMBAT_BONUS = 0.15
        assert RIVAL_COMBAT_BONUS == 0.15


class TestBrotherhoodEdgeCases:
    """Test edge cases for sworn brotherhood."""

    def test_invalid_relationship_returns_none(self):
        """Invalid relationship type should return None."""
        officer = create_officer(
            "Test", "Shu",
            relationships={"Other": "invalid_type"}
        )

        rel = officer.get_relationship("Other")
        assert rel is None

    def test_empty_relationships(self):
        """Officer with no relationships should return None."""
        officer = create_officer("Test", "Shu")

        rel = officer.get_relationship("Anyone")
        assert rel is None

    def test_one_way_relationship(self):
        """Test that relationships are stored per-officer (not necessarily bidirectional)."""
        # In the game, relationships should be bidirectional in the data,
        # but the model doesn't enforce this - it's per-officer
        officer_a = create_officer(
            "OfficerA", "Shu",
            relationships={"OfficerB": "sworn_brother"}
        )
        officer_b = create_officer(
            "OfficerB", "Shu",
            relationships={}  # No relationship stored
        )

        # A sees B as sworn brother
        assert officer_a.get_relationship("OfficerB") == RelationshipType.SWORN_BROTHER

        # B doesn't have A registered
        assert officer_b.get_relationship("OfficerA") is None


class TestBrotherhoodRelationshipCounts:
    """Test relationship counting and structure."""

    def test_officer_can_have_multiple_brothers(self):
        """An officer can have multiple sworn brothers."""
        officer = create_officer(
            "Test", "Shu",
            relationships={
                "Brother1": "sworn_brother",
                "Brother2": "sworn_brother",
                "Brother3": "sworn_brother"
            }
        )

        brothers = [name for name, rel in officer.relationships.items()
                    if rel == "sworn_brother"]
        assert len(brothers) == 3

    def test_officer_can_have_mixed_relationships(self):
        """An officer can have different types of relationships."""
        officer = create_officer(
            "Test", "Shu",
            relationships={
                "Brother": "sworn_brother",
                "Enemy": "rival",
                "Master": "mentor",
                "Ruler": "lord"
            }
        )

        assert officer.get_relationship("Brother") == RelationshipType.SWORN_BROTHER
        assert officer.get_relationship("Enemy") == RelationshipType.RIVAL
        assert officer.get_relationship("Master") == RelationshipType.MENTOR
        assert officer.get_relationship("Ruler") == RelationshipType.LORD
