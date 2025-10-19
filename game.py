# game.py — Bilingual Characters & Assignments with Traits & Loyalty
from adventurelib import when, start, say
import random, json, os
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple
from i18n import i18n
from src.models import Officer, City, Faction, GameState
from src.constants import TASKS, TASK_SYNONYMS, ALIASES

# =================== Data Models ===================
# Models have been moved to src/models.py

STATE = GameState()

# Override log method to include say() for adventurelib
_original_log = STATE.log
def _log_with_say(msg: str):
    _original_log(msg)
    say(msg)
STATE.log = _log_with_say

# =================== Constants ===================
# Constants have been moved to src/constants.py

# =================== World Setup ===================
def add_officer(off: Officer):
    STATE.officers[off.name] = off
    STATE.factions[off.faction].officers.append(off.name)

def init_world(player_choice: Optional[str] = None):
    random.seed(42)
    factions = ["Wei", "Shu", "Wu"]
    rulers = {"Wei":"曹操","Shu":"劉備","Wu":"孫權"}

    if player_choice and player_choice in factions:
        STATE.player_faction = player_choice
    STATE.player_ruler = rulers[STATE.player_faction]

    cities = {
        "Xuchang": City("Xuchang","Wei",gold=700,food=1000,troops=420,defense=70,morale=65,agri=60,commerce=65,tech=55,walls=70),
        "Luoyang": City("Luoyang","Wei",gold=600,food=900,troops=360,defense=60,morale=60,agri=55,commerce=60,tech=50,walls=62),
        "Chengdu": City("Chengdu","Shu",gold=650,food=980,troops=380,defense=65,morale=72,agri=65,commerce=58,tech=52,walls=66),
        "Hanzhong": City("Hanzhong","Shu",gold=560,food=820,troops=320,defense=58,morale=63,agri=60,commerce=52,tech=48,walls=60),
        "Jianye": City("Jianye","Wu",gold=680,food=980,troops=390,defense=66,morale=68,agri=62,commerce=64,tech=54,walls=65),
        "Wuchang": City("Wuchang","Wu",gold=560,food=820,troops=310,defense=58,morale=61,agri=58,commerce=55,tech=49,walls=60),
    }
    adj = {
        "Xuchang": ["Luoyang","Hanzhong"],
        "Luoyang": ["Xuchang","Hanzhong","Wuchang"],
        "Hanzhong": ["Luoyang","Xuchang","Chengdu"],
        "Chengdu": ["Hanzhong"],
        "Jianye": ["Wuchang"],
        "Wuchang": ["Jianye","Luoyang"],
    }

    factions_map: Dict[str,Faction] = {f:Faction(f) for f in factions}
    for c in cities.values():
        factions_map[c.owner].cities.append(c.name)
    for f in factions:
        factions_map[f].relations = {g:(0 if f==g else random.randint(-20,10)) for g in factions}
        factions_map[f].ruler = rulers[f]

    STATE.cities = cities
    STATE.adj = adj
    STATE.factions = factions_map
    STATE.officers.clear()

    # Officers with traits & initial loyalty
    add_officer(Officer("劉備","Shu",86,80,88,96, loyalty=90, traits=["Benevolent","Charismatic"], city="Chengdu"))
    add_officer(Officer("關羽","Shu",98,79,92,84, loyalty=85, traits=["Brave","Strict"], city="Chengdu"))
    add_officer(Officer("張飛","Shu",97,65,60,82, loyalty=75, traits=["Brave"], city="Chengdu"))
    add_officer(Officer("曹操","Wei",92,94,96,90, loyalty=90, traits=["Charismatic","Scholar"], city="Xuchang"))
    add_officer(Officer("張遼","Wei",94,78,70,76, loyalty=80, traits=["Brave"], city="Luoyang"))
    add_officer(Officer("孫權","Wu",86,80,85,92, loyalty=88, traits=["Charismatic","Merchant"], city="Jianye"))
    add_officer(Officer("周瑜","Wu",90,92,88,88, loyalty=85, traits=["Scholar","Engineer"], city="Jianye"))

    STATE.year = 208
    STATE.month = 1
    STATE.messages.clear()
    STATE.log(i18n.t("game.welcome", ruler=STATE.player_ruler, faction=STATE.player_faction))
    STATE.log(i18n.t("game.time", year=STATE.year, month=STATE.month))

