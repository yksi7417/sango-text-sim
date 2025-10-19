# game.py — Bilingual Characters & Assignments with Traits & Loyalty
from adventurelib import when, start, say
import random, json, os
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple
from i18n import i18n
from src.models import Officer, City, Faction, GameState
from src.constants import TASKS, TASK_SYNONYMS, ALIASES
from src import utils
from src import engine
from src import world
from src import persistence

# =================== Data Models ===================
# Models have been moved to src/models.py

STATE = GameState()

# Override log method to include say() for adventurelib
_original_log = STATE.log
def _log_with_say(msg: str):
    _original_log(msg)
    say(msg)
STATE.log = _log_with_say

# =================== World Initialization ===================
# World initialization has been moved to src/world.py

# Wrapper functions that pass STATE to world
def add_officer(off: Officer):
    world.add_officer(STATE, off)

def init_world(player_choice: Optional[str] = None):
    world.init_world(STATE, player_choice)

# =================== Utilities ===================

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
# Utilities have been moved to src/utils.py

# Wrapper functions that pass STATE to utils
def clamp(v, lo, hi): return utils.clamp(v, lo, hi)
def valid_city(name): return utils.valid_city(STATE, name)
def is_adjacent(a, b): return utils.is_adjacent(STATE, a, b)
def ensure_player_city(city): return utils.ensure_player_city(STATE, city)
def officer_by_name(name): return utils.officer_by_name(STATE, name)
def officers_in_city(faction, city_name): return utils.officers_in_city(STATE, faction, city_name)
def trait_mult(off, task): return utils.trait_mult(off, task)
def task_key(s): return utils.task_key(s)

def print_status(target: Optional[str] = None):
    """Display faction overview or city status"""
    if not target:
        overview, resources, relations = utils.format_faction_overview(STATE)
        say(overview)
        say(resources)
        say(relations)
    else:
        lines = utils.format_city_status(STATE, target)
        if lines:
            for line in lines:
                say(line)
        else:
            say(i18n.t("errors.no_city"))

# =================== Wrapper Functions for Engine ===================
def tech_attack_bonus(faction: str) -> float:
    return engine.tech_attack_bonus(STATE, faction)

def battle(attacker: City, defender: City, atk_size: int) -> Tuple[bool, int]:
    return engine.battle(STATE, attacker, defender, atk_size)

def transfer_city(new_owner: str, city: City) -> None:
    engine.transfer_city(STATE, new_owner, city)

def assignment_effect(off: Officer, city: City) -> None:
    engine.assignment_effect(STATE, off, city)

def process_assignments() -> None:
    engine.process_assignments(STATE)

def monthly_economy() -> None:
    engine.monthly_economy(STATE)

def ai_turn(faction_name: str) -> None:
    engine.ai_turn(STATE, faction_name)

def try_defections() -> None:
    engine.try_defections(STATE)

def end_turn() -> None:
    engine.end_turn(STATE)

def check_victory() -> bool:
    return engine.check_victory(STATE)

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

# =================== Save/Load ===================
# Persistence has been moved to src/persistence.py

def _do_save(path):
    if persistence.save_game(STATE, path):
        say(f"Saved to {path}.")
    else:
        say("Save failed.")

def _do_load(path):
    error = persistence.load_game(STATE, path)
    if error:
        say(i18n.t(error))
    else:
        say(i18n.t("game.time", year=STATE.year, month=STATE.month))

@when("save FILE")
def save_cmd_with_file(file):
    _do_save(file)

@when("save")
def save_cmd():
    _do_save(persistence.get_default_save_path())

@when("load FILE")
def load_cmd_with_file(file):
    _do_load(file)

@when("load")
def load_cmd():
    _do_load(persistence.get_default_save_path())

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
