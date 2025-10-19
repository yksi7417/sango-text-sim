"""
Game Engine - Core game mechanics including combat, economy, and turn processing.

This module contains the central game logic:
- Battle system with tech bonuses and trait effects
- City ownership transfer
- Officer assignment processing (farming, trading, research, etc.)
- Monthly economy (income, upkeep, starvation)
- AI turn logic
- Officer defection system
- Turn progression and victory conditions
"""

import random
from typing import Tuple
from .models import Officer, City, GameState, Faction
from .constants import TASKS
from . import utils
from i18n import i18n


def tech_attack_bonus(game_state: GameState, faction: str) -> float:
    """
    Calculate technology-based attack multiplier for a faction.
    
    Args:
        game_state: Current game state
        faction: Name of the faction
    
    Returns:
        Multiplier based on average city tech level (1.0 + tech/50)
    """
    faction_cities = [game_state.cities[c] for c in game_state.factions[faction].cities]
    if not faction_cities:
        return 1.0
    avg_tech = sum(city.tech for city in faction_cities) / len(faction_cities)
    return 1.0 + avg_tech / 50.0


def battle(game_state: GameState, attacker: City, defender: City, atk_size: int) -> Tuple[bool, int]:
    """
    Resolve a battle between two cities.
    
    Combat calculation includes:
    - Base attack/defense from troop counts
    - Commander trait bonuses
    - City defense bonus for defender
    - Technology bonuses
    - Random variance
    
    Side effects:
    - Updates troop counts
    - Adjusts morale
    - Affects officer loyalty
    
    Args:
        game_state: Current game state
        attacker: Attacking city
        defender: Defending city
        atk_size: Number of attacking troops
    
    Returns:
        Tuple of (victory: bool, casualties: int)
    """
    # Find commanders
    atk_officers = utils.officers_in_city(game_state, attacker.owner, attacker.name)
    def_officers = utils.officers_in_city(game_state, defender.owner, defender.name)
    atk_comm = max(atk_officers, key=lambda o: o.leadership, default=None)
    def_comm = max(def_officers, key=lambda o: o.leadership, default=None)
    
    # Base power
    atk_pow = atk_size * (1 + attacker.morale / 100.0)
    def_pow = defender.troops * (1 + defender.morale / 100.0)
    
    # Commander bonuses
    if atk_comm:
        mult = utils.trait_mult(atk_comm, "leader")
        atk_pow *= (1.0 + atk_comm.leadership / 100.0 * mult)
    if def_comm:
        mult = utils.trait_mult(def_comm, "leader")
        def_pow *= (1.0 + def_comm.leadership / 100.0 * mult)
    
    # Defense bonus
    def_pow *= (1.0 + defender.defense / 100.0)
    
    # Tech bonus for attacker
    tech_mult = tech_attack_bonus(game_state, attacker.owner)
    atk_pow *= tech_mult
    
    # Random factor
    atk_pow *= random.uniform(0.85, 1.15)
    def_pow *= random.uniform(0.85, 1.15)
    
    # Determine outcome
    victory = atk_pow > def_pow
    casualties = int(atk_size * random.uniform(0.25, 0.45))
    
    # Update troops
    if victory:
        defender.troops = max(0, defender.troops - int(atk_size * 0.5))
        attacker.troops -= casualties
        attacker.morale = utils.clamp(attacker.morale + 5, 0, 100)
        defender.morale = utils.clamp(defender.morale - 10, 0, 100)
        game_state.log(i18n.t("battle.victory", attacker=attacker.name, defender=defender.name))
    else:
        attacker.troops -= casualties
        attacker.morale = utils.clamp(attacker.morale - 10, 0, 100)
        defender.morale = utils.clamp(defender.morale + 5, 0, 100)
        game_state.log(i18n.t("battle.defeat", attacker=attacker.name, defender=defender.name))
    
    # Loyalty effects
    if atk_comm:
        atk_comm.loyalty = utils.clamp(atk_comm.loyalty + (5 if victory else -5), 0, 100)
    if def_comm:
        def_comm.loyalty = utils.clamp(def_comm.loyalty + (-5 if victory else 5), 0, 100)
    
    return victory, casualties


def transfer_city(game_state: GameState, new_owner: str, city: City) -> None:
    """
    Transfer ownership of a city to a new faction.
    
    Args:
        game_state: Current game state
        new_owner: Name of the faction gaining the city
        city: City being transferred
    """
    old_owner = city.owner
    if old_owner in game_state.factions:
        if city.name in game_state.factions[old_owner].cities:
            game_state.factions[old_owner].cities.remove(city.name)
    
    city.owner = new_owner
    city.defense = 20
    city.morale = 50
    
    if new_owner not in game_state.factions:
        game_state.factions[new_owner] = Faction(name=new_owner, cities=[city.name], officers=[], relations={})
    else:
        if city.name not in game_state.factions[new_owner].cities:
            game_state.factions[new_owner].cities.append(city.name)
    
    game_state.log(i18n.t("game.city_captured", city=city.name, faction=new_owner))


