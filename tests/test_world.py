"""
Tests for the world initialization module.

This module tests world setup including:
- City creation and configuration
- Officer initialization
- Faction setup with diplomatic relations
- Map adjacency configuration
"""

import pytest
from src.models import Officer, City, Faction, GameState
from src import world


class TestAddOfficer:
    """Tests for adding officers to game state."""
    
    def test_add_officer_to_empty_state(self, empty_game_state):
        """Adding officer should update both officers dict and faction list."""
        empty_game_state.factions["Shu"] = Faction(name="Shu", cities=[], officers=[], relations={})
        
        officer = Officer(
            name="TestOfficer",
            faction="Shu",
            leadership=80,
            intelligence=70,
            politics=60,
            charisma=75,
            loyalty=80,
            traits=["Brave"],
            city="TestCity"
        )
        
        world.add_officer(empty_game_state, officer)
        
        assert "TestOfficer" in empty_game_state.officers
        assert empty_game_state.officers["TestOfficer"] == officer
        assert "TestOfficer" in empty_game_state.factions["Shu"].officers
    
    def test_add_multiple_officers(self, empty_game_state):
        """Adding multiple officers should update state correctly."""
        empty_game_state.factions["Shu"] = Faction(name="Shu", cities=[], officers=[], relations={})
        
        officer1 = Officer(
            name="Officer1", faction="Shu", leadership=80, intelligence=70,
            politics=60, charisma=75, loyalty=80, traits=[], city="City1"
        )
        officer2 = Officer(
            name="Officer2", faction="Shu", leadership=85, intelligence=75,
            politics=65, charisma=80, loyalty=85, traits=[], city="City2"
        )
        
        world.add_officer(empty_game_state, officer1)
        world.add_officer(empty_game_state, officer2)
        
        assert len(empty_game_state.officers) == 2
        assert len(empty_game_state.factions["Shu"].officers) == 2


