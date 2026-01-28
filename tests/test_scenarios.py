"""Tests for multiple scenario support."""
import pytest
from src.world import load_scenario, list_scenarios


class TestListScenarios:
    def test_lists_scenarios(self):
        scenarios = list_scenarios()
        assert len(scenarios) >= 4  # 190, 200, 208, 220

    def test_scenario_has_fields(self):
        for s in list_scenarios():
            assert "id" in s
            assert "name" in s
            assert "year" in s

    def test_includes_208(self):
        ids = [s["id"] for s in list_scenarios()]
        assert "china_208" in ids

    def test_includes_190(self):
        ids = [s["id"] for s in list_scenarios()]
        assert "china_190" in ids

    def test_includes_220(self):
        ids = [s["id"] for s in list_scenarios()]
        assert "china_220" in ids


class TestLoadScenarios:
    def test_load_190(self):
        data = load_scenario("china_190")
        assert data["metadata"]["year"] == 190
        assert len(data["cities"]) == 6

    def test_load_200(self):
        data = load_scenario("china_200")
        assert data["metadata"]["year"] == 200
        assert len(data["cities"]) == 6

    def test_load_220(self):
        data = load_scenario("china_220")
        assert data["metadata"]["year"] == 220
        assert len(data["cities"]) == 6

    def test_scenario_owners_differ(self):
        d190 = load_scenario("china_190")
        d208 = load_scenario("china_208")
        owners_190 = {c["id"]: c["owner"] for c in d190["cities"]}
        owners_208 = {c["id"]: c["owner"] for c in d208["cities"]}
        # At least some owners should differ
        assert owners_190 != owners_208
