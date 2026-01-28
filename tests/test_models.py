"""
Unit tests for data models
"""
import pytest
from dataclasses import asdict
from src.models import Officer, City, Faction, GameState, Season, get_current_season, TerrainType


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


class TestSeason:
    """Tests for Season enum and related functions"""

    def test_season_enum_exists(self):
        """Test that Season enum has all four seasons"""
        assert hasattr(Season, 'SPRING')
        assert hasattr(Season, 'SUMMER')
        assert hasattr(Season, 'AUTUMN')
        assert hasattr(Season, 'WINTER')

    def test_get_current_season_spring(self):
        """Test spring season (months 3-5)"""
        assert get_current_season(3) == Season.SPRING
        assert get_current_season(4) == Season.SPRING
        assert get_current_season(5) == Season.SPRING

    def test_get_current_season_summer(self):
        """Test summer season (months 6-8)"""
        assert get_current_season(6) == Season.SUMMER
        assert get_current_season(7) == Season.SUMMER
        assert get_current_season(8) == Season.SUMMER

    def test_get_current_season_autumn(self):
        """Test autumn season (months 9-11)"""
        assert get_current_season(9) == Season.AUTUMN
        assert get_current_season(10) == Season.AUTUMN
        assert get_current_season(11) == Season.AUTUMN

    def test_get_current_season_winter(self):
        """Test winter season (months 12, 1, 2)"""
        assert get_current_season(12) == Season.WINTER
        assert get_current_season(1) == Season.WINTER
        assert get_current_season(2) == Season.WINTER

    def test_get_current_season_boundary_values(self):
        """Test boundary month values"""
        # Test edge cases at season transitions
        assert get_current_season(2) == Season.WINTER
        assert get_current_season(3) == Season.SPRING
        assert get_current_season(5) == Season.SPRING
        assert get_current_season(6) == Season.SUMMER
        assert get_current_season(8) == Season.SUMMER
        assert get_current_season(9) == Season.AUTUMN
        assert get_current_season(11) == Season.AUTUMN
        assert get_current_season(12) == Season.WINTER

    def test_season_enum_values(self):
        """Test that season enum values are distinct"""
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
        assert len(seasons) == len(set(seasons))


class TestTerrainType:
    """Tests for TerrainType enum"""

    def test_terrain_enum_exists(self):
        """Test that TerrainType enum has all five terrain types"""
        assert hasattr(TerrainType, 'PLAINS')
        assert hasattr(TerrainType, 'MOUNTAIN')
        assert hasattr(TerrainType, 'FOREST')
        assert hasattr(TerrainType, 'COASTAL')
        assert hasattr(TerrainType, 'RIVER')

    def test_terrain_enum_values(self):
        """Test that terrain enum values match expected strings"""
        assert TerrainType.PLAINS.value == "plains"
        assert TerrainType.MOUNTAIN.value == "mountain"
        assert TerrainType.FOREST.value == "forest"
        assert TerrainType.COASTAL.value == "coastal"
        assert TerrainType.RIVER.value == "river"

    def test_terrain_enum_from_string(self):
        """Test creating TerrainType from string value"""
        assert TerrainType("plains") == TerrainType.PLAINS
        assert TerrainType("mountain") == TerrainType.MOUNTAIN
        assert TerrainType("forest") == TerrainType.FOREST
        assert TerrainType("coastal") == TerrainType.COASTAL
        assert TerrainType("river") == TerrainType.RIVER

    def test_terrain_enum_unique_values(self):
        """Test that all terrain types are distinct"""
        terrains = [TerrainType.PLAINS, TerrainType.MOUNTAIN, TerrainType.FOREST,
                   TerrainType.COASTAL, TerrainType.RIVER]
        assert len(terrains) == len(set(terrains))

    def test_city_with_terrain(self):
        """Test that City can be created with terrain"""
        city = City(
            name="TestCity",
            owner="Wei",
            terrain=TerrainType.MOUNTAIN
        )
        assert city.terrain == TerrainType.MOUNTAIN

    def test_city_default_terrain(self):
        """Test that City defaults to PLAINS terrain"""
        city = City(name="TestCity", owner="Wei")
        assert city.terrain == TerrainType.PLAINS


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
