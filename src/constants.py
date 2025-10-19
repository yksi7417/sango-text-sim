"""
Game constants and configuration

This module contains all game constants including:
- Task types and their synonyms (English + Chinese)
- Command aliases for bilingual support
- Default game settings
"""
from typing import Dict, List

# =================== Task Types ===================
TASKS = ["farm", "trade", "research", "train", "fortify", "recruit"]

# Task synonyms for English and Chinese input
TASK_SYNONYMS: Dict[str, List[str]] = {
    "farm": ["farm", "agriculture", "農", "農業"],
    "trade": ["trade", "commerce", "商", "商業"],
    "research": ["research", "tech", "科技", "科研"],
    "train": ["train", "drill", "訓練", "練兵"],
    "fortify": ["fortify", "fortress", "築城", "防禦", "加固"],
    "recruit": ["recruit", "conscription", "徵兵", "募兵"]
}

# Command keyword aliases for bilingual support
ALIASES: Dict[str, List[str]] = {
    "to": ["to", "至", "到"],
    "in": ["in", "於", "在"],
    "from": ["from", "自", "從"],
    "with": ["with", "以"]
}

# =================== Game Settings ===================
DEFAULT_YEAR = 208
DEFAULT_MONTH = 1
DEFAULT_DIFFICULTY = "Normal"

# Starting resources for a typical city
DEFAULT_CITY_GOLD = 500
DEFAULT_CITY_FOOD = 800
DEFAULT_CITY_TROOPS = 300
DEFAULT_CITY_DEFENSE = 50
DEFAULT_CITY_MORALE = 60

# Development stats
DEFAULT_AGRI = 50
DEFAULT_COMMERCE = 50
DEFAULT_TECH = 40
DEFAULT_WALLS = 50

# Officer defaults
DEFAULT_OFFICER_ENERGY = 100
DEFAULT_OFFICER_LOYALTY = 70

# Stat limits
MIN_STAT = 0
MAX_STAT = 100
MIN_MORALE = 10
MAX_MORALE = 95
MIN_DEFENSE = 40
MAX_DEFENSE = 95

# =================== Factions ===================
FACTIONS = ["Wei", "Shu", "Wu"]
FACTION_RULERS = {
    "Wei": "曹操",
    "Shu": "劉備",
    "Wu": "孫權"
}

# =================== Traits ===================
TRAITS = [
    "Brave",        # Combat bonus
    "Strict",       # Training bonus
    "Benevolent",   # Farming bonus
    "Charismatic",  # Recruiting bonus
    "Scholar",      # Research bonus
    "Engineer",     # Fortification bonus
    "Merchant"      # Trade bonus
]

# Trait effects on tasks (multipliers)
TRAIT_EFFECTS = {
    "train": {"Strict": 1.10},
    "farm": {"Benevolent": 1.10},
    "trade": {"Merchant": 1.10},
    "research": {"Scholar": 1.10},
    "fortify": {"Engineer": 1.10},
    "recruit": {"Charismatic": 1.10}
}

# =================== Costs ===================
SPY_COST_GOLD = 50
NEGOTIATE_COST_GOLD = 100
RECRUIT_BASE_COST_GOLD = 80
RECRUIT_BASE_COST_FOOD = 80
RECRUIT_BASE_TROOPS = 70

# Energy costs for tasks
ENERGY_COST_ADMIN = 8   # farm, trade, research
ENERGY_COST_MILITARY = 10  # train, fortify, recruit
ENERGY_RECOVERY = 12  # For idle officers

# =================== Economy ===================
TROOP_UPKEEP_RATE = 0.12  # Food consumption per troop
DESERTION_MIN_RATE = 0.05
DESERTION_MAX_RATE = 0.15
MONTHLY_DEFENSE_GAIN = 1

# Tax/harvest multipliers
JANUARY_TAX_MULTIPLIER = 5  # Commerce * 5 in January
JULY_HARVEST_MULTIPLIER = 5  # Agriculture * 5 in July

# =================== Combat ===================
TECH_BONUS_BASELINE = 50
TECH_BONUS_DIVISOR = 500
WALL_DEFENSE_DIVISOR = 400

BRAVE_TRAIT_ATTACK_BONUS = 1.08
ENGINEER_TRAIT_DEFENSE_BONUS = 1.08

ATTACKER_CASUALTIES_MIN = 0.2
ATTACKER_CASUALTIES_MAX = 0.6
DEFENDER_CASUALTIES_MIN = 0.25
DEFENDER_CASUALTIES_MAX = 0.55

# Battle outcome thresholds
DECISIVE_VICTORY_RATIO = 1.1
DECISIVE_DEFEAT_RATIO = 0.7

# Morale changes from battle
VICTORY_MORALE_GAIN = 10
DEFEAT_MORALE_LOSS = -8
DEFENDER_VICTORY_MORALE_GAIN = 8
DEFENDER_DEFEAT_MORALE_LOSS = -12

# Loyalty changes from battle
VICTORY_LOYALTY_GAIN = 2
DEFEAT_LOYALTY_LOSS = -1

# =================== Loyalty & Defection ===================
CRITICAL_LOYALTY_THRESHOLD = 35
DEFECTION_CHANCE_MONTHLY = 0.10  # 10% if loyalty < threshold
LOYALTY_GAIN_FROM_WORK = 1
LOYALTY_LOSS_FROM_EXHAUSTION = -2
EXHAUSTION_THRESHOLD = 10
