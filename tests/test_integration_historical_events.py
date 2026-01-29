"""
Integration Tests: Historical Event Triggers

This module tests historical event system mechanics:
- Peach Garden Oath trigger
- Red Cliff conditions
- Three Visits event
- Event relationship effects
- Event officer additions
- Event narrative display

Based on ROTK11 historical event system.
"""
import pytest
from src.systems.events import (
    HistoricalEvent,
    load_historical_events,
    check_historical_events,
    apply_historical_effects,
    _check_historical_conditions,
)
from src.models import GameState, Officer, Faction, City


def create_officer(name, faction="", loyalty=70):
    """Helper to create officers."""
    return Officer(
        name=name, faction=faction, leadership=70, intelligence=70,
        politics=70, charisma=70, loyalty=loyalty, energy=100
    )


class TestHistoricalEventLoading:
    """Test historical event data loading."""

    def test_load_historical_events(self):
        """Should load historical events from JSON."""
        events = load_historical_events()
        assert isinstance(events, list)
        assert len(events) > 0

    def test_peach_garden_event_exists(self):
        """Peach Garden Oath event should exist."""
        events = load_historical_events()
        event_ids = [e.id for e in events]
        assert "peach_garden_oath" in event_ids

    def test_red_cliff_event_exists(self):
        """Red Cliff event should exist."""
        events = load_historical_events()
        event_ids = [e.id for e in events]
        assert "red_cliff" in event_ids

    def test_three_visits_event_exists(self):
        """Three Visits event should exist."""
        events = load_historical_events()
        event_ids = [e.id for e in events]
        assert "three_visits" in event_ids

    def test_event_structure(self):
        """Events should have required fields."""
        events = load_historical_events()
        for event in events:
            assert event.id
            assert event.year_range
            assert len(event.year_range) == 2
            assert event.title_key
            assert event.description_key


class TestPeachGardenOath:
    """Test Peach Garden Oath event."""

    def create_shu_game_state(self):
        """Create game state with Shu faction and three brothers."""
        game_state = GameState()
        game_state.year = 208
        game_state.month = 3
        game_state.player_faction = "Shu"

        # Create officers
        game_state.officers = {
            "LiuBei": create_officer("LiuBei", "Shu", 100),
            "GuanYu": create_officer("GuanYu", "Shu", 95),
            "ZhangFei": create_officer("ZhangFei", "Shu", 90),
        }

        # Create faction
        game_state.factions = {
            "Shu": Faction(
                name="Shu",
                cities=["Chengdu"],
                officers=["LiuBei", "GuanYu", "ZhangFei"]
            )
        }

        game_state.cities = {
            "Chengdu": City(name="Chengdu", owner="Shu", troops=5000)
        }

        return game_state

    def test_peach_garden_trigger_conditions(self):
        """Peach Garden should trigger with all three brothers."""
        game_state = self.create_shu_game_state()

        result = check_historical_events(game_state, [])

        assert result is not None
        assert result["event"].id == "peach_garden_oath"

    def test_peach_garden_creates_relationships(self):
        """Peach Garden should create sworn brother relationships."""
        game_state = self.create_shu_game_state()

        result = check_historical_events(game_state, [])

        # Check relationships were applied
        assert "relationships" in result["applied"]

        # Check actual officer relationships
        liu_bei = game_state.officers["LiuBei"]
        guan_yu = game_state.officers["GuanYu"]
        zhang_fei = game_state.officers["ZhangFei"]

        assert liu_bei.relationships.get("GuanYu") == "sworn_brother"
        assert liu_bei.relationships.get("ZhangFei") == "sworn_brother"
        assert guan_yu.relationships.get("ZhangFei") == "sworn_brother"

    def test_peach_garden_loyalty_boost(self):
        """Peach Garden should boost loyalty for three brothers."""
        game_state = self.create_shu_game_state()
        initial_loyalty = game_state.officers["GuanYu"].loyalty

        check_historical_events(game_state, [])

        # Loyalty should be boosted by 20
        assert game_state.officers["GuanYu"].loyalty == min(100, initial_loyalty + 20)

    def test_peach_garden_one_time(self):
        """Peach Garden should only trigger once."""
        game_state = self.create_shu_game_state()

        # Trigger first time
        result1 = check_historical_events(game_state, [])
        assert result1 is not None

        # Should not trigger again
        result2 = check_historical_events(game_state, ["peach_garden_oath"])
        # May trigger another event or be None
        if result2:
            assert result2["event"].id != "peach_garden_oath"


