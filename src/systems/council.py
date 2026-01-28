"""
Council System - Morning council meetings with advisor recommendations.

Advisors present agenda items based on game state analysis:
- Economic: resource shortages, development opportunities
- Military: threats, attack opportunities
- Diplomatic: faction relations, alliance possibilities
- Personnel: officer loyalty, vacant positions
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from ..models import GameState, Officer
from i18n import i18n


class AgendaCategory(Enum):
    """Categories for council agenda items."""
    ECONOMIC = "economic"
    MILITARY = "military"
    DIPLOMATIC = "diplomatic"
    PERSONNEL = "personnel"


@dataclass
class AgendaItem:
    """A single agenda item presented by an advisor."""
    category: AgendaCategory
    presenter: str  # Officer name
    title: str
    recommendation: str
    data: dict = field(default_factory=dict)


@dataclass
class Council:
    """Represents a council meeting session."""
    agenda: List[AgendaItem] = field(default_factory=list)
    faction: str = ""
    year: int = 208
    month: int = 1


def _find_best_advisor(game_state: GameState, stat: str) -> Optional[Officer]:
    """Find the officer with highest stat in player faction."""
    faction = game_state.factions.get(game_state.player_faction)
    if not faction:
        return None

    best = None
    best_val = -1
    for name in faction.officers:
        off = game_state.officers.get(name)
        if off and getattr(off, stat, 0) > best_val:
            best = off
            best_val = getattr(off, stat, 0)
    return best


def _check_economic_issues(game_state: GameState) -> List[AgendaItem]:
    """Generate economic agenda items."""
    items = []
    advisor = _find_best_advisor(game_state, "politics")
    if not advisor:
        return items

    faction = game_state.factions[game_state.player_faction]

    for city_name in faction.cities:
        city = game_state.cities.get(city_name)
        if not city:
            continue

        if city.food < 200:
            items.append(AgendaItem(
                category=AgendaCategory.ECONOMIC,
                presenter=advisor.name,
                title=i18n.t("council.economic.low_food_title", city=city_name),
                recommendation=i18n.t("council.economic.low_food_rec", city=city_name),
                data={"city": city_name, "food": city.food}
            ))

        if city.gold < 100:
            items.append(AgendaItem(
                category=AgendaCategory.ECONOMIC,
                presenter=advisor.name,
                title=i18n.t("council.economic.low_gold_title", city=city_name),
                recommendation=i18n.t("council.economic.low_gold_rec", city=city_name),
                data={"city": city_name, "gold": city.gold}
            ))

        if city.agri < 40:
            items.append(AgendaItem(
                category=AgendaCategory.ECONOMIC,
                presenter=advisor.name,
                title=i18n.t("council.economic.low_agri_title", city=city_name),
                recommendation=i18n.t("council.economic.low_agri_rec", city=city_name),
                data={"city": city_name, "agri": city.agri}
            ))

    return items


def _check_military_issues(game_state: GameState) -> List[AgendaItem]:
    """Generate military agenda items."""
    items = []
    advisor = _find_best_advisor(game_state, "leadership")
    if not advisor:
        return items

    faction = game_state.factions[game_state.player_faction]

    for city_name in faction.cities:
        city = game_state.cities.get(city_name)
        if not city:
            continue

        # Check for adjacent enemy threats
        adj_cities = game_state.adj.get(city_name, [])
        for adj_name in adj_cities:
            adj_city = game_state.cities.get(adj_name)
            if adj_city and adj_city.owner != game_state.player_faction:
                if adj_city.troops > city.troops:
                    items.append(AgendaItem(
                        category=AgendaCategory.MILITARY,
                        presenter=advisor.name,
                        title=i18n.t("council.military.threat_title", city=city_name, enemy=adj_name),
                        recommendation=i18n.t("council.military.threat_rec", city=city_name),
                        data={"city": city_name, "enemy": adj_name}
                    ))

        # Weak garrison
        if city.troops < 100:
            items.append(AgendaItem(
                category=AgendaCategory.MILITARY,
                presenter=advisor.name,
                title=i18n.t("council.military.weak_garrison_title", city=city_name),
                recommendation=i18n.t("council.military.weak_garrison_rec", city=city_name),
                data={"city": city_name, "troops": city.troops}
            ))

    return items


def _check_diplomatic_issues(game_state: GameState) -> List[AgendaItem]:
    """Generate diplomatic agenda items."""
    items = []
    advisor = _find_best_advisor(game_state, "charisma")
    if not advisor:
        return items

    faction = game_state.factions[game_state.player_faction]

    for other_name, relation in faction.relations.items():
        if relation < -30:
            items.append(AgendaItem(
                category=AgendaCategory.DIPLOMATIC,
                presenter=advisor.name,
                title=i18n.t("council.diplomatic.hostile_title", faction=other_name),
                recommendation=i18n.t("council.diplomatic.hostile_rec", faction=other_name),
                data={"faction": other_name, "relation": relation}
            ))

    return items


def _check_personnel_issues(game_state: GameState) -> List[AgendaItem]:
    """Generate personnel agenda items."""
    items = []
    advisor = _find_best_advisor(game_state, "intelligence")
    if not advisor:
        return items

    faction = game_state.factions[game_state.player_faction]

    for off_name in faction.officers:
        off = game_state.officers.get(off_name)
        if not off:
            continue

        if off.loyalty < 50:
            items.append(AgendaItem(
                category=AgendaCategory.PERSONNEL,
                presenter=advisor.name,
                title=i18n.t("council.personnel.low_loyalty_title", officer=off.name),
                recommendation=i18n.t("council.personnel.low_loyalty_rec", officer=off.name),
                data={"officer": off.name, "loyalty": off.loyalty}
            ))

    # Check for cities without officers
    for city_name in faction.cities:
        has_officer = any(
            game_state.officers.get(n) and game_state.officers[n].city == city_name
            for n in faction.officers
        )
        if not has_officer:
            items.append(AgendaItem(
                category=AgendaCategory.PERSONNEL,
                presenter=advisor.name,
                title=i18n.t("council.personnel.no_officer_title", city=city_name),
                recommendation=i18n.t("council.personnel.no_officer_rec", city=city_name),
                data={"city": city_name}
            ))

    return items


def generate_council_agenda(game_state: GameState) -> Council:
    """
    Generate a council meeting agenda based on current game state.

    Analyzes the player's faction situation and creates agenda items
    covering economic, military, diplomatic, and personnel concerns.

    Args:
        game_state: Current game state

    Returns:
        Council object with populated agenda
    """
    council = Council(
        faction=game_state.player_faction,
        year=game_state.year,
        month=game_state.month
    )

    council.agenda.extend(_check_economic_issues(game_state))
    council.agenda.extend(_check_military_issues(game_state))
    council.agenda.extend(_check_diplomatic_issues(game_state))
    council.agenda.extend(_check_personnel_issues(game_state))

    return council
