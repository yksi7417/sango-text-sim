async function initGame() {
  const r = await fetch('/api/init');
  const j = await r.json();
  renderState(j);
}

function renderState(state) {
  document.getElementById('state').textContent = JSON.stringify(state, null, 2);
}

async function sendCommand(cmd) {
  const r = await fetch('/api/echo', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command: cmd})
  });
  const j = await r.json();
  document.getElementById('output').textContent = JSON.stringify(j, null, 2);
}

async function saveStateToCookie() {
  // Ask server to save current state; the server sets the cookie
  const stateText = document.getElementById('state').textContent;
  let state;
  try { state = JSON.parse(stateText); } catch(e) { state = {note: 'manual save', raw: stateText}; }
  const r = await fetch('/api/save', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(state)
  });
  if (r.ok) {
    alert('Saved to cookie');
  } else {
    alert('Save failed');
  }
}

async function loadStateFromCookie() {
  const r = await fetch('/api/load');
  const j = await r.json();
  if (j.ok && j.state) {
    renderState(j.state);
  } else {
    alert('No saved state: ' + (j.error || JSON.stringify(j)));
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-init').addEventListener('click', initGame);
  document.getElementById('btn-send').addEventListener('click', () => {
    const cmd = document.getElementById('cmd-input').value.trim();
    if (cmd) sendCommand(cmd);
  });
  document.getElementById('btn-save').addEventListener('click', saveStateToCookie);
  document.getElementById('btn-load').addEventListener('click', loadStateFromCookie);
});
