"""
World Initialization - Setup game world with cities, factions, and officers.

This module contains functions for initializing the game world:
- City data templates
- Officer data templates
- Faction setup
- Map adjacency configuration
"""

import json
import random
from pathlib import Path
from typing import Optional, Dict
from .models import Officer, City, Faction, GameState
from i18n import i18n


# City data templates
CITY_DATA = {
    "Xuchang": {
        "owner": "Wei",
        "gold": 700,
        "food": 1000,
        "troops": 420,
        "defense": 70,
        "morale": 65,
        "agri": 60,
        "commerce": 65,
        "tech": 55,
        "walls": 70
    },
    "Luoyang": {
        "owner": "Wei",
        "gold": 600,
        "food": 900,
        "troops": 360,
        "defense": 60,
        "morale": 60,
        "agri": 55,
        "commerce": 60,
        "tech": 50,
        "walls": 62
    },
    "Chengdu": {
        "owner": "Shu",
        "gold": 650,
        "food": 980,
        "troops": 380,
        "defense": 65,
        "morale": 72,
        "agri": 65,
        "commerce": 58,
        "tech": 52,
        "walls": 66
    },
    "Hanzhong": {
        "owner": "Shu",
        "gold": 560,
        "food": 820,
        "troops": 320,
        "defense": 58,
        "morale": 63,
        "agri": 60,
        "commerce": 52,
        "tech": 48,
        "walls": 60
    },
    "Jianye": {
        "owner": "Wu",
        "gold": 680,
        "food": 980,
        "troops": 390,
        "defense": 66,
        "morale": 68,
        "agri": 62,
        "commerce": 64,
        "tech": 54,
        "walls": 65
    },
    "Wuchang": {
        "owner": "Wu",
        "gold": 560,
        "food": 820,
        "troops": 310,
        "defense": 58,
        "morale": 61,
        "agri": 58,
        "commerce": 55,
        "tech": 49,
        "walls": 60
    }
}

# Map adjacency configuration
ADJACENCY_MAP = {
    "Xuchang": ["Luoyang", "Hanzhong"],
    "Luoyang": ["Xuchang", "Hanzhong", "Wuchang"],
    "Hanzhong": ["Luoyang", "Xuchang", "Chengdu"],
    "Chengdu": ["Hanzhong"],
    "Jianye": ["Wuchang"],
    "Wuchang": ["Jianye", "Luoyang"]
}

# Officer data templates
# Internal IDs are used for game logic, display names come from i18n
OFFICER_DATA = [
    {
        "id": "LiuBei",
        "faction": "Shu",
        "leadership": 86,
        "intelligence": 80,
        "politics": 88,
        "charisma": 96,
        "loyalty": 90,
        "traits": ["Benevolent", "Charismatic"],
        "city": "Chengdu"
    },
    {
        "id": "GuanYu",
        "faction": "Shu",
        "leadership": 98,
        "intelligence": 79,
        "politics": 92,
        "charisma": 84,
        "loyalty": 85,
        "traits": ["Brave", "Strict"],
        "city": "Chengdu"
    },
    {
        "id": "ZhangFei",
        "faction": "Shu",
        "leadership": 97,
        "intelligence": 65,
        "politics": 60,
        "charisma": 82,
        "loyalty": 75,
        "traits": ["Brave"],
        "city": "Chengdu"
    },
    {
        "id": "CaoCao",
        "faction": "Wei",
        "leadership": 92,
        "intelligence": 94,
        "politics": 96,
        "charisma": 90,
        "loyalty": 90,
        "traits": ["Charismatic", "Scholar"],
        "city": "Xuchang"
    },
    {
        "id": "ZhangLiao",
        "faction": "Wei",
        "leadership": 94,
        "intelligence": 78,
        "politics": 70,
        "charisma": 76,
        "loyalty": 80,
        "traits": ["Brave"],
        "city": "Luoyang"
    },
    {
        "id": "SunQuan",
        "faction": "Wu",
        "leadership": 86,
        "intelligence": 80,
        "politics": 85,
        "charisma": 92,
        "loyalty": 88,
        "traits": ["Charismatic", "Merchant"],
        "city": "Jianye"
    },
    {
        "id": "ZhouYu",
        "faction": "Wu",
        "leadership": 90,
        "intelligence": 92,
        "politics": 88,
        "charisma": 88,
        "loyalty": 85,
        "traits": ["Scholar", "Engineer"],
        "city": "Jianye"
    }
]

# Faction rulers mapping (using officer IDs)
FACTION_RULERS = {
    "Wei": "CaoCao",
    "Shu": "LiuBei",
    "Wu": "SunQuan"
}