class TestInitWorld:
    """Tests for world initialization."""
    
    def test_init_world_creates_cities(self, empty_game_state):
        """World initialization should create all cities."""
        world.init_world(empty_game_state)
        
        # Should create 6 cities
        assert len(empty_game_state.cities) == 6
        assert "Xuchang" in empty_game_state.cities
        assert "Luoyang" in empty_game_state.cities
        assert "Chengdu" in empty_game_state.cities
        assert "Hanzhong" in empty_game_state.cities
        assert "Jianye" in empty_game_state.cities
        assert "Wuchang" in empty_game_state.cities
    
    def test_init_world_creates_factions(self, empty_game_state):
        """World initialization should create three factions."""
        world.init_world(empty_game_state)
        
        assert len(empty_game_state.factions) == 3
        assert "Wei" in empty_game_state.factions
        assert "Shu" in empty_game_state.factions
        assert "Wu" in empty_game_state.factions
    
    def test_init_world_creates_officers(self, empty_game_state):
        """World initialization should create all officers."""
        world.init_world(empty_game_state)

        # Should create 31 officers (loaded from legendary.json)
        assert len(empty_game_state.officers) >= 30  # At least 30 from JSON
        assert "LiuBei" in empty_game_state.officers
        assert "GuanYu" in empty_game_state.officers
        assert "ZhangFei" in empty_game_state.officers
        assert "CaoCao" in empty_game_state.officers
        assert "ZhangLiao" in empty_game_state.officers
        assert "SunQuan" in empty_game_state.officers
        assert "ZhouYu" in empty_game_state.officers
    
    def test_init_world_sets_adjacency(self, empty_game_state):
        """World initialization should configure map adjacency."""
        world.init_world(empty_game_state)
        
        assert "Xuchang" in empty_game_state.adj
        assert "Luoyang" in empty_game_state.adj["Xuchang"]
        assert "Hanzhong" in empty_game_state.adj["Xuchang"]
    
    def test_init_world_assigns_cities_to_factions(self, empty_game_state):
        """Cities should be assigned to their owning factions."""
        world.init_world(empty_game_state)
        
        # Wei should own Xuchang and Luoyang
        assert "Xuchang" in empty_game_state.factions["Wei"].cities
        assert "Luoyang" in empty_game_state.factions["Wei"].cities
        
        # Shu should own Chengdu and Hanzhong
        assert "Chengdu" in empty_game_state.factions["Shu"].cities
        assert "Hanzhong" in empty_game_state.factions["Shu"].cities
        
        # Wu should own Jianye and Wuchang
        assert "Jianye" in empty_game_state.factions["Wu"].cities
        assert "Wuchang" in empty_game_state.factions["Wu"].cities
    
    def test_init_world_assigns_officers_to_factions(self, empty_game_state):
        """Officers should be assigned to their factions."""
        world.init_world(empty_game_state)
        
        # Each faction should have officers
        assert len(empty_game_state.factions["Wei"].officers) > 0
        assert len(empty_game_state.factions["Shu"].officers) > 0
        assert len(empty_game_state.factions["Wu"].officers) > 0
        
        # Check specific officer assignments
        assert "LiuBei" in empty_game_state.factions["Shu"].officers
        assert "CaoCao" in empty_game_state.factions["Wei"].officers
        assert "SunQuan" in empty_game_state.factions["Wu"].officers
    
    def test_init_world_sets_player_faction(self, empty_game_state):
        """Player faction should be set correctly."""
        world.init_world(empty_game_state, player_choice="Wei")
        
        assert empty_game_state.player_faction == "Wei"
        assert empty_game_state.player_ruler == "CaoCao"
    
    def test_init_world_default_player_faction(self, empty_game_state):
        """Default player faction should be Shu."""
        world.init_world(empty_game_state)
        
        assert empty_game_state.player_faction == "Shu"
        assert empty_game_state.player_ruler == "LiuBei"
    
    def test_init_world_sets_diplomatic_relations(self, empty_game_state):
        """Factions should have diplomatic relations set."""
        world.init_world(empty_game_state)
        
        # Each faction should have relations with all factions
        for faction_name, faction in empty_game_state.factions.items():
            assert len(faction.relations) == 3
            assert faction.relations[faction_name] == 0  # Self-relation is 0
    
    def test_init_world_sets_initial_time(self, empty_game_state):
        """Initial game time should be set."""
        world.init_world(empty_game_state)
        
        assert empty_game_state.year == 208
        assert empty_game_state.month == 1
    
    def test_init_world_clears_messages(self, empty_game_state):
        """Messages should be cleared on init."""
        empty_game_state.messages = ["Old message"]
        
        world.init_world(empty_game_state)
        
        # Should have welcome message only (time message removed for web UI)
        assert len(empty_game_state.messages) == 1
        assert 'Welcome' in empty_game_state.messages[0] or '歡迎' in empty_game_state.messages[0]
    
    def test_init_world_with_seed(self, empty_game_state):
        """Same seed should produce same diplomatic relations."""
        world.init_world(empty_game_state, seed=123)
        relations1 = {f: dict(faction.relations) for f, faction in empty_game_state.factions.items()}
        
        empty_game_state2 = GameState()
        world.init_world(empty_game_state2, seed=123)
        relations2 = {f: dict(faction.relations) for f, faction in empty_game_state2.factions.items()}
        
        assert relations1 == relations2
    
    def test_init_world_different_seeds(self, empty_game_state):
        """Different seeds should produce different diplomatic relations."""
        world.init_world(empty_game_state, seed=123)
        relations1 = {f: dict(faction.relations) for f, faction in empty_game_state.factions.items()}
        
        empty_game_state2 = GameState()
        world.init_world(empty_game_state2, seed=456)
        relations2 = {f: dict(faction.relations) for f, faction in empty_game_state2.factions.items()}
        
        # At least one relation should be different
        assert relations1 != relations2


