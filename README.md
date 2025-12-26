# One Breath Left

A psychological survival game where the player is guided by an AI companion that is actually a recording from their previous playthrough.

## Concept

In "One Breath Left," you navigate a foggy, minimal world filled with abstract enemies. Your only guide is an AI companion - but this companion is actually you from your last playthrough. Every decision you make is recorded and will shape the advice given to the next player (or your next attempt).

## Features

### Core Mechanics
- **Survival System**: Manage health, stamina, and fear levels
- **Tense Exploration**: Navigate a foggy, minimal environment with limited visibility
- **Abstract Enemies**: Face psychological threats that adapt to your behavior

### AI Companion System
- **Recording Playthrough**: All your actions are recorded and saved
- **AI Guidance**: The companion gives advice based on previous player behavior
- **Trust vs Defiance**: Choose to follow or ignore the AI's advice
- **Adaptive AI**: The AI learns from player behavior and may lie or doubt itself
- **Dynamic Personality**: AI behavior changes based on how the previous player ended

### Dynamic Difficulty
- **Trust-Based Scaling**: Following advice makes the game easier; defying it makes it harder
- **Environment Changes**: The world becomes foggier and more hostile based on trust level
- **Adaptive Enemies**: Enemy behavior scales with your trust/defiance choices

### Multiple Endings
- **Death**: Succumb to the environment
- **Trust**: Complete faith in the AI companion
- **Defiance**: Complete rejection of the AI
- **Balance**: Find your own path between trust and defiance
- **Transcendence**: Understand the true nature of the cycle

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Controls

- **WASD / Arrow Keys**: Move
- **Shift**: Run (drains stamina)
- **Y**: Accept/Follow AI advice (increases trust)
- **N**: Reject/Ignore AI advice (decreases trust)
- **ESC**: Quit game

## Gameplay Tips

1. **Manage Your Resources**: Keep an eye on health, stamina, and fear levels
2. **Trust Carefully**: The AI may not always tell the truth
3. **Explore Wisely**: New zones can be safe, dangerous, or mysterious
4. **Learn from History**: The AI's advice is based on what happened before
5. **Your Legacy Matters**: Your choices will shape the next player's experience

## Technical Details

- Built with Python and Pygame
- Playthrough data stored in JSON format in `playthroughs/` directory
- Each game saves as `latest.json` (loaded next time) and a timestamped file
- Minimal graphics emphasizing atmosphere over visuals

## The Loop

1. Play the game, making choices
2. Your actions are recorded
3. On your next playthrough, the AI uses your previous choices to guide you
4. The AI's personality changes based on how you ended
5. Your trust or defiance shapes the difficulty and environment
6. Multiple endings based on your relationship with the AI

The game is about the relationship between you and your past self, mediated through an AI that may not have your best interests at heart.
