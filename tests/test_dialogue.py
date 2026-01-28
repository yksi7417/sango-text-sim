"""Tests for the officer dialogue system."""
import pytest
from src.models import Officer
from src.systems.dialogue import generate_dialogue, _get_style, CONTEXTS


def _make_officer(traits=None, leadership=70, intelligence=70, politics=70, charisma=70):
    return Officer(name="TestOfficer", faction="Shu",
                   leadership=leadership, intelligence=intelligence,
                   politics=politics, charisma=charisma,
                   traits=traits or [])


class TestGetStyle:
    def test_brave_trait(self):
        off = _make_officer(traits=["Brave"])
        assert _get_style(off) == "brave"

    def test_scholar_trait(self):
        off = _make_officer(traits=["Scholar"])
        assert _get_style(off) == "scholar"

    def test_charismatic_trait(self):
        off = _make_officer(traits=["Charismatic"])
        assert _get_style(off) == "charismatic"

    def test_merchant_trait(self):
        off = _make_officer(traits=["Merchant"])
        assert _get_style(off) == "merchant"

    def test_fallback_to_leadership(self):
        off = _make_officer(leadership=95, intelligence=50, politics=50, charisma=50)
        assert _get_style(off) == "brave"

    def test_fallback_to_intelligence(self):
        off = _make_officer(leadership=50, intelligence=95, politics=50, charisma=50)
        assert _get_style(off) == "scholar"

    def test_first_trait_wins(self):
        off = _make_officer(traits=["Brave", "Scholar"])
        assert _get_style(off) == "brave"


class TestGenerateDialogue:
    def test_all_contexts_return_text(self):
        off = _make_officer(traits=["Brave"])
        for ctx in CONTEXTS:
            result = generate_dialogue(off, ctx)
            assert len(result) > 0

    def test_scholar_dialogue(self):
        off = _make_officer(traits=["Scholar"])
        result = generate_dialogue(off, "greeting")
        assert len(result) > 0

    def test_default_fallback(self):
        off = _make_officer(traits=[])
        off.leadership = 50
        off.intelligence = 50
        off.politics = 50
        off.charisma = 51  # charismatic wins
        result = generate_dialogue(off, "greeting")
        assert len(result) > 0

    def test_battle_context(self):
        off = _make_officer(traits=["Brave"])
        result = generate_dialogue(off, "battle_start")
        assert len(result) > 0

    def test_victory_context(self):
        off = _make_officer(traits=["Charismatic"])
        result = generate_dialogue(off, "victory")
        assert len(result) > 0

    def test_defeat_context(self):
        off = _make_officer(traits=["Scholar"])
        result = generate_dialogue(off, "defeat")
        assert len(result) > 0
