"""Tests for the council display renderer (p3-02)."""
import pytest
from src.models import GameState
from src.systems.council import (
    AgendaCategory, AgendaItem, Council, generate_council_agenda
)
from src.display.council_view import render_council, render_agenda_item
from src.world import init_world


class TestRenderCouncil:
    """Test council rendering."""

    def test_render_empty_council(self):
        council = Council(faction="Shu", year=208, month=3)
        output = render_council(council)
        assert "208" in output
        assert "03" in output

    def test_render_with_items(self):
        item = AgendaItem(
            category=AgendaCategory.ECONOMIC,
            presenter="Zhuge Liang",
            title="Food shortage in Chengdu",
            recommendation="Assign officers to farm."
        )
        council = Council(faction="Shu", year=208, month=3, agenda=[item])
        output = render_council(council)
        assert "Food shortage" in output
        assert "Zhuge Liang" in output
        assert "farm" in output

    def test_render_multiple_items(self):
        items = [
            AgendaItem(
                category=AgendaCategory.ECONOMIC,
                presenter="A",
                title="Economic issue",
                recommendation="Fix it"
            ),
            AgendaItem(
                category=AgendaCategory.MILITARY,
                presenter="B",
                title="Military issue",
                recommendation="Defend"
            ),
        ]
        council = Council(faction="Shu", agenda=items)
        output = render_council(council)
        assert "1." in output
        assert "2." in output

    def test_category_icons(self):
        items = [
            AgendaItem(category=AgendaCategory.ECONOMIC, presenter="A", title="E", recommendation="R"),
            AgendaItem(category=AgendaCategory.MILITARY, presenter="B", title="M", recommendation="R"),
            AgendaItem(category=AgendaCategory.DIPLOMATIC, presenter="C", title="D", recommendation="R"),
            AgendaItem(category=AgendaCategory.PERSONNEL, presenter="D", title="P", recommendation="R"),
        ]
        council = Council(faction="Shu", agenda=items)
        output = render_council(council)
        assert "[$]" in output
        assert "[!]" in output
        assert "[&]" in output
        assert "[@]" in output


class TestRenderAgendaItem:
    """Test individual agenda item rendering."""

    def test_render_single_item(self):
        item = AgendaItem(
            category=AgendaCategory.MILITARY,
            presenter="Guan Yu",
            title="Enemy at the gates",
            recommendation="Prepare defenses"
        )
        output = render_agenda_item(item, 1)
        assert "Enemy at the gates" in output
        assert "Guan Yu" in output

    def test_item_index(self):
        item = AgendaItem(
            category=AgendaCategory.ECONOMIC,
            presenter="A",
            title="Title",
            recommendation="Rec"
        )
        output = render_agenda_item(item, 3)
        assert "Item 3" in output


class TestCouncilIntegration:
    """Test council display with real game state."""

    def test_full_council_renders(self):
        gs = GameState()
        init_world(gs)
        # Create conditions that trigger items
        faction = gs.factions[gs.player_faction]
        city_name = faction.cities[0]
        gs.cities[city_name].food = 50
        gs.cities[city_name].troops = 50

        council = generate_council_agenda(gs)
        output = render_council(council)
        assert isinstance(output, str)
        assert len(output) > 0