# =================== Utilities ===================
def clamp(v, lo, hi): return max(lo, min(hi, v))

def valid_city(name:str) -> Optional[City]: return STATE.cities.get(name)
def is_adjacent(a:str,b:str)->bool: return b in STATE.adj.get(a, [])
def ensure_player_city(city:str)->bool:
    c = valid_city(city); return c is not None and c.owner == STATE.player_faction
def officer_by_name(name:str) -> Optional[Officer]: return STATE.officers.get(name)

def officers_in_city(faction:str, city_name:str) -> List[Officer]:
    return [o for o in STATE.officers.values() if o.faction==faction and o.city==city_name]

def trait_mult(off: Officer, task:str) -> float:
    mult = 1.0
    if task=="train" and "Strict" in off.traits: mult *= 1.10
    if task=="farm" and "Benevolent" in off.traits: mult *= 1.10
    if task=="trade" and "Merchant" in off.traits: mult *= 1.10
    if task=="research" and "Scholar" in off.traits: mult *= 1.10
    if task=="fortify" and "Engineer" in off.traits: mult *= 1.10
    if task=="recruit" and "Charismatic" in off.traits: mult *= 1.10
    return mult

def print_status(target: Optional[str] = None):
    if not target:
        pf = STATE.factions[STATE.player_faction]
        owned = ", ".join(sorted(pf.cities))
        treasury = sum(STATE.cities[c].gold for c in pf.cities)
        granary = sum(STATE.cities[c].food for c in pf.cities)
        army = sum(STATE.cities[c].troops for c in pf.cities)
        say(i18n.t("ui.overview", year=STATE.year, month=STATE.month, faction=STATE.player_faction, num=len(pf.cities), cities=owned))
        say(i18n.t("ui.resources", gold=treasury, food=granary, troops=army))
        rels = ", ".join(f"{k}:{v:+d}" for k,v in pf.relations.items() if k!=STATE.player_faction)
        say(i18n.t("ui.relations", rels=rels))
        return
    c = valid_city(target)
    if not c:
        say(i18n.t("errors.no_city"))
        return
    owner_tag = "(You)" if c.owner == STATE.player_faction else ""
    say(i18n.t("ui.city_header", name=c.name, owner=c.owner, tag=owner_tag))
    say(i18n.t("ui.city_stats1", gold=c.gold, food=c.food, troops=c.troops, defense=c.defense, morale=c.morale))
    say(i18n.t("ui.city_stats2", agri=c.agri, commerce=c.commerce, tech=c.tech, walls=c.walls))
    garrison = [f"{o.name}(Loy{ o.loyalty },{ '/'.join(i18n.t('traits.'+t) for t in o.traits) })" for o in STATE.officers.values() if o.city == c.name]
    if garrison:
        say(i18n.t("ui.officers_list_header", names=", ".join(garrison)))

def task_key(s: str) -> Optional[str]:
    low = s.lower()
    for key, syns in TASK_SYNONYMS.items():
        if low in [x.lower() for x in syns]:
            return key
    return None

# =================== Core Systems ===================
def tech_attack_bonus(faction: str) -> float:
    f = STATE.factions[faction]
    if not f.cities:
        return 1.0
    avg_tech = sum(STATE.cities[c].tech for c in f.cities) / len(f.cities)
    return 1.0 + (avg_tech - 50) / 500.0

