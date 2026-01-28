"""Tests for the officer relationship system (p3-04)."""
import pytest
from src.models import RelationshipType, Officer, GameState
from src.world import init_world


class TestRelationshipType:
    """Test RelationshipType enum."""

    def test_all_types(self):
        assert RelationshipType.SWORN_BROTHER.value == "sworn_brother"
        assert RelationshipType.RIVAL.value == "rival"
        assert RelationshipType.LORD.value == "lord"
        assert RelationshipType.SPOUSE.value == "spouse"
        assert RelationshipType.MENTOR.value == "mentor"

    def test_type_count(self):
        assert len(RelationshipType) == 5


class TestOfficerRelationships:
    """Test Officer relationship methods."""

    def test_get_relationship(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "sworn_brother"})
        assert off.get_relationship("B") == RelationshipType.SWORN_BROTHER

    def test_get_relationship_none(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50)
        assert off.get_relationship("B") is None

    def test_get_relationship_invalid(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "unknown_type"})
        assert off.get_relationship("B") is None

    def test_sworn_brother_loyalty_bonus(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "sworn_brother"})
        assert off.get_relationship_bonus("B", "loyalty") == 30.0

    def test_lord_loyalty_bonus(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "lord"})
        assert off.get_relationship_bonus("B", "loyalty") == 20.0

    def test_rival_combat_bonus(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "rival"})
        assert off.get_relationship_bonus("B", "combat") == 0.15

    def test_no_relationship_no_bonus(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50)
        assert off.get_relationship_bonus("B", "loyalty") == 0.0
        assert off.get_relationship_bonus("B", "combat") == 0.0

    def test_spouse_loyalty_bonus(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "spouse"})
        assert off.get_relationship_bonus("B", "loyalty") == 25.0

    def test_mentor_loyalty_bonus(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "mentor"})
        assert off.get_relationship_bonus("B", "loyalty") == 15.0

    def test_rival_loyalty_penalty(self):
        off = Officer(name="A", faction="Wei", leadership=80, intelligence=70,
                      politics=60, charisma=50,
                      relationships={"B": "rival"})
        assert off.get_relationship_bonus("B", "loyalty") == -10.0


class TestRelationshipsFromJSON:
    """Test that relationships load from JSON data."""

    def test_liu_bei_has_sworn_brothers(self):
        gs = GameState()
        init_world(gs)
        liu_bei = gs.officers.get("LiuBei")
        assert liu_bei is not None
        assert liu_bei.get_relationship("GuanYu") == RelationshipType.SWORN_BROTHER
        assert liu_bei.get_relationship("ZhangFei") == RelationshipType.SWORN_BROTHER

    def test_guan_yu_rival(self):
        gs = GameState()
        init_world(gs)
        guan_yu = gs.officers.get("GuanYu")
        assert guan_yu is not None
        rel = guan_yu.get_relationship("LuBu")
        # LuBu may or may not exist in the loaded officers
        if "LuBu" in guan_yu.relationships:
            assert rel == RelationshipType.RIVAL

    def test_zhuge_liang_lord_relationship(self):
        gs = GameState()
        init_world(gs)
        zhuge = gs.officers.get("ZhugeLiang")
        assert zhuge is not None
        assert zhuge.get_relationship("LiuBei") == RelationshipType.LORD

    def test_officers_have_relationships_dict(self):
        gs = GameState()
        init_world(gs)
        for off in gs.officers.values():
            assert hasattr(off, 'relationships')
            assert isinstance(off.relationships, dict)
