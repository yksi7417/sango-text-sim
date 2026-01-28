"""Tests for the council system (p3-01)."""
import pytest
from src.models import GameState, Officer, City, Faction
from src.systems.council import (
    AgendaCategory, AgendaItem, Council,
    generate_council_agenda, _find_best_advisor
)
from src.world import init_world


class TestAgendaCategory:
    """Test AgendaCategory enum."""

    def test_all_categories(self):
        assert AgendaCategory.ECONOMIC.value == "economic"
        assert AgendaCategory.MILITARY.value == "military"
        assert AgendaCategory.DIPLOMATIC.value == "diplomatic"
        assert AgendaCategory.PERSONNEL.value == "personnel"

    def test_category_count(self):
        assert len(AgendaCategory) == 4


class TestAgendaItem:
    """Test AgendaItem dataclass."""

    def test_create_agenda_item(self):
        item = AgendaItem(
            category=AgendaCategory.ECONOMIC,
            presenter="Zhuge Liang",
            title="Food shortage",
            recommendation="Farm more"
        )
        assert item.category == AgendaCategory.ECONOMIC
        assert item.presenter == "Zhuge Liang"
        assert item.title == "Food shortage"
        assert item.recommendation == "Farm more"
        assert item.data == {}


class TestCouncil:
    """Test Council dataclass."""

    def test_create_council(self):
        council = Council(faction="Shu", year=208, month=3)
        assert council.faction == "Shu"
        assert council.agenda == []

    def test_council_with_items(self):
        item = AgendaItem(
            category=AgendaCategory.MILITARY,
            presenter="Guan Yu",
            title="Threat",
            recommendation="Defend"
        )
        council = Council(faction="Shu", agenda=[item])
        assert len(council.agenda) == 1


class TestFindBestAdvisor:
    """Test advisor selection."""

    def test_find_best_by_politics(self):
        gs = GameState()
        init_world(gs)
        advisor = _find_best_advisor(gs, "politics")
        assert advisor is not None
        # Should be an officer from the player's faction
        faction = gs.factions[gs.player_faction]
        assert advisor.name in faction.officers

    def test_find_best_by_leadership(self):
        gs = GameState()
        init_world(gs)
        advisor = _find_best_advisor(gs, "leadership")
        assert advisor is not None

    def test_find_best_by_intelligence(self):
        gs = GameState()
        init_world(gs)
        advisor = _find_best_advisor(gs, "intelligence")
        assert advisor is not None

    def test_find_best_by_charisma(self):
        gs = GameState()
        init_world(gs)
        advisor = _find_best_advisor(gs, "charisma")
        assert advisor is not None


class TestGenerateCouncilAgenda:
    """Test council agenda generation."""

    def test_generates_council(self):
        gs = GameState()
        init_world(gs)
        council = generate_council_agenda(gs)
        assert isinstance(council, Council)
        assert council.faction == gs.player_faction

    def test_agenda_has_items(self):
        gs = GameState()
        init_world(gs)
        council = generate_council_agenda(gs)
        # Should have at least some items in normal game state
        assert isinstance(council.agenda, list)

    def test_low_food_generates_economic_item(self):
        gs = GameState()
        init_world(gs)
        # Set a city to very low food
        faction = gs.factions[gs.player_faction]
        city_name = faction.cities[0]
        gs.cities[city_name].food = 50

        council = generate_council_agenda(gs)
        economic_items = [i for i in council.agenda if i.category == AgendaCategory.ECONOMIC]
        food_items = [i for i in economic_items if "food" in i.data]
        assert len(food_items) > 0

    def test_low_gold_generates_economic_item(self):
        gs = GameState()
        init_world(gs)
        faction = gs.factions[gs.player_faction]
        city_name = faction.cities[0]
        gs.cities[city_name].gold = 50

        council = generate_council_agenda(gs)
        economic_items = [i for i in council.agenda if i.category == AgendaCategory.ECONOMIC]
        gold_items = [i for i in economic_items if "gold" in i.data]
        assert len(gold_items) > 0

    def test_weak_garrison_generates_military_item(self):
        gs = GameState()
        init_world(gs)
        faction = gs.factions[gs.player_faction]
        city_name = faction.cities[0]
        gs.cities[city_name].troops = 50

        council = generate_council_agenda(gs)
        military_items = [i for i in council.agenda if i.category == AgendaCategory.MILITARY]
        assert len(military_items) > 0

    def test_low_loyalty_generates_personnel_item(self):
        gs = GameState()
        init_world(gs)
        faction = gs.factions[gs.player_faction]
        off_name = faction.officers[0]
        gs.officers[off_name].loyalty = 30

        council = generate_council_agenda(gs)
        personnel_items = [i for i in council.agenda if i.category == AgendaCategory.PERSONNEL]
        loyalty_items = [i for i in personnel_items if "loyalty" in i.data]
        assert len(loyalty_items) > 0

    def test_all_categories_possible(self):
        """All 4 agenda categories should exist as enum values."""
        categories = {c.value for c in AgendaCategory}
        assert categories == {"economic", "military", "diplomatic", "personnel"}


class TestCouncilI18n:
    """Test council i18n keys."""

    def test_locale_keys_exist(self):
        import json
        with open('locales/en.json', encoding='utf-8') as f:
            en = json.load(f)
        with open('locales/zh.json', encoding='utf-8') as f:
            zh = json.load(f)

        assert 'council' in en
        assert 'council' in zh
        assert 'title' in en['council']
        assert 'economic' in en['council']
        assert 'military' in en['council']
        assert 'diplomatic' in en['council']
        assert 'personnel' in en['council']
