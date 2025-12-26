# Playthrough Files

This directory contains saved playthrough data that the AI companion uses to guide future players.

## Files

- `latest.json` - The most recent playthrough, automatically loaded by the game
- `playthrough_*.json` - Archived playthroughs with timestamps
- `example.json` - Example playthrough data structure

## Format

Each playthrough file contains:

```json
{
  "timestamp": 1234567890,       // Unix timestamp when game started
  "duration": 245.5,              // Total game time in seconds
  "ending": "death",              // How the game ended
  "final_trust": 0.35,            // Final trust level (0.0-1.0)
  "advice_followed": 8,           // Number of times advice was followed
  "advice_ignored": 15,           // Number of times advice was ignored
  "actions": [                    // Array of recorded actions
    {
      "time": 10.2,               // Time in seconds
      "type": "move",             // Action type
      "data": {...},              // Action-specific data
      "trust_level": 0.5          // Trust level at this moment
    }
  ]
}
```

## Action Types

- `move` - Player movement with position and running state
- `advice_followed` - Player pressed Y to follow advice
- `advice_ignored` - Player pressed N to ignore advice
- `zone_explored` - Player discovered a new zone

## Privacy Note

These files only contain gameplay data, no personal information.
