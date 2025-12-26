// One Breath Left - Client-side game logic

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game state
let sessionId = null;
let gameState = null;
let keys = {};
let lastUpdate = Date.now();

// Initialize game
async function initGame() {
    try {
        const response = await fetch('/api/game/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        sessionId = data.session_id;
        gameState = data.state;
        
        document.getElementById('loadingScreen').style.display = 'none';
        
        // Start game loop
        requestAnimationFrame(gameLoop);
    } catch (error) {
        console.error('Failed to start game:', error);
        alert('Failed to connect to game server');
    }
}

// Game loop
async function gameLoop() {
    const now = Date.now();
    const dt = (now - lastUpdate) / 1000;
    lastUpdate = now;
    
    // Prepare input
    const input = {
        move_x: 0,
        move_y: 0,
        running: keys['Shift']
    };
    
    if (keys['w'] || keys['ArrowUp']) input.move_y = -1;
    if (keys['s'] || keys['ArrowDown']) input.move_y = 1;
    if (keys['a'] || keys['ArrowLeft']) input.move_x = -1;
    if (keys['d'] || keys['ArrowRight']) input.move_x = 1;
    
    // Update game state on server
    try {
        const response = await fetch('/api/game/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                input: input,
                dt: dt
            })
        });
        
        const data = await response.json();
        gameState = data.state;
        
        // Render
        render();
        
        // Update UI
        updateUI();
        
        // Check for ending
        if (gameState.game.ending_triggered) {
            showEnding();
            return;
        }
    } catch (error) {
        console.error('Game update failed:', error);
    }
    
    // Continue loop
    requestAnimationFrame(gameLoop);
}

// Render game
function render() {
    if (!gameState) return;
    
    const { player, world, enemies } = gameState;
    
    // Clear canvas
    ctx.fillStyle = '#0f0f14';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Render fog overlay
    const darkness = Math.floor(255 * world.ambient_darkness);
    ctx.fillStyle = `rgba(30, 30, 40, ${world.ambient_darkness})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Render zones (relative to player)
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    world.zones.forEach(zone => {
        const screenX = centerX + (zone.x - player.x);
        const screenY = centerY + (zone.y - player.y);
        
        // Calculate distance from player
        const dx = zone.x - player.x;
        const dy = zone.y - player.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Only render if in visibility range
        if (distance < world.visibility_radius) {
            const alpha = 1 - (distance / world.visibility_radius);
            
            if (zone.explored) {
                ctx.strokeStyle = `rgba(60, 60, 80, ${alpha})`;
            } else {
                ctx.strokeStyle = `rgba(80, 80, 100, ${alpha})`;
            }
            
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(screenX, screenY, zone.radius, 0, Math.PI * 2);
            ctx.stroke();
        }
    });
    
    // Render enemies
    enemies.forEach(enemy => {
        const screenX = centerX + (enemy.x - player.x);
        const screenY = centerY + (enemy.y - player.y);
        
        const dx = enemy.x - player.x;
        const dy = enemy.y - player.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < world.visibility_radius) {
            const alpha = (1 - (distance / world.visibility_radius)) * 0.7;
            
            // Choose color based on type
            let color;
            if (enemy.type === 'shadow') color = [80, 60, 90];
            else if (enemy.type === 'whisper') color = [90, 70, 70];
            else color = [100, 50, 50];
            
            ctx.fillStyle = `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${alpha})`;
            
            if (enemy.alert) {
                // Triangle when alert
                ctx.beginPath();
                ctx.moveTo(screenX, screenY - 20);
                ctx.lineTo(screenX + 20, screenY + 20);
                ctx.lineTo(screenX - 20, screenY + 20);
                ctx.closePath();
                ctx.fill();
            } else {
                // Circle when passive
                ctx.beginPath();
                ctx.arc(screenX, screenY, 15, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    });
    
    // Render player (always at center)
    ctx.fillStyle = '#b4b4c8';
    ctx.beginPath();
    ctx.arc(centerX, centerY, 8, 0, Math.PI * 2);
    ctx.fill();
    
    // Direction indicator if moving
    if (player.velocity_x !== 0 || player.velocity_y !== 0) {
        const angle = Math.atan2(player.velocity_y, player.velocity_x);
        const endX = centerX + Math.cos(angle) * 15;
        const endY = centerY + Math.sin(angle) * 15;
        
        ctx.strokeStyle = '#b4b4c8';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    }
}

// Update UI elements
function updateUI() {
    if (!gameState) return;
    
    const { player, game, ai } = gameState;
    
    // Update stat bars
    document.getElementById('healthText').textContent = Math.floor(player.health);
    document.getElementById('healthBar').style.width = (player.health / player.max_health * 100) + '%';
    
    document.getElementById('staminaText').textContent = Math.floor(player.stamina);
    document.getElementById('staminaBar').style.width = (player.stamina / player.max_stamina * 100) + '%';
    
    document.getElementById('fearText').textContent = Math.floor(player.fear);
    document.getElementById('fearBar').style.width = player.fear + '%';
    
    // Update trust and time
    document.getElementById('trustText').textContent = Math.floor(game.trust_level * 100);
    document.getElementById('timeText').textContent = Math.floor(game.time);
    
    // Show advice if available
    const adviceBox = document.getElementById('adviceBox');
    if (ai.advice) {
        document.getElementById('adviceText').textContent = ai.advice;
        adviceBox.style.display = 'block';
    } else {
        adviceBox.style.display = 'none';
    }
}

// Accept advice
async function acceptAdvice() {
    try {
        await fetch('/api/game/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                action: 'accept_advice'
            })
        });
    } catch (error) {
        console.error('Failed to accept advice:', error);
    }
}

// Reject advice
async function rejectAdvice() {
    try {
        await fetch('/api/game/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                action: 'reject_advice'
            })
        });
    } catch (error) {
        console.error('Failed to reject advice:', error);
    }
}

// Show ending screen
async function showEnding() {
    const { game } = gameState;
    
    const endings = {
        'death': 'You took your last breath.',
        'trust': 'You became one with the voice.',
        'defiance': 'You broke free, but at what cost?',
        'balance': 'You found your own path.',
        'transcendence': 'You understood the cycle.'
    };
    
    document.getElementById('endingTitle').textContent = endings[game.ending_type] || 'The end.';
    document.getElementById('endingStats').innerHTML = `
        Time survived: ${Math.floor(game.time)}s<br>
        Trust level: ${Math.floor(game.trust_level * 100)}%<br>
        Zones explored: ${gameState.player.zones_explored}<br>
        Advice followed: ${game.advice_followed}<br>
        Advice ignored: ${game.advice_ignored}
    `;
    
    document.getElementById('endingScreen').style.display = 'flex';
    
    // Save playthrough
    try {
        await fetch('/api/game/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
    } catch (error) {
        console.error('Failed to save playthrough:', error);
    }
}

// Keyboard input
document.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
    keys[e.key] = true;
    
    // Handle advice responses
    if (e.key.toLowerCase() === 'y') {
        acceptAdvice();
    } else if (e.key.toLowerCase() === 'n') {
        rejectAdvice();
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
    keys[e.key] = false;
});

// Start game when page loads
window.addEventListener('load', initGame);
