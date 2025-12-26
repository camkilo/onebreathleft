#!/usr/bin/env python3
"""
Web server for One Breath Left
Provides API endpoints for the browser-based game
"""

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import json
import os
import secrets
from datetime import datetime

# Import game logic (without pygame dependencies)
from game.game_state_web import GameStateWeb
from game.ai_companion import AICompanion

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Store active game sessions in memory
# In production, use Redis or similar
game_sessions = {}

@app.route('/')
def index():
    """Serve the game page"""
    return render_template('index.html')

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Initialize a new game session"""
    session_id = secrets.token_hex(16)
    
    # Create new game state
    game_state = GameStateWeb()
    game_sessions[session_id] = game_state
    
    # Return initial game state
    return jsonify({
        'session_id': session_id,
        'state': game_state.get_state_dict()
    })

@app.route('/api/game/update', methods=['POST'])
def update_game():
    """Update game state based on player input"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    game_state = game_sessions[session_id]
    
    # Apply player input
    if 'input' in data:
        game_state.apply_input(data['input'])
    
    # Update game (delta time in seconds)
    dt = data.get('dt', 0.016)  # Default ~60fps
    game_state.update(dt)
    
    return jsonify({
        'state': game_state.get_state_dict()
    })

@app.route('/api/game/action', methods=['POST'])
def game_action():
    """Handle specific game actions (accept/reject advice)"""
    data = request.json
    session_id = data.get('session_id')
    action = data.get('action')
    
    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    game_state = game_sessions[session_id]
    
    if action == 'accept_advice':
        game_state.follow_advice()
    elif action == 'reject_advice':
        game_state.ignore_advice()
    
    return jsonify({
        'state': game_state.get_state_dict()
    })

@app.route('/api/game/end', methods=['POST'])
def end_game():
    """End game session and save playthrough"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    game_state = game_sessions[session_id]
    game_state.save_playthrough()
    
    # Clean up session
    del game_sessions[session_id]
    
    return jsonify({'success': True})

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(game_sessions)
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('playthroughs', exist_ok=True)
    
    # Run server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
