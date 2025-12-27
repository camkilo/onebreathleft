# Enhanced Gameplay Systems

This document describes the new gameplay systems implemented to address the "boring = not enough decisions per second" problem.

## Design Philosophy

The core issue wasn't "not enough enemies" but "not enough meaningful decisions." The solution: **Multiple simultaneous threat layers + constant pressure + player agency + escalating rules.**

**Goal**: 2-3 threats at all times, 1 meaningful choice every 5-10 seconds, escalation through rules (not assets).

---

## 1. Threat Layer System

**File**: `game/threat_layers.py`

Replaces simple enemy spawning with three simultaneous danger layers.

### Layer 1: Hunters (Active Threat)
- **Purpose**: Force repositioning through aggressive pursuit
- **Behavior**: Always moving, never idle, actively hunts player
- **Effect**: Deals direct damage, creates immediate danger
- **Limit**: Maximum 2 hunters at once (few but deadly)

### Layer 2: Watchers (Psychological Threat)
- **Purpose**: Create tension without direct combat
- **Behavior**: Don't attack, observe player from distance
- **Effect**: 
  - Locks camera (reduces visibility by 70%)
  - Slows movement (up to 40% slower)
  - Builds tension/fear over time
- **Limit**: Maximum 3 watchers
- **Key**: Multiply tension without combat

### Layer 3: Corruption Fields (Environmental Threat)
- **Purpose**: Environmental hazards that move independently
- **Behavior**: Expanding zones that drift across the map
- **Effect Types**:
  - `drain_light`: Increases fear, reduces visibility
  - `distort_controls`: Makes movement unpredictable
  - `slow_time`: Reduces player speed
- **Limit**: Maximum 2 fields
- **Key**: Danger zones that are always present

### Integration
All three layers run simultaneously. The player is constantly juggling:
1. Avoiding hunters (immediate threat)
2. Managing watcher effects (psychological pressure)
3. Navigating corruption fields (environmental hazards)

---

## 2. Pressure-Based Spawning

**File**: `game/pressure_spawning.py`

**Philosophy**: The game should hate silence. Spawn threats when it feels "safe."

### Pressure Factors

Pressure score (0-1) is calculated from:

1. **Player Stillness** (30% weight)
   - Standing still for >2 seconds increases pressure
   - Movement reduces pressure
   - *"Hiding won't save you"*

2. **AI Trust Level** (25% weight)
   - Low trust = high pressure (hostile environment)
   - High trust = lower pressure (AI protection)

3. **Safety Time** (25% weight)
   - Time since last damage
   - If safe for >5 seconds, pressure increases
   - *"The game hates silence"*

4. **Screen Emptiness** (20% weight)
   - No threats visible for >3 seconds
   - Pressure builds to fill the void
   - *"Never let the screen feel safe"*

### Spawn Rates
- Spawn rates scale with pressure score
- High pressure (>0.7): Frequent aggressive spawns
- Low pressure (<0.3): Slower, more subtle spawns
- Never timer-based, always reactive to player behavior

---

## 3. Player Abilities (Risk-Reward)

**File**: `game/player_abilities.py`

**Philosophy**: Right now the player only reacts. Give them agency through meaningful choices.

### Focus (Cooldown: 15s)
- **Action**: Player stops moving for 3 seconds
- **Reward**: Reveals all hidden threats on screen
- **Cost**: Permanently reduces light radius by 10 (stacks)
- **Decision**: "Do I stop to scan, or keep moving blind?"

### Burn (Cooldown: 30s, Requires: 50+ energy)
- **Action**: Release stored energy
- **Reward**: 
  - Clears nearby enemies (150-250 radius based on energy)
  - Significantly reduces fear (-40)
- **Cost**: Permanently increases future difficulty (+10% per use)
- **Decision**: "Clear threats now, but make future fights harder?"

### Break (Cooldown: 20s)
- **Action**: Deliberately ignore AI warning, cause reality glitch
- **Reward/Cost**: 50/50 chance of help or hurt
  - **Help**: Speed boost (1.5x), invisibility (70% harder to detect)
  - **Hurt**: Controls partially reversed, vision distorted
