#!/usr/bin/env python3
"""
Web server wrapper for Sango Text Sim to run on Fly.io.
Provides a simple web interface for the text-based game.
"""
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os
import sys
from io import StringIO
from contextlib import redirect_stdout
import uuid

from src.models import GameState
from src import utils, engine, world, persistence

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Store game states in memory (consider Redis for production)
game_states = {}


def get_or_create_game_state(session_id):
    """Get existing game state or create new one."""
    if session_id not in game_states:
        gs = GameState()
        game_states[session_id] = gs
    return game_states[session_id]


def execute_command(gs, command_text):
    """Execute a game command and return the output."""
    output = StringIO()
    
    try:
        # Parse and execute command
        parts = command_text.strip().split()
        if not parts:
            return ""
        
        cmd = parts[0].lower()
        
        # Handle commands
        if cmd in ['help', '幫助']:
            return get_help_text()
        
        elif cmd in ['start']:
            world.init_world(gs)
            return "Game started! Choose your faction with: choose Wei/Shu/Wu"
        
        elif cmd in ['choose', '選擇']:
            if len(parts) < 2:
                return "Usage: choose Wei/Shu/Wu"
            faction = parts[1]
            world.init_world(gs, player_choice=faction)
            return f"You are now playing as {faction}!"
        
        elif cmd in ['status', '狀態']:
            # Check if game has been initialized
            if not gs.factions or gs.player_faction not in gs.factions:
                return "Game not initialized. Use 'start' or 'choose Wei/Shu/Wu' first."
            
            if len(parts) > 1:
                return utils.format_city_status(gs, parts[1])
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

Game Setup:
  start                 - Start a new game
  choose FACTION        - Choose Wei, Shu, or Wu

Information:
  help                  - Show this help
  status                - Show faction overview
  status CITY           - Show city details
  officers              - List your officers

Actions:
  turn                  - End turn and process AI
  
Save/Load:
  save [FILE]           - Save game
  load [FILE]           - Load game

Full command list available in the terminal version.
For advanced features, run: python game_cmd.py
"""


@app.route('/')
def index():
    """Main game page."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('game.html')


@app.route('/api/command', methods=['POST'])
def api_command():
    """Process game command via API."""
    data = request.get_json()
    command = data.get('command', '')
    
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    gs = get_or_create_game_state(session_id)
    
    # Execute command
    output = execute_command(gs, command)
    
    # Get messages
    messages = gs.messages[-10:] if gs.messages else []
    
    return jsonify({
        'output': output,
        'messages': messages,
        'game_state': {
            'year': gs.year,
            'month': gs.month,
            'faction': gs.player_faction
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
