#!/usr/bin/env python3
"""
Web server wrapper for Sango Text Sim to run on Fly.io.
Provides a simple web interface for the text-based game.
"""
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_session import Session
import os
import sys
from io import StringIO
from contextlib import redirect_stdout
import uuid

from src.models import GameState
from src import utils, engine, world, persistence
from src.constants import INTERNAL_ACTION_GOLD_COSTS, INTERNAL_ACTION_ENERGY_COST
from i18n import i18n

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Store game states in memory (consider Redis for production)
game_states = {}
# Store current menu state and selected city for each session
session_states = {}


def get_or_create_game_state(session_id):
    """Get existing game state or create new one."""
    if session_id not in game_states:
        gs = GameState()
        game_states[session_id] = gs
    return game_states[session_id]


def get_session_state(session_id):
    """Get or create session state for menu navigation."""
    if session_id not in session_states:
        session_states[session_id] = {
            'current_menu': 'pregame',
            'current_city': None,
            'language': 'en',
            'game_started': False
        }
    return session_states[session_id]


def get_current_city(gs, session_state):
    """Get the current city, defaulting to the first city of the player's faction if None."""
    current_city = session_state.get('current_city')
    
    # If no current city is set, default to the first city
    if not current_city and gs.factions and gs.player_faction in gs.factions:
        faction = gs.factions[gs.player_faction]
        if faction.cities:
            current_city = list(faction.cities)[0]
            session_state['current_city'] = current_city
    
    return current_city


def format_menu(menu_type, gs, session_state):
    """Format a menu for display."""
    lang = session_state.get('language', 'en')
    i18n.load(lang)
    
    menu_key = f"menu.{menu_type}"
    lines = []
    
    # Don't show title or prompt in web version - buttons handle this
    # Just show current city if set
    if session_state.get('current_city'):
        current_city_msg = i18n.t("menu.common.current_city", city=session_state['current_city'])
        lines.append(current_city_msg)
    
    # Handle special case for city selection
    if menu_type == 'city':
        if not gs.factions or gs.player_faction not in gs.factions:
            return i18n.t("menu.city.none")
        
        faction = gs.factions[gs.player_faction]
        if not faction.cities:
            return i18n.t("menu.city.none")
        
        # Don't show city list in text - buttons will handle it
        return ""
    
    # For other menus, don't print menu text - buttons handle the UI
    return ""