def battle(attacker: City, defender: City, atk_size: int) -> Tuple[bool,int]:
    if atk_size <= 0 or atk_size > attacker.troops:
        return (False, 0)
    atk_mult = tech_attack_bonus(attacker.owner)
    def_mult = tech_attack_bonus(defender.owner) * (1.0 + defender.walls/400.0)
    # Trait influence from stationed officers (highest L officer considered)
    atk_offs = officers_in_city(attacker.owner, attacker.name)
    def_offs = officers_in_city(defender.owner, defender.name)
    if any("Brave" in o.traits for o in atk_offs): atk_mult *= 1.08
    if any("Engineer" in o.traits for o in def_offs): def_mult *= 1.08

    atk_power = atk_size * (attacker.morale/100) * random.uniform(0.8,1.2) * atk_mult
    def_power = (defender.troops + defender.defense*3) * (defender.morale/100) * random.uniform(0.8,1.2) * def_mult
    ratio = atk_power / max(1, def_power)
    if ratio > 1.1: attacker_wins = True
    elif ratio < 0.7: attacker_wins = False
    else: attacker_wins = random.random() < 0.5
    a_loss = int(atk_size * random.uniform(0.2, 0.6))
    d_loss = int(defender.troops * random.uniform(0.25, 0.55))
    attacker.troops -= a_loss
    defender.troops = max(0, defender.troops - d_loss)
    attacker.morale = clamp(attacker.morale + (10 if attacker_wins else -8), 20, 95)
    defender.morale = clamp(defender.morale + (-12 if attacker_wins else 8), 15, 95)
    # loyalty nudge for attackers stationed
    for o in atk_offs:
        o.loyalty = clamp(o.loyalty + (2 if attacker_wins else -1), 0, 100)
    for o in def_offs:
        o.loyalty = clamp(o.loyalty + (2 if not attacker_wins else -1), 0, 100)
    return attacker_wins, a_loss

def transfer_city(new_owner: str, city: City):
    old_owner = city.owner
    if city.name in STATE.factions[old_owner].cities:
        STATE.factions[old_owner].cities.remove(city.name)
    city.owner = new_owner
    STATE.factions[new_owner].cities.append(city.name)
    city.defense = max(40, int(city.defense * 0.8))
    city.morale = 55
    STATE.log(i18n.t("game.taken_city", owner=new_owner, city=city.name))

# --- Assignment resolution ---
def assignment_effect(off: Officer, city: City):
    if not off.task or not off.task_city or city.name != off.task_city:
        return
    energy_cost = 8 if off.task in ("farm","trade","research") else 10
    off.energy = clamp(off.energy - energy_cost, 0, 100)

    mult = trait_mult(off, off.task)
    if off.task == "farm":
        stat = off.politics * mult
        delta = int(1 + stat/25 + random.uniform(0,2))
        city.agri = clamp(city.agri + delta, 0, 100)
        city.food += int(30 + stat/3)
        STATE.log(i18n.t("officer_effect.farm", name=off.name, city=city.name, delta=delta))
    elif off.task == "trade":
        stat = ((off.politics + off.charisma)/2) * mult
        delta = int(1 + stat/30 + random.uniform(0,2))
        city.commerce = clamp(city.commerce + delta, 0, 100)
        city.gold += int(40 + stat/3)
        STATE.log(i18n.t("officer_effect.trade", name=off.name, city=city.name, delta=delta))
    elif off.task == "research":
        stat = off.intelligence * mult
        delta = int(1 + stat/28 + random.uniform(0,2))
        city.tech = clamp(city.tech + delta, 0, 100)
        STATE.log(i18n.t("officer_effect.research", name=off.name, city=city.name, delta=delta))
    elif off.task == "train":
        stat = off.leadership * mult
        troops_gain = int(10 + stat/2)
        morale_gain = int(2 + stat/25)
        city.morale = clamp(city.morale + morale_gain, 20, 95)
        city.troops += troops_gain
        STATE.log(i18n.t("officer_effect.train", name=off.name, city=city.name, troops_gain=troops_gain, morale_gain=morale_gain))
    elif off.task == "fortify":
        stat = ((off.leadership + off.politics)/2) * mult
        delta = int(1 + stat/35 + random.uniform(0,2))
        city.walls = clamp(city.walls + delta, 0, 100)
        city.defense = clamp(city.defense + int(delta/2), 40, 95)
        STATE.log(i18n.t("officer_effect.fortify", name=off.name, city=city.name, delta=delta))
    elif off.task == "recruit":
        stat = ((off.charisma + off.politics)/2) * mult
        batches = int(1 + stat/40)
        cost_gold = 80 * batches
        cost_food = 80 * batches
        if city.gold >= cost_gold and city.food >= cost_food:
            city.gold -= cost_gold; city.food -= cost_food
            gains = 70 * batches
            city.troops += gains
            STATE.log(i18n.t("officer_effect.recruit_success", name=off.name, city=city.name, gains=gains, gold=cost_gold, food=cost_food))
        else:
            STATE.log(i18n.t("officer_effect.recruit_fail", name=off.name, city=city.name))

    # Loyalty dynamics
    off.loyalty = clamp(off.loyalty + 1, 0, 100)  # productive month feels good
    if off.energy <= 10:
        off.loyalty = clamp(off.loyalty - 2, 0, 100)  # overworked

