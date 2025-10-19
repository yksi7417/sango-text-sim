"""
Pytest configuration and shared fixtures
"""
import pytest
from src.models import Officer, City, Faction, GameState


@pytest.fixture
def empty_game_state():
    """Create an empty GameState for testing"""
    return GameState()


@pytest.fixture
def test_officer():
    """Create a sample officer for testing"""
    return Officer(
        name="TestOfficer",
        faction="Shu",
        leadership=80,
        intelligence=70,
        politics=60,
        charisma=75,
        energy=100,
        loyalty=80,
        traits=["Brave"],
        city="TestCity"
    )


@pytest.fixture
def test_city():
    """Create a sample city for testing"""
    return City(
        name="TestCity",
        owner="Shu",
        gold=500,
        food=800,
        troops=300,
        defense=50,
        morale=60,
        agri=50,
        commerce=50,
        tech=40,
        walls=50
    )


@pytest.fixture
def test_faction():
    """Create a sample faction for testing"""
    return Faction(
        name="Shu",
        relations={"Wei": -20, "Wu": 10, "Shu": 0},
        cities=["Chengdu", "Hanzhong"],
        officers=["劉備", "關羽"],
        ruler="劉備"
    )


@pytest.fixture
def populated_game_state(test_officer, test_city, test_faction):
    """Create a GameState with some test data"""
    state = GameState()
    state.cities[test_city.name] = test_city
    state.officers[test_officer.name] = test_officer
    state.factions[test_faction.name] = test_faction
    state.player_faction = "Shu"
    state.adj = {
        "TestCity": ["OtherCity"],
        "OtherCity": ["TestCity"]
    }
    return state