def handle_menu_input(gs, session_state, input_text):
    """Handle menu navigation and command execution."""
    current_menu = session_state.get('current_menu', 'pregame')
    lang = session_state.get('language', 'en')
    i18n.load(lang)
    
    # Check if game is started for non-pregame menus
    # Game is considered started if faction exists in game state
    if current_menu not in ['pregame', 'main']:
        if not gs.factions or gs.player_faction not in gs.factions:
            session_state['current_menu'] = 'pregame'
            session_state['game_started'] = False
            return "Game not properly initialized. Please start a new game and choose your faction."
    
    # Allow 'menu' command to return to main menu
    if input_text.lower() == 'menu':
        session_state['current_menu'] = 'main'
        return ""  # No text output, buttons will update
    
    # Allow 'back' or '0' to go back
    if input_text.lower() in ['back', '0']:
        session_state['current_menu'] = 'main'
        return ""  # No text output, buttons will update
    
    # Allow 'again' or 'continue' to stay in current submenu
    if input_text.lower() in ['again', 'continue', 'c'] and current_menu != 'main':
        return ""  # No text output, just stay in menu
    
    # Main menu routing
    if current_menu == 'main':
        menu_map = {
            '1': 'city',
            '2': 'war',
            '3': 'officer',
            '4': 'diplomacy',
            '5': 'internal',
            '6': 'merchant',
            '7': 'tactics',
            '8': 'advice'
        }
        
        if input_text in menu_map:
            session_state['current_menu'] = menu_map[input_text]
            return ""  # No text output, buttons will update
        else:
            return i18n.t("menu.common.invalid")
    
    # City selection
    elif current_menu == 'city':
        if not gs.factions or gs.player_faction not in gs.factions:
            session_state['current_menu'] = 'main'
            return "Game not initialized. Use 'start' or 'choose Wei/Shu/Wu' first."
        
        faction = gs.factions[gs.player_faction]
        cities = list(faction.cities)
        
        # Try numeric selection
        if input_text.isdigit():
            idx = int(input_text) - 1
            if 0 <= idx < len(cities):
                session_state['current_city'] = cities[idx]
                session_state['current_menu'] = 'main'
                return i18n.t("menu.city.set", city=cities[idx])
        
        # Try name selection
        city_name = input_text.title()
        if city_name in cities:
            session_state['current_city'] = city_name
            session_state['current_menu'] = 'main'
            return i18n.t("menu.city.set", city=city_name)
        
        return i18n.t("menu.common.invalid")
    
    # Internal Affairs menu
    elif current_menu == 'internal':
        if not gs.factions or gs.player_faction not in gs.factions:
            session_state['current_menu'] = 'main'
            return "Game not initialized. Use 'start' or 'choose Wei/Shu/Wu' first."

        # Get current city, defaulting to first city if None
        city_name = get_current_city(gs, session_state)

        if not city_name:
            session_state['current_menu'] = 'main'
            return "You don't control any cities."

        # Validate city ownership
        faction = gs.factions[gs.player_faction]
        if city_name not in faction.cities:
            session_state['current_menu'] = 'main'
            return f"{city_name} is no longer under your control."

        # If awaiting officer selection, handle that first
        if session_state.get('pending_assignment'):
            return handle_internal_officer_selection(gs, session_state, input_text)

        # Internal Affairs action mapping
        if input_text == '1':  # Agriculture
            return handle_internal_action(gs, session_state, city_name, 'farm')
        elif input_text == '2':  # Flood Management
            return handle_internal_action(gs, session_state, city_name, 'flood')
        elif input_text == '3':  # Commerce
            return handle_internal_action(gs, session_state, city_name, 'trade')
        elif input_text == '4':  # Technology
            return handle_internal_action(gs, session_state, city_name, 'research')
        elif input_text == '5':  # Build School
            return handle_build_school(gs, session_state, city_name)
        else:
            return i18n.t("menu.common.invalid")
    
    # Other menus - not yet implemented
    else:
        return i18n.t("menu.common.not_implemented")


def handle_internal_action(gs, session_state, city_name, action_type):
    """Handle internal affairs actions like agriculture, commerce, etc."""
    lang = session_state.get('language', 'en')
    i18n.load(lang)

    city = gs.cities.get(city_name)
    if not city:
        session_state['current_menu'] = 'main'
        return "City not found."

    faction = gs.factions[gs.player_faction]

    # Map action types to task types
    task_map = {
        'farm': 'farm',
        'trade': 'trade',
        'research': 'research',
        'flood': 'farm'  # Flood management is also agriculture-related
    }

    task = task_map.get(action_type, 'farm')
    energy_cost = INTERNAL_ACTION_ENERGY_COST
    gold_cost = INTERNAL_ACTION_GOLD_COSTS.get(action_type, 0)

    # Find available officers in the city
    available_officers = [
        off for off_name in faction.officers
        if (off := gs.officers.get(off_name)) and
        off.city == city_name and
        off.energy >= energy_cost and
        not off.busy
    ]

    if not available_officers:
        template = i18n.t("menu.internal.no_officers")
        if template != "menu.internal.no_officers":
            return template.format(city=city_name)
        return (
            f"No available officers in {city_name} with sufficient energy ({energy_cost}+).\n\n"
            f"Assign officers to {city_name} or wait for them to recover energy."
        )

    # Sort officers by suitability for the task
    def officer_score(off):
        base_stat = off.politics if task in ['farm', 'trade'] else off.intelligence
        return utils.trait_mult(off, task) * base_stat

    sorted_officers = sorted(
        available_officers,
        key=lambda o: (officer_score(o), o.energy),
        reverse=True
    )

    options = i18n.t("menu.internal.options")
    action_names = {
        'farm': options[0] if isinstance(options, list) and len(options) > 0 else "Agriculture",
        'flood': options[1] if isinstance(options, list) and len(options) > 1 else "Flood Management",
        'trade': options[2] if isinstance(options, list) and len(options) > 2 else "Commerce",
        'research': options[3] if isinstance(options, list) and len(options) > 3 else "Technology"
    }

    action_name = action_names.get(action_type, action_type.title())

    # Store pending assignment info for follow-up selection
    session_state['pending_assignment'] = {
        'city': city_name,
        'task': task,
        'action_type': action_type,
        'action_display': action_name,
        'officers': [off.name for off in sorted_officers],
        'gold_cost': gold_cost,
        'energy_cost': energy_cost,
    }

    if i18n.lang == 'zh':
        header = f"請選擇派遣至{city_name}負責{action_name}的武將。"
        cost_line = f"需要金錢 {gold_cost}，消耗體力 {energy_cost}。"
        footer = "輸入編號或姓名。輸入 'cancel' 取消。"
        roster_header = "可用武將："
    else:
        header = f"Select an officer to handle {action_name} in {city_name}."
        cost_line = f"Cost: {gold_cost} gold, {energy_cost} energy."
        footer = "Enter the number or officer name. Type 'cancel' to choose another action."
        roster_header = "Available officers:"

    lines = [header, cost_line, "", roster_header]
    for idx, officer in enumerate(sorted_officers, start=1):
        display_name = utils.get_officer_name(officer.name)
        lines.append(
            f"  {idx}. {display_name} (POL {officer.politics} | INT {officer.intelligence} | EN {officer.energy})"
        )
    lines.append(footer)

    return "\n".join(lines)


