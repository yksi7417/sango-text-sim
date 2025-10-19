from flask import Flask, send_from_directory, jsonify, request, make_response
import json
import base64
import os

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/init', methods=['GET'])
def api_init():
    initial = {
        "version": "0.1",
        "factions": [],
        "cities": [],
        "officers": [],
        "turn": {"year": 190, "month": 1}
    }
    return jsonify(initial)

@app.route('/api/echo', methods=['POST'])
def api_echo():
    data = request.json or {}
    cmd = data.get('command', '')
    return jsonify({"ok": True, "command": cmd, "message": f"Received command: {cmd}"})

@app.route('/api/save', methods=['POST'])
def api_save():
    state = request.json or {}
    raw = json.dumps(state)
    encoded = base64.b64encode(raw.encode()).decode()
    resp = make_response(jsonify({"ok": True}))
    resp.set_cookie('sango_state', encoded, httponly=False, samesite='Lax')
    return resp

@app.route('/api/load', methods=['GET'])
def api_load():
    encoded = request.cookies.get('sango_state')
    if not encoded:
        return jsonify({"ok": False, "error": "no_state"})
    try:
        raw = base64.b64decode(encoded).decode()
        state = json.loads(raw)
        return jsonify({"ok": True, "state": state})
    except Exception as e:
        return jsonify({"ok": False, "error": "invalid_state", "detail": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
