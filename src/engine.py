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
from typing import Tuple, List
from .models import Officer, City, GameState, Faction, TurnEvent, EventCategory
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


def challenge_to_duel(game_state: GameState, challenger_name: str, target_name: str) -> dict:
    """
    Initiate a duel challenge from one officer to another.

    The challenger must be from the player's faction.
    The target must be from a different faction and stationed at a city.

    Args:
        game_state: Current game state
        challenger_name: Name of the officer issuing the challenge
        target_name: Name of the officer being challenged

    Returns:
        dict with 'success' (bool), 'message' (str), and optionally 'accepted' (bool)
    """
    from src.systems.duel import start_duel

    # Validate challenger exists and is player's officer
    if challenger_name not in game_state.officers:
        return {'success': False, 'message': i18n.t("duel.error.challenger_not_found")}

    challenger = game_state.officers[challenger_name]
    if challenger.faction != game_state.player_faction:
        return {'success': False, 'message': i18n.t("duel.error.not_your_officer")}

    # Validate target exists
    if target_name not in game_state.officers:
        return {'success': False, 'message': i18n.t("duel.error.target_not_found")}

    target = game_state.officers[target_name]

    # Cannot duel same faction
    if target.faction == challenger.faction:
        return {'success': False, 'message': i18n.t("duel.error.same_faction")}

    # Check if there's already an active duel
    if game_state.active_duel is not None:
        return {'success': False, 'message': i18n.t("duel.error.duel_in_progress")}

    # AI decides whether to accept the duel
    accepted = _ai_accept_duel(game_state, target, challenger)

    if accepted:
        # Start the duel
        duel = start_duel(challenger, target)
        game_state.active_duel = duel
        return {
            'success': True,
            'accepted': True,
            'message': i18n.t("duel.challenge_accepted", challenger=challenger_name, target=target_name)
        }
    else:
        return {
            'success': True,
            'accepted': False,
            'message': i18n.t("duel.challenge_declined", target=target_name)
        }


def _ai_accept_duel(game_state: GameState, defender: Officer, challenger: Officer) -> bool:
    """
    AI logic for deciding whether to accept a duel challenge.

    Factors considered:
    - Leadership differential (won't accept if much weaker)
    - Traits (Brave more likely to accept)
    - Difficulty level (harder AI more aggressive)

    Args:
        game_state: Current game state
        defender: Officer being challenged
        challenger: Officer issuing the challenge

    Returns:
        True if AI accepts, False otherwise
    """
    # Base acceptance chance
    base_chance = 0.5

    # Leadership differential
    leadership_diff = defender.leadership - challenger.leadership
    # +10 leadership = +10% chance, -10 leadership = -10% chance
    leadership_factor = leadership_diff * 0.01

    # Brave trait increases acceptance
    trait_factor = 0.0
    if "Brave" in defender.traits:
        trait_factor += 0.2

    # Difficulty affects AI aggression
    difficulty_factor = 0.0
    if game_state.difficulty == "Easy":
        difficulty_factor = -0.1  # AI less likely to accept
    elif game_state.difficulty == "Hard":
        difficulty_factor = 0.1   # AI more likely to accept

    # Calculate final chance
    accept_chance = base_chance + leadership_factor + trait_factor + difficulty_factor
    accept_chance = max(0.1, min(0.9, accept_chance))  # Clamp between 10% and 90%

    return random.random() < accept_chance


def process_duel_action(game_state: GameState, player_action: str) -> dict:
    """
    Process a player's action during an active duel.

    Args:
        game_state: Current game state
        player_action: Action chosen by player ("attack", "defend", or "special")

    Returns:
        dict with 'success', 'message', 'duel_over', and optionally 'winner'/'loser'
    """
    from src.systems.duel import process_duel_round, is_duel_over, get_duel_winner, DuelAction

    if game_state.active_duel is None:
        return {'success': False, 'message': i18n.t("duel.error.no_active_duel")}

    # Parse player action
    action_map = {
        'attack': DuelAction.ATTACK,
        'defend': DuelAction.DEFEND,
        'special': DuelAction.SPECIAL
    }

    if player_action not in action_map:
        return {'success': False, 'message': i18n.t("duel.error.invalid_action")}

    player_duel_action = action_map[player_action]

    # AI chooses action for opponent
    opponent_action = _ai_choose_duel_action(game_state.active_duel)

    # Process the round
    result = process_duel_round(game_state.active_duel, player_duel_action, opponent_action)

    # Check if duel is over
    if is_duel_over(game_state.active_duel):
        winner = get_duel_winner(game_state.active_duel)
        loser = game_state.active_duel.defender if winner == game_state.active_duel.attacker else game_state.active_duel.attacker

        # Apply duel consequences
        _apply_duel_outcome(game_state, winner, loser)

        # Clear active duel
        game_state.active_duel = None

        return {
            'success': True,
            'duel_over': True,
            'winner': winner.name,
            'loser': loser.name,
            'message': result.message
        }
    else:
        return {
            'success': True,
            'duel_over': False,
            'message': result.message
        }


