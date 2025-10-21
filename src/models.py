"""
Data models for Sango Text Sim

This module contains all the dataclasses representing game entities:
- Officer: Individual characters with stats, loyalty, and assignments
- City: Settlements with resources, troops, and development
- Faction: Political entities controlling cities and officers
- GameState: Global game state container
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
    assignment_energy_spent: bool = False


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

    def log(self, msg: str):
        """Add a message to the game log"""
        self.messages.append(msg)