def assignment_effect(game_state: GameState, off: Officer, city: City) -> None:
    """
    Apply the effects of an officer's assigned task.
    
    Tasks and their effects:
    - farm: +food, +morale, loyalty bonus from diligent trait
    - trade: +gold, +morale, loyalty bonus from charming trait
    - research: +tech, loyalty bonus from brilliant trait
    - train: +troops, loyalty penalty
    - fortify: +defense, morale penalty
    - recruit: +officers (new random officer), energy penalty
    
    Args:
        game_state: Current game state
        off: Officer performing the task
        city: City where task is performed
    """
    task = off.task
    energy_cost = 20
    
    if task == "farm":
        base = 15
        mult = utils.trait_mult(off, "diligent")
        city.food += int(base * mult)
        city.morale = utils.clamp(city.morale + 2, 0, 100)
        if "diligent" in off.traits:
            off.loyalty = utils.clamp(off.loyalty + 2, 0, 100)
    
    elif task == "trade":
        base = 20
        mult = utils.trait_mult(off, "charming")
        city.gold += int(base * mult)
        city.morale = utils.clamp(city.morale + 3, 0, 100)
        if "charming" in off.traits:
            off.loyalty = utils.clamp(off.loyalty + 2, 0, 100)
    
    elif task == "research":
        base = 3
        mult = utils.trait_mult(off, "brilliant")
        city.tech += int(base * mult)
        if "brilliant" in off.traits:
            off.loyalty = utils.clamp(off.loyalty + 2, 0, 100)
    
    elif task == "train":
        city.troops += 10
        off.loyalty = utils.clamp(off.loyalty - 1, 0, 100)
    
    elif task == "fortify":
        city.defense = utils.clamp(city.defense + 5, 0, 100)
        city.morale = utils.clamp(city.morale - 2, 0, 100)
    
    elif task == "recruit":
        # Create new random officer
        new_name = f"Officer_{len(game_state.officers) + 1}"
        new_off = Officer(
            name=new_name,
            faction=off.faction,
            city=city.name,
            leadership=random.randint(40, 70),
            intelligence=random.randint(40, 70),
            politics=random.randint(40, 70),
            charisma=random.randint(40, 70),
            energy=100,
            loyalty=random.randint(50, 80),
            traits=[],
            task=None,
            task_city=None,
            busy=False
        )
        game_state.officers[new_name] = new_off
        game_state.factions[off.faction].officers.append(new_name)
        game_state.log(i18n.t("game.recruit", name=new_name, city=city.name))
        energy_cost = 30
    
    # Apply energy cost
    off.energy = utils.clamp(off.energy - energy_cost, 0, 100)
    
    # Clear task
    off.task = None
    off.task_city = None
    off.busy = False


def process_assignments(game_state: GameState) -> None:
    """
    Process all officer assignments for the current turn.
    
    Iterates through all officers and applies their assigned tasks
    if they are in a city still owned by their faction.
    """
    # Create a list of officers to avoid RuntimeError when dict changes size during iteration
    for off in list(game_state.officers.values()):
        if off.task and off.task_city:
            city = game_state.cities.get(off.task_city)
            if city and city.owner == off.faction:
                assignment_effect(game_state, off, city)


def monthly_economy(game_state: GameState) -> None:
    """
    Process monthly economic updates for all cities.
    
    Economic events:
    - Base income from city gold production
    - Troop upkeep costs
    - Starvation effects (food < 0)
    - Desertion effects (gold < 0)
    - Special seasonal events (January tax, July harvest)
    """
    for city in game_state.cities.values():
        # Income
        city.gold += 10
        
        # Upkeep
        upkeep = city.troops // 10
        city.gold -= upkeep
        city.food -= upkeep
        
        # Starvation
        if city.food < 0:
            loss = int(city.troops * 0.1)
            city.troops -= loss
            city.morale = utils.clamp(city.morale - 10, 0, 100)
            game_state.log(i18n.t("game.starvation", city=city.name, loss=loss))
            city.food = 0
        
        # Desertion
        if city.gold < 0:
            loss = int(city.troops * 0.05)
            city.troops -= loss
            city.morale = utils.clamp(city.morale - 5, 0, 100)
            game_state.log(i18n.t("game.desertion", city=city.name, loss=loss))
            city.gold = 0
    
    # Special months
    if game_state.month == 1:  # January: tax season
        for city in game_state.cities.values():
            tax = city.gold // 10
            city.gold += tax
            game_state.log(i18n.t("game.tax", city=city.name, amount=tax))
    
    if game_state.month == 7:  # July: harvest
        for city in game_state.cities.values():
            harvest = city.food // 5
            city.food += harvest
            game_state.log(i18n.t("game.harvest", city=city.name, amount=harvest))