def process_assignments():
    for off in STATE.officers.values():
        if off.task and off.task_city:
            c = STATE.cities.get(off.task_city)
            if c and c.owner == off.faction: assignment_effect(off, c)
            else: off.task=None; off.task_city=None; off.busy=False

# --- Monthly economy & taxes ---
def monthly_economy():
    for city in STATE.cities.values():
        gold_gain = int(30 + city.commerce * 0.8)
        food_gain = int(40 + city.agri * 0.8)
        city.gold += gold_gain
        city.food += food_gain
        upkeep = int(city.troops * 0.12)
        city.food = max(0, city.food - upkeep)
        if city.food == 0:
            desertion = int(city.troops * random.uniform(0.05,0.15))
            city.troops = max(0, city.troops - desertion)
            city.morale = clamp(city.morale - 10, 10, 95)
        city.defense = clamp(city.defense + 1, 40, 95)

    if STATE.month == 1:
        for city in STATE.cities.values():
            if city.owner:
                city.gold += city.commerce * 5
        STATE.log(i18n.t("game.jan_tax"))
    if STATE.month == 7:
        for city in STATE.cities.values():
            if city.owner:
                city.food += city.agri * 5
        STATE.log(i18n.t("game.jul_harvest"))

# --- AI and Loyalty/Defection ---
def ai_turn(faction_name: str):
    if faction_name == STATE.player_faction: return
    f = STATE.factions[faction_name]
    if not f.cities: return
    offs = [STATE.officers[n] for n in f.officers]
    random.shuffle(offs)
    for off in offs:
        if off.energy < 25:
            off.task=None; off.task_city=None; off.busy=False
            off.energy = clamp(off.energy + 10, 0, 100)
            continue
        if not off.task:
            base_city = STATE.cities[random.choice(f.cities)]
            off.city = base_city.name
            choice = random.choice(["farm","trade","research","train","fortify","recruit","attack","rest"])
            if choice in TASKS:
                off.task = choice; off.task_city = base_city.name; off.busy=True
            elif choice == "attack":
                targets = [nb for nb in STATE.adj.get(base_city.name,[]) if STATE.cities[nb].owner != faction_name]
                if targets and base_city.troops >= 140:
                    dst = random.choice(targets)
                    size = int(base_city.troops * random.uniform(0.3,0.6))
                    win, _ = battle(base_city, STATE.cities[dst], size)
                    if win and STATE.cities[dst].troops <= 0:
                        transfer_city(faction_name, STATE.cities[dst])
            else:
                off.energy = clamp(off.energy + 5, 0, 100)

