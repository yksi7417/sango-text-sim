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

from i18n import i18n

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def index():
    return render_template('game.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