def ai_turn(game_state: GameState, faction_name: str) -> None:
    """
    Execute AI decision-making for a faction's turn.
    
    AI logic:
    - Officers with low energy (<25) rest and recover
    - Officers without tasks get randomly assigned:
      - Work tasks (farm, trade, research, train, fortify, recruit)
      - Attack adjacent enemy cities if sufficient troops
      - Rest to recover energy
    
    Args:
        game_state: Current game state
        faction_name: Name of the faction taking its turn
    """
    if faction_name == game_state.player_faction:
        return
    
    f = game_state.factions.get(faction_name)
    if not f or not f.cities:
        return
    
    for off_name in f.officers:
        off = game_state.officers[off_name]
        
        # Low energy officers rest
        if off.energy < 25:
            off.task = None
            off.task_city = None
            off.busy = False
            off.energy = utils.clamp(off.energy + 10, 0, 100)
            continue
        
        # Assign tasks to idle officers
        if not off.task:
            base_city = game_state.cities[random.choice(f.cities)]
            off.city = base_city.name
            choice = random.choice(["farm", "trade", "research", "train", "fortify", "recruit", "attack", "rest"])
            
            if choice in TASKS:
                off.task = choice
                off.task_city = base_city.name
                off.busy = True
            
            elif choice == "attack":
                targets = [nb for nb in game_state.adj.get(base_city.name, [])
                          if game_state.cities[nb].owner != faction_name]
                if targets and base_city.troops >= 140:
                    dst = random.choice(targets)
                    size = int(base_city.troops * random.uniform(0.3, 0.6))
                    win, _ = battle(game_state, base_city, game_state.cities[dst], size)
                    if win and game_state.cities[dst].troops <= 0:
                        transfer_city(game_state, faction_name, game_state.cities[dst])
            
            else:  # rest
                off.energy = utils.clamp(off.energy + 5, 0, 100)


def try_defections(game_state: GameState) -> None:
    """
    Process potential officer defections based on loyalty.
    
    Player officers with very low loyalty (<35) have a 10% chance
    to defect to an adjacent enemy city each month.
    """
    player_officers = [game_state.officers[n] for n in game_state.factions[game_state.player_faction].officers]
    
    for off in player_officers:
        if off.loyalty < 35 and random.random() < 0.10:  # 10% monthly if loyalty dangerously low
            # Find any adjacent enemy city
            if not off.city:
                continue
            
            adjacents = game_state.adj.get(off.city, [])
            enemy_cities = [cn for cn in adjacents if game_state.cities[cn].owner != game_state.player_faction]
            if not enemy_cities:
                continue
            
            dst_city = game_state.cities[random.choice(enemy_cities)]
            
            # Migrate officer to enemy faction
            game_state.factions[game_state.player_faction].officers.remove(off.name)
            off.faction = dst_city.owner
            game_state.factions[off.faction].officers.append(off.name)
            off.city = dst_city.name
            off.task = None
            off.task_city = None
            off.busy = False
            off.loyalty = 60  # Reset base loyalty to new lord
            
            game_state.log(i18n.t("game.defect", name=off.name, new_faction=off.faction))


def end_turn(game_state: GameState) -> None:
    """
    Process end-of-turn updates.
    
    Turn sequence:
    1. Process all officer assignments
    2. Update monthly economy
    3. Execute AI turns for all factions
    4. Check for defections
    5. Advance time (month/year)
    6. Recover energy for idle officers
    """
    process_assignments(game_state)
    monthly_economy(game_state)
    
    for f in list(game_state.factions.keys()):
        ai_turn(game_state, f)
    
    try_defections(game_state)
    
    # Time passes
    game_state.month += 1
    if game_state.month > 12:
        game_state.month = 1
        game_state.year += 1
        game_state.log(i18n.t("game.new_year", year=game_state.year))
    
    # Recovery for idle officers
    for off in game_state.officers.values():
        if not off.task:
            off.energy = utils.clamp(off.energy + 12, 0, 100)


def check_victory(game_state: GameState) -> bool:
    """
    Check for victory or defeat conditions.
    
    Victory: Player controls all cities
    Defeat: Player has no cities remaining
    
    Args:
        game_state: Current game state
    
    Returns:
        True if game should end, False otherwise
    """
    all_player = all(c.owner == game_state.player_faction for c in game_state.cities.values())
    if all_player:
        game_state.log(i18n.t("game.unify", faction=game_state.player_faction, year=game_state.year))
        return True
    
    if not game_state.factions[game_state.player_faction].cities:
        game_state.log(i18n.t("game.fallen"))
        return True
    
    return False
