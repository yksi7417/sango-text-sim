"""
Utility functions for Sango Text Sim

This module contains helper functions for:
- Math utilities (clamp)
- Validation (city ownership, adjacency)
- Queries (finding officers, cities)
- Task resolution (converting synonyms to task keys)
- Trait effects calculations
- Status formatting
"""
from typing import Optional, List, Tuple
from src.models import Officer, City, Faction, GameState
from src.constants import TASK_SYNONYMS, TRAIT_EFFECTS, MIN_STAT, MAX_STAT
from i18n import i18n


def get_officer_name(officer_id: str) -> str:
    """
    Get the localized display name for an officer.
    
    Args:
        officer_id: Internal officer ID (e.g., "GuanYu", "CaoCao")
        
    Returns:
        Localized officer name based on current language setting
        
    Example:
        >>> get_officer_name("GuanYu")  # Returns "Guan Yu" in English, "關羽" in Chinese
    """
    return i18n.t(f"officers.{officer_id}")


def resolve_officer_name(input_name: str, game_state: GameState) -> Optional[str]:
    """
    Resolve a user-inputted officer name to the internal officer ID.
    
    Accepts both English and Chinese names, and returns the internal ID.
    
    Args:
        input_name: The name entered by the user (could be in any language)
        game_state: Current game state
        
    Returns:
        Internal officer ID if found, None otherwise
        
    Example:
        >>> resolve_officer_name("Guan Yu", game_state)  # Returns "GuanYu"
        >>> resolve_officer_name("關羽", game_state)     # Returns "GuanYu"
        >>> resolve_officer_name("GuanYu", game_state)  # Returns "GuanYu"
    """
    # First try exact match with internal ID
    if input_name in game_state.officers:
        return input_name
    
    # Try to match against localized names in both languages
    # We need to check both en and zh translations
    for officer_id in game_state.officers.keys():
        # Try English name
        en_name = i18n.trans.get("officers", {}).get(officer_id, "")
        if en_name.lower() == input_name.lower():
            return officer_id
            
        # Load Chinese translations temporarily to check
        import json
        import os
        try:
            zh_path = os.path.join(i18n.base_dir, "zh.json")
            with open(zh_path, "r", encoding="utf-8") as f:
                zh_trans = json.load(f)
                zh_name = zh_trans.get("officers", {}).get(officer_id, "")
                if zh_name == input_name:
                    return officer_id
        except:
            pass
    
    return None