def try_defections():
    # Simple defection model: player's officers with very low loyalty may defect to an adjacent enemy city.
    player_officers = [STATE.officers[n] for n in STATE.factions[STATE.player_faction].officers]
    for off in player_officers:
        if off.loyalty < 35 and random.random() < 0.10:  # 10% monthly if loyalty dangerously low
            # find any adjacent enemy city to current city
            if not off.city: continue
            adjacents = STATE.adj.get(off.city, [])
            enemy_cities = [cn for cn in adjacents if STATE.cities[cn].owner != STATE.player_faction]
            if not enemy_cities: continue
            dst_city = STATE.cities[random.choice(enemy_cities)]
            # migrate officer to enemy faction
            STATE.factions[STATE.player_faction].officers.remove(off.name)
            off.faction = dst_city.owner
            STATE.factions[off.faction].officers.append(off.name)
            off.city = dst_city.name
            off.task=None; off.task_city=None; off.busy=False
            off.loyalty = 60  # reset base loyalty to new lord
            STATE.log(i18n.t("game.defect", name=off.name, new_faction=off.faction))

def end_turn():
    process_assignments()
    monthly_economy()
    for f in list(STATE.factions.keys()):
        ai_turn(f)
    try_defections()
    # Time passes
    STATE.month += 1
    if STATE.month > 12:
        STATE.month = 1
        STATE.year += 1
        STATE.log(i18n.t("game.new_year", year=STATE.year))
    # recovery for idle officers
    for off in STATE.officers.values():
        if not off.task:
            off.energy = clamp(off.energy + 12, 0, 100)

def check_victory():
    all_player = all(c.owner == STATE.player_faction for c in STATE.cities.values())
    if all_player:
        STATE.log(i18n.t("game.unify", faction=STATE.player_faction, year=STATE.year))
        return True
    if not STATE.factions[STATE.player_faction].cities:
        STATE.log(i18n.t("game.fallen"))
        return True
    return False

# =================== Commands (EN + ZH) ===================
def show_help():
    say(i18n.t("help.header"))
    for line in i18n.t("help.lines"):
        say(line)
    say("Examples:")
    for ex in i18n.t("help.examples"):
        say("  " + ex)

@when("help")
def help_cmd():
    show_help()

@when("lang LANGUAGE")
def lang_cmd(language):
    lang = language.lower() if language else ""
    if lang not in ("en","zh"):
        say(i18n.t("lang.usage"))
        return
    i18n.load(lang)
    say(i18n.t("lang.set", lang=lang))
    say(i18n.t("game.time", year=STATE.year, month=STATE.month))

@when("status")
def status_self():
    print_status()

@when("status CITY")
def status_city_cmd(city):
    target = city.title() if city else ""
    print_status(target)

@when("officers")
def list_officers():
    pf = STATE.factions[STATE.player_faction]
    lines = []
    for name in pf.officers:
        o = STATE.officers[name]
        t = o.task or "idle"
        tc = f" @ {o.task_city}" if o.task_city else ""
        trait_str = "/".join(i18n.t('traits.'+t) for t in o.traits) if o.traits else "-"
        lines.append(f"- {o.name} L{o.leadership} I{o.intelligence} P{o.politics} C{o.charisma}  Energy:{o.energy}  Loyalty:{o.loyalty}  Traits:{trait_str}  City:{o.city}  Task:{t}{tc}")
    say("\n".join(lines))

@when("tasks CITY")
def tasks_city(city):
    city = city.title() if city else ""
    if city not in STATE.cities:
        say(i18n.t("errors.no_city"))
        return
    lines = []
    for o in STATE.officers.values():
        if o.task_city == city:
            lines.append(f"- {o.name} : {o.task}")
    say("\n".join(lines) if lines else ("（無任務）" if i18n.lang=="zh" else "(no tasks)"))

@when("assign OFFICER to TASK in CITY")
def assign_cmd(officer, task, city):
    officer_name = officer
    task_raw = task
    city_name = city.title()

    task = task_key(task_raw)
    if task is None:
        say(i18n.t("errors.invalid_task"))
        return

    off = officer_by_name(officer_name)
    if not off:
        say(i18n.t("errors.no_officer"))
        return
    if off.faction != STATE.player_faction:
        say(i18n.t("errors.not_your_officer"))
        return
    if off.energy < 20:
        say(i18n.t("errors.officer_tired", name=off.name))
        return
    if not ensure_player_city(city_name):
        say(i18n.t("errors.not_yours"))
        return
    off.city = city_name
    off.task = task
    off.task_city = city_name
    off.busy = True
    say(i18n.t("cmd_feedback.assigned", name=off.name, task=task, city=city_name, desc=i18n.t(f"tasks.{task}")))