class TestCityData:
    """Tests for city data configuration."""
    
    def test_city_data_completeness(self):
        """All cities should have complete data."""
        for city_name, data in world.CITY_DATA.items():
            assert "owner" in data
            assert "gold" in data
            assert "food" in data
            assert "troops" in data
            assert "defense" in data
            assert "morale" in data
            assert "agri" in data
            assert "commerce" in data
            assert "tech" in data
            assert "walls" in data
    
    def test_city_data_reasonable_values(self):
        """City data should have reasonable value ranges."""
        for city_name, data in world.CITY_DATA.items():
            assert data["gold"] >= 0
            assert data["food"] >= 0
            assert data["troops"] >= 0
            assert 0 <= data["defense"] <= 100
            assert 0 <= data["morale"] <= 100
            assert 0 <= data["agri"] <= 100
            assert 0 <= data["commerce"] <= 100
            assert 0 <= data["tech"] <= 100
            assert 0 <= data["walls"] <= 100


class TestOfficerData:
    """Tests for officer data configuration."""
    
    def test_officer_data_completeness(self):
        """All officers should have complete data."""
        for officer_data in world.OFFICER_DATA:
            assert "id" in officer_data
            assert "faction" in officer_data
            assert "leadership" in officer_data
            assert "intelligence" in officer_data
            assert "politics" in officer_data
            assert "charisma" in officer_data
            assert "loyalty" in officer_data
            assert "traits" in officer_data
            # Note: "city" is optional - will be assigned by init_world if not present
    
    def test_officer_data_reasonable_stats(self):
        """Officer stats should be in reasonable ranges."""
        for officer_data in world.OFFICER_DATA:
            assert 0 <= officer_data["leadership"] <= 100
            assert 0 <= officer_data["intelligence"] <= 100
            assert 0 <= officer_data["politics"] <= 100
            assert 0 <= officer_data["charisma"] <= 100
            assert 0 <= officer_data["loyalty"] <= 100
    
    def test_officer_factions_valid(self):
        """Officers should belong to valid factions."""
        valid_factions = ["Wei", "Shu", "Wu"]
        for officer_data in world.OFFICER_DATA:
            assert officer_data["faction"] in valid_factions


class TestAdjacencyMap:
    """Tests for map adjacency configuration."""
    
    def test_adjacency_symmetry(self):
        """Adjacency should be symmetric (if A adjacent to B, then B adjacent to A)."""
        for city, neighbors in world.ADJACENCY_MAP.items():
            for neighbor in neighbors:
                assert neighbor in world.ADJACENCY_MAP
                assert city in world.ADJACENCY_MAP[neighbor], \
                    f"{city} is adjacent to {neighbor}, but {neighbor} is not adjacent to {city}"
    
    def test_adjacency_no_self_loops(self):
        """Cities should not be adjacent to themselves."""
        for city, neighbors in world.ADJACENCY_MAP.items():
            assert city not in neighbors
    
    def test_all_cities_connected(self):
        """All cities should be part of the adjacency map."""
        cities_in_data = set(world.CITY_DATA.keys())
        cities_in_adj = set(world.ADJACENCY_MAP.keys())
        
        assert cities_in_data == cities_in_adj


