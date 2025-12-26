# Quick Start Guide

## Installation (5 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/camkilo/onebreathleft.git
   cd onebreathleft
   ```

2. **Install Python 3.7+** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game**
   ```bash
   python main.py
   ```
   
   Or use the launcher:
   - **Linux/Mac**: `./run.sh`
   - **Windows**: `run.bat`

## First Playthrough

### Understanding the Basics

On your first playthrough, there's no previous data, so the AI companion will give generic advice. This is your chance to:

1. **Learn the controls**
   - **WASD / Arrow Keys**: Move around
   - **Shift**: Run (watch your stamina!)
   - **Y**: Accept AI advice
   - **N**: Reject AI advice

2. **Explore the world**
   - The world is foggy and dark
   - Look for exploration zones (subtle circles)
   - Some zones are safe, others dangerous

3. **Survive**
   - Watch your health (red bar)
   - Manage stamina (blue bar)
   - Control fear (pink bar)
   - Avoid abstract enemies

4. **Make choices**
   - When the AI gives advice, decide: trust or defy?
   - Your choices affect the game difficulty
   - Following advice = easier game, clearer world
   - Ignoring advice = harder game, denser fog

### Your First Death (It's Part of the Experience)

Don't worry if you die on your first attempt! That's part of the design:

1. Your actions are recorded
2. The next time you play, the AI will reference "the last person here"
3. That person was you!
4. The AI's personality will change based on how you ended

## Second Playthrough - The Real Game Begins

Now the game becomes truly psychological:

### The AI Remembers

- **"They went left here..."** - The AI references your past choices
- **"I remember this place..."** - The AI recalls your exploration
- **"The last one who was here died..."** - The AI knows your fate

### Trust Becomes Critical

Your relationship with the AI (your past self) becomes the core mechanic:

- **High Trust Path**: Clear world, easier enemies, but are you being led?
- **Low Trust Path**: Foggy world, harder enemies, but you're independent
- **Balanced Path**: The hardest but most rewarding

### The AI May Lie

Based on your previous ending:
- If you died → AI becomes doubtful
- If you trusted too much → AI becomes confident
- If you defied it → AI becomes deceptive

## Achieving Different Endings

### Death Ending
- Lose all health
- Easiest to achieve, but affects next playthrough

### Trust Ending  
- Maintain trust ≥ 95%
- Survive 3+ minutes
- Complete faith in the AI

### Defiance Ending
- Maintain trust ≤ 5%
- Survive 3+ minutes
- Complete rejection of the AI

### Balance Ending
- Keep trust between 40-60%
- Survive 5+ minutes
- Find your own path

### Transcendence Ending
- Explore 10+ zones
- Maintain trust near 50%
- Understand the cycle

## Tips for Success

1. **Don't always trust yourself** - Your past choices might have been wrong
2. **Manage resources** - Don't run everywhere, you'll need stamina
3. **Fear is dangerous** - High fear reduces visibility and speed
4. **Enemies scale** - They get harder if you defy the AI
5. **Explore carefully** - Some zones help, others hurt
6. **Listen, then decide** - Consider the AI's advice before acting
7. **Your legacy matters** - Each playthrough shapes the next

## Understanding the Meta-Game

```
You Play → Die/Win → Data Saved
    ↓
Next Play → AI Uses Your Data → Gives "Advice"
    ↓
You Face Your Past Choices
    ↓
New Ending → New Data → Affects Next Time
```

The game is a dialogue between your past and present selves, mediated by an AI that may not have your best interests at heart.

## Troubleshooting

### Game won't start
- Ensure Python 3.7+ is installed: `python --version`
- Install pygame: `pip install pygame`

### No AI advice appearing
- This is normal on first playthrough
- The AI needs previous data to give specific advice

### Game is too hard
- Follow the AI's advice more (press Y)
- This increases trust and makes the game easier

### Game is too easy
- Reject the AI's advice more (press N)
- This decreases trust and increases difficulty

## Next Steps

- Read [DESIGN.md](DESIGN.md) for deeper understanding
- Check [README.md](README.md) for full documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

Have a question? Open an issue on GitHub!

---

**Remember**: Every choice you make becomes advice for your future self. Choose wisely.
