"""
Unit tests for utility functions
"""
import pytest
from src.models import Officer, City, Faction, GameState
from src import utils


class TestClamp:
    """Tests for clamp function"""
    
    def test_clamp_below_min(self):
        """Test clamping value below minimum"""
        assert utils.clamp(-10, 0, 100) == 0
        
    def test_clamp_above_max(self):
        """Test clamping value above maximum"""
        assert utils.clamp(150, 0, 100) == 100
        
    def test_clamp_within_range(self):
        """Test value within range unchanged"""
        assert utils.clamp(50, 0, 100) == 50
        assert utils.clamp(0, 0, 100) == 0
        assert utils.clamp(100, 0, 100) == 100
        
    def test_clamp_negative_range(self):
        """Test clamping with negative values"""
        assert utils.clamp(-50, -100, -10) == -50
        assert utils.clamp(-150, -100, -10) == -100
        assert utils.clamp(-5, -100, -10) == -10


class TestCityValidation:
    """Tests for city validation functions"""
    
    def test_valid_city_exists(self, populated_game_state):
        """Test finding an existing city"""
        city = utils.valid_city(populated_game_state, "TestCity")
        assert city is not None
        assert city.name == "TestCity"
        
    def test_valid_city_not_exists(self, empty_game_state):
        """Test looking for non-existent city"""
        city = utils.valid_city(empty_game_state, "NonExistent")
        assert city is None
        
    def test_ensure_player_city_success(self, populated_game_state):
        """Test validating player-owned city"""
        assert utils.ensure_player_city(populated_game_state, "TestCity") is True
        
    def test_ensure_player_city_not_owned(self, populated_game_state):
        """Test validating enemy-owned city"""
        enemy_city = City("EnemyCity", "Wei")
        populated_game_state.cities["EnemyCity"] = enemy_city
        assert utils.ensure_player_city(populated_game_state, "EnemyCity") is False
        
    def test_ensure_player_city_not_exists(self, empty_game_state):
        """Test validating non-existent city"""
        assert utils.ensure_player_city(empty_game_state, "NonExistent") is False


class TestAdjacency:
    """Tests for adjacency checks"""
    
    def test_is_adjacent_true(self, populated_game_state):
        """Test cities that are adjacent"""
        assert utils.is_adjacent(populated_game_state, "TestCity", "OtherCity") is True
        
    def test_is_adjacent_false(self, populated_game_state):
        """Test cities that are not adjacent"""
        assert utils.is_adjacent(populated_game_state, "TestCity", "FarCity") is False
        
    def test_is_adjacent_city_not_exists(self, empty_game_state):
        """Test adjacency with non-existent city"""
        assert utils.is_adjacent(empty_game_state, "City1", "City2") is False


class TestOfficerQueries:
    """Tests for officer query functions"""
    
    def test_officer_by_name_exists(self, populated_game_state):
        """Test finding an existing officer"""
        officer = utils.officer_by_name(populated_game_state, "TestOfficer")
        assert officer is not None
        assert officer.name == "TestOfficer"
        
    def test_officer_by_name_not_exists(self, empty_game_state):
        """Test looking for non-existent officer"""
        officer = utils.officer_by_name(empty_game_state, "NonExistent")
        assert officer is None
        
    def test_officers_in_city(self, populated_game_state):
        """Test finding officers in a city"""
        officers = utils.officers_in_city(populated_game_state, "Shu", "TestCity")
        assert len(officers) == 1
        assert officers[0].name == "TestOfficer"
        
    def test_officers_in_city_empty(self, populated_game_state):
        """Test finding officers in city with none"""
        officers = utils.officers_in_city(populated_game_state, "Shu", "EmptyCity")
        assert len(officers) == 0
        
    def test_officers_in_city_wrong_faction(self, populated_game_state):
        """Test filtering by faction"""
        officers = utils.officers_in_city(populated_game_state, "Wei", "TestCity")
        assert len(officers) == 0  # Officer is Shu, not Wei


class TestTraitEffects:
    """Tests for trait multiplier calculations"""
    
    def test_trait_mult_no_bonus(self, test_officer):
        """Test officer without relevant trait"""
        test_officer.traits = ["Brave"]
        mult = utils.trait_mult(test_officer, "farm")
        assert mult == 1.0
        
    def test_trait_mult_with_bonus(self, test_officer):
        """Test officer with relevant trait"""
        test_officer.traits = ["Benevolent"]
        mult = utils.trait_mult(test_officer, "farm")
        assert mult == 1.10
        
    def test_trait_mult_multiple_traits(self):
        """Test officer with multiple traits"""
        officer = Officer("Hero", "Shu", 80, 70, 60, 75, traits=["Brave", "Strict"])
        mult = utils.trait_mult(officer, "train")
        assert mult == 1.10
        
    def test_trait_mult_all_tasks(self):
        """Test each task has correct trait"""
        test_cases = [
            ("Strict", "train"),
            ("Benevolent", "farm"),
            ("Merchant", "trade"),
            ("Scholar", "research"),
            ("Engineer", "fortify"),
            ("Charismatic", "recruit")
        ]
        
        for trait, task in test_cases:
            officer = Officer("Test", "Shu", 80, 70, 60, 75, traits=[trait])
            mult = utils.trait_mult(officer, task)
            assert mult == 1.10, f"{trait} should give bonus to {task}"


