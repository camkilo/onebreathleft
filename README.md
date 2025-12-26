# One Breath Left

A psychological survival game where the player is guided by an AI companion that is actually a recording from their previous playthrough.

## Play Online

**Live Demo**: [Deploy on Render](https://render.com) or [Deploy on Vercel](https://vercel.com)

The game is available in two versions:
- **Web Version** (recommended): Play directly in your browser
- **Desktop Version**: Download and run locally with Python + Pygame

## Web Version (Browser-Based)

### Quick Start
1. Visit the deployed URL (Render or Vercel)
2. Game loads automatically in your browser
3. Use WASD to move, Shift to run
4. Press Y to follow AI advice, N to ignore it

### Deploy Your Own Instance

#### Deploy on Render
1. Fork this repository
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect the `render.yaml` configuration
6. Click "Create Web Service"
7. Your game will be live at `https://your-app.onrender.com`

#### Deploy on Vercel
1. Fork this repository
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New..." → "Project"
4. Import your GitHub repository
5. Vercel will auto-detect the `vercel.json` configuration
6. Click "Deploy"
7. Your game will be live at `https://your-app.vercel.app`

### Local Development (Web Version)
```bash
# Install dependencies
pip install -r requirements-web.txt

# Run the web server
python app.py

# Open browser to http://localhost:5000
```

## Desktop Version (Pygame)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Desktop Version Controls

- **WASD / Arrow Keys**: Move
- **Shift**: Run (drains stamina)
- **Y**: Accept/Follow AI advice (increases trust)
- **N**: Reject/Ignore AI advice (decreases trust)
- **ESC**: Quit game

### Web Version Controls

- **WASD / Arrow Keys**: Move
- **Shift**: Run (drains stamina)
- **Y / Click "Follow"**: Accept AI advice (increases trust)
- **N / Click "Ignore"**: Reject AI advice (decreases trust)

## Game Features

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