@when("cancel OFFICER")
def cancel_cmd(officer):
    name = officer
    off = officer_by_name(name)
    if not off or off.faction != STATE.player_faction:
        say(i18n.t("errors.no_officer"))
        return
    off.task=None; off.task_city=None; off.busy=False
    say(i18n.t("cmd_feedback.assignment_canceled", name=name))

@when("move OFFICER to CITY")
def move_officer_cmd(officer, city):
    officer_name = officer
    city_name = city.title()
    off = officer_by_name(officer_name)
    if not off or off.faction != STATE.player_faction:
        say(i18n.t("errors.no_officer"))
        return
    if not ensure_player_city(city_name):
        say(i18n.t("errors.not_yours"))
        return
    off.city = city_name
    say(i18n.t("cmd_feedback.relocated", name=off.name, city=city_name))

@when("march NUMBER from SOURCE to DESTINATION", number=int)
def march_cmd(number, source, destination):
    n = number
    src = source.title()
    dst = destination.title()
    if not ensure_player_city(src):
        say(i18n.t("errors.not_source"))
        return
    if not valid_city(dst):
        say(i18n.t("errors.no_city"))
        return
    if not is_adjacent(src, dst):
        say(i18n.t("errors.not_adjacent"))
        return
    sc = STATE.cities[src]; dc = STATE.cities[dst]
    if sc.troops < n:
        say(i18n.t("errors.not_enough_troops"))
        return
    sc.troops -= n
    if dc.owner == STATE.player_faction:
        dc.troops += n
        say(i18n.t("cmd_feedback.marched", n=n, src=src, dst=dst))
    else:
        say(i18n.t("cmd_feedback.attack_launch", n=n, src=src, dst=dst))
        win, _ = battle(sc, dc, n)
        if win and dc.troops <= 0:
            transfer_city(STATE.player_faction, dc)
        else:
            say(i18n.t("cmd_feedback.assault_fail", city=dc.name))

@when("attack TARGET from SOURCE with NUMBER", number=int)
def attack_cmd(target, source, number):
    city_name = target.title()
    src = source.title()
    n = number
    if not ensure_player_city(src):
        say(i18n.t("errors.not_source"))
        return
    target_city = valid_city(city_name)
    if not target_city:
        say(i18n.t("errors.no_city"))
        return
    if src == city_name:
        say(i18n.t("errors.same_city"))
        return
    if not is_adjacent(src, city_name):
        say(i18n.t("errors.not_adjacent"))
        return
    src_city = STATE.cities[src]
    if n <= 0 or n > src_city.troops:
        say(i18n.t("errors.invalid_troops"))
        return
    win, _ = battle(src_city, target_city, n)
    if win and target_city.troops <= 0:
        transfer_city(STATE.player_faction, target_city)
    else:
        say(i18n.t("cmd_feedback.assault_fail", city=target_city.name))

@when("spy CITY")
def spy_cmd(city):
    city_name = city.title()
    c = valid_city(city_name)
    if not c:
        say(i18n.t("errors.no_city"))
        return
    for cn in STATE.factions[STATE.player_faction].cities:
        city = STATE.cities[cn]
        if city.gold >= 50:
            city.gold -= 50
            say(i18n.t("spy.report", name=c.name, owner=c.owner, troops=c.troops, defense=c.defense, morale=c.morale, agri=c.agri, commerce=c.commerce, tech=c.tech, walls=c.walls))
            return
    say(i18n.t("errors.need_gold50"))