class TestLoadOfficers:
    """Test load_officers function."""

    def test_load_officers_default(self):
        """Verify load_officers loads legendary roster by default."""
        data = world.load_officers()
        assert "metadata" in data
        assert "officers" in data
        assert data["metadata"]["roster_id"] == "legendary"

    def test_load_officers_specific(self):
        """Verify load_officers can load specific roster."""
        data = world.load_officers("legendary")
        assert data["metadata"]["roster_id"] == "legendary"

    def test_load_officers_nonexistent(self):
        """Verify load_officers raises error for missing file."""
        import pytest

        with pytest.raises(FileNotFoundError):
            world.load_officers("nonexistent")

    def test_officer_data_loaded_from_json(self):
        """Verify OFFICER_DATA is populated from JSON."""
        # Load JSON directly
        roster_data = world.load_officers("legendary")

        # Verify OFFICER_DATA has officers from JSON
        officer_ids = {officer["id"] for officer in world.OFFICER_DATA}

        # Should have more than the original 7 hardcoded officers
        assert len(officer_ids) >= 30, "Should have at least 30 officers from legendary.json"

        # Verify some new officers are present
        new_officers = ["ZhaoYun", "MaChao", "HuangZhong", "XuChu", "LuSu", "GanNing"]
        for officer_id in new_officers:
            assert officer_id in officer_ids, f"Officer {officer_id} should be loaded from JSON"

    def test_officer_data_maintains_backward_compatibility(self):
        """Verify OFFICER_DATA structure is compatible with existing code."""
        required_fields = ["id", "faction", "leadership", "intelligence",
                          "politics", "charisma", "loyalty", "traits"]

        for officer_data in world.OFFICER_DATA:
            for field in required_fields:
                assert field in officer_data, \
                    f"Officer {officer_data.get('id', 'unknown')} missing field {field}"

    def test_init_world_with_json_officers(self, empty_game_state):
        """Verify init_world works with JSON-loaded officers."""
        world.init_world(empty_game_state, player_choice="Wei", seed=42)

        # Should have more officers than the original 7
        assert len(empty_game_state.officers) >= 30, "Should have at least 30 officers"

        # Verify all officers are assigned to valid cities
        for officer in empty_game_state.officers.values():
            assert officer.city in empty_game_state.cities, \
                f"Officer {officer.name} assigned to invalid city {officer.city}"

        # Verify officers are assigned to their faction's cities
        for officer in empty_game_state.officers.values():
            city = empty_game_state.cities[officer.city]
            assert city.owner == officer.faction, \
                f"Officer {officer.name} ({officer.faction}) assigned to enemy city {city.name} ({city.owner})"

    def test_json_officers_have_valid_stats(self, empty_game_state):
        """Verify officers loaded from JSON have valid stats."""
        world.init_world(empty_game_state, player_choice="Wei", seed=42)

        stat_fields = ["leadership", "intelligence", "politics", "charisma", "loyalty"]

        for officer in empty_game_state.officers.values():
            for stat in stat_fields:
                value = getattr(officer, stat)
                assert 0 <= value <= 100, \
                    f"Officer {officer.name} has invalid {stat}: {value}"


class TestWorldIntegration:
    """Integration tests for world setup."""

    def test_full_world_setup(self, empty_game_state):
        """Complete world setup should create a playable game state."""
        world.init_world(empty_game_state)
        
        # Verify complete setup
        assert len(empty_game_state.cities) > 0
        assert len(empty_game_state.factions) > 0
        assert len(empty_game_state.officers) > 0
        assert len(empty_game_state.adj) > 0
        
        # Verify all officers are in valid cities
        for officer in empty_game_state.officers.values():
            assert officer.city in empty_game_state.cities
        
        # Verify all faction cities exist
        for faction in empty_game_state.factions.values():
            for city_name in faction.cities:
                assert city_name in empty_game_state.cities
        
        # Verify all faction officers exist
        for faction in empty_game_state.factions.values():
            for officer_name in faction.officers:
                assert officer_name in empty_game_state.officers
    
    def test_world_reset(self, empty_game_state):
        """Re-initializing world should reset state completely."""
        # First initialization
        world.init_world(empty_game_state, player_choice="Wei")
        empty_game_state.year = 220  # Simulate some game progress
        empty_game_state.cities["Xuchang"].gold = 9999
        
        # Re-initialize
        world.init_world(empty_game_state, player_choice="Shu")
        
        # Should be reset to initial state
        assert empty_game_state.player_faction == "Shu"
        assert empty_game_state.year == 208
        assert empty_game_state.cities["Xuchang"].gold == 700  # Back to initial value
