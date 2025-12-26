#!/usr/bin/env python3
"""
Test script to verify game components work correctly
"""

import sys
import os

# Add game directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all game modules can be imported"""
    print("Testing imports...")
    try:
        from game.game_state import GameState
        from game.player import Player
        from game.world import World
        from game.ai_companion import AICompanion
        from game.enemy_manager import EnemyManager, Enemy
        from game.renderer import Renderer
        from game.input_handler import InputHandler
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_player():
    """Test player creation and basic mechanics"""
    print("\nTesting Player...")
    from game.player import Player
    
    player = Player(100, 100)
    assert player.x == 100
    assert player.y == 100
    assert player.health == 100
    assert player.stamina == 100
    assert player.fear == 0
    
    # Test movement
    player.move(1, 0)
    assert player.velocity_x > 0
    
    # Test damage
    player.take_damage(20)
    assert player.health == 80
    assert player.fear > 0
    
    print("✓ Player tests passed")
    return True

def test_world():
    """Test world creation and mechanics"""
    print("\nTesting World...")
    from game.world import World
    
    world = World()
    assert len(world.zones) == 15
    assert 0 <= world.fog_density <= 1
    assert 0 <= world.ambient_darkness <= 1
    
    # Test visibility
    visibility = world.get_visibility_radius(0)
    assert visibility > 0
    
    print("✓ World tests passed")
    return True

def test_ai_companion():
    """Test AI companion"""
    print("\nTesting AI Companion...")
    from game.ai_companion import AICompanion
    
    ai = AICompanion()
    ai.load_previous_playthrough()
    
    assert 0 <= ai.confidence <= 1
    assert 0 <= ai.honesty <= 1
    assert 0 <= ai.doubt <= 1
    
    print("✓ AI Companion tests passed")
    return True

def test_enemy_manager():
    """Test enemy management"""
    print("\nTesting Enemy Manager...")
    from game.enemy_manager import EnemyManager, Enemy
    from game.player import Player
    
    manager = EnemyManager()
    player = Player(400, 300)
    
    # Create an enemy
    enemy = Enemy(500, 300, "shadow")
    assert enemy.x == 500
    assert enemy.y == 300
    assert enemy.type == "shadow"
    
    # Test enemy behavior
    attacked = enemy.update(0.1, player, 0.5)
    assert isinstance(attacked, bool)
    
    print("✓ Enemy Manager tests passed")
    return True

def test_game_state():
    """Test game state management"""
    print("\nTesting Game State...")
    from game.game_state import GameState
    
    state = GameState()
    assert state.player is not None
    assert state.world is not None
    assert state.ai_companion is not None
    assert state.enemy_manager is not None
    
    assert state.trust_level == 0.5
    assert state.game_time == 0
    
    # Test trust mechanics
    initial_trust = state.trust_level
    state.follow_advice()
    assert state.trust_level > initial_trust
    
    state.ignore_advice()
    assert state.trust_level < initial_trust + 0.05
    
    print("✓ Game State tests passed")
    return True

def test_playthrough_recording():
    """Test playthrough recording system"""
    print("\nTesting Playthrough Recording...")
    from game.game_state import GameState
    import json
    import os
    
    state = GameState()
    
    # Record some actions
    state.record_action("move", {"x": 100, "y": 100})
    state.record_action("advice_followed", {"trust": 0.55})
    
    assert len(state.playthrough_actions) == 2
    
    # Test save (without actually writing)
    assert hasattr(state, 'save_playthrough')
    
    print("✓ Playthrough Recording tests passed")
    return True

def test_endings():
    """Test ending conditions"""
    print("\nTesting Ending Conditions...")
    from game.game_state import GameState
    
    # Test death ending
    state = GameState()
    state.player.health = 0
    state._check_ending_conditions()
    assert state.ending_triggered
    assert state.ending_type == "death"
    
    # Test trust ending
    state = GameState()
    state.trust_level = 0.96
    state.game_time = 200
    state._check_ending_conditions()
    assert state.ending_triggered
    assert state.ending_type == "trust"
    
    print("✓ Ending tests passed")
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("One Breath Left - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_player,
        test_world,
        test_ai_companion,
        test_enemy_manager,
        test_game_state,
        test_playthrough_recording,
        test_endings,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