def handle_internal_officer_selection(gs, session_state, input_text):
    """Handle the officer selection step for internal affairs."""
    lang = session_state.get('language', 'en')
    i18n.load(lang)

    pending = session_state.get('pending_assignment') or {}
    city_name = pending.get('city')
    city = gs.cities.get(city_name) if city_name else None
    if not city:
        session_state.pop('pending_assignment', None)
        return "City not found."

    selection = input_text.strip()

    if selection.lower() == 'cancel':
        session_state.pop('pending_assignment', None)
        if i18n.lang == 'zh':
            return "已取消指派。"
        return "Assignment cancelled."

    officer_names = pending.get('officers', [])
    selected_officer = None

    if selection.isdigit():
        idx = int(selection) - 1
        if 0 <= idx < len(officer_names):
            selected_officer = gs.officers.get(officer_names[idx])
    else:
        for name in officer_names:
            off = gs.officers.get(name)
            if not off:
                continue
            display_name = utils.get_officer_name(off.name)
            if selection.lower() in (off.name.lower(), display_name.lower()):
                selected_officer = off
                break

    if not selected_officer:
        if i18n.lang == 'zh':
            return "請輸入有效的武將編號或姓名。"
        return "Please choose a valid officer number or name."

    energy_cost = pending.get('energy_cost', INTERNAL_ACTION_ENERGY_COST)
    if selected_officer.energy < energy_cost:
        if i18n.lang == 'zh':
            return f"{utils.get_officer_name(selected_officer.name)} 體力不足 ({selected_officer.energy}/{energy_cost})。"
        return f"{utils.get_officer_name(selected_officer.name)} does not have enough energy ({selected_officer.energy}/{energy_cost})."

    if selected_officer.busy:
        if i18n.lang == 'zh':
            return f"{utils.get_officer_name(selected_officer.name)} 正在執行其他任務。"
        return f"{utils.get_officer_name(selected_officer.name)} is already assigned elsewhere."

    gold_cost = pending.get('gold_cost', 0)
    if city.gold < gold_cost:
        session_state.pop('pending_assignment', None)
        if i18n.lang == 'zh':
            return f"{city.name} 的金錢不足，需要 {gold_cost}。"
        return f"{city.name} does not have enough gold (needs {gold_cost})."

    # Deduct resources and assign the officer
    city.gold -= gold_cost
    selected_officer.city = city.name
    selected_officer.task = pending.get('task')
    selected_officer.task_city = city.name
    selected_officer.busy = True
    selected_officer.assignment_energy_spent = True
    selected_officer.energy = utils.clamp(selected_officer.energy - energy_cost, 0, 100)

    action_display = pending.get('action_display', pending.get('action_type', 'task'))
    session_state.pop('pending_assignment', None)

    officer_display = utils.get_officer_name(selected_officer.name)

    if i18n.lang == 'zh':
        lines = [
            f"[OK] {officer_display} 已派往 {city.name} 負責{action_display}。",
            f"  消耗金錢 {gold_cost} | 體力 {selected_officer.energy}/100",
            "  成果將於月底結算。",
            "",
            "城市現況:",
            f"  農業: {city.agri}",
            f"  商業: {city.commerce}",
            f"  科技: {city.tech}",
            f"  金錢: {city.gold} | 糧草: {city.food}"
        ]
    else:
        lines = [
            f"[OK] {officer_display} assigned to {action_display} in {city.name} for the month.",
            f"  Cost: {gold_cost} gold | Energy: {selected_officer.energy}/100",
            "  Results will apply at the end of the month.",
            "",
            "City Status:",
            f"  Agriculture: {city.agri}",
            f"  Commerce: {city.commerce}",
            f"  Technology: {city.tech}",
            f"  Gold: {city.gold} | Food: {city.food}"
        ]

    return "\n".join(lines)


