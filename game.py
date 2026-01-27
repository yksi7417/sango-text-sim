# game.py — Bilingual Characters & Assignments with Traits & Loyalty
from adventurelib import when, start, say
import random, json, os
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple
from i18n import i18n
from src.models import Officer, City, Faction, GameState, get_current_season, TurnEvent
from src.constants import TASKS, TASK_SYNONYMS, ALIASES
from src import utils
from src import engine
from src import world
from src import persistence
from src.display import map_view
from src.display import reports

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

def end_turn() -> List[TurnEvent]:
    return engine.end_turn(STATE)

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

@when("map")
def map_cmd():
    """Display the strategic map"""
    if not STATE.game_started:
        say(i18n.t("errors.not_started"))
        return
    map_display = map_view.render_strategic_map(STATE)
    say(map_display)

@when("officers")
def list_officers():
    pf = STATE.factions[STATE.player_faction]
    lines = []
    for name in pf.officers:
        o = STATE.officers[name]
        t = o.task or "idle"
        tc = f" @ {o.task_city}" if o.task_city else ""
        trait_str = "/".join(i18n.t('traits.'+t) for t in o.traits) if o.traits else "-"
        display_name = utils.get_officer_name(o.name)
        lines.append(f"- {display_name} L{o.leadership} I{o.intelligence} P{o.politics} C{o.charisma}  Energy:{o.energy}  Loyalty:{o.loyalty}  Traits:{trait_str}  City:{o.city}  Task:{t}{tc}")
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
            display_name = utils.get_officer_name(o.name)
            lines.append(f"- {display_name} : {o.task}")
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
        say(i18n.t("errors.officer_tired", name=utils.get_officer_name(off.name)))
        return
    if not ensure_player_city(city_name):
        say(i18n.t("errors.not_yours"))
        return
    off.city = city_name
    off.task = task
    off.task_city = city_name
    off.busy = True
    say(i18n.t("cmd_feedback.assigned", name=utils.get_officer_name(off.name), task=task, city=city_name, desc=i18n.t(f"tasks.{task}")))

@when("cancel OFFICER")
def cancel_cmd(officer):
    name = officer
    off = officer_by_name(name)
    if not off or off.faction != STATE.player_faction:
        say(i18n.t("errors.no_officer"))
        return
    off.task=None; off.task_city=None; off.busy=False
    say(i18n.t("cmd_feedback.assignment_canceled", name=utils.get_officer_name(name)))

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
    say(i18n.t("cmd_feedback.relocated", name=utils.get_officer_name(off.name), city=city_name))

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
    say(i18n.t("cmd_feedback.reward", name=utils.get_officer_name(off.name), gold=amount, delta=delta, loyalty=off.loyalty))

@when("end")
def end_turn_cmd():
    STATE.log(i18n.t("game.ending", year=STATE.year, month=STATE.month))
    events = end_turn()
    STATE.log(i18n.t("game.begin", year=STATE.year, month=STATE.month))

    # Generate and display turn report
    current_season = get_current_season(STATE.month)
    turn_report = reports.generate_turn_report(events, current_season)
    say(turn_report)

    # Show strategic map at start of new turn
    map_display = map_view.render_strategic_map(STATE)
    say(map_display)
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