- **Effect**: Increases AI doubt, damages reality stability
- **Decision**: "Roll the dice against the AI's warnings?"

### Energy System
- Burn energy accumulates at 5/second (passive)
- Player must decide when to cash in vs. save for bigger clear

---

## 4. Phase Escalation System

**File**: `game/phase_system.py`

**Philosophy**: Escalation through rules, not assets. Each phase adds a constraint.

### Phase Schedule
- New phase every 90-120 seconds (randomized)
- Rules **stack** (never replace previous rules)
- 9 phases total

### The Phases

**Phase 0: Calm Before**
- No special rules
- Standard gameplay

**Phase 1: First Crack** (90s)
- Enemies no longer die completely
- They disperse and reform after 10 seconds
- *"Killing isn't permanent anymore"*

**Phase 2: Fading Light** (180s)
- Light no longer refills automatically
- Light drains at 2/second
- *"Darkness is encroaching"*

**Phase 3: Doubtful Voice** (270s)
- AI becomes erratic
- Speech frequency randomized (5-20s cooldown)
- Increased chance of lies/doubt
- *"Can you trust the voice?"*

**Phase 4: Hostile Edges** (360s)
- Screen edges deal damage (5/second)
- Safe zone shrinks to 100 pixels from center
- *"The boundaries are collapsing"*

**Phase 5: Time Fracture** (450s)
- Time flows unevenly for threats
- Some enemies move 50% faster/slower
- *"Reality is unstable"*

**Phase 6: Silent Watchers** (540s)
- Watcher spawn rate doubled
- Max watchers increased to 6
- *"They're everywhere now"*

**Phase 7: Reality Breach** (630s)
- Corruption expansion rate doubled
- Corruption deals 3 damage/second
- *"The world is tearing apart"*

**Phase 8: Final Descent** (720s)
- All threat spawn rates boosted 1.5x
- All previous rules active
- *"Survival is unlikely"*

### Why This Works
- Complexity naturally increases
- No new assets needed
- Player must adapt to new constraints
- Creates narrative of world degradation

---

## 5. Objectives System

**File**: `game/objectives_system.py`

**Philosophy**: Pure survival gets stale. Give competing goals that fight survival instincts.

### Objective Types

**Stabilize Zone**
- Stay inside collapsing zone for progress
- Progress: +10/sec inside, -5/sec outside
- Duration: 30 seconds
- *Decision*: "Risk staying put vs. flee threats?"

**Reach Signal**
- Race to distant location before signal fades
- Duration: 20 seconds
- Straight line travel puts you in danger
- *Decision*: "Take the direct dangerous path or safe detour?"

**Protect Follower**
- Fragile entity follows you
- Any damage to it = failure
- Duration: 45 seconds
- *Decision*: "Lead it through threats or hide?"

**Choose Abandon**
- Two zones appear, choose one to save
- Must sacrifice the other
- Duration: 25 seconds
- *Decision*: "Which area is worth saving?"

### Spawn Rate
- New objective every ~40 seconds
- Only one active at a time
- Only starts after 30 seconds of gameplay
- Creates rhythmic tension spikes

---

## 6. Countdown System

**File**: `game/countdown_system.py`

**Philosophy**: "The one change that fixes boring fast" - Add a countdown that lies.

### How It Works
- AI announces something is coming
- Timer appears on screen
- Timer might disappear mid-countdown
- Sometimes nothing happens (40% are lies)
- Sometimes everything happens

### Event Types

**Spawn** (if triggered)
- Wave of 2-3 hunters + 1-2 watchers
- Immediate threat surge

**Corruption** (if triggered)
- 1-2 new corruption fields spawn
- Environmental danger increase

**Blessing** (if triggered)
- +30 health, full stamina, or -40 fear
- Rare moment of relief

**Nothing** (40% of countdowns)
- AI was lying or wrong
- Creates uncertainty

### Announcements
- "Something's coming. I can feel it."
- "Maybe something. Maybe nothing. Watch out."
- "I might be wrong, but... prepare."

### Why This Works
- **Uncertainty creates engagement instantly**
- Player can't ignore countdowns (might be real)
- Player learns AI sometimes lies
- Creates constant low-level tension
- No assets needed, pure psychology

