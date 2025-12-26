# Static Assets

This directory contains client-side JavaScript for the web version of One Breath Left.

## Files

- `game.js` - Main game loop, rendering, and API communication

## Game Loop

The client-side game loop:
1. Sends player input to Flask backend via `/api/game/update`
2. Receives updated game state (player, enemies, world, AI advice)
3. Renders the game state on HTML5 canvas
4. Updates UI elements (health bars, trust meter, etc.)
5. Displays AI advice when available
6. Handles endings and playthrough saving

## Rendering

- **Canvas**: 800x600px game world
- **Player-centered camera**: World scrolls, player stays in center
- **Fog effects**: Dynamic opacity based on distance and visibility
- **Abstract shapes**: Circles/triangles for enemies
- **Minimal aesthetic**: Dark colors, simple geometry

## Input Handling

- **WASD/Arrows**: Movement (sent to backend)
- **Shift**: Run toggle
- **Y/N**: Accept/reject AI advice
- **Keyboard + Click**: Dual input support

## API Integration

All API calls use fetch() with JSON:
- `POST /api/game/start` - Initialize new session
- `POST /api/game/update` - Update game state
- `POST /api/game/action` - Handle advice responses
- `POST /api/game/end` - Save playthrough