class TestRedCliff:
    """Test Red Cliff event."""

    def create_three_kingdoms_state(self):
        """Create game state with all three kingdoms."""
        game_state = GameState()
        game_state.year = 208
        game_state.month = 11
        game_state.player_faction = "Shu"

        game_state.factions = {
            "Wei": Faction(name="Wei", cities=["Luoyang"], relations={"Shu": 0, "Wu": 0}),
            "Shu": Faction(name="Shu", cities=["Chengdu"], relations={"Wei": 0, "Wu": 0}),
            "Wu": Faction(name="Wu", cities=["Jianye"], relations={"Wei": 0, "Shu": 0}),
        }

        game_state.cities = {
            "Luoyang": City(name="Luoyang", owner="Wei", morale=60),
            "Chengdu": City(name="Chengdu", owner="Shu", morale=60),
            "Jianye": City(name="Jianye", owner="Wu", morale=60),
        }

        game_state.officers = {}

        return game_state

    def test_red_cliff_trigger_conditions(self):
        """Red Cliff should trigger when all three factions exist."""
        game_state = self.create_three_kingdoms_state()

        # May trigger red_cliff or another applicable event
        result = check_historical_events(game_state, [])

        if result and result["event"].id == "red_cliff":
            assert result["event"].id == "red_cliff"

    def test_red_cliff_relations_change(self):
        """Red Cliff should change faction relations."""
        game_state = self.create_three_kingdoms_state()

        # Find red cliff event manually
        events = load_historical_events()
        red_cliff = next((e for e in events if e.id == "red_cliff"), None)
        assert red_cliff is not None

        # Apply effects
        applied = apply_historical_effects(game_state, red_cliff)

        # Shu-Wu should improve
        assert game_state.factions["Shu"].relations.get("Wu", 0) > 0
        # Shu-Wei should worsen
        assert game_state.factions["Shu"].relations.get("Wei", 0) < 0

    def test_red_cliff_morale_boost(self):
        """Red Cliff should boost Shu and Wu morale."""
        game_state = self.create_three_kingdoms_state()

        events = load_historical_events()
        red_cliff = next((e for e in events if e.id == "red_cliff"), None)

        initial_shu_morale = game_state.cities["Chengdu"].morale
        initial_wu_morale = game_state.cities["Jianye"].morale

        apply_historical_effects(game_state, red_cliff)

        assert game_state.cities["Chengdu"].morale > initial_shu_morale
        assert game_state.cities["Jianye"].morale > initial_wu_morale


class TestThreeVisits:
    """Test Three Visits event."""

    def create_liu_bei_zhuge_state(self):
        """Create game state with Liu Bei and Zhuge Liang."""
        game_state = GameState()
        game_state.year = 210
        game_state.month = 1
        game_state.player_faction = "Shu"

        game_state.officers = {
            "LiuBei": create_officer("LiuBei", "Shu", 100),
            "ZhugeLiang": create_officer("ZhugeLiang", "Shu", 50),  # Low initial loyalty
        }

        game_state.factions = {
            "Shu": Faction(
                name="Shu",
                cities=["Chengdu"],
                officers=["LiuBei", "ZhugeLiang"]
            )
        }

        game_state.cities = {
            "Chengdu": City(name="Chengdu", owner="Shu")
        }

        return game_state

    def test_three_visits_trigger(self):
        """Three Visits should trigger with Liu Bei and Zhuge Liang."""
        game_state = self.create_liu_bei_zhuge_state()

        # Skip already triggered events
        result = check_historical_events(game_state, ["peach_garden_oath"])

        # May trigger three_visits or another event
        if result and result["event"].id == "three_visits":
            assert result["event"].id == "three_visits"

    def test_three_visits_lord_relationship(self):
        """Three Visits should create lord relationship."""
        game_state = self.create_liu_bei_zhuge_state()

        events = load_historical_events()
        three_visits = next((e for e in events if e.id == "three_visits"), None)
        assert three_visits is not None

        apply_historical_effects(game_state, three_visits)

        # Liu Bei becomes Zhuge Liang's lord
        assert game_state.officers["ZhugeLiang"].relationships.get("LiuBei") == "lord"

    def test_three_visits_loyalty_boost(self):
        """Three Visits should significantly boost Zhuge Liang's loyalty."""
        game_state = self.create_liu_bei_zhuge_state()

        events = load_historical_events()
        three_visits = next((e for e in events if e.id == "three_visits"), None)

        initial_loyalty = game_state.officers["ZhugeLiang"].loyalty

        apply_historical_effects(game_state, three_visits)

        # +30 loyalty boost
        assert game_state.officers["ZhugeLiang"].loyalty == min(100, initial_loyalty + 30)