def handle_build_school(gs, session_state, city_name):
    """Handle building schools (future feature)."""
    lang = session_state.get('language', 'en')
    i18n.load(lang)
    
    return i18n.t("menu.common.not_implemented") + "\n\nSchool construction will be available in a future update.\n\nType 'menu' to return to main menu."


def execute_command(gs, command_text, session_state=None):
    """Execute a game command and return the output."""
    output = StringIO()
    
    # If session_state is provided and we're in menu mode, handle menu navigation
    if session_state:
        current_menu = session_state.get('current_menu', 'main')
        
        # Check if command is a menu navigation (pure numbers or 'menu'/'back')
        is_menu_command = (
            command_text.strip().isdigit() or 
            command_text.lower() in ['menu', 'back', '0'] or
            (current_menu == 'city' and command_text.strip())  # City names
        )
        
        # If in a menu (not main/pregame) or it's a menu navigation command, use menu handler
        # Pregame menu should use regular command handler for 'start' and 'choose'
        if (current_menu not in ['main', 'pregame']) or is_menu_command:
            return handle_menu_input(gs, session_state, command_text.strip())
    
    try:
        # Parse and execute command
        parts = command_text.strip().split()
        if not parts:
            # If no command and session_state exists, don't show menu text
            if session_state:
                return ""
            return ""
        
        cmd = parts[0].lower()
        
        # Handle 'menu' command to enter menu mode
        if cmd == 'menu' and session_state:
            session_state['current_menu'] = 'main'
            return ""  # Buttons will show the menu
        
        # Handle 'lang' command
        if cmd == 'lang':
            if len(parts) < 2:
                return "Usage: lang en|zh"
            lang = parts[1].lower()
            if lang not in ['en', 'zh']:
                return "Usage: lang en|zh"
            if session_state:
                session_state['language'] = lang
            i18n.load(lang)
            return f"Language set to {lang}."
        
        # Handle commands
        if cmd in ['help', '幫助']:
            return get_help_text()
        
        elif cmd in ['start']:
            world.init_world(gs)
            if session_state:
                session_state['current_menu'] = 'pregame'
                session_state['game_started'] = False
                return "Game started! Choose your faction with: choose Wei/Shu/Wu"
            return "Game started! Choose your faction with: choose Wei/Shu/Wu"
        
        elif cmd in ['choose', '選擇']:
            if len(parts) < 2:
                return "Usage: choose Wei/Shu/Wu"
            faction = parts[1]
            world.init_world(gs, player_choice=faction)
            if session_state:
                session_state['current_menu'] = 'main'
                session_state['game_started'] = True
            return f"You are now playing as {faction}!"
        
        elif cmd in ['status', '狀態']:
            # Check if game has been initialized
            if not gs.factions or gs.player_faction not in gs.factions:
                return "Game not initialized. Use 'start' or 'choose Wei/Shu/Wu' first."
            
            if len(parts) > 1:
                city_status = utils.format_city_status(gs, parts[1])
                if city_status is None:
                    return "City not found."
                return "\n".join(city_status)
            else:
                overview, resources, relations = utils.format_faction_overview(gs)
                return f"{overview}\n{resources}\n{relations}"
        
        elif cmd in ['officers', '武將']:
            # Check if game has been initialized
            if not gs.factions or gs.player_faction not in gs.factions:
                return "Game not initialized. Use 'start' or 'choose Wei/Shu/Wu' first."
            
            faction = gs.factions.get(gs.player_faction)
            if not faction:
                return "No faction selected. Use 'choose' command first."
            
            lines = ["=== Officers ==="]
            for off_name in faction.officers:
                off = gs.officers[off_name]
                lines.append(
                    f"{off.name} | L{off.leadership} I{off.intelligence} "
                    f"P{off.politics} C{off.charisma} | "
                    f"Energy:{off.energy} Loyalty:{off.loyalty}"
                )
            return "\n".join(lines)
        
        elif cmd in ['turn', 'end', '結束']:
            engine.end_turn(gs)
            if engine.check_victory(gs):
                return "=== GAME OVER ==="
            return "Turn ended. AI factions have moved."
        
        elif cmd in ['save', '保存']:
            filepath = parts[1] if len(parts) > 1 else f"save_{session.get('session_id')}.json"
            if persistence.save_game(gs, filepath):
                return f"Game saved to {filepath}"
            return "Save failed"
        
        elif cmd in ['load', '讀取']:
            filepath = parts[1] if len(parts) > 1 else f"save_{session.get('session_id')}.json"
            error = persistence.load_game(gs, filepath)
            if error:
                return f"Load failed: {error}"
            return f"Game loaded from {filepath}"
        
        else:
            return f"Unknown command: {cmd}. Type 'help' for available commands."
    
    except Exception as e:
        return f"Error: {str(e)}"