class TestTaskResolution:
    """Tests for task synonym resolution"""
    
    def test_task_key_english(self):
        """Test English task names"""
        assert utils.task_key("farm") == "farm"
        assert utils.task_key("trade") == "trade"
        assert utils.task_key("research") == "research"
        
    def test_task_key_synonyms(self):
        """Test task synonyms"""
        assert utils.task_key("agriculture") == "farm"
        assert utils.task_key("commerce") == "trade"
        assert utils.task_key("tech") == "research"
        
    def test_task_key_chinese(self):
        """Test Chinese task names"""
        assert utils.task_key("農") == "farm"
        assert utils.task_key("商") == "trade"
        assert utils.task_key("科技") == "research"
        
    def test_task_key_case_insensitive(self):
        """Test case insensitivity"""
        assert utils.task_key("FARM") == "farm"
        assert utils.task_key("Trade") == "trade"
        assert utils.task_key("RESEARCH") == "research"
        
    def test_task_key_invalid(self):
        """Test invalid task name"""
        assert utils.task_key("invalid") is None
        assert utils.task_key("") is None


class TestFormatFactionOverview:
    """Tests for faction overview formatting"""
    
    def test_format_faction_overview(self, populated_game_state):
        """Test formatting faction overview"""
        # Add some data
        populated_game_state.cities["City2"] = City("City2", "Shu", gold=300, food=400, troops=200)
        populated_game_state.factions["Shu"].cities.append("City2")
        
        overview, resources, relations = utils.format_faction_overview(populated_game_state)
        
        assert "Shu" in overview
        assert "208" in overview  # Year
        assert isinstance(resources, str)
        assert isinstance(relations, str)
        
    def test_format_faction_overview_aggregates_resources(self, populated_game_state):
        """Test that resources are summed correctly"""
        # Add second city
        populated_game_state.cities["City2"] = City("City2", "Shu", gold=300, food=400, troops=200)
        populated_game_state.factions["Shu"].cities.append("City2")
        
        overview, resources, relations = utils.format_faction_overview(populated_game_state)
        
        # TestCity has 500 gold + City2 has 300 = 800 total
        assert "800" in resources  # Gold
        # TestCity has 800 food + City2 has 400 = 1200 total
        assert "1200" in resources  # Food


class TestFormatCityStatus:
    """Tests for city status formatting"""
    
    def test_format_city_status_exists(self, populated_game_state):
        """Test formatting existing city"""
        lines = utils.format_city_status(populated_game_state, "TestCity")
        assert lines is not None
        assert len(lines) >= 3  # Header + 2 stat lines minimum
        assert "TestCity" in lines[0]
        
    def test_format_city_status_not_exists(self, empty_game_state):
        """Test formatting non-existent city"""
        lines = utils.format_city_status(empty_game_state, "NonExistent")
        assert lines is None
        
    def test_format_city_status_with_officers(self, populated_game_state):
        """Test city with officers shows them"""
        lines = utils.format_city_status(populated_game_state, "TestCity")
        assert lines is not None
        
        # Check if officer info is included
        officer_line = [l for l in lines if "TestOfficer" in l]
        assert len(officer_line) > 0


class TestValidateMarch:
    """Tests for march validation"""
    
    def test_validate_march_success(self, populated_game_state):
        """Test valid march"""
        # Add adjacent city
        populated_game_state.cities["OtherCity"] = City("OtherCity", "Wei")
        
        valid, error = utils.validate_march(
            populated_game_state, 100, "TestCity", "OtherCity"
        )
        assert valid is True
        assert error is None
        
    def test_validate_march_not_player_city(self, populated_game_state):
        """Test marching from non-player city"""
        populated_game_state.cities["EnemyCity"] = City("EnemyCity", "Wei")
        
        valid, error = utils.validate_march(
            populated_game_state, 100, "EnemyCity", "TestCity"
        )
        assert valid is False
        assert error is not None
        
    def test_validate_march_dest_not_exists(self, populated_game_state):
        """Test marching to non-existent city"""
        valid, error = utils.validate_march(
            populated_game_state, 100, "TestCity", "NonExistent"
        )
        assert valid is False
        assert error is not None
        
    def test_validate_march_not_adjacent(self, populated_game_state):
        """Test marching to non-adjacent city"""
        populated_game_state.cities["FarCity"] = City("FarCity", "Wei")
        
        valid, error = utils.validate_march(
            populated_game_state, 100, "TestCity", "FarCity"
        )
        assert valid is False
        assert error is not None
        
    def test_validate_march_insufficient_troops(self, populated_game_state):
        """Test marching with too many troops"""
        populated_game_state.cities["OtherCity"] = City("OtherCity", "Wei")
        
        valid, error = utils.validate_march(
            populated_game_state, 99999, "TestCity", "OtherCity"
        )
        assert valid is False
        assert error is not None


@pytest.mark.unit
class TestUtilsIntegration:
    """Integration tests for utils working together"""
    
    def test_city_and_officer_workflow(self, populated_game_state):
        """Test typical workflow of querying cities and officers"""
        # Find city
        city = utils.valid_city(populated_game_state, "TestCity")
        assert city is not None
        
        # Check it's player's
        assert utils.ensure_player_city(populated_game_state, "TestCity")
        
        # Find officers in city
        officers = utils.officers_in_city(populated_game_state, "Shu", "TestCity")
        assert len(officers) == 1
        
        # Check officer traits
        officer = officers[0]
        mult = utils.trait_mult(officer, "farm")
        assert isinstance(mult, float)
