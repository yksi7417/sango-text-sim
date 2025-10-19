"""
Unit tests for data models
"""
import pytest
from dataclasses import asdict
from src.models import Officer, City, Faction, GameState


class TestOfficer:
    """Tests for Officer dataclass"""
    
    def test_officer_creation(self):
        """Test creating an officer with minimal attributes"""
        officer = Officer("TestOfficer", "Shu", 80, 70, 60, 75)
        assert officer.name == "TestOfficer"
        assert officer.faction == "Shu"
        assert officer.leadership == 80
        assert officer.intelligence == 70
        assert officer.politics == 60
        assert officer.charisma == 75
        
    def test_officer_defaults(self):
        """Test officer default values"""
        officer = Officer("Test", "Wei", 50, 50, 50, 50)
        assert officer.energy == 100
        assert officer.loyalty == 70
        assert officer.traits == []
        assert officer.city is None
        assert officer.task is None
        assert officer.task_city is None
        assert officer.busy is False
        
    def test_officer_with_traits(self):
        """Test officer with traits"""
        officer = Officer(
            "Hero", "Wu", 90, 80, 70, 85,
            traits=["Brave", "Scholar"]
        )
        assert "Brave" in officer.traits
        assert "Scholar" in officer.traits
        assert len(officer.traits) == 2
        
    def test_officer_serialization(self):
        """Test officer can be serialized to dict"""
        officer = Officer("Test", "Shu", 80, 70, 60, 75, loyalty=85)
        data = asdict(officer)
        assert data["name"] == "Test"
        assert data["loyalty"] == 85
        assert isinstance(data, dict)


class TestCity:
    """Tests for City dataclass"""
    
    def test_city_creation(self):
        """Test creating a city with minimal attributes"""
        city = City("TestCity", "Shu")
        assert city.name == "TestCity"
        assert city.owner == "Shu"
        
    def test_city_defaults(self):
        """Test city default values"""
        city = City("City", "Wei")
        assert city.gold == 500
        assert city.food == 800
        assert city.troops == 300
        assert city.defense == 50
        assert city.morale == 60
        assert city.agri == 50
        assert city.commerce == 50
        assert city.tech == 40
        assert city.walls == 50
        
    def test_city_custom_values(self):
        """Test city with custom values"""
        city = City(
            "Capital", "Wu",
            gold=1000, food=1500, troops=500,
            defense=80, morale=75
        )
        assert city.gold == 1000
        assert city.food == 1500
        assert city.troops == 500
        assert city.defense == 80
        assert city.morale == 75
        
    def test_city_serialization(self):
        """Test city can be serialized"""
        city = City("Test", "Shu", gold=600)
        data = asdict(city)
        assert data["name"] == "Test"
        assert data["gold"] == 600


class TestFaction:
    """Tests for Faction dataclass"""
    
    def test_faction_creation(self):
        """Test creating a faction"""
        faction = Faction("Shu")
        assert faction.name == "Shu"
        
    def test_faction_defaults(self):
        """Test faction default values"""
        faction = Faction("Wei")
        assert faction.relations == {}
        assert faction.cities == []
        assert faction.officers == []
        assert faction.ruler == ""
        
    def test_faction_with_data(self):
        """Test faction with relations and assets"""
        faction = Faction(
            "Wu",
            relations={"Wei": -20, "Shu": 10},
            cities=["Jianye", "Wuchang"],
            officers=["孫權", "周瑜"],
            ruler="孫權"
        )
        assert faction.relations["Wei"] == -20
        assert faction.relations["Shu"] == 10
        assert len(faction.cities) == 2
        assert len(faction.officers) == 2
        assert faction.ruler == "孫權"


class TestGameState:
    """Tests for GameState dataclass"""
    
    def test_game_state_creation(self):
        """Test creating a game state"""
        state = GameState()
        assert state.year == 208
        assert state.month == 1
        
    def test_game_state_defaults(self):
        """Test game state default values"""
        state = GameState()
        assert state.factions == {}
        assert state.cities == {}
        assert state.adj == {}
        assert state.officers == {}
        assert state.player_faction == "Shu"
        assert state.player_ruler == "劉備"
        assert state.difficulty == "Normal"
        assert state.messages == []
        
    def test_game_state_log(self):
        """Test game state logging"""
        state = GameState()
        state.log("Test message")
        assert len(state.messages) == 1
        assert state.messages[0] == "Test message"
        
    def test_game_state_multiple_logs(self):
        """Test multiple log messages"""
        state = GameState()
        state.log("Message 1")
        state.log("Message 2")
        state.log("Message 3")
        assert len(state.messages) == 3
        assert state.messages[-1] == "Message 3"
        
    def test_game_state_with_data(self):
        """Test game state with cities and factions"""
        state = GameState()
        state.cities["City1"] = City("City1", "Shu")
        state.factions["Shu"] = Faction("Shu", cities=["City1"])
        
        assert "City1" in state.cities
        assert "Shu" in state.factions
        assert state.factions["Shu"].cities[0] == "City1"
        
    def test_game_state_adjacency(self):
        """Test adjacency map"""
        state = GameState()
        state.adj = {
            "City1": ["City2", "City3"],
            "City2": ["City1"],
            "City3": ["City1"]
        }
        assert len(state.adj["City1"]) == 2
        assert "City2" in state.adj["City1"]


@pytest.mark.unit
class TestModelIntegration:
    """Integration tests for models working together"""
    
    def test_full_game_setup(self):
        """Test setting up a complete game scenario"""
        state = GameState()
        
        # Create cities
        city1 = City("Chengdu", "Shu", gold=600, troops=400)
        city2 = City("Hanzhong", "Shu", gold=500, troops=300)
        state.cities["Chengdu"] = city1
        state.cities["Hanzhong"] = city2
        
        # Create faction
        faction = Faction(
            "Shu",
            relations={"Wei": -10, "Wu": 5},
            cities=["Chengdu", "Hanzhong"],
            ruler="劉備"
        )
        state.factions["Shu"] = faction
        
        # Create officers
        officer1 = Officer("劉備", "Shu", 86, 80, 88, 96, city="Chengdu")
        officer2 = Officer("關羽", "Shu", 98, 79, 92, 84, city="Chengdu")
        state.officers["劉備"] = officer1
        state.officers["關羽"] = officer2
        
        # Verify everything is connected
        assert len(state.cities) == 2
        assert len(state.factions) == 1
        assert len(state.officers) == 2
        assert state.factions["Shu"].cities[0] == "Chengdu"
        assert state.officers["劉備"].faction == "Shu"