def get_help_text():
    """Return help text."""
    return """
=== Sango Text Sim - Commands ===

Taxes: Commerce taxes in January, Agriculture taxes in July

Game Setup:
  start                 - Start a new game
  choose FACTION        - Choose Wei, Shu, or Wu

Information:
  help                  - Show this help
  menu                  - Show interactive menu system
  status                - Show faction overview
  status CITY           - Show city details
  officers              - List your officers

Actions:
  turn                  - End turn and process AI
  lang en|zh            - Switch language
  
Save/Load:
  save [FILE]           - Save game
  load [FILE]           - Load game

Full command list available in the terminal version.
For advanced features, run: python game_cmd.py

TIP: Type 'menu' for an easier menu-based interface!
"""


@app.route('/')
def index():
    """Main game page."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('game.html')


@app.route('/locales/<path:filename>')
def serve_locales(filename):
    """Serve locale JSON files."""
    return send_from_directory('locales', filename)


@app.route('/api/command', methods=['POST'])
def api_command():
    """Process game command via API."""
    data = request.get_json()
    command = data.get('command', '')
    
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    gs = get_or_create_game_state(session_id)
    session_state = get_session_state(session_id)
    
    # Execute command with session state for menu support
    output = execute_command(gs, command, session_state)
    
    # Get messages
    messages = gs.messages[-10:] if gs.messages else []
    
    # Prepare city list for dynamic buttons if in city menu
    city_list = []
    if session_state.get('current_menu') == 'city' and gs.factions and gs.player_faction in gs.factions:
        faction = gs.factions[gs.player_faction]
        city_list = list(faction.cities) if faction.cities else []
    
    # Get current city (with default to first city)
    current_city = get_current_city(gs, session_state)
    
    # Calculate game_started based on whether faction is properly initialized
    game_started = bool(gs.factions and gs.player_faction in gs.factions)
    if game_started and not session_state.get('game_started'):
        session_state['game_started'] = True
    
    return jsonify({
        'output': output,
        'messages': messages,
        'game_state': {
            'year': gs.year,
            'month': gs.month,
            'faction': gs.player_faction,
            'game_started': game_started
        },
        'menu_state': {
            'current_menu': session_state.get('current_menu', 'pregame'),
            'current_city': current_city,
            'language': session_state.get('language', 'en'),
            'cities': city_list
        }
    })


@app.route('/api/state', methods=['GET'])
def api_state():
    """Get current game state."""
    if 'session_id' not in session:
        return jsonify({'error': 'No active session'})
    
    session_id = session['session_id']
    gs = get_or_create_game_state(session_id)
    
    return jsonify({
        'year': gs.year,
        'month': gs.month,
        'faction': gs.player_faction,
        'messages': gs.messages[-10:] if gs.messages else []
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
