# Game State Management Fixes

## Problem Statement
The game had issues with state persistence and inconsistent game start logic:
1. Sometimes state would be lost after clicking buttons
2. Players could sometimes bypass the game start screen and go directly to menus
3. No enforcement of proper game initialization sequence

## Root Causes
1. **No explicit game_started flag**: The frontend relied solely on checking if `faction !== 'None'`, which could be bypassed
2. **Session state not tracking initialization**: Session state initialized with `current_menu: 'main'` even before game was started
3. **Inconsistent state validation**: Menu handlers didn't consistently validate that the game was properly initialized

## Solutions Implemented

### 1. Added `game_started` Flag to Session State
**File**: `web_server.py`

- Added `game_started: False` to default session state initialization
- Set `game_started: True` when a faction is chosen via the 'choose' command
- Set `game_started: False` when 'start' command is issued (before faction selection)
- Calculate `game_started` based on actual game state (faction existence) in API responses

```python
def get_session_state(session_id):
    """Get or create session state for menu navigation."""
    if session_id not in session_states:
        session_states[session_id] = {
            'current_menu': 'pregame',  # Start in pregame mode
            'current_city': None,
            'language': 'en',
            'game_started': False  # Track initialization explicitly
        }
    return session_states[session_id]
```

### 2. Enforced Pregame State
**File**: `web_server.py`

- Changed default `current_menu` from `'main'` to `'pregame'`
- Added validation in `handle_menu_input()` to check game initialization
- Redirect to pregame menu if trying to access internal affairs without initialized game

```python
def handle_menu_input(gs, session_state, input_text):
    current_menu = session_state.get('current_menu', 'pregame')
    
    # Check if game is started for non-pregame menus
    # Game is considered started if faction exists in game state
    if current_menu not in ['pregame', 'main']:
        if not gs.factions or gs.player_faction not in gs.factions:
            session_state['current_menu'] = 'pregame'
            session_state['game_started'] = False
            return "Game not properly initialized. Please start a new game and choose your faction."
```

### 3. Frontend Button State Management
**File**: `templates/game.html`

- Updated `updateButtons()` to check both `gameStarted` flag AND faction value
- Force pregame buttons if game isn't properly initialized
- Prevents showing game menu buttons until faction is chosen

```javascript
function updateButtons(menuState, gameState) {
    const currentMenu = menuState?.current_menu || 'pregame';
    const faction = gameState?.faction || 'None';
    const gameStarted = gameState?.game_started || false;
    
    // Only show game menus if game is properly started AND faction is set
    if (gameStarted && faction && faction !== 'None' && faction !== null && faction !== '') {
        // Show menu buttons
        buttons = menuConfig[currentMenu] || menuConfig.main;
    } else {
        // Force pregame buttons if game hasn't been properly started
        buttons = menuConfig.pregame;
    }
}
```

### 4. API Response Enhancement
**File**: `web_server.py`

- Calculate `game_started` from actual game state (presence of factions and player_faction)
- Automatically sync session_state `game_started` flag if game is detected as started
- Include `game_started` in JSON response to frontend

```python
# Calculate game_started based on whether faction is properly initialized
game_started = bool(gs.factions and gs.player_faction in gs.factions)
if game_started and not session_state.get('game_started'):
    session_state['game_started'] = True

return jsonify({
    'game_state': {
        'year': gs.year,
        'month': gs.month,
        'faction': gs.player_faction,
        'game_started': game_started  # Explicit flag
    },
    ...
})
```

## Benefits

1. **State Persistence**: Game state is now consistently tracked and validated
2. **Forced Initialization**: Players must start a game and choose faction before accessing menus
3. **Clear Game Flow**: 
   - Start game → Choose faction → Access main menu → Play game
4. **Resilient to Edge Cases**: 
   - If session state is lost but game state exists, it auto-recovers
   - If trying to access internal menus without initialization, redirects to pregame
5. **Better UX**: Clear feedback when game isn't initialized
6. **Test Compatibility**: Tests work whether or not they set the `game_started` flag (auto-detected from game state)

## Testing

All 187 tests pass, including:
- Menu navigation tests
- Internal affairs tests  
- Integration tests
- Game state persistence tests

The solution is backward-compatible with existing test code that directly calls `world.init_world()` without setting session flags.

## Future Improvements

Consider:
1. Add visual indicators in UI for game state (e.g., "Game Not Started" banner)
2. Persist game state to Redis/database for production deployment
3. Add session timeout warnings
4. Implement autosave on state changes