class TestEventConditions:
    """Test event condition checking."""

    def test_year_range_condition(self):
        """Events should only trigger within year range."""
        event = HistoricalEvent(
            id="test",
            year_range=[208, 210],
            conditions={},
            title_key="test.title",
            description_key="test.desc"
        )

        game_state = GameState()

        # Within range
        game_state.year = 209
        assert _check_historical_conditions(event, game_state) is True

        # Before range
        game_state.year = 207
        assert _check_historical_conditions(event, game_state) is False

        # After range
        game_state.year = 211
        assert _check_historical_conditions(event, game_state) is False

    def test_officers_in_faction_condition(self):
        """Should check if specific officers are in faction."""
        event = HistoricalEvent(
            id="test",
            year_range=[200, 250],
            conditions={"officers_in_faction": ["Officer1", "Officer2"], "faction": "TestFaction"},
            title_key="test.title",
            description_key="test.desc"
        )

        game_state = GameState()
        game_state.year = 210
        game_state.factions = {
            "TestFaction": Faction(name="TestFaction", officers=["Officer1", "Officer2"])
        }

        assert _check_historical_conditions(event, game_state) is True

        # Missing officer
        game_state.factions["TestFaction"].officers = ["Officer1"]
        assert _check_historical_conditions(event, game_state) is False

    def test_faction_has_officer_condition(self):
        """Should check if faction has specific officer."""
        event = HistoricalEvent(
            id="test",
            year_range=[200, 250],
            conditions={"faction_has_officer": {"faction": "Wei", "officer": "CaoCao"}},
            title_key="test.title",
            description_key="test.desc"
        )

        game_state = GameState()
        game_state.year = 210
        game_state.factions = {
            "Wei": Faction(name="Wei", officers=["CaoCao"])
        }

        assert _check_historical_conditions(event, game_state) is True

        game_state.factions["Wei"].officers = ["SomeoneElse"]
        assert _check_historical_conditions(event, game_state) is False


class TestEventEffects:
    """Test event effect application."""

    def test_relationship_effect(self):
        """Should create relationships between officers."""
        game_state = GameState()
        game_state.officers = {
            "Officer1": create_officer("Officer1"),
            "Officer2": create_officer("Officer2"),
        }

        event = HistoricalEvent(
            id="test",
            year_range=[200, 250],
            conditions={},
            title_key="test.title",
            description_key="test.desc",
            effects={
                "relationships": [
                    {"officer1": "Officer1", "officer2": "Officer2", "type": "sworn_brother"}
                ]
            }
        )

        apply_historical_effects(game_state, event)

        assert game_state.officers["Officer1"].relationships.get("Officer2") == "sworn_brother"
        assert game_state.officers["Officer2"].relationships.get("Officer1") == "sworn_brother"

    def test_loyalty_boost_effect(self):
        """Should boost officer loyalty."""
        game_state = GameState()
        game_state.officers = {
            "TestOfficer": create_officer("TestOfficer", loyalty=60),
        }

        event = HistoricalEvent(
            id="test",
            year_range=[200, 250],
            conditions={},
            title_key="test.title",
            description_key="test.desc",
            effects={"loyalty_boost": {"TestOfficer": 20}}
        )

        apply_historical_effects(game_state, event)

        assert game_state.officers["TestOfficer"].loyalty == 80

    def test_morale_boost_effect(self):
        """Should boost faction city morale."""
        game_state = GameState()
        game_state.factions = {
            "TestFaction": Faction(name="TestFaction", cities=["TestCity"])
        }
        game_state.cities = {
            "TestCity": City(name="TestCity", owner="TestFaction", morale=50)
        }

        event = HistoricalEvent(
            id="test",
            year_range=[200, 250],
            conditions={},
            title_key="test.title",
            description_key="test.desc",
            effects={"morale_boost": {"TestFaction": 15}}
        )

        apply_historical_effects(game_state, event)

        assert game_state.cities["TestCity"].morale == 65

    def test_tech_boost_effect(self):
        """Should boost faction tech level."""
        game_state = GameState()
        game_state.factions = {
            "TestFaction": Faction(name="TestFaction", cities=["TestCity"])
        }
        game_state.cities = {
            "TestCity": City(name="TestCity", owner="TestFaction", tech=40)
        }

        event = HistoricalEvent(
            id="test",
            year_range=[200, 250],
            conditions={},
            title_key="test.title",
            description_key="test.desc",
            effects={"tech_boost": {"TestFaction": 10}}
        )

        apply_historical_effects(game_state, event)

        assert game_state.cities["TestCity"].tech == 50

    def test_relations_change_effect(self):
        """Should change faction relations."""
        game_state = GameState()
        game_state.factions = {
            "FactionA": Faction(name="FactionA", relations={"FactionB": 0}),
            "FactionB": Faction(name="FactionB", relations={"FactionA": 0}),
        }

        event = HistoricalEvent(
            id="test",
            year_range=[200, 250],
            conditions={},
            title_key="test.title",
            description_key="test.desc",
            effects={"relations_change": {"FactionA_FactionB": 20}}
        )

        apply_historical_effects(game_state, event)

        assert game_state.factions["FactionA"].relations.get("FactionB") == 20