def load_scenario(scenario_name: str = "china_208") -> Dict:
    """
    Load scenario data from JSON file.

    Args:
        scenario_name: Name of the scenario to load (default: "china_208")

    Returns:
        Dictionary containing scenario data with keys:
        - metadata: scenario information
        - provinces: list of province data
        - cities: list of city data

    Raises:
        FileNotFoundError: If the scenario file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    scenario_path = Path(__file__).parent / "data" / "maps" / f"{scenario_name}.json"

    with open(scenario_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_city_data_from_json(scenario_name: str = "china_208") -> tuple:
    """
    Load city data and adjacency from JSON scenario file.

    Args:
        scenario_name: Name of the scenario to load

    Returns:
        Tuple of (city_data_dict, adjacency_map_dict)
    """
    try:
        scenario_data = load_scenario(scenario_name)

        # Build city data dictionary
        city_data = {}
        adjacency_map = {}

        for city in scenario_data["cities"]:
            city_id = city["id"]

            # Convert JSON structure to legacy CITY_DATA format
            city_data[city_id] = {
                "owner": city["owner"],
                "gold": city["resources"]["gold"],
                "food": city["resources"]["food"],
                "troops": city["resources"]["troops"],
                "defense": city["military"]["defense"],
                "morale": city["military"]["morale"],
                "agri": city["development"]["agriculture"],
                "commerce": city["development"]["commerce"],
                "tech": city["development"]["technology"],
                "walls": city["development"]["walls"]
            }

            # Build adjacency map
            adjacency_map[city_id] = city["adjacency"]

        return city_data, adjacency_map

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Fall back to hardcoded data if JSON loading fails
        return None, None


# Try to load from JSON, fall back to hardcoded if it fails
_json_city_data, _json_adjacency = _load_city_data_from_json()

if _json_city_data is not None:
    # Use JSON data as primary source
    CITY_DATA = _json_city_data
    ADJACENCY_MAP = _json_adjacency
# else: CITY_DATA and ADJACENCY_MAP already defined above with hardcoded values


def add_officer(game_state: GameState, officer: Officer) -> None:
    """
    Add an officer to the game state.
    
    Args:
        game_state: Current game state
        officer: Officer to add
    """
    game_state.officers[officer.name] = officer
    game_state.factions[officer.faction].officers.append(officer.name)


def init_world(game_state: GameState, player_choice: Optional[str] = None, seed: Optional[int] = 42) -> None:
    """
    Initialize the game world with cities, factions, and officers.
    
    Creates:
    - Three factions (Wei, Shu, Wu) with rulers
    - Six cities with resources and troops
    - Seven legendary officers with unique traits
    - Map adjacency relationships
    - Initial diplomatic relations
    
    Args:
        game_state: Game state to initialize
        player_choice: Which faction the player controls (Wei, Shu, or Wu)
        seed: Random seed for reproducible initialization
    """
    if seed is not None:
        random.seed(seed)
    
    factions = ["Wei", "Shu", "Wu"]
    
    # Set player faction
    if player_choice and player_choice in factions:
        game_state.player_faction = player_choice
    game_state.player_ruler = FACTION_RULERS[game_state.player_faction]
    
    # Create cities
    cities = {}
    for city_name, data in CITY_DATA.items():
        cities[city_name] = City(
            name=city_name,
            owner=data["owner"],
            gold=data["gold"],
            food=data["food"],
            troops=data["troops"],
            defense=data["defense"],
            morale=data["morale"],
            agri=data["agri"],
            commerce=data["commerce"],
            tech=data["tech"],
            walls=data["walls"]
        )
    
    # Set adjacency map
    adj = ADJACENCY_MAP.copy()
    
    # Create factions
    factions_map: Dict[str, Faction] = {f: Faction(name=f) for f in factions}
    
    # Assign cities to factions
    for city in cities.values():
        factions_map[city.owner].cities.append(city.name)
    
    # Set up diplomatic relations and rulers
    for f in factions:
        factions_map[f].relations = {
            g: (0 if f == g else random.randint(-20, 10)) for g in factions
        }
        factions_map[f].ruler = FACTION_RULERS[f]
    
    # Update game state
    game_state.cities = cities
    game_state.adj = adj
    game_state.factions = factions_map
    game_state.officers.clear()
    
    # Add officers
    for officer_data in OFFICER_DATA:
        officer = Officer(
            name=officer_data["id"],
            faction=officer_data["faction"],
            leadership=officer_data["leadership"],
            intelligence=officer_data["intelligence"],
            politics=officer_data["politics"],
            charisma=officer_data["charisma"],
            loyalty=officer_data["loyalty"],
            traits=officer_data["traits"],
            city=officer_data["city"]
        )
        add_officer(game_state, officer)
    
    # Set initial time
    game_state.year = 208
    game_state.month = 1
    game_state.messages.clear()
    
    # Welcome message with localized ruler name
    ruler_display_name = i18n.t(f"officers.{game_state.player_ruler}")
    game_state.log(i18n.t("game.welcome", ruler=ruler_display_name, faction=game_state.player_faction))
    # Don't log time message - it's shown in the UI header