def clamp(value: int, min_val: int, max_val: int) -> int:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: The value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        The clamped value
        
    Example:
        >>> clamp(150, 0, 100)
        100
        >>> clamp(-10, 0, 100)
        0
        >>> clamp(50, 0, 100)
        50
    """
    return max(min_val, min(max_val, value))


def valid_city(game_state: GameState, name: str) -> Optional[City]:
    """
    Get a city by name if it exists.
    
    Args:
        game_state: Current game state
        name: City name to look up
        
    Returns:
        City object if found, None otherwise
    """
    return game_state.cities.get(name)


def is_adjacent(game_state: GameState, city_a: str, city_b: str) -> bool:
    """
    Check if two cities are adjacent (border each other).
    
    Args:
        game_state: Current game state
        city_a: First city name
        city_b: Second city name
        
    Returns:
        True if cities are adjacent, False otherwise
    """
    return city_b in game_state.adj.get(city_a, [])


def ensure_player_city(game_state: GameState, city_name: str) -> bool:
    """
    Verify that a city exists and is owned by the player.
    
    Args:
        game_state: Current game state
        city_name: Name of city to check
        
    Returns:
        True if city exists and belongs to player, False otherwise
    """
    city = valid_city(game_state, city_name)
    return city is not None and city.owner == game_state.player_faction


def officer_by_name(game_state: GameState, name: str) -> Optional[Officer]:
    """
    Get an officer by name (supports both localized names and internal IDs).
    
    Args:
        game_state: Current game state
        name: Officer name to look up (can be English, Chinese, or internal ID)
        
    Returns:
        Officer object if found, None otherwise
    """
    officer_id = resolve_officer_name(name, game_state)
    if officer_id:
        return game_state.officers.get(officer_id)
    return None


def officers_in_city(game_state: GameState, faction: str, city_name: str) -> List[Officer]:
    """
    Get all officers of a faction stationed in a specific city.
    
    Args:
        game_state: Current game state
        faction: Faction name
        city_name: City name
        
    Returns:
        List of officers matching criteria
    """
    return [
        officer for officer in game_state.officers.values()
        if officer.faction == faction and officer.city == city_name
    ]


def trait_mult(officer: Officer, task: str) -> float:
    """
    Calculate trait multiplier for a task.
    
    Officers with relevant traits get bonuses on certain tasks:
    - Strict: +10% to training
    - Benevolent: +10% to farming
    - Merchant: +10% to trade
    - Scholar: +10% to research
    - Engineer: +10% to fortification
    - Charismatic: +10% to recruiting
    
    Args:
        officer: Officer performing the task
        task: Task type (farm, trade, research, etc.)
        
    Returns:
        Multiplier (1.0 = no bonus, 1.1 = +10% bonus)
    """
    mult = 1.0
    
    # Check if this task has trait effects defined
    if task in TRAIT_EFFECTS:
        for trait, bonus in TRAIT_EFFECTS[task].items():
            if trait in officer.traits:
                mult *= bonus
                
    return mult


def task_key(task_string: str) -> Optional[str]:
    """
    Convert a task synonym to the canonical task key.
    
    Supports English and Chinese synonyms:
    - farm/agriculture/農/農業 -> "farm"
    - trade/commerce/商/商業 -> "trade"
    - etc.
    
    Args:
        task_string: User input for task (any synonym)
        
    Returns:
        Canonical task key if recognized, None otherwise
        
    Example:
        >>> task_key("agriculture")
        "farm"
        >>> task_key("商業")
        "trade"
    """
    normalized = task_string.lower()
    
    for key, synonyms in TASK_SYNONYMS.items():
        if normalized in [syn.lower() for syn in synonyms]:
            return key
            
    return None


def format_faction_overview(game_state: GameState) -> Tuple[str, str, str]:
    """
    Format overview information for the player's faction.
    
    Args:
        game_state: Current game state
        
    Returns:
        Tuple of (overview_text, resources_text, relations_text)
    """
    faction = game_state.factions[game_state.player_faction]
    
    # Cities
    owned = ", ".join(sorted(faction.cities))
    
    # Resources
    treasury = sum(game_state.cities[c].gold for c in faction.cities)
    granary = sum(game_state.cities[c].food for c in faction.cities)
    army = sum(game_state.cities[c].troops for c in faction.cities)
    
    # Relations
    relations = ", ".join(
        f"{k}:{v:+d}"
        for k, v in faction.relations.items()
        if k != game_state.player_faction
    )
    
    overview = i18n.t(
        "ui.overview",
        year=game_state.year,
        month=game_state.month,
        faction=game_state.player_faction,
        num=len(faction.cities),
        cities=owned
    )
    
    resources = i18n.t(
        "ui.resources",
        gold=treasury,
        food=granary,
        troops=army
    )
    
    relations_text = i18n.t("ui.relations", rels=relations)
    
    return overview, resources, relations_text


def format_city_status(game_state: GameState, city_name: str) -> Optional[List[str]]:
    """
    Format detailed status information for a city.
    
    Args:
        game_state: Current game state
        city_name: Name of city to format
        
    Returns:
        List of formatted status lines, or None if city doesn't exist
    """
    city = valid_city(game_state, city_name)
    if not city:
        return None
        
    lines = []
    
    # Header
    owner_tag = "(You)" if city.owner == game_state.player_faction else ""
    lines.append(i18n.t("ui.city_header", name=city.name, owner=city.owner, tag=owner_tag))
    
    # Stats
    lines.append(i18n.t(
        "ui.city_stats1",
        gold=city.gold,
        food=city.food,
        troops=city.troops,
        defense=city.defense,
        morale=city.morale
    ))
    
    lines.append(i18n.t(
        "ui.city_stats2",
        agri=city.agri,
        commerce=city.commerce,
        tech=city.tech,
        walls=city.walls
    ))
    
    # Officers
    garrison = [
        f"{get_officer_name(o.name)}(Loy{o.loyalty},{'/'.join(i18n.t('traits.'+t) for t in o.traits)})"
        for o in game_state.officers.values()
        if o.city == city.name
    ]
    
    if garrison:
        lines.append(i18n.t("ui.officers_list_header", names=", ".join(garrison)))
        
    return lines


def validate_march(
    game_state: GameState,
    troops: int,
    source_city: str,
    dest_city: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate a troop march command.
    
    Args:
        game_state: Current game state
        troops: Number of troops to march
        source_city: Source city name
        dest_city: Destination city name
        
    Returns:
        Tuple of (is_valid, error_message)
        error_message is None if valid
    """
    # Check source city
    if not ensure_player_city(game_state, source_city):
        return False, i18n.t("errors.not_source")
        
    # Check destination exists
    if not valid_city(game_state, dest_city):
        return False, i18n.t("errors.no_city")
        
    # Check adjacency
    if not is_adjacent(game_state, source_city, dest_city):
        return False, i18n.t("errors.not_adjacent")
        
    # Check troop count
    src = game_state.cities[source_city]
    if troops <= 0 or troops > src.troops:
        return False, i18n.t("errors.not_enough_troops")
        
    return True, None
