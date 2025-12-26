# One Breath Left - Design Document

## Core Concept

"One Breath Left" is a psychological survival horror game where the player's companion AI is actually a recording from their previous playthrough. This creates a unique meta-narrative loop where each playthrough influences the next.

## Key Innovation

The "AI companion" is not a traditional AI - it's a playback system that records every action, decision, and outcome from one playthrough and uses that data to guide the next player through the same journey. This means:

1. **Your past self guides your future self**
2. **The AI can "remember" what happened**
3. **Advice is based on actual experience, not scripted**
4. **The AI's personality reflects how the previous game ended**

## Game Systems

### 1. Recording System

Every playthrough records:
- Player position and movement
- Decisions (advice followed/ignored)
- Zone explorations
- Encounters with enemies
- Trust level changes
- Time stamps for all events
- Final ending achieved

This data is saved as JSON in `playthroughs/latest.json` and loaded by the next game.

### 2. AI Companion Behavior

The AI companion:
- **Gives advice** based on what happened at similar timestamps in the previous playthrough
- **Changes personality** based on previous ending:
  - Death ending → Doubtful, uncertain
  - Trust ending → Confident, encouraging
  - Defiance ending → Deceptive, unreliable
  - Balance ending → Measured, thoughtful
  - Transcendence ending → Mysterious, knowing
- **May lie** with probability based on previous player's trust level
- **May doubt itself** if the previous player died or failed

### 3. Trust/Defiance System

- **Trust Level**: Ranges from 0.0 (complete defiance) to 1.0 (complete trust)
- **Starts at 0.5** (neutral)
- **Increases** when player follows advice (Y key)
- **Decreases** when player ignores advice (N key)

Effects of trust level:
- **High Trust (>0.7)**:
  - Clearer visibility
  - Less hostile environment
  - Easier enemy encounters (0.8x difficulty)
  - More reliable AI advice
  
- **Low Trust (<0.3)**:
  - Dense fog
  - Hostile environment
  - Harder enemy encounters (1.3x difficulty)
  - AI may mislead player

### 4. Survival Mechanics

**Health (0-100)**:
- Decreases from enemy attacks
- Slowly regenerates when fear is low
- Death at 0 health

**Stamina (0-100)**:
- Used for running (Shift key)
- Drains when running
- Regenerates when walking

**Fear (0-100)**:
- Increases from damage and enemy encounters
- Reduces visibility
- Slows movement at high levels
- Slowly decreases over time

### 5. World and Exploration

**Environment**:
- Foggy, minimal aesthetic
- Dark ambient lighting
- Visibility based on fog density and fear level

**Exploration Zones**:
- 15 zones scattered around the world
- Types: Safe, Dangerous, Mysterious
- Safe zones reduce fear
- Dangerous zones increase fear
- Tracking of zones explored for endings

### 6. Enemy System

**Abstract Enemies**:
- Three types: Shadow, Whisper, Presence
- Visual representation changes based on type
- Spawn periodically (every 20 seconds)
- Maximum of 5 enemies at once

**Enemy Behavior**:
- **Passive state**: Wander randomly
- **Alert state**: Chase player when detected
- **Detection radius**: Modified by trust level (lower trust = easier detection)
- **Attack**: Deals damage when very close
- **Visual**: Appear as abstract shapes (circles when passive, triangles when alert)

### 7. Multiple Endings

**Death Ending**:
- Player health reaches 0
- Triggers immediately

**Trust Ending**:
- Trust level ≥ 0.95
- Survive at least 180 seconds
- Player becomes "one with the voice"

**Defiance Ending**:
- Trust level ≤ 0.05
- Survive at least 180 seconds
- Player "breaks free, but at what cost?"

**Balance Ending**:
- Trust level between 0.4 and 0.6
- Survive at least 300 seconds
- Player "finds their own path"

**Transcendence Ending**:
- Explore at least 10 zones
- Maintain trust near 0.5 (±0.1)
- Player "understands the cycle"

## The Meta Loop

```
First Playthrough (No previous data)
    ↓
  AI gives generic advice
    ↓
  Player makes choices
    ↓
  Ending achieved + Data saved
    ↓
Second Playthrough (Loads previous data)
    ↓
  AI references "last person here"
    ↓
  AI personality reflects previous ending
    ↓
  Advice based on previous player's actions
    ↓
  New choices create new data
    ↓
  (Cycle repeats)
```

## Psychological Elements

1. **Trust Paradox**: Should you trust yourself from the past? Did you make good choices?

2. **Guilt**: If you fail, the next player (or your next attempt) will hear about it

3. **Self-Doubt**: The AI doubting itself is really your past self doubting

4. **Deception**: When the AI lies, is it helping or hurting? Was your past self malicious or just wrong?

5. **Legacy**: Each playthrough leaves a mark that affects the next traveler

## Technical Implementation

- **Engine**: Python + Pygame
- **Architecture**: Component-based with separate systems
- **Data Format**: JSON for playthrough recording
- **Rendering**: Minimal, atmospheric graphics emphasizing mood
- **Performance**: Lightweight, runs on most systems

## Future Enhancements (Not implemented yet)

- Multiple save slots for different "AI personalities"
- Sharing playthrough files with other players
- More complex advice generation using actual path data
- Visual representation of previous player's path
- Audio atmosphere and soundscapes
- More enemy types and behaviors
- Procedural world generation
- Achievement system for endings
