"""
Data models for Sango Text Sim

This module contains all the dataclasses representing game entities:
- Officer: Individual characters with stats, loyalty, and assignments
- City: Settlements with resources, troops, and development
- Faction: Political entities controlling cities and officers
- GameState: Global game state container
- Season: Seasonal system affecting gameplay
- TurnEvent: Events that occur during turn processing
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class Season(Enum):
    """
    Seasons that affect gameplay mechanics.

    Seasons are based on month:
    - Spring: months 3-5 (March-May)
    - Summer: months 6-8 (June-August)
    - Autumn: months 9-11 (September-November)
    - Winter: months 12, 1-2 (December-February)
    """
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


def get_current_season(month: int) -> Season:
    """
    Get the current season based on the game month.

    Args:
        month: Game month (1-12)

    Returns:
        Season enum corresponding to the month
    """
    if 3 <= month <= 5:
        return Season.SPRING
    elif 6 <= month <= 8:
        return Season.SUMMER
    elif 9 <= month <= 11:
        return Season.AUTUMN
    else:  # 12, 1, 2
        return Season.WINTER


class UnitType(Enum):
    """Military unit types with rock-paper-scissors combat dynamics."""
    INFANTRY = "infantry"
    CAVALRY = "cavalry"
    ARCHER = "archer"


class WeatherType(Enum):
    """Weather conditions that affect battles and movement."""
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    DROUGHT = "drought"


class TerrainType(Enum):
    """
    Terrain types that affect combat and movement.

    Each terrain type provides different tactical advantages:
    - Plains: Normal combat, no modifiers
    - Mountain: +30% defense, -20% cavalry effectiveness
    - Forest: +20% ambush success, fire attack bonus
    - Coastal: Naval units required for attack
    - River: Crossing penalty during attack
    """
    PLAINS = "plains"
    MOUNTAIN = "mountain"
    FOREST = "forest"
    COASTAL = "coastal"
    RIVER = "river"


class RelationshipType(Enum):
    """Types of relationships between officers."""
    SWORN_BROTHER = "sworn_brother"
    RIVAL = "rival"
    LORD = "lord"
    SPOUSE = "spouse"
    MENTOR = "mentor"


@dataclass
class Technology:
    """A technology that can be researched."""
    id: str
    category: str  # military, economy, special
    name_key: str
    cost: int
    turns: int
    prerequisites: List[str] = field(default_factory=list)
    effects: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Building:
    """A building that can be constructed in a city."""
    id: str
    name_key: str
    cost: int
    turns: int
    effects: Dict[str, Any] = field(default_factory=dict)


class EventCategory(Enum):
    """Categories for turn events."""
    ECONOMY = "economy"
    MILITARY = "military"
    DIPLOMATIC = "diplomatic"
    OFFICER = "officer"


@dataclass
class TurnEvent:
    """
    Represents a single event that occurred during a turn.

    Attributes:
        category: Event category (Economy, Military, etc.)
        message: Human-readable description of the event
        data: Additional structured data about the event
    """
    category: EventCategory
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BattleState:
    """
    Represents the state of an ongoing tactical battle.

    Attributes:
        attacker_city: Name of the attacking city
        defender_city: Name of the defending city
        attacker_faction: Name of the attacking faction
        defender_faction: Name of the defending faction
        attacker_commander: Name of the officer commanding the attack
        defender_commander: Name of the officer commanding the defense
        attacker_troops: Number of attacking troops
        defender_troops: Number of defending troops
        terrain: Terrain type of the battlefield
        weather: Current weather conditions (optional)
        round: Current battle round number
        attacker_morale: Morale of attacking forces (0-100)
        defender_morale: Morale of defending forces (0-100)
        supply_days: Days of supply remaining for attacker
        siege_progress: Progress toward breaking city walls (0-100)
        combat_log: List of battle events
    """
    attacker_city: str
    defender_city: str
    attacker_faction: str
    defender_faction: str
    attacker_commander: str
    defender_commander: str
    attacker_troops: int
    defender_troops: int
    terrain: TerrainType
    weather: Optional[str] = None
    round: int = 0
    attacker_morale: int = 70
    defender_morale: int = 70
    supply_days: int = 10
    siege_progress: int = 0
    combat_log: List[str] = field(default_factory=list)


@dataclass
class Officer:
    """
    Represents a military/political officer in the game.
    
    Attributes:
        name: Officer's name (can be Chinese characters)
        faction: Which faction they belong to
        leadership: Military leadership ability (affects training, combat)
        intelligence: Strategic thinking (affects research)
        politics: Administrative skill (affects farming, commerce)
        charisma: Personal magnetism (affects recruiting, loyalty)
        energy: Current stamina (0-100, depletes with assignments)
        loyalty: Devotion to faction (0-100, affects defection risk)
        traits: Special abilities (Brave, Scholar, Merchant, etc.)
        city: Current stationed city
        task: Current assignment (farm, trade, research, etc.)
        task_city: City where task is being performed
        busy: Whether currently on an assignment
    """
    name: str
    faction: str
    leadership: int
    intelligence: int
    politics: int
    charisma: int
    energy: int = 100
    loyalty: int = 70
    traits: List[str] = field(default_factory=list)
    city: Optional[str] = None
    task: Optional[str] = None
    task_city: Optional[str] = None
    busy: bool = False
    relationships: Dict[str, str] = field(default_factory=dict)

    def get_relationship(self, other_name: str) -> Optional['RelationshipType']:
        """Get relationship type with another officer."""
        rel = self.relationships.get(other_name)
        if rel:
            try:
                return RelationshipType(rel)
            except ValueError:
                return None
        return None

    def get_relationship_bonus(self, other_name: str, context: str = "loyalty") -> float:
        """
        Get relationship bonus for a given context.

        Args:
            other_name: Name of the other officer
            context: 'loyalty' or 'combat'

        Returns:
            Bonus modifier (additive for loyalty, multiplicative for combat)
        """
        rel = self.get_relationship(other_name)
        if not rel:
            return 0.0

        if context == "loyalty":
            if rel == RelationshipType.SWORN_BROTHER:
                return 30.0
            elif rel == RelationshipType.LORD:
                return 20.0
            elif rel == RelationshipType.SPOUSE:
                return 25.0
            elif rel == RelationshipType.MENTOR:
                return 15.0
            elif rel == RelationshipType.RIVAL:
                return -10.0
        elif context == "combat":
            if rel == RelationshipType.RIVAL:
                return 0.15  # +15% damage
            elif rel == RelationshipType.SWORN_BROTHER:
                return 0.10  # +10% when fighting together
        return 0.0


@dataclass
class City:
    """
    Represents a city/settlement in the game.

    Attributes:
        name: City name
        owner: Faction that controls this city
        gold: Treasury (currency for recruiting, espionage, etc.)
        food: Granary (feeds troops, used for recruiting)
        troops: Military strength
        defense: Defensive capability
        morale: Army morale (affects combat performance)
        agri: Agriculture development (affects food production)
        commerce: Commercial development (affects gold income)
        tech: Technology level (affects combat bonuses)
        walls: Fortification level (affects defense)
        terrain: Terrain type affecting combat and movement
    """
    name: str
    owner: str
    gold: int = 500
    food: int = 800
    troops: int = 300
    defense: int = 50
    morale: int = 60
    agri: int = 50
    commerce: int = 50
    tech: int = 40
    walls: int = 50
    terrain: TerrainType = TerrainType.PLAINS
    unit_composition: Dict[str, int] = field(default_factory=lambda: {
        "infantry": 0, "cavalry": 0, "archer": 0
    })
    buildings: List[str] = field(default_factory=list)  # IDs of constructed buildings

    def __post_init__(self):
        """Initialize unit composition from troops if not set."""
        total_units = sum(self.unit_composition.values())
        if total_units == 0 and self.troops > 0:
            # Default split: 50% infantry, 25% cavalry, 25% archer
            self.unit_composition = {
                "infantry": self.troops // 2,
                "cavalry": self.troops // 4,
                "archer": self.troops - self.troops // 2 - self.troops // 4
            }

    def get_units(self, unit_type: 'UnitType') -> int:
        """Get count of a specific unit type."""
        return self.unit_composition.get(unit_type.value, 0)

    def sync_troops(self):
        """Sync total troops from unit composition."""
        self.troops = sum(self.unit_composition.values())


@dataclass
class Faction:
    """
    Represents a political faction (Wei, Shu, Wu).
    
    Attributes:
        name: Faction name
        relations: Diplomatic relations with other factions (-100 to +100)
        cities: List of city names controlled by this faction
        officers: List of officer names serving this faction
        ruler: Name of the faction leader
    """
    name: str
    relations: Dict[str, int] = field(default_factory=dict)
    cities: List[str] = field(default_factory=list)
    officers: List[str] = field(default_factory=list)
    ruler: str = ""
    technologies: List[str] = field(default_factory=list)  # IDs of researched techs


@dataclass
class GameState:
    """
    Global game state container.

    Attributes:
        year: Current year (starts at 208 CE)
        month: Current month (1-12)
        factions: All factions in the game
        cities: All cities in the game
        adj: Adjacency map (which cities border each other)
        officers: All officers in the game
        player_faction: Which faction the player controls
        player_ruler: Name of the player's ruler
        difficulty: Game difficulty level
        messages: Log of recent game events
        active_duel: Current ongoing duel (if any)
        pending_duel_challenge: Details of a duel challenge awaiting response
    """
    year: int = 208
    month: int = 1
    factions: Dict[str, Faction] = field(default_factory=dict)
    cities: Dict[str, City] = field(default_factory=dict)
    adj: Dict[str, List[str]] = field(default_factory=dict)
    officers: Dict[str, Officer] = field(default_factory=dict)
    player_faction: str = "Shu"
    player_ruler: str = "劉備"
    difficulty: str = "Normal"
    messages: List[str] = field(default_factory=list)
    active_duel: Optional[Any] = None  # Will be Duel from systems.duel
    pending_duel_challenge: Optional[Dict[str, Any]] = None  # For async challenge/response flow
    active_battle: Optional['BattleState'] = None  # Current ongoing tactical battle
    weather: WeatherType = WeatherType.CLEAR
    weather_turns_remaining: int = 0
    pending_event: Optional[Dict[str, Any]] = None  # Pending random event awaiting player choice
    research_progress: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # faction -> {tech_id, progress, officer, city}
    construction_queue: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # city_name -> {building_id, progress, turns_needed}

    def log(self, msg: str):
        """Add a message to the game log"""
        self.messages.append(msg)
