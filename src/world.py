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
from typing import Optional, Dict, List
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


def list_scenarios() -> List[Dict]:
    """List all available scenarios."""
    maps_dir = Path(__file__).parent / "data" / "maps"
    scenarios = []
    for f in sorted(maps_dir.glob("china_*.json")):
        if f.name == "china_208_full.json":
            continue
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            meta = data.get("metadata", {})
            scenarios.append({
                "id": meta.get("scenario_id", f.stem),
                "name": meta.get("name", f.stem),
                "year": meta.get("year", 0),
                "description": meta.get("description", "")
            })
        except (json.JSONDecodeError, KeyError):
            pass
    return scenarios


def load_officers(roster_name: str = "legendary") -> Dict:
    """
    Load officer roster data from JSON file.

    Args:
        roster_name: Name of the officer roster to load (default: "legendary")

    Returns:
        Dictionary containing officer roster data with keys:
        - metadata: roster information
        - officers: list of officer data

    Raises:
        FileNotFoundError: If the roster file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    roster_path = Path(__file__).parent / "data" / "officers" / f"{roster_name}.json"

    with open(roster_path, "r", encoding="utf-8") as f:
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
                "walls": city["development"]["walls"],
                "terrain": city.get("terrain", "plains")  # Default to plains if not specified
            }

            # Build adjacency map
            adjacency_map[city_id] = city["adjacency"]

        return city_data, adjacency_map

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Fall back to hardcoded data if JSON loading fails
        return None, None


def _load_officer_data_from_json(roster_name: str = "legendary") -> Optional[list]:
    """
    Load officer data from JSON roster file.

    Args:
        roster_name: Name of the officer roster to load

    Returns:
        List of officer data dictionaries, or None if loading fails
    """
    try:
        roster_data = load_officers(roster_name)

        # Convert JSON structure to legacy OFFICER_DATA format
        officer_list = []
        for officer in roster_data["officers"]:
            officer_list.append({
                "id": officer["id"],
                "faction": officer["faction"],
                "leadership": officer["leadership"],
                "intelligence": officer["intelligence"],
                "politics": officer["politics"],
                "charisma": officer["charisma"],
                "loyalty": officer["loyalty"],
                "traits": officer["traits"],
                "relationships": officer.get("relationships", {})
            })

        return officer_list

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Fall back to hardcoded data if JSON loading fails
        return None


# Try to load from JSON, fall back to hardcoded if it fails
_json_city_data, _json_adjacency = _load_city_data_from_json()

if _json_city_data is not None:
    # Use JSON data as primary source
    CITY_DATA = _json_city_data
    ADJACENCY_MAP = _json_adjacency
# else: CITY_DATA and ADJACENCY_MAP already defined above with hardcoded values

# Try to load officers from JSON
_json_officer_data = _load_officer_data_from_json()

if _json_officer_data is not None:
    # Use JSON data as primary source
    OFFICER_DATA = _json_officer_data
# else: OFFICER_DATA already defined above with hardcoded values


def add_officer(game_state: GameState, officer: Officer) -> None:
    """
    Add an officer to the game state.
    
    Args:
        game_state: Current game state
        officer: Officer to add
    """
    game_state.officers[officer.name] = officer
    game_state.factions[officer.faction].officers.append(officer.name)


def init_world(game_state: GameState, player_choice: Optional[str] = None, seed: Optional[int] = 42, scenario: str = "china_208") -> None:
    """
    Initialize the game world with cities, factions, and officers.

    Creates:
    - Factions with rulers based on scenario
    - Cities with resources and troops from scenario
    - Officers available in the scenario
    - Map adjacency relationships
    - Initial diplomatic relations

    Args:
        game_state: Game state to initialize
        player_choice: Which faction the player controls
        seed: Random seed for reproducible initialization
        scenario: Scenario to load (default: "china_208")
    """
    if seed is not None:
        random.seed(seed)

    # Load scenario data
    try:
        scenario_data = load_scenario(scenario)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fall back to default scenario
        scenario_data = load_scenario("china_208")

    # Get factions from scenario, or use defaults
    scenario_factions = scenario_data.get("factions", {})
    if not scenario_factions:
        # Default factions for backward compatibility
        scenario_factions = {
            "Wei": {"ruler": "CaoCao", "description": "Wei"},
            "Shu": {"ruler": "LiuBei", "description": "Shu"},
            "Wu": {"ruler": "SunQuan", "description": "Wu"}
        }

    faction_names = list(scenario_factions.keys())

    # Build faction rulers map from scenario
    faction_rulers = {name: data.get("ruler", name) for name, data in scenario_factions.items()}

    # Set player faction
    if player_choice and player_choice in faction_names:
        game_state.player_faction = player_choice
    elif faction_names:
        # Default to first faction if player_faction not in scenario
        if game_state.player_faction not in faction_names:
            game_state.player_faction = faction_names[0]

    game_state.player_ruler = faction_rulers.get(game_state.player_faction, game_state.player_faction)

    # Load city data from scenario
    city_data, adjacency_map = _load_city_data_from_json(scenario)
    if city_data is None:
        city_data = CITY_DATA
        adjacency_map = ADJACENCY_MAP

    # Create cities
    cities = {}
    for city_name, data in city_data.items():
        # Import TerrainType here to avoid circular import
        from .models import TerrainType

        # Get terrain, default to PLAINS if not specified
        terrain_str = data.get("terrain", "plains")
        terrain = TerrainType(terrain_str)

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
            walls=data["walls"],
            terrain=terrain
        )

    # Set adjacency map
    adj = adjacency_map.copy()

    # Create factions - include all factions that own cities plus scenario factions
    all_faction_names = set(faction_names)
    for city in cities.values():
        all_faction_names.add(city.owner)

    factions_map: Dict[str, Faction] = {f: Faction(name=f) for f in all_faction_names}

    # Assign cities to factions
    for city in cities.values():
        if city.owner in factions_map:
            factions_map[city.owner].cities.append(city.name)

    # Set up diplomatic relations and rulers
    for f in all_faction_names:
        factions_map[f].relations = {
            g: (0 if f == g else random.randint(-20, 10)) for g in all_faction_names
        }
        factions_map[f].ruler = faction_rulers.get(f, f)

    # Update game state
    game_state.cities = cities
    game_state.adj = adj
    game_state.factions = factions_map
    game_state.officers.clear()

    # Get officer availability from scenario
    officer_availability = scenario_data.get("officer_availability", None)

    # Filter officers based on scenario availability
    officers_to_add = OFFICER_DATA
    if officer_availability:
        officers_to_add = [o for o in OFFICER_DATA if o["id"] in officer_availability]

    # Map officers to factions that exist in this scenario
    # If officer's faction doesn't exist, try to find a matching one
    for officer_data in officers_to_add:
        officer_faction = officer_data["faction"]

        # Check if officer's faction exists in this scenario
        if officer_faction not in factions_map:
            # Try to find a faction that has this officer's ruler
            # or skip if no matching faction
            found = False
            for faction_name, faction in factions_map.items():
                if faction.ruler == officer_data["id"]:
                    officer_faction = faction_name
                    found = True
                    break
            if not found:
                continue  # Skip this officer

        # Find an appropriate city for the officer
        faction_cities = factions_map[officer_faction].cities
        assigned_city = None
        if faction_cities:
            assigned_city = faction_cities[0]
        else:
            # Find any city owned by this faction
            for city_name, city in cities.items():
                if city.owner == officer_faction:
                    assigned_city = city_name
                    break

        if not assigned_city:
            continue  # Skip if no city available

        officer = Officer(
            name=officer_data["id"],
            faction=officer_faction,
            leadership=officer_data["leadership"],
            intelligence=officer_data["intelligence"],
            politics=officer_data["politics"],
            charisma=officer_data["charisma"],
            loyalty=officer_data["loyalty"],
            traits=officer_data["traits"],
            city=assigned_city,
            relationships=officer_data.get("relationships", {})
        )
        add_officer(game_state, officer)

    # Set initial time from scenario metadata
    metadata = scenario_data.get("metadata", {})
    game_state.year = metadata.get("year", 208)
    game_state.month = metadata.get("month", 1)
    game_state.messages.clear()

    # Mark game as started
    game_state.game_started = True

    # Welcome message with localized ruler name
    ruler_display_name = i18n.t(f"officers.{game_state.player_ruler}", default=game_state.player_ruler)
    game_state.log(i18n.t("game.welcome", ruler=ruler_display_name, faction=game_state.player_faction))
    # Don't log time message - it's shown in the UI header