@when("negotiate FACTION")
def negotiate_cmd(faction):
    target = faction.title()
    if target not in STATE.factions:
        say("No such faction.")
        return
    if target == STATE.player_faction:
        say("...")
        return
    paid = False
    for cn in STATE.factions[STATE.player_faction].cities:
        city = STATE.cities[cn]
        if city.gold >= 100:
            city.gold -= 100; paid = True; break
    if not paid:
        say(i18n.t("errors.need_gold", amount=100))
        return
    delta = random.randint(3, 10)
    pf = STATE.factions[STATE.player_faction]
    pf.relations[target] = clamp(pf.relations.get(target,0) + delta, -100, 100)
    STATE.factions[target].relations[STATE.player_faction] = clamp(STATE.factions[target].relations.get(STATE.player_faction,0) + delta//2, -100, 100)
    say(f"Relations with {target} {delta:+d}.")

@when("reward OFFICER with NUMBER", number=int)
def reward_cmd(officer, number):
    name = officer
    amount = number
    off = officer_by_name(name)
    if not off or off.faction != STATE.player_faction:
        say(i18n.t("errors.no_officer"))
        return
    # pay from any player city
    payer = None
    for cn in STATE.factions[STATE.player_faction].cities:
        city = STATE.cities[cn]
        if city.gold >= amount:
            payer = city; break
    if payer is None:
        say(i18n.t("errors.need_gold", amount=amount))
        return
    payer.gold -= amount
    delta = max(1, amount // 100)
    off.loyalty = clamp(off.loyalty + delta, 0, 100)
    off.energy = clamp(off.energy + 5, 0, 100)
    say(i18n.t("cmd_feedback.reward", name=off.name, gold=amount, delta=delta, loyalty=off.loyalty))

@when("end")
def end_turn_cmd():
    STATE.log(i18n.t("game.ending", year=STATE.year, month=STATE.month))
    end_turn()
    STATE.log(i18n.t("game.begin", year=STATE.year, month=STATE.month))
    if check_victory():
        say("help / load FILE")

def _do_save(path):
    data = asdict(STATE)
    data["cities"] = {k:asdict(v) for k,v in STATE.cities.items()}
    data["factions"] = {k:{"name":f.name,"relations":f.relations,"cities":f.cities,"officers":f.officers,"ruler":f.ruler} for k,f in STATE.factions.items()}
    data["officers"] = {k:asdict(v) for k,v in STATE.officers.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    say(f"Saved to {path}.")

@when("save FILE")
def save_cmd_with_file(file):
    _do_save(file)

@when("save")
def save_cmd():
    _do_save("savegame.json")

def _do_load(path):
    if not os.path.exists(path):
        say(i18n.t("errors.file_missing"))
        return
    with open(path,"r",encoding="utf-8") as f:
        data = json.load(f)
    STATE.year = data["year"]
    STATE.month = data["month"]
    STATE.player_faction = data["player_faction"]
    STATE.player_ruler = data["player_ruler"]
    STATE.difficulty = data.get("difficulty","Normal")
    STATE.messages = []
    STATE.cities = {k:City(**v) for k,v in data["cities"].items()}
    STATE.factions = {}
    for k, fv in data["factions"].items():
        STATE.factions[k] = Faction(fv["name"], fv["relations"], fv["cities"], fv.get("officers",[]), fv.get("ruler",""))
    STATE.officers = {k:Officer(**v) for k,v in data["officers"].items()}
    STATE.adj = {k:v for k,v in data["adj"].items()}
    say(i18n.t("game.time", year=STATE.year, month=STATE.month))

@when("load FILE")
def load_cmd_with_file(file):
    _do_load(file)

@when("load")
def load_cmd():
    _do_load("savegame.json")

@when("choose FACTION")
def choose_cmd(faction):
    name = faction.title()
    if name not in ["Wei","Shu","Wu"]:
        say("Wei/Shu/Wu")
        return
    init_world(player_choice=name)

@when("start")
def start_cmd():
    say("Running.")

def main():
    print("==== Sango Characters Strategy (Traits & Loyalty, Bilingual) ====")
    print("Type 'lang zh' for Chinese, 'lang en' for English.")
    print("Try: officers/武將, assign/指派, reward/賞賜, end/結束")
    init_world(None)
    start()

if __name__ == "__main__":
    main()
