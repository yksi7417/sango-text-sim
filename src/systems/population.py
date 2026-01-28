"""
Population System - City population management.

Population affects:
- Maximum recruitment (can't recruit more than 10% of population)
- Production output (agriculture, commerce scaled by population)
- Growth based on prosperity (food, commerce, morale)
- War and famine reduce population
- Migration between friendly cities
"""
from typing import Dict, Any, List
from ..models import GameState, City
from i18n import i18n


# Population constants
BASE_GROWTH_RATE = 0.02  # 2% base growth per turn
MAX_POPULATION = 50000
MIN_POPULATION = 1000
RECRUITMENT_POPULATION_RATIO = 0.10  # Max 10% of population can be recruited
WAR_POPULATION_LOSS = 0.05  # 5% population loss when city is conquered
FAMINE_THRESHOLD = 100  # Food below this triggers famine
FAMINE_POPULATION_LOSS = 0.03  # 3% population loss from famine
PROSPERITY_BONUS = 0.01  # Extra growth per 20 points of commerce
MIGRATION_RATE = 0.01  # 1% migration per turn


def get_max_recruitment(city: City) -> int:
    """Get maximum troops that can be recruited based on population."""
    return int(city.population * RECRUITMENT_POPULATION_RATIO)


def get_production_modifier(city: City) -> float:
    """
    Get production modifier based on population.
    Cities with more population produce more.
    Base: 1.0 at 10000 population.
    """
    return max(0.5, min(2.0, city.population / 10000.0))


def calculate_growth(city: City) -> int:
    """
    Calculate population growth for a city.

    Growth is based on:
    - Base growth rate
    - Commerce prosperity bonus
    - Negative if food is low (famine)
    - Negative if morale is very low
    """
    growth_rate = BASE_GROWTH_RATE

    # Commerce prosperity bonus
    growth_rate += (city.commerce / 20) * PROSPERITY_BONUS

    # Morale penalty
    if city.morale < 30:
        growth_rate -= 0.02

    # Famine
    if city.food < FAMINE_THRESHOLD:
        growth_rate = -FAMINE_POPULATION_LOSS

    growth = int(city.population * growth_rate)
    return growth


def process_population(game_state: GameState) -> List[Dict[str, Any]]:
    """
    Process population changes for all cities.

    Returns list of population event messages.
    """
    events = []

    for city_name, city in game_state.cities.items():
        growth = calculate_growth(city)
        old_pop = city.population

        city.population = max(MIN_POPULATION, min(MAX_POPULATION, city.population + growth))

        if city.food < FAMINE_THRESHOLD:
            events.append({
                "city": city_name,
                "type": "famine",
                "change": city.population - old_pop,
                "message": i18n.t("population.famine", city=city_name,
                                  default=f"Famine in {city_name}! Population declining.")
            })
        elif growth > 0:
            events.append({
                "city": city_name,
                "type": "growth",
                "change": growth,
                "message": i18n.t("population.growth", city=city_name, growth=growth,
                                  default=f"{city_name} population grew by {growth}.")
            })

    return events


def apply_war_losses(city: City) -> int:
    """Apply population losses when a city is conquered."""
    losses = int(city.population * WAR_POPULATION_LOSS)
    city.population = max(MIN_POPULATION, city.population - losses)
    return losses


def process_migration(game_state: GameState) -> List[Dict[str, Any]]:
    """
    Process migration between friendly cities.
    People move from low-morale to high-morale cities.
    """
    events = []

    for faction_name, faction in game_state.factions.items():
        if len(faction.cities) < 2:
            continue

        # Find highest and lowest morale cities
        cities = [(cn, game_state.cities[cn]) for cn in faction.cities
                  if cn in game_state.cities]
        if len(cities) < 2:
            continue

        cities.sort(key=lambda x: x[1].morale)
        low_name, low_city = cities[0]
        high_name, high_city = cities[-1]

        if high_city.morale - low_city.morale > 20:
            migrants = int(low_city.population * MIGRATION_RATE)
            if migrants > 0:
                low_city.population = max(MIN_POPULATION, low_city.population - migrants)
                high_city.population = min(MAX_POPULATION, high_city.population + migrants)
                events.append({
                    "from": low_name,
                    "to": high_name,
                    "count": migrants,
                    "message": i18n.t("population.migration",
                                      count=migrants, from_city=low_name, to_city=high_name,
                                      default=f"{migrants} people migrated from {low_name} to {high_name}.")
                })

    return events
