// game.js - Client-side JavaScript for Sango Text Sim

let gameState = null;

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    initializeGame();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const commandInput = document.getElementById('command-input');
    commandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendCommand();
        }
    });
}

// Initialize game state
async function initializeGame() {
    try {
        const response = await fetch('/api/init');
        const data = await response.json();
        gameState = data;
        updateStateDisplay();
        showMessage('save-load-message', 'Game initialized successfully', 'success');
    } catch (error) {
        showMessage('save-load-message', `Error initializing game: ${error.message}`, 'error');
    }
}

// Update state display
function updateStateDisplay() {
    const stateDisplay = document.getElementById('state-display');
    if (!gameState) {
        stateDisplay.textContent = 'No state available';
        stateDisplay.className = 'state-content loading';
        return;
    }

    const stateText = formatGameState(gameState);
    stateDisplay.textContent = stateText;
    stateDisplay.className = 'state-content';
}

// Format game state for display
function formatGameState(state) {
    let output = [];
    
    output.push(`=== Sango Text Sim ===`);
    output.push(`Version: ${state.version || 'N/A'}`);
    output.push('');
    
    if (state.turn) {
        output.push(`Turn: Year ${state.turn.year}, Month ${state.turn.month}`);
        output.push('');
    }
    
    if (state.factions && state.factions.length > 0) {
        output.push(`Factions: ${state.factions.length}`);
        state.factions.forEach(f => {
            output.push(`  - ${f}`);
        });
        output.push('');
    } else {
        output.push('Factions: None');
        output.push('');
    }
    
    if (state.cities && state.cities.length > 0) {
        output.push(`Cities: ${state.cities.length}`);
        state.cities.forEach(c => {
            output.push(`  - ${c}`);
        });
        output.push('');
    } else {
        output.push('Cities: None');
        output.push('');
    }
    
    if (state.officers && state.officers.length > 0) {
        output.push(`Officers: ${state.officers.length}`);
        state.officers.forEach(o => {
            output.push(`  - ${o}`);
        });
        output.push('');
    } else {
        output.push('Officers: None');
        output.push('');
    }
    
    if (state.message) {
        output.push(`Message: ${state.message}`);
    }
    
    return output.join('\n');
}

// Send command to server
async function sendCommand() {
    const commandInput = document.getElementById('command-input');
    const command = commandInput.value.trim();
    
    if (!command) {
        showMessage('command-response', 'Please enter a command', 'error');
        return;
    }
    
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    
    try {
        const response = await fetch('/api/echo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: command,
                state: gameState
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            const responseText = `Command: ${data.command}\n${data.message || 'Command processed'}`;
            showMessage('command-response', responseText, 'info');
            
            // Update state if returned
            if (data.state) {
                gameState = data.state;
                updateStateDisplay();
            }
        } else {
            showMessage('command-response', `Error: ${data.error || 'Unknown error'}`, 'error');
        }
        
        commandInput.value = '';
    } catch (error) {
        showMessage('command-response', `Error sending command: ${error.message}`, 'error');
    } finally {
        sendBtn.disabled = false;
        commandInput.focus();
    }
}

// Save game state
async function saveGame() {
    if (!gameState) {
        showMessage('save-load-message', 'No game state to save', 'error');
        return;
    }
    
    const saveBtn = document.getElementById('save-btn');
    saveBtn.disabled = true;
    
    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(gameState)
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showMessage('save-load-message', '✓ Game saved successfully to cookie', 'success');
        } else {
            showMessage('save-load-message', `Error saving game: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showMessage('save-load-message', `Error saving game: ${error.message}`, 'error');
    } finally {
        saveBtn.disabled = false;
    }
}

// Load game state
async function loadGame() {
    const loadBtn = document.getElementById('load-btn');
    loadBtn.disabled = true;
    
    try {
        const response = await fetch('/api/load');
        const data = await response.json();
        
        if (data.ok && data.state) {
            gameState = data.state;
            updateStateDisplay();
            showMessage('save-load-message', '✓ Game loaded successfully from cookie', 'success');
        } else {
            const errorMsg = data.error === 'no_state' 
                ? 'No saved game found. Please save a game first.' 
                : `Error loading game: ${data.error || 'Unknown error'}`;
            showMessage('save-load-message', errorMsg, 'error');
        }
    } catch (error) {
        showMessage('save-load-message', `Error loading game: ${error.message}`, 'error');
    } finally {
        loadBtn.disabled = false;
    }
}

// Show message in specified element
function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message-area ${type}`;
    
    // For response area, use response-area class
    if (elementId === 'command-response') {
        element.className = `response-area ${type}`;
    }
}