def _ai_choose_duel_action(duel) -> 'DuelAction':
    """
    AI logic for choosing a duel action.

    Simple strategy:
    - If HP is low (< 30%), prefer Defend
    - If HP is high (> 70%), mix of Attack and Special
    - Otherwise, mostly Attack with occasional Defend

    Args:
        duel: Current duel state

    Returns:
        DuelAction chosen by AI
    """
    from src.systems.duel import DuelAction

    # Defender is the AI in this context
    defender_hp_percent = duel.defender_hp / (duel.defender.leadership * 2)

    if defender_hp_percent < 0.3:
        # Low HP: favor defense (70% defend, 30% attack)
        return DuelAction.DEFEND if random.random() < 0.7 else DuelAction.ATTACK
    elif defender_hp_percent > 0.7:
        # High HP: favor aggression (50% attack, 30% special, 20% defend)
        roll = random.random()
        if roll < 0.5:
            return DuelAction.ATTACK
        elif roll < 0.8:
            return DuelAction.SPECIAL
        else:
            return DuelAction.DEFEND
    else:
        # Medium HP: balanced (60% attack, 10% special, 30% defend)
        roll = random.random()
        if roll < 0.6:
            return DuelAction.ATTACK
        elif roll < 0.7:
            return DuelAction.SPECIAL
        else:
            return DuelAction.DEFEND


def _apply_duel_outcome(game_state: GameState, winner: Officer, loser: Officer) -> None:
    """
    Apply consequences of a duel outcome.

    Winner gains loyalty boost.
    Loser has chance of being captured or killed.
    If during battle, affects morale.

    Args:
        game_state: Current game state
        winner: Victorious officer
        loser: Defeated officer
    """
    # Winner loyalty boost
    winner.loyalty = min(100, winner.loyalty + 5)

    # Loser consequences
    # 50% chance of capture, 50% chance of surviving with injury
    if random.random() < 0.5:
        # Captured: transfer to winner's faction but with low loyalty
        loser.faction = winner.faction
        loser.loyalty = 30  # Captured officers start with low loyalty
        game_state.factions[winner.faction].officers.append(loser.name)
        if loser.name in game_state.factions[loser.faction].officers:
            game_state.factions[loser.faction].officers.remove(loser.name)
        game_state.log(i18n.t("duel.outcome.captured", loser=loser.name, winner=winner.name))
    else:
        # Survived but injured: loyalty penalty
        loser.loyalty = max(0, loser.loyalty - 10)
        loser.energy = max(0, loser.energy - 30)
        game_state.log(i18n.t("duel.outcome.injured", loser=loser.name))


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
                else:
                    # Can't attack, rest instead
                    off.energy = utils.clamp(off.energy + 5, 0, 100)
            
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
            
            game_state.log(i18n.t("game.defect", name=utils.get_officer_name(off.name), new_faction=off.faction))


def end_turn(game_state: GameState) -> List[TurnEvent]:
    """
    Process end-of-turn updates and collect events.

    Turn sequence:
    1. Process all officer assignments
    2. Update monthly economy
    3. Execute AI turns for all factions
    4. Check for defections
    5. Advance time (month/year)
    6. Recover energy for idle officers

    Returns:
        List of TurnEvent objects describing what happened during the turn
    """
    events: List[TurnEvent] = []

    # Track initial message count to separate new messages
    initial_msg_count = len(game_state.messages)

    # Process assignments and collect events
    process_assignments(game_state)

    # Process economy and collect events
    monthly_economy(game_state)

    # AI turns
    for f in list(game_state.factions.keys()):
        ai_turn(game_state, f)

    # Defections
    try_defections(game_state)

    # Collect events from game log messages generated during turn
    new_messages = game_state.messages[initial_msg_count:]
    for msg in new_messages:
        # Categorize events based on message content
        category = categorize_message(msg)
        events.append(TurnEvent(category=category, message=msg, data={}))

    # Time passes
    game_state.month += 1
    if game_state.month > 12:
        game_state.month = 1
        game_state.year += 1
        year_msg = i18n.t("game.new_year", year=game_state.year)
        game_state.log(year_msg)
        events.append(TurnEvent(
            category=EventCategory.ECONOMY,
            message=year_msg,
            data={"year": game_state.year}
        ))

    # Recovery for idle officers
    for off in game_state.officers.values():
        if not off.task:
            off.energy = utils.clamp(off.energy + 12, 0, 100)

    return events


def categorize_message(msg: str) -> EventCategory:
    """
    Categorize a log message into an event category.

    Args:
        msg: Log message to categorize

    Returns:
        EventCategory enum value
    """
    # Check for military keywords
    if any(keyword in msg.lower() for keyword in ['battle', 'victory', 'defeat', 'attack', 'captured', 'troops']):
        return EventCategory.MILITARY

    # Check for officer keywords
    if any(keyword in msg.lower() for keyword in ['defect', 'recruit', 'loyalty', 'officer']):
        return EventCategory.OFFICER

    # Check for diplomatic keywords
    if any(keyword in msg.lower() for keyword in ['alliance', 'treaty', 'relation', 'diplomatic']):
        return EventCategory.DIPLOMATIC

    # Default to economy for things like income, tax, harvest, starvation, etc.
    return EventCategory.ECONOMY


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