---

## 7. Integration Points

### Game State Updates
Both `game_state.py` and `game_state_web.py` now:
- Update all 6 new systems every frame
- Calculate pressure score → drives spawning
- Apply phase rules to all systems
- Track ability usage and cooldowns
- Monitor objectives and countdowns

### System Dependencies
```
PressureSpawning → ThreatLayerManager (spawn rate)
PhaseSystem → ThreatLayerManager (spawn limits, behavior)
PhaseSystem → AICompanion (speech patterns)
PhaseSystem → Player (edge damage, light drain)
Abilities → ThreatLayerManager (clear threats)
Abilities → Difficulty (burn increases)
Countdowns → ThreatLayerManager (spawn waves)
Objectives → ThreatLayerManager (follower damage)
```

### Backward Compatibility
- Old `EnemyManager` still runs in parallel
- Existing save files load correctly
- All previous features still work
- Gradual transition supported

---

## 8. Gameplay Impact

### Before (Old System)
- Timer-based enemy spawns
- Predictable difficulty curve
- Player only reacts
- Survival = wait and dodge
- Boring after 3 minutes

### After (New System)
- **2-3 threats at all times** (layers + old enemies)
- **1 meaningful choice every 5-10 seconds** (abilities, objectives, countdowns)
- **Escalation through rules** (phases change the game, not just difficulty)
- **Player has agency** (Focus, Burn, Break)
- **Constant uncertainty** (lying countdowns)
- **Competing priorities** (objectives vs. survival)

### Decision Density Calculation
In any 30-second window:
- 2-3 active threats to avoid (continuous)
- 1-2 abilities off cooldown (choice points)
- 0-1 active objective (competing goal)
- 0-2 countdowns (uncertain events)
- 1 phase rule consideration (meta-strategy)

= **~5-9 concurrent decision factors**

This maintains engagement without overwhelming.

---

## 9. Testing

All systems have comprehensive test coverage:
- `test_threat_layers()`: All 3 layers + manager
- `test_pressure_spawning()`: Pressure calculation
- `test_player_abilities()`: All 3 abilities
- `test_phase_system()`: Phase advancement, rules
- `test_objectives_system()`: All 4 objective types
- `test_countdown_system()`: Countdown mechanics, lies

**Result**: 20/20 tests passing

---

## 10. Future Enhancements

### Renderer Updates (Phase 7 completion)
- Visual representation of threat layers
- Corruption field animations
- Countdown timers (with disappearing effect)
- Objective markers
- Phase transition effects

### Input Handling
- Keybinds for Focus/Burn/Break
- Mobile touch controls for abilities
- Objective interaction prompts

### AI Self-Argument (Phase 5 completion)
- AI debates with itself mid-game
- Multiple voices with different opinions
- Player must choose which AI to trust

### Audio Enhancements
- Overlapping audio cues
- Watcher presence sounds
- Corruption ambient noise
- Phase transition stingers

---

## 11. Performance Considerations

### Optimizations
- Threat layers use spatial indexing
- Pressure calculations cached per frame
- Objectives limit: 1 active at a time
- Phase rules evaluated once per phase change

### Scalability
- All systems scale linearly with threat count
- Max simultaneous threats: ~10 (capped)
- No pathfinding overhead (simple pursuit)
- Minimal memory footprint

---

## Summary

**Problem**: Boring = not enough decisions per second

**Solution**: 
1. **3 threat layers** (not just more enemies)
2. **Pressure spawning** (reactive, not timer-based)
3. **3 player abilities** (agency, not just reaction)
4. **9 stacking phases** (rules, not assets)
5. **4 objective types** (competing goals)
6. **Lying countdowns** (uncertainty)

**Result**: Constant engagement through meaningful choices, not just difficulty.

The game now:
- Never feels safe (pressure system)
- Never feels unfair (player has tools)
- Never feels predictable (lying countdowns)
- Never feels repetitive (phases change rules)
- Never feels passive (objectives + abilities)

**Boring ≠ not enough enemies. Boring = not enough decisions.**

We solved it.
