"""Tests for the technology system (p3-08)."""
import pytest
from src.models import Technology, Faction
from src.tech import load_technologies, get_technology, get_available_techs


class TestTechnology:
    """Test Technology dataclass."""

    def test_create_technology(self):
        tech = Technology(id="test", category="military", name_key="t",
                         cost=100, turns=2)
        assert tech.id == "test"
        assert tech.category == "military"
        assert tech.prerequisites == []
        assert tech.effects == {}


class TestLoadTechnologies:
    """Test loading techs from JSON."""

    def test_loads_techs(self):
        techs = load_technologies()
        assert len(techs) >= 20

    def test_tech_structure(self):
        techs = load_technologies()
        for t in techs:
            assert isinstance(t, Technology)
            assert t.id
            assert t.category in ("military", "economy", "special")
            assert t.cost > 0
            assert t.turns > 0

    def test_categories_represented(self):
        techs = load_technologies()
        categories = {t.category for t in techs}
        assert "military" in categories
        assert "economy" in categories
        assert "special" in categories

    def test_some_have_prerequisites(self):
        techs = load_technologies()
        has_prereq = [t for t in techs if t.prerequisites]
        assert len(has_prereq) > 0

    def test_prerequisite_ids_valid(self):
        techs = load_technologies()
        all_ids = {t.id for t in techs}
        for t in techs:
            for prereq in t.prerequisites:
                assert prereq in all_ids, f"Invalid prereq {prereq} for {t.id}"


class TestGetTechnology:
    """Test getting single tech."""

    def test_get_existing(self):
        tech = get_technology("iron_weapons")
        assert tech is not None
        assert tech.id == "iron_weapons"

    def test_get_nonexistent(self):
        assert get_technology("nonexistent") is None


class TestGetAvailableTechs:
    """Test available tech filtering."""

    def test_no_research_shows_base_techs(self):
        available = get_available_techs([])
        # Should show techs with no prerequisites
        for t in available:
            assert len(t.prerequisites) == 0

    def test_with_prereqs_met(self):
        available = get_available_techs(["iron_weapons"])
        ids = [t.id for t in available]
        assert "steel_armor" in ids  # Requires iron_weapons
        assert "iron_weapons" not in ids  # Already researched

    def test_prereqs_not_met_excluded(self):
        available = get_available_techs([])
        ids = [t.id for t in available]
        assert "steel_armor" not in ids  # Requires iron_weapons

    def test_already_researched_excluded(self):
        available = get_available_techs(["irrigation"])
        ids = [t.id for t in available]
        assert "irrigation" not in ids


class TestFactionTechnologies:
    """Test Faction.technologies field."""

    def test_faction_has_technologies(self):
        f = Faction(name="Wei")
        assert f.technologies == []

    def test_faction_stores_techs(self):
        f = Faction(name="Wei", technologies=["iron_weapons", "irrigation"])
        assert "iron_weapons" in f.technologies


class TestTechI18n:
    """Test tech i18n keys."""

    def test_locale_keys_exist(self):
        import json
        with open('locales/en.json', encoding='utf-8') as f:
            en = json.load(f)
        with open('locales/zh.json', encoding='utf-8') as f:
            zh = json.load(f)

        assert 'tech' in en
        assert 'tech' in zh

        techs = load_technologies()
        for t in techs:
            # name_key format: "tech.iron_weapons"
            key = t.id
            assert key in en['tech'], f"Missing en tech.{key}"
            assert key in zh['tech'], f"Missing zh tech.{key}"