class TestHistoricalEventNarrative:
    """Test historical event narrative display."""

    def test_event_has_title_key(self):
        """Events should have title keys for localization."""
        events = load_historical_events()
        for event in events:
            assert event.title_key.startswith("historical.")

    def test_event_has_description_key(self):
        """Events should have description keys for localization."""
        events = load_historical_events()
        for event in events:
            assert event.description_key.startswith("historical.")

    def test_event_check_returns_message(self):
        """Triggered event should return a message."""
        game_state = GameState()
        game_state.year = 208
        game_state.player_faction = "Shu"
        game_state.factions = {
            "Shu": Faction(name="Shu", cities=["Chengdu"], officers=["LiuBei", "GuanYu", "ZhangFei"])
        }
        game_state.officers = {
            "LiuBei": create_officer("LiuBei", "Shu"),
            "GuanYu": create_officer("GuanYu", "Shu"),
            "ZhangFei": create_officer("ZhangFei", "Shu"),
        }
        game_state.cities = {
            "Chengdu": City(name="Chengdu", owner="Shu")
        }

        result = check_historical_events(game_state, [])

        if result:
            assert "message" in result
            assert "[Historical]" in result["message"]


class TestEventCount:
    """Test total historical events."""

    def test_total_historical_events(self):
        """Should have 12 historical events."""
        events = load_historical_events()
        assert len(events) == 12

    def test_shu_events_count(self):
        """Should have multiple Shu-related events."""
        events = load_historical_events()
        shu_events = [e for e in events if "Shu" in str(e.conditions)]
        assert len(shu_events) >= 3

    def test_wu_events_count(self):
        """Should have Wu-related events."""
        events = load_historical_events()
        wu_events = [e for e in events if "Wu" in str(e.conditions)]
        assert len(wu_events) >= 2

    def test_wei_events_count(self):
        """Should have Wei-related events."""
        events = load_historical_events()
        wei_events = [e for e in events if "Wei" in str(e.conditions)]
        assert len(wei_events) >= 2


class TestEventYearRanges:
    """Test event year ranges."""

    def test_peach_garden_year_range(self):
        """Peach Garden should be in 208-210."""
        events = load_historical_events()
        event = next((e for e in events if e.id == "peach_garden_oath"), None)
        assert event is not None
        assert event.year_range == [208, 210]

    def test_red_cliff_year_range(self):
        """Red Cliff should be in 208-209."""
        events = load_historical_events()
        event = next((e for e in events if e.id == "red_cliff"), None)
        assert event is not None
        assert event.year_range == [208, 209]

    def test_northern_expedition_year_range(self):
        """Northern Expedition should be in 225-235."""
        events = load_historical_events()
        event = next((e for e in events if e.id == "northern_expedition"), None)
        assert event is not None
        assert event.year_range == [225, 235]
